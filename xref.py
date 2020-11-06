import subprocess
import re
import sys
from subprocess import call

file_name = sys.argv[1]
executable_name = sys.argv[2]
opt_level = sys.argv[3]

call(["rustc", "-g","-C", "opt-level="+ opt_level,"-o",executable_name, file_name])

f = open('objdump.txt', 'w')
call(["objdump", "-d", executable_name], stdout=f)
f.close()

f = open('output.txt', 'w')
# subprocess.run(["llvm-dwarfdump", "-o", "output.txt", "--debug-line", "main"], check=True)
call(["llvm-dwarfdump", "-o", "output.txt", "--debug-line", executable_name], stdout=f)
f.close()

### READ FROM RUST FILE ###
rust_code = {}
fc = open(file_name, 'r')
count = 1
for line in fc.readlines():
    rust_code[count] = line
    count += 1
fc.close()
#for x, y in rust_code.items():
#    print(x, y)

### READ FROM LLVM OUTPUT FILE ###
"""
from output.txt file (file that contains llvm drawfdrump output), extracts from 
the relevant table 2 dictionaries: 
address_line = {<address> : <line>} - dictionary of address and the corresponding line in the source code
line_dict = {<line> : <address>} - dictionary of a line and the first address in the assembly code that executes that line
"""
line_number = 0
cur_line = 0
start = False
start_address = ""
line_dict = {}
pattern = re.compile(r"(0x0{12})([a-z0-9]{4})")
address_line = {}
prev_line = 1
with open('output.txt', 'r') as llvm:
    for line in llvm:
        line_number += 1
        if file_name in line:
            break

    placeholder = 0 
    while(llvm.readline().strip() != ''):
        placeholder += 1

    llvm.readline(); llvm.readline()

    for line in llvm:
        if line.strip() == '':
            break
        m = pattern.match(line)
        # if matched, we take out the actual address part
        if m:
            memory_addr = m.group(2)
            
            # split the line by whitespaces
            tup = tuple(part for part in re.split(r"\s+", line) if part)
            # if the line in the table is 0, match it to the line in the prevous row (prev_line)
            if not start and int(tup[1]) > 0 and int(tup[1]) < count:
                start_address = memory_addr
                start = True
            if tup[1] == '0':
                address_line[memory_addr] = prev_line
            # if not, then the value of this current memory address in the dict is the line value in the table
            else: 
                address_line[memory_addr] = int(tup[1])
                prev_line = int(tup[1])
                # put the address value in line_dict if this is the first time the line is executed in the assembly code
                if int(tup[1]) not in line_dict.keys() and int(tup[1]) < count :
                    line_dict[int(tup[1])] = memory_addr

end_address = list(address_line.keys())[-1]
start_int = int("0x"+start_address, 16)
end_int = int("0x"+end_address, 16)
llvm.close()

# for x, y in address_line.items():
#     print(x, y)

### READ FROM OBJDUMP FILE ###
"""""
from the objdump.txt file, extract:
- assembly_dict =  {<address>: (<address>, <bytes>, <instruction>)}
- ref_dict = {<address>: <address>}
- code_block = list of tuples {<index>, (<line number>, [list of corresponding assembly addresses], not-grayed)}
index is the counter starting from 1
line number: the line number from rust source file

"""""
addr_to_line_dict = {}
assembly_dict = {}
ref_dict = {}
code_block = {1: (0, [], False)}
index = 1
fr = open('objdump.txt', 'r')
obj_pattern = re.compile(r"[\s]{4}[a-z0-9]{4}.*")

# since the addresses presented on the HTML file should only be in the range of start and end addresses
# only starts reading when cur address >= start_address and stops when cur address > end_address
start_code = False
for line in fr.readlines():
    m = obj_pattern.match(line)
    if m:
        address = m.group()[4:8]
        tup = tuple(re.sub(r"\:|\s+", " ", part) for part in m.group().split('\t') if part) 
        assembly_dict[address] = tup
        addr_to_line_dict[address] = line.split(":")[1]

        # add address to code_block
        # if address has a corresponding line in the table (based on address_line)
        ad_str = "0x" + address
        ad_int = int(ad_str, 16)
        if ad_int >= start_int: 
            start_code = True
        if ad_int > end_int:
            break
        if start_code: 
            if len(tup) > 2: 
                instruction = tup[2].split(" ")
                if instruction[0].startswith("j") or (instruction[0].startswith("callq")):
                    match = re.match(r'[a-z0-9]{4}', instruction[1])
                    if match:
                        adref = instruction[1][0:4]
                        ref_dict[address] = adref
            if address in address_line.keys():
                # get the line corresponding to that address
                cur_line = address_line[address]
                # if this line is equal to the line in the current block, add it in the list
                # {1: (3, [7200])} => {1: (3, [7200, 7204])}
                if cur_line == code_block[index][0]: 
                    code_block[index][1].append(address)
                # else, start a new block
                else: 
                    index += 1
                    # if this is the code block when the line is executed in the fist time  
                    # ({line: address} value appears in line_dict), set the 3rd tuple of the block to be True  
                    code_block[index] = (int(address_line[address]), [address], False)
                    if line_dict[code_block[index][0]] == address: 
                        code_block[index] = (int(address_line[address]), [address], True)    
            # if address doesn't has a corresponding line in the table, put it in the current block
            else:
                code_block[index][1].append(address)
    
fr.close()
# for x, y in code_block.items():
#     print(x, y)

### WRITE TO HTML ###
html = open("cross-indexer.html", "w+")
html.write("""
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>xref</title>
        <script src="https://cdn.jsdelivr.net/gh/google/code-prettify@master/loader/run_prettify.js"></script>
        <style>
            .code-block
            {
                display: table;
                box-sizing: border-box;
                position: relative;
                table-layout: fixed;
                width: 100%;
                border: 2px solid black;
                border-radius: 5px;
            }
            .grayed{
                background-color: #cccccc;
            }
            pre
            {
                margin: 0;
                overflow: auto;
                white-space: pre-wrap;
                word-wrap: break-word;
            }
            .bgColor{
                background-color: cyan;
            }
            .asm-block {
                    font-size: 10pt;
                    font-family: 'Courier New', Courier, monospace;
            }
            .src-block {
                    width: 50%;
                    display: table-cell;
                    vertical-align: top;
                    padding-top: -5px;
                    font-size: 10pt;
                    font-family: 'Courier New', Courier, monospace;
            }
            li.L0, li.L1, li.L2, li.L3,
            li.L5, li.L6, li.L7, li.L8
            {
                list-style-type: decimal !important;
            }
        </style>
    </head>
    <h1>XREF</h1>
    <body>
""")

for key in code_block.keys():
    tuple = code_block[key]
    line_num = tuple[0]
    addr_list = tuple[1]
    not_grayed = tuple[2]
    if line_num == 0:
        continue
    
    html.write("""
        <div class="code-block">
    """)

    html.write("""
        <div class="asm-block">
    """)
    i = 1 # for alternating the background color
    for addr in addr_list:
        if i % 2 == 0:
            html.write('<pre class="bgColor">' + '<a name="'+addr+'" href="#'+addr+'">'+addr+ "</a>"+ ":" + addr_to_line_dict[addr])
        else:
            html.write('<pre>' + '<a name="'+addr+'" href="#'+addr+'">'+addr+ "</a>"+ ":" + addr_to_line_dict[addr])
            
        if addr in ref_dict.keys():
            jump_addr = ref_dict[addr]
            html.write("REF TO " + '<a href="#'+jump_addr+'">'+jump_addr+"</a>"+"</pre>\n")
        else:
            html.write("</pre>\n")
        i +=1
            

    html.write("</div>")
    html.write("""
        <div class="src-block">""")
    
    html.write("<p")
    if not not_grayed:
        html.write(""" class="grayed" """)
    html.write(">" + str(key) + "." + rust_code[line_num] + "</p>\n")
    html.write("""</div>""")

    html.write("</div>\n")

html.write("</body>")
html.write("</html>")
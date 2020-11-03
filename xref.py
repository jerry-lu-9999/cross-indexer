import subprocess
import re
from subprocess import call

subprocess.call("date", shell=True)

f = open('objdump.txt', 'w')
call(["objdump", "-d", "example"], stdout=f)
f.close()

f = open('output.txt', 'w')
# subprocess.run(["llvm-dwarfdump", "-o", "output.txt", "--debug-line", "main"], check=True)
call(["llvm-dwarfdump", "-o", "output.txt", "--debug-line", "example"], stdout=f)
f.close()

### READ FROM LLVM OUTPUT FILE ###
line_number = 0
line_dict = {}
pattern = re.compile(r"(0x0{12})([a-z0-9]{4})")
with open('output.txt', 'r') as llvm:
    for line in llvm:
        line_number += 1
        if "example.rs" in line:
            break
    for i in range(line_number, line_number + 6):
        llvm.readline()
    for line in llvm:
        if line.strip() == '':
            break
        m = pattern.match(line)
        # if matched, we take out the actually address part
        if m:
            memory_addr = m.group(2)
            #print(memory_addr)
            tup = tuple(part for part in re.split(r"\s+", line) if part)
            if tup[1] not in line_dict:
                line_dict.update({tup[1]:[memory_addr]})
            else:
                line_dict[tup[1]].append(memory_addr)
            #print(tup)
#for x, y in line_dict.items():
#   print(x, y)

### READ FROM OBJDUMP FILE ###
"""""
from the objdump.txt file, extract:
- assembly_dict =  {<address>: (<address>, <bytes>, <instruction>)}
- ref_dict = {<address>: <address>}
"""""
assembly_dict = {}
ref_dict = {}
fr = open('objdump.txt', 'r')
obj_pattern = re.compile(r"[\s]{4}[a-z0-9]{4}.*")
for line in fr.readlines():
    m = obj_pattern.match(line)
    if m:
        address = m.group()[4:8]
        tup = tuple(re.sub(r"\:|\s+", " ", part) for part in m.group().split('\t') if part) 
        assembly_dict[address] = tup
        if len(tup) > 2: 
            instruction = tup[2].split(" ")
            if instruction[0].startswith("j") | (instruction[0].startswith("callq")):
                match = re.match(r'[a-z0-9]{4}', instruction[1])
                if match:
                    adref = instruction[1][0:4]
                    ref_dict[address] = adref

#for x, y in assembly_dict.items():
#    print(x, y)
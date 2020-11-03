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

# 715
line_number = 0
pattern = re.compile("(0x0{12})(\d{4})")
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
            print(memory_addr)
            line_num = line.split("\s+")[1]
            print(line_num)


import subprocess
from subprocess import call

subprocess.call("date", shell=True)

f = open('objdump.txt', 'w')
call(["objdump", "-d", "example"], stdout=f)
f.close()

f = open('output.txt', 'w')
# subprocess.run(["llvm-dwarfdump", "-o", "output.txt", "--debug-line", "main"], check=True)
call(["llvm-dwarfdump", "-o", "output.txt", "--debug-line", "example"], stdout=f)
f.close()

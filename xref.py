import subprocess

subprocess.call("date", shell=True)

subprocess.run(["objdump", "-d", "main"], check=True)

subprocess.run(["llvm-dwarfdump", "-o", "output.txt", "--debug-line", "main"], check=True)


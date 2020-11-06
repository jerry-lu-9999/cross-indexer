# cross-indexer

Thu Hoang, Jiahao Lu

How to compile:

The ONLY command you need: python3 xref.py [filename.rs] [exectuable name] [level]

level is either 0 or 1 or 2 or 3

For simplicity, our python script will compile the rust file internally at the very beginning of our program, and then generate objdump file(objump.txt) and llvm file(output.txt)

For each file, including the original rust file, we have dictionaries from line number to the actual code

We have detailed comments for each block of code
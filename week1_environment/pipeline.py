import sys
import pandas as pd

# print out all the args
print(sys.argv) # arg[0] = name of file, arg[1] = whatever we pass

# store what we pass in as an arg into a vriable
day = sys.argv[1]

# TODO some work with pandas

print(f"Job finished successfully for day = f{day}")
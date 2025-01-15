import sys
import pandas as pd

# Print out all the args
print("Arguments: ", sys.argv) # arg[0] = name of file, arg[1] = whatever we pass

# Store what we pass in as an arg into a variable
# To use when running Docker container, run: `docker run -it test:pandas 2021-01-15`
day = sys.argv[1]

# TODO
# Fancy data manipulation

print(f"Job successfully finished for day = {day}")
import sys
import os
from data import openIterationsOfProblemSet
from problemInstance import ProblemInstance

if sys.argv[1] in ["help", "--help", "-h"]: # if the user gave one of these arguments on the command line then a help message is ourputted
    """ there's three types of problems in Solomon's instances:
    - C - clustered customers
    - R - uniformly distributed customers
    - RC - a mix of R and C
    """
    
    print(f"To execute a problem set, please enter a set's details. The details required, and in this order, are:{os.linesep} 1. Amount of customers - can be either '25', '50' or '100'{os.linesep} 2. Type of problem - can be either 'C', 'R', or 'RC'{os.linesep} 3. Problem set - can be either '1' or '2'{os.linesep}An example command is: \"main.py 25 RC 2\"")
else:
    problemInstances = openIterationsOfProblemSet(sys.argv[1], sys.argv[2], sys.argv[3])
    
    if not problemInstances == []: # this output will be removed later; it only exists now to show that the problem instances were loaded correctly
        print([problemInstance.__str__() for problemInstance in problemInstances])
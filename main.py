import sys
import os
from typing import List
from problemInstance import ProblemInstance
from data import openIterationsOfProblemSet
from MMOEASA.mmoeasa import MMOEASA
from MMOEASA.constants import MMOEASA_POPULATION_SIZE

def executeMMOEASA(problemInstances: List[ProblemInstance]) -> None:
    for i in enumerate(problemInstances):
        problemInstances[i].calculateDistances()

    MMOEASA(problemInstances[0], MMOEASA_POPULATION_SIZE, 10, 40, 0.25, 0.25, 100, 20, 10)

if __name__ == '__main__':
    if not len(sys.argv) > 1:
        print("If you're unsure how to use the application, type h (help) for information")
    elif sys.argv[1] in ["help", "h"]: # if the user gave one of these arguments on the command line then a help message is ourputted
        """ there's multiple types of problems in Solomon's instances, here's what they are:
        - 25 - 25 customers
        - 50 - 50 customers
        - 100 - 100 customers

        - C - clustered customers
        - R - uniformly distributed customers
        - RC - a mix of R and C

        - 1 - destinations with narrow time windows
        - 2 - destinations with wide time windows
        """
        
        print(f"To execute a problem set, please enter a set's details. The details required, and in this order, are:{os.linesep} 1. Amount of customers - can be either '25', '50' or '100'{os.linesep} 2. Type of problem - can be either 'C', 'R', or 'RC'{os.linesep} 3. Problem set - can be either '1' or '2'{os.linesep}An example command is: \"main.py 25 RC 2\"")
    else:
        problemInstances = openIterationsOfProblemSet(*sys.argv[1:])
        
        if not problemInstances == []: # this output will be removed later; it only exists now to show that the problem instances were loaded correctly
            print([problemInstance.__str__() for problemInstance in problemInstances])
        
        # Terminating Condition (TC) is set to 40 seconds

        executeMMOEASA(problemInstances)

import sys
import os
import json
from problemInstance import ProblemInstance
from data import openIterationsOfProblemSet
from MMOEASA.mmoeasa import MMOEASA
from MMOEASA.constants import MMOEASA_POPULATION_SIZE

def executeMMOEASA(problemInstance: ProblemInstance) -> None:
    #for i, _ in enumerate(problemInstances):
        #print(problemInstances[i].name, len(problemInstances[i].MMOEASA_distances))
    #problemInstances[i].calculateDistances()
    problemInstance.calculateDistances()

    #for instance in problemInstances:
    #print(instance.name)
    with open("MMOEASA/hypervolumes.json") as json_file:
        Hypervolumes = json.load(json_file)
        ND_solutions = MMOEASA(problemInstance, MMOEASA_POPULATION_SIZE, 10, 100000, 25, 25, 100.0, 50.0, 10.0, Hypervolumes[problemInstance.name])
        for solution in ND_solutions:
            print(str(solution))

if __name__ == '__main__':
    if not len(sys.argv) > 1:
        print("If you're unsure how to use the application, type h (help) for information")
    elif sys.argv[1] in ["--help", "-h"]: # if the user gave one of these arguments on the command line then a help message is ourputted
        print(f"There's multiple types of problems in Solomon's instances, here's what they are:{os.linesep}{os.linesep}"
              f"- Number of customers:"
              f"  - 25 - 25 customers{os.linesep}"
              f"  - 50 - 50 customers{os.linesep}"
              f"  - 100 - 100 customers{os.linesep}{os.linesep}"
              f"- Customers' location:"
              f"  - C - clustered customers{os.linesep}"
              f"  - R - uniformly distributed customers{os.linesep}"
              f"  - RC - a mix of R and C{os.linesep}{os.linesep}"
              f"- Width of deliveries' time windows:"
              f"  - 1 - destinations with narrow time windows{os.linesep}"
              f"  - 2 - destinations with wide time windows{os.linesep}{os.linesep}"
            f"To execute a problem set, please enter a set's details. The details required, and in this order, are:{os.linesep}"
              f"  1. Amount of customers - can be either '25', '50' or '100'{os.linesep}"
              f"  2. Type of problem - can be either 'C', 'R', or 'RC'{os.linesep}"
              f"  3. Problem set - can be either '1' or '2'{os.linesep}{os.linesep}"
            f"An example command is: \"main.py 25 RC 2\""
        )
    else:
        problemInstances = openIterationsOfProblemSet(sys.argv[1])#*sys.argv[1:])

        #if len(problemInstances) > 0:
            #print([problemInstance.__str__() for problemInstance in problemInstances])

        executeMMOEASA(problemInstances)

import sys
import os
import json
from problemInstance import ProblemInstance
from data import open_problem_instance
from MMOEASA.mmoeasa import MMOEASA, TWIH_ref_point
from MMOEASA.evaluation import calculate_median_Hypervolumes
from MMOEASA.constants import POPULATION_SIZE
from Ombuki.ombuki import Ombuki
from typing import List

def execute_MMOEASA(problem_instance: ProblemInstance, Hypervolumes: List[float]=None) -> None:
    num_customers = len(problem_instance.nodes) - 1
    
    TC = 0 # termination condition = the number of iterations to perform
    if num_customers == 25:
        TC = 100000
    elif num_customers == 50:
        TC = 50000
    elif num_customers == 100:
        TC = 2000

    ND_solutions = MMOEASA(problem_instance, POPULATION_SIZE, 10, TC, 25, 25, 100.0, 50.0, 30.0) # TODO: try changing the numerical parameters to command line arguments and experiment with them
    for solution in ND_solutions:
        print("\n", str(solution))
    print(calculate_median_Hypervolumes(ND_solutions, TWIH_ref_point(problem_instance))) # TODO: currently, the TWIH usually has a cargo unbalance of 20 and the ND_solutions usually have as low as 90; therefore, TWIH_ref_point's Hypervolume may need to be multiplied by a higher value

def execute_Ombuki(problem_instance: ProblemInstance, Hypervolumes: List[float]=None) -> None:
    ND_solutions = Ombuki(problem_instance, 300, 350, 80, 10)
    for solution in ND_solutions:
        print("\n", str(solution))

if __name__ == '__main__':
    if not len(sys.argv) > 1:
        print("If you're unsure how to use the application, give the argument -h (--help) for information")
    elif sys.argv[1] in {"--help", "-h"}: # if the user gave one of these arguments on the command line then a help message is ourputted
        print(f"Format: main(.py) [ algorithm ] [ problem instance ] [ acceptance criteria ]{os.linesep}{os.linesep}"
              f"The algorithms and acceptance criteria available to solve the problem are:{os.linesep}"
              f" - MMOEASA{os.linesep}"
              f" - Ombuki{os.linesep}{os.linesep}"
              f"There's multiple types of problems in Solomon's instances, and here's what they are:{os.linesep}"
              f" - Number of customers:{os.linesep}"
              f"   - 25 - 25 customers{os.linesep}"
              f"   - 50 - 50 customers{os.linesep}"
              f"   - 100 - 100 customers{os.linesep}"
              f" - Customers' location:{os.linesep}"
              f"   - C - clustered customers{os.linesep}"
              f"   - R - uniformly distributed customers{os.linesep}"
              f"   - RC - a mix of R and C{os.linesep}"
              f" - Width of deliveries' time windows:{os.linesep}"
              f"   - 1 - destinations with narrow time windows{os.linesep}"
              f"   - 2 - destinations with wide time windows{os.linesep}{os.linesep}"
              f"To execute a problem set, please enter a problem's filename. The details required, and the argument format, are:{os.linesep}"
              f" - solomon_[ number of customers ]/[ customers' location ][ width of time windows ]XX.txt{os.linesep}"
              f" - Where XX is the instance number; see the folder \"solomon_[ number of customers ]\" for available instances{os.linesep}{os.linesep}"
              f"An example command is: \"main.py MMOEASA solomon_100/C101.txt\"")
    elif len(sys.argv) == 4:
        if not sys.argv[3].upper() in {"MMOEASA", "OMBUKI"}:
            exc = ValueError(f"Acceptance criterion \"{sys.argv[1]}\" was not recognised")
            raise exc
        problem_instance = open_problem_instance(sys.argv[2], sys.argv[3])

        problem_instance.calculate_distances()

        if sys.argv[1].upper() == "MMOEASA":
            execute_MMOEASA(problem_instance)
        elif sys.argv[1].upper() == "OMBUKI":
            execute_Ombuki(problem_instance)
        else:
            exc = ValueError(f"Algorithm \"{sys.argv[1]}\" was not recognised")
            raise exc

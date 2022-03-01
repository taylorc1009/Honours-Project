import sys
import os
from typing import List, Union, Tuple, Dict
from MMOEASA.mmoeasaSolution import MMOEASASolution
from Ombuki.ombukiSolution import OmbukiSolution
from CustomGA.customGASolution import CustomGASolution
from problemInstance import ProblemInstance
from data import open_problem_instance
from MMOEASA.mmoeasa import MMOEASA
from MMOEASA.constants import POPULATION_SIZE
from Ombuki.ombuki import Ombuki
from evaluation import calculate_area
from CustomGA.custom import CustomGA

def execute_MMOEASA(problem_instance: ProblemInstance) -> Tuple[List[Union[MMOEASASolution, OmbukiSolution]], Dict[str, int]]:
    num_customers = len(problem_instance.nodes) - 1
    TC = 0 # termination condition = the number of iterations to perform
    if num_customers == 25:
        TC = 10000
    elif num_customers == 50:
        TC = 5000
    elif num_customers == 100:
        TC = 200

    return MMOEASA(problem_instance, POPULATION_SIZE, 10, TC, 25, 25, 100.0, 50.0, 30.0)

def execute_Ombuki(problem_instance: ProblemInstance) -> Tuple[List[Union[OmbukiSolution, MMOEASASolution]], Dict[str, int]]:
    return Ombuki(problem_instance, 300, 350, 80, 10)

def execute_Custom(problem_instance: ProblemInstance) -> Tuple[List[CustomGASolution], Dict[str, int]]:
    return CustomGA(problem_instance, 300, 350, 80, 10)

if __name__ == '__main__':
    if not len(sys.argv) in {2, 4} or (len(sys.argv) == 2 and sys.argv[1] not in {"--help", "-h"}):
        print("If you're unsure how to use the application, give the argument -h (--help) for information")
    elif sys.argv[1] in {"--help", "-h"}: # if the user gave one of these arguments on the command line then a help message is outputted
        if len(sys.argv) == 2:
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
        else:
            print("Argument \"-h\"/\"--help\" does not take any arguments")
    else:
        if not sys.argv[3].upper() in {"MMOEASA", "OMBUKI"}:
            exc = ValueError(f"Acceptance criterion \"{sys.argv[1]}\" was not recognised")
            raise exc
        problem_instance = open_problem_instance(sys.argv[2], sys.argv[3])

        problem_instance.calculate_distances()

        nondominated_set, statistics = None, None
        if sys.argv[1].upper() == "MMOEASA":
            nondominated_set, statistics = execute_MMOEASA(problem_instance)
        elif sys.argv[1].upper() == "OMBUKI":
            nondominated_set, statistics = execute_Ombuki(problem_instance)
        elif sys.argv[1].upper() == "CUSTOM":
            if sys.argv[3].upper() != "OMBUKI":
                print("Only Ombuki's acceptance criterion is implemented in the custom algorithm")
            else:
                nondominated_set, statistics = execute_Custom(problem_instance)
        else:
            exc = ValueError(f"Algorithm \"{sys.argv[1]}\" was not recognised")
            raise exc

        for solution in nondominated_set:
            print(f"{os.linesep + str(solution)}")
        print(f"{os.linesep}Algorithm {sys.argv[3]}'s statistics:")
        for statistic, value in statistics.items():
            print(f" - {statistic}: {value}")
        print(f"{os.linesep + str(problem_instance)}")
        calculate_area(problem_instance, nondominated_set, sys.argv[1], sys.argv[3])

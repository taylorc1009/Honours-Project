import sys
import os
from typing import List, Union, Tuple, Dict
from MMOEASA.mmoeasaSolution import MMOEASASolution
from Ombuki.ombukiSolution import OmbukiSolution
from CustomGA.customGASolution import CustomGASolution
from problemInstance import ProblemInstance
from data import open_problem_instance
from MMOEASA.mmoeasa import MMOEASA
from Ombuki.ombuki import Ombuki
from evaluation import calculate_area
from CustomGA.custom import CustomGA

def execute_MMOEASA(problem_instance: ProblemInstance) -> Tuple[List[Union[MMOEASASolution, OmbukiSolution]], Dict[str, int]]:
    from MMOEASA.parameters import POPULATION_SIZE, MULTI_STARTS, TERMINATION_CONDITION_ITERATIONS, TERMINATION_CONDITION_SECONDS, TERMINATION_CONDITION_TYPE, CROSSOVER_PROBABILITY, MUTATION_PROBABILITY, TEMPERATURE_MAX, TEMPERATURE_MIN, TEMPERATURE_STOP
    return MMOEASA(problem_instance, POPULATION_SIZE, MULTI_STARTS, TERMINATION_CONDITION_SECONDS, TERMINATION_CONDITION_TYPE, CROSSOVER_PROBABILITY, MUTATION_PROBABILITY, TEMPERATURE_MAX, TEMPERATURE_MIN, TEMPERATURE_STOP)

def execute_Ombuki(problem_instance: ProblemInstance) -> Tuple[List[Union[OmbukiSolution, MMOEASASolution]], Dict[str, int]]:
    from Ombuki.parameters import POPULATION_SIZE, TERMINATION_CONDITION_ITERATIONS, TERMINATION_CONDITION_SECONDS, TERMINATION_CONDITION_TYPE, CROSSOVER_PROBABILITY, MUTATION_PROBABILITY
    return Ombuki(problem_instance, POPULATION_SIZE, TERMINATION_CONDITION_SECONDS, TERMINATION_CONDITION_TYPE, CROSSOVER_PROBABILITY, MUTATION_PROBABILITY)

def execute_Custom(problem_instance: ProblemInstance) -> Tuple[List[CustomGASolution], Dict[str, int]]:
    from CustomGA.parameters import POPULATION_SIZE, TERMINATION_CONDITION_ITERATIONS, TERMINATION_CONDITION_SECONDS, TERMINATION_CONDITION_TYPE, CROSSOVER_PROBABILITY, MUTATION_PROBABILITY
    return CustomGA(problem_instance, POPULATION_SIZE, TERMINATION_CONDITION_SECONDS, TERMINATION_CONDITION_TYPE, CROSSOVER_PROBABILITY, MUTATION_PROBABILITY)

if __name__ == '__main__':
    argc = len(sys.argv)
    if not 2 <= argc <= 4 or (argc == 2 and sys.argv[1] not in {"--help", "-h"}):
        print("If you're unsure how to use the application, give the argument -h (--help) for information")
    elif sys.argv[1] in {"--help", "-h"}: # if the user gave one of these arguments on the command line then a help message is outputted
        if argc == 2:
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
        if sys.argv[1].upper() == "CUSTOM":
            if argc == 3:
                sys.argv.append("Ombuki")
            else:
                exc = ValueError("Custom algorithm should not be given a pre-determined acceptance criterion; it only has one")
                raise exc

        if not sys.argv[3].upper() in {"MMOEASA", "OMBUKI"}:
            exc = ValueError(f"Acceptance criterion \"{sys.argv[3]}\" was not recognised")
            raise exc
        problem_instance = open_problem_instance(sys.argv[2], sys.argv[3])

        nondominated_set, statistics = None, None
        if sys.argv[1].upper() == "MMOEASA":
            nondominated_set, statistics = execute_MMOEASA(problem_instance)
        elif sys.argv[1].upper() == "OMBUKI":
            nondominated_set, statistics = execute_Ombuki(problem_instance)
        elif sys.argv[1].upper() == "CUSTOM":
            nondominated_set, statistics = execute_Custom(problem_instance)
        else:
            exc = ValueError(f"Algorithm \"{sys.argv[1]}\" was not recognised")
            raise exc

        for solution in nondominated_set:
            print(f"{os.linesep + str(solution)}")
        print(f"{os.linesep}Algorithm \"{sys.argv[1]}'s\" statistics:")
        for statistic, value in statistics.items():
            print(f" - {statistic}: {value}")
        print(f"{os.linesep + str(problem_instance)}")
        calculate_area(problem_instance, nondominated_set, sys.argv[1], sys.argv[3])

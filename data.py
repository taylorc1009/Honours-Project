import re
from pathlib import Path
from node import Node
from problemInstance import ProblemInstance
from MMOEASA.solution import Solution

def loadInstance(filename) -> ProblemInstance:
    try:
        with open(filename, 'r') as file:
            problemInstance = None
            problemName = file.readline().strip() # because the problem name is the first line in the text files, this line quickly adds it to a variable (so we can add it to a "ProblemInstance" object later"
            next(file) # skips the first line (containing the problem name), preventing it from being iterated over

            for line in file:
                if line is not None and not re.search('[a-zA-Z]', line): # checks if the current line contains any characters; we don't want to work with any of the alphabetical characters in the text files, only the numbers
                    curLine = line.split()
                    if curLine: # prevents any work being done with empty lines (lines that contained only a new line; '\n')
                        if len(curLine) == 2: # if the current line only contains two numbers then it's the line that holds only the amount of vehicles and vehicles' capacity, so use them to make a "ProblemInstance"
                            problemInstance = ProblemInstance(problemName, *curLine, nodes=dict())
                        else: # if the current line doesn't contain only two values, it will, instead, always contain seven and lines with seven values represent destinations
                            node = Node(*curLine)
                            problemInstance.nodes[int(node.number)] = node

        return problemInstance
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Couldn't open file \"{filename}\"\nCause: {e}")

def openIterationsOfProblemSet(filename) -> ProblemInstance:#amountOfCustomers, typeOfProblem, problemSet) -> List[ProblemInstance]:
    #problemInstances = []
    #partialPath = f"solomon_{amountOfCustomers}/{typeOfProblem.upper()}{problemSet}"

    # is this neater than the for loop below? 
    # the for loop allows for a more helpful error as it shows which specific directory the file couldn't be found in and the file name it was searching for
    #i = 1
    #path = f"{partialPath}{1:02}.txt"
    #while(os.path.isfile(path)):
        #problemInstances.append(loadInstance(path))

        #i += 1
        #path = f"{partialPath}{i:02}.txt"

    #if i == 1:
    #    print(f"Couldn't open file set \"solomon_{amountOfCustomers}/{typeOfProblem}{problemSet}xx.txt\"\n")
    
    #for i in range(1, sys.maxsize): # "sys.maxsize" is almost the same as "INT_MAX"; it's a dummy value that will never be reached
    try:
        return loadInstance(filename)#f"{partialPath}{i:02}.txt")
        #problemInstances.append(loadInstance(f"{partialPath}{i:02}.txt"))
    except FileNotFoundError as e: # if the file is not found, then we've either iterated over every file in the problem set or the problem set details entered are incorrect
        #if i == 1: # if the problem set's details are incorrect then "i" will still be 1, so, if it is, output an error message
        print(e)
        #break

    #return problemInstances

def write_solution_for_validation(solution: Solution) -> None:
    relative_path = str(Path(__file__).parent.resolve()) + "\\MMOEASA\\validator\\solution.csv"

    with open(relative_path, "w+") as csv:
        csv.write(f"{solution.total_distance},{solution.distance_unbalance},{solution.cargo_unbalance},{len(solution.vehicles)}\n")
        for vehicle in solution.vehicles:
            csv.write(f"{vehicle.current_capacity},{vehicle.route_distance},{len(vehicle.destinations)}\n")
            for destination in vehicle.destinations:
                csv.write(f"{destination.arrival_time},{destination.departure_time},{destination.wait_time}\n")
                node = destination.node
                csv.write(f"{node.number},{node.x},{node.y},{node.demand},{node.ready_time},{node.due_date},{node.service_duration}\n")

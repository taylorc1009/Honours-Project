import os.path
from destination import Destination
from problemInstance import ProblemInstance

def loadInstance(filename):
    if not os.path.isfile(filename):
        return None

    lines = []
    problemInstance = None
    problemName = ""

    with open(filename) as f:
        problemName = f.readline().strip()

        for line in f:
            if line[0] is not None and not line[0].isalpha() and not line[0] == '\n':
                lines.append(line.split())

                curLine = lines[len(lines) - 1]
                if curLine == []:
                    del lines[len(lines) - 1]
                else:
                    if len(curLine) == 2:
                        problemInstance = ProblemInstance(problemName, *curLine)
                    else:
                        problemInstance.destinations.append(Destination(*curLine))

    print(problemInstance.__str__())
    return problemInstance

loadInstance("solomon_100/C101.txt")
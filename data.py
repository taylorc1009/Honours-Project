import os.path

def loadInstance(filename):
    if not os.path.isfile(filename):
        return None

    lines = []

    with open(filename) as f:
        for line in f:
            if line[0] is not None and not line[0].isalpha() and not line[0] == '\n':
                lines.append(line.split())
                if lines[len(lines) - 1] == []:
                    del lines[len(lines) - 1]
    
    print(lines)
    return

loadInstance("solomon_100/C101.txt")
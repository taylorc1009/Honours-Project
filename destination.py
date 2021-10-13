class Destination():
    def __init__(self, number, x, y, demand, readyTime, dueDate, serviceDuration):
        self.number = number
        self.x = x
        self.y = y
        self.demand = demand
        self.readyTime = readyTime
        self.dueDate = dueDate
        self.serviceDuration = serviceDuration

    def getDistance(self, x, y):
        import math
        xPow, yPow = (x - self.x) ** 2, (y - self.y) ** 2
        return math.sqrt(x + y)
    
    def __str__(self) -> str:
        return f"{self.number}, {self.x}, {self.y}, {self.demand}, {self.readyTime}, {self.dueDate}, {self.serviceDuration}"
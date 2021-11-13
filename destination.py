class Destination():
    assignedVehicle: int=None
    T: float=None
    T_cooling: float=None

    def __init__(self, number: int, x: int, y: int, demand: int, readyTime: int, dueDate: int, serviceDuration: int):
        self.number = number
        self.x = int(x)
        self.y = int(y)
        self.demand = int(demand)
        self.readyTime = int(readyTime)
        self.dueDate = int(dueDate)
        self.serviceDuration = int(serviceDuration)

    def getDistance(self, x, y):
        import math
        xPow, yPow = (x - self.x) ** 2, (y - self.y) ** 2
        return math.sqrt(x + y)
    
    def __str__(self) -> str:
        return f"{self.number}, {self.x}, {self.y}, {self.demand}, {self.readyTime}, {self.dueDate}, {self.serviceDuration}"
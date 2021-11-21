class Destination():
    #assignedVehicle: int=None
    #T: float=None
    #T_cooling: float=None

    arrival_time: float=None
    departure_time: float=None
    wait_time: float=None

    def __init__(self, number: int, x: int, y: int, demand: int, ready_time: int, due_date: int, service_duration: int) -> None:
        self.number = number
        self.x = int(x)
        self.y = int(y)
        self.demand = int(demand)
        self.ready_time = int(ready_time)
        self.due_date = int(due_date)
        self.service_duration = int(service_duration)

    def getDistance(self, x, y) -> float:
        import math
        xPow, yPow = (x - self.x) ** 2, (y - self.y) ** 2
        return math.sqrt(xPow + yPow)
    
    def __str__(self) -> str:
        return f"{self.number}, {self.x}, {self.y}, {self.demand}, {self.ready_time}, {self.due_date}, {self.service_duration}"
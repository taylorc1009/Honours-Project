from destination import Destination
from typing import List

class Vehicle():
    def __init__(self, number: int, maxCapacity: int, currentCapacity=0, destinations: List[Destination]=list()) -> None:
        self.number = int(number)
        self.maxCapacity = int(maxCapacity)
        self.currentCapacity = int(currentCapacity)
        self.destinations: List[destinations]=destinations

    def __str__(self) -> str:
        return f"{self.number}, {self.maxCapacity}, {self.currentCapacity}, {[destination.number for destination in self.destinations]}"
    
    def getIndexOfDestination(self, destination: int) -> int:
        for i, d in enumerate(self.destinations):
            if d.number == destination:
                return i
        return None
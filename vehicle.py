from destination import Destination
from typing import List

class Vehicle():
    def __init__(self, number: int, maxCapacity: int, currentCapacity=0, destinations: List[Destination]=list()):
        self.number = int(number)
        self.maxCapacity = int(maxCapacity)
        self.currentCapacity = int(currentCapacity)
        self.destinations = destinations

    def __str__(self):
        return f"{self.number}, {self.maxCapacity}, {self.currentCapacity}, {[destination.number for destination in self.destinations]}"
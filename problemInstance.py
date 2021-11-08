from typing import Dict
from destination import Destination

class ProblemInstance():
    def __init__(self, name: str, amountOfVehicles: int, capacityOfVehicles: int, destinations: Dict[int, Destination]={}):
        self.name = name
        self.amountOfVehicles = int(amountOfVehicles)
        self.capacityOfVehicles = int(capacityOfVehicles)
        self.destinations = destinations

    def __str__(self) -> str:
        return f"{self.name}, {self.amountOfVehicles}, {self.capacityOfVehicles}, {[(key, value.__str__()) for key, value in self.destinations.items()]}"

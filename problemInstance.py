from MMOEASA.auxiliary import Euclidean_distance
from typing import List, Dict
from destination import Destination
from numpy import matrix

class ProblemInstance():
    MMOEASA_distances: matrix[int][int]

    def __init__(self, name: str, amount_of_vehicles: int, capacity_of_vehicles: int, destinations: Dict[int, Destination]=dict()) -> None:
        self.name: str=name
        self.amount_of_vehicles = int(amount_of_vehicles)
        self.capacity_of_vehicles = int(capacity_of_vehicles)
        self.destinations: List[Destination]=destinations

    def __str__(self) -> str:
        return f"{self.name}, {self.amountOfVehicles}, {self.capacityOfVehicles}, {[(key, value.__str__()) for key, value in self.destinations.items()]}"
    
    def calculateDistances(self):
        for i in enumerate(self.destinations):
            for j in enumerate(self.destinations):
                if i == j:
                    self.MMOEASA_distances[i][j] = -1
                else:
                    self.MMOEASA_distances[i][j] = self.destinations[i].getDistance(self.destinations[j].x, self.destinations[j].y)

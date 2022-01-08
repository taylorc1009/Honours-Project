from typing import Dict, List
from node import Node

class ProblemInstance:
    MMOEASA_distances: List[List[float]]=None

    def __init__(self, name: str, amount_of_vehicles: int, capacity_of_vehicles: int, nodes: Dict[int, Node]=None) -> None:
        self.name: str=name
        self.amount_of_vehicles: int=int(amount_of_vehicles)
        self.capacity_of_vehicles: int=int(capacity_of_vehicles)
        self.nodes: Dict[int, Node]=nodes

    def __str__(self) -> str:
        return f"{self.name}, {self.amount_of_vehicles}, {self.capacity_of_vehicles}, {[(key, value.__str__()) for key, value in self.nodes.items()]}"
    
    def calculateDistances(self) -> None:
        self.MMOEASA_distances: List[List[float]]=[[-1.0 for _, _ in enumerate(self.nodes)] for _, _ in enumerate(self.nodes)]

        for i, _ in enumerate(self.nodes):
            for j, _ in enumerate(self.nodes):
                self.MMOEASA_distances[i][j] = self.nodes[i].getDistance(self.nodes[j].x, self.nodes[j].y) if not i == j else -1.0

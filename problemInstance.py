from typing import Dict, List
from node import Node
from numpy import arange

class ProblemInstance:
    distances: List[float]=None

    def __init__(self, name: str, amount_of_vehicles: int, capacity_of_vehicles: int, nodes: Dict[int, Node]=None) -> None:
        self.name: str=name
        self.amount_of_vehicles: int=int(amount_of_vehicles)
        self.capacity_of_vehicles: int=int(capacity_of_vehicles)
        self.nodes: Dict[int, Node]=nodes

    def __str__(self) -> str:
        return f"{self.name}, {self.amount_of_vehicles}, {self.capacity_of_vehicles}, {[(key, str(value)) for key, value in self.nodes.items()]}"
    
    def calculate_distances(self) -> None:
        n = len(self.nodes)
        self.distances: List[float]=[-1.0 for _ in range(0, n ** 2)]

        for i in range(0, n):
            for j in range(0, n):
                if not i == j:
                    self.distances[n * i + j] = self.nodes[i].get_distance(self.nodes[j].x, self.nodes[j].y)

    def get_distance(self, from_node: int, to_node: int):
        return self.distances[len(self.nodes) * from_node + to_node]

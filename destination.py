import copy
from typing import List, Dict
from node import Node

class Destination():
    #assignedVehicle: int=None

    def __init__(self, node: Node=None, arrival_time: float=0.0, departure_time: float=0.0, wait_time: float=0.0) -> None:
        self.node: Node=node
        self.arrival_time: float=arrival_time
        self.departure_time: float=departure_time
        self.wait_time: float=wait_time
    
    def __str__(self) -> str:
        return f"{self.arrival_time}, {self.departure_time}, {self.wait_time}, {self.node.__str__()}"
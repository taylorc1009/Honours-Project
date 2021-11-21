from typing import List
from node import Node

class Destination():
    #assignedVehicle: int=None

    def __init__(self, arrival_time: float, departure_time: float, wait_time: float, node_args: List[int]=list()) -> None:
        self.arrival_time: float=arrival_time
        self.departure_time: float=departure_time
        self.wait_time: float=wait_time
        
        if not node_args.empty():
            self.node: Node=Node(*node_args)
    
    def __str__(self) -> str:
        return f"{self.arrival_time}, {self.departure_time}, {self.wait_time}, {self.node.__str__()}"
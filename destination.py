import copy
from typing import Dict
from node import Node

class Destination:
    def __init__(self, node: Node=None, arrival_time: float=0.0, departure_time: float=0.0, wait_time: float=0.0) -> None:
        self.node: Node=node
        self.arrival_time: float=arrival_time
        self.departure_time: float=departure_time
        self.wait_time: float=wait_time
    
    def __str__(self) -> str:
        return f"Destination(arrival_time={self.arrival_time}, departure_time={self.departure_time}, wait_time={self.wait_time}, {str(self.node)})"

    def __deepcopy__(self, memodict: Dict=None):
        return Destination(node=copy.deepcopy(self.node), arrival_time=self.arrival_time, departure_time=self.departure_time, wait_time=self.wait_time)
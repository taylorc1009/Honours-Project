from typing import List
from vehicle import Vehicle
from problemInstance import ProblemInstance
from common import INT_MAX

class Solution:
    def __init__(self, _id: int=None, vehicles: List[Vehicle]=None, feasible: bool=True, total_distance: float=0.0, rank: int=INT_MAX) -> None:
        self.id: int=int(_id)
        self.vehicles: List[Vehicle]=vehicles
        self.feasible: bool=feasible
        self.total_distance: float=float(total_distance)

        # ranking used in Ombuki's Algorithm
        self.rank: int=int(rank)

    def calculate_nodes_time_windows(self, instance: ProblemInstance) -> None:
        for i, _ in enumerate(self.vehicles):
            self.vehicles[i].calculate_destinations_time_windows(instance)

    def calculate_vehicles_loads(self, instance: ProblemInstance) -> None:
        for i, _ in enumerate(self.vehicles):
            self.vehicles[i].calculate_vehicle_load(instance)

    def calculate_length_of_routes(self, instance: ProblemInstance) -> None:
        for i, _ in enumerate(self.vehicles):
            self.vehicles[i].calculate_length_of_route(instance)
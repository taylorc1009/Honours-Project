import copy
from typing import List, Dict
from vehicle import Vehicle
from problemInstance import ProblemInstance

class Solution:
    def __init__(self, _id: int=None, vehicles: List[Vehicle]=None, feasible: bool=True, total_distance: float=0.0) -> None:
        self.id: int=int(_id)
        self.vehicles: List[Vehicle]=vehicles
        self.feasible: bool=feasible
        self.total_distance: float=float(total_distance)

    def __str__(self) -> str:
        return f"id={self.id}, feasible={self.feasible}, total_distance={self.total_distance}, {len(self.vehicles)=}, {[(i, str(v)) for i, v in enumerate(self.vehicles)]}"

    def calculate_nodes_time_windows(self, instance: ProblemInstance) -> None:
        for i, _ in enumerate(self.vehicles):
            self.vehicles[i].calculate_destinations_time_windows(instance)

    def calculate_vehicles_loads(self, instance: ProblemInstance) -> None:
        for i, _ in enumerate(self.vehicles):
            self.vehicles[i].calculate_vehicle_load(instance)

    def calculate_length_of_routes(self, instance: ProblemInstance) -> None:
        for i, _ in enumerate(self.vehicles):
            self.vehicles[i].calculate_length_of_route(instance)

    def __deepcopy__(self, memodict: Dict=None):
        return Solution(_id=self.id, vehicles=[copy.deepcopy(v) for v in self.vehicles], feasible=self.feasible, total_distance=self.total_distance)

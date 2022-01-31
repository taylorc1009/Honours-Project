import copy
from typing import List, Tuple, Dict
from MMOEASA.constants import MMOEASA_INFINITY
from vehicle import Vehicle
from problemInstance import ProblemInstance

class Solution:
    def __init__(self, _id: int=None, vehicles: List[Vehicle]=None, feasible: bool=True, T_default: float=0.0, T: float=0.0, T_cooling: float=0.0, total_distance: float=0.0, distance_unbalance: float=0.0, cargo_unbalance: float=0.0) -> None:
        self.id: int=int(_id)
        self.vehicles: List[Vehicle]=vehicles
        self.feasible: bool=feasible
        self.T_default: float=float(T_default)
        self.T: float=float(T)
        self.T_cooling: float=float(T_cooling)
        self.total_distance: float=float(total_distance)
        self.distance_unbalance: float=float(distance_unbalance)
        self.cargo_unbalance: float=float(cargo_unbalance)

    def __str__(self) -> str:
        return f"id={self.id}, feasible={self.feasible}, T_default={self.T_default}, T={self.T}, T_cooling={self.T_cooling}, total_distance={self.total_distance}, distance_unbalance={self.distance_unbalance}, cargo_unbalance={self.cargo_unbalance}, {len(self.vehicles)=}, {[(i, str(v)) for i, v in enumerate(self.vehicles)]}"

    def calculate_nodes_time_windows(self, instance: ProblemInstance) -> None:
        for i, _ in enumerate(self.vehicles):
            self.vehicles[i].calculate_destinations_time_windows(instance)

    def calculate_vehicles_loads(self, instance: ProblemInstance) -> None:
        for i, _ in enumerate(self.vehicles):
            self.vehicles[i].calculate_vehicle_load(instance)

    def calculate_length_of_routes(self, instance: ProblemInstance) -> None:
        for i, _ in enumerate(self.vehicles):
            self.vehicles[i].calculate_length_of_route(instance)

    def objective_function(self, instance: ProblemInstance) -> None:
        vehicle = 0
        self.total_distance = 0.0
        self.feasible = True # set the solution as feasible temporarily

        while vehicle < len(self.vehicles) and self.feasible:
            self.total_distance += self.vehicles[vehicle].route_distance

            for i in range(1, len(self.vehicles[vehicle].destinations) - 1):
                node_number = self.vehicles[vehicle].destinations[i].node.number
                if self.vehicles[vehicle].destinations[i].arrival_time > instance.nodes[node_number].due_date or self.vehicles[vehicle].current_capacity > instance.capacity_of_vehicles:
                    self.feasible = False
                    self.total_distance = MMOEASA_INFINITY
                    self.distance_unbalance = MMOEASA_INFINITY
                    self.cargo_unbalance = MMOEASA_INFINITY
                    break
            vehicle += 1
        
        if self.feasible:
            minimum_distance = MMOEASA_INFINITY
            maximum_distance = 0
            minimum_cargo = MMOEASA_INFINITY
            maximum_cargo = 0

            for i, _ in enumerate(self.vehicles):
                # these cannot be converted to "if ... elif" because we may miss, for example, our "maximum_distance" as on the first iteration it will also be less than "MMOEASA_INFINITY" ("minimum_distance")
                if self.vehicles[i].route_distance < minimum_distance:
                    minimum_distance = self.vehicles[i].route_distance
                if self.vehicles[i].route_distance > maximum_distance:
                    maximum_distance = self.vehicles[i].route_distance
                if self.vehicles[i].current_capacity < minimum_cargo:
                    minimum_cargo = self.vehicles[i].current_capacity
                if self.vehicles[i].current_capacity > maximum_cargo:
                    maximum_cargo = self.vehicles[i].current_capacity
            self.distance_unbalance = maximum_distance - minimum_distance
            self.cargo_unbalance = maximum_cargo - minimum_cargo

    def __deepcopy__(self, memodict: Dict=None):
        return Solution(_id=self.id, vehicles=[copy.deepcopy(v) for v in self.vehicles], feasible=self.feasible, T_default=self.T_default, T=self.T, T_cooling=self.T_cooling, total_distance=self.total_distance, distance_unbalance=self.distance_unbalance, cargo_unbalance=self.cargo_unbalance)

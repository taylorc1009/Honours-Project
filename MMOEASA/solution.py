from typing import List, Tuple
from MMOEASA.constants import MMOEASA_INFINITY
from vehicle import Vehicle
from problemInstance import ProblemInstance

class Solution():
    feasible: bool=True

    T_default: float=0.0
    T: float=0.0
    T_cooling: float=0.0

    total_distance: float=0.0
    #distance_unbalance: float=None
    cargo_unbalance: float=0.0

    def __init__(self, _id: int=None, vehicles: List[Vehicle]=list()) -> None:
        self.id: int=_id
        self.vehicles: List[Vehicle]=vehicles

    def __str__(self) -> str:
        return f"{self.id}, {self.feasible}, {self.T}, {self.T_cooling}, {self.total_distance}, {self.cargo_unbalance}, {[v.__str__() for v in self.vehicles]}"

    def calculate_nodes_time_windows(self, instance: ProblemInstance) -> None:
        for i, _ in enumerate(self.vehicles):
            self.vehicles[i].calculate_destinations_time_windows(instance)

    def calculate_vehicles_loads(self, instance: ProblemInstance) -> None:
        for i, _ in enumerate(self.vehicles):
            self.vehicles[i].calculate_vehicle_load(instance)

    def calculate_customers_on_routes(self, instance: ProblemInstance) -> None:
        for i, _ in enumerate(self.vehicles):
            self.vehicles[i].calculate_customers_on_route(instance)

    def objective_function(self, instance: ProblemInstance) -> Tuple[float, float]:
        vehicle = 0
        while vehicle < len(self.vehicles) and self.feasible:
            self.total_distance += self.vehicles[vehicle].route_distance

            for i in range(1, len(self.vehicles[vehicle].destinations)):
                node_number = self.vehicles[vehicle].destinations[i].node.number
                if self.vehicles[vehicle].destinations[i].arrival_time > instance.nodes[node_number].due_date or self.vehicles[i].current_capacity > instance.capacity_of_vehicles:
                    self.feasible = False
                    self.total_distance = MMOEASA_INFINITY
                    #self.distance_unbalance = MMOEASA_INFINITY
                    self.cargo_unbalance = MMOEASA_INFINITY
                    break
            vehicle += 1
        
        if self.feasible:
            #minimum_distance = MMOEASA_INFINITY
            #maximum_distance = 0
            minimum_cargo = MMOEASA_INFINITY
            maximum_cargo = 0

            for i, _ in enumerate(self.vehicles):
                """if self.vehicle[i].route_distance < minimum_distance: # these cannot be converted to "if ... elif" because we may miss, for example, our "maximum_distance" as on the first iteration it will also be less than "MMOEASA_INFINITY" ("minimum_distance")
                    minimum_distance = self.vehicle[i].route_distance
                if self.vehicle[i].route_distance > maximum_distance:
                    maximum_distance = self.vehicle[i].route_distance"""
                if self.vehicles[i].current_capacity < minimum_cargo:
                    minimum_cargo = self.vehicles[i].current_capacity
                if self.vehicles[i].current_capacity > maximum_cargo:
                    maximum_cargo = self.vehicles[i].route_distance
            #self.distance_unbalance = maximum_distance - minimum_distance
            self.cargo_unbalance = maximum_cargo - minimum_cargo
        
        return self.total_distance, self.cargo_unbalance

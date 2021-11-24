from typing import List, Union
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
            for j in range(1, len(self.vehicles[i].destinations)):
                previous_node = self.vehicles[i].destinations[j - 1].node.number
                current_node = self.vehicles[i].destinations[j].node.number
                self.vehicles[i].destinations[j].arrival_time = self.vehicles[i].destinations[j - 1].departure_time + instance.MMOEASA_distances[previous_node][current_node]
                if self.vehicles[i].destinations[j].arrival_time < instance.nodes[current_node].ready_time:
                    self.vehicles[i].destinations[j].wait_time = instance.nodes[current_node].ready_time - self.vehicles[i].destinations[j].arrival_time
                    self.vehicles[i].destinations[j].arrival_time = instance.nodes[current_node].ready_time
                self.vehicles[i].destinations[j].departure_time = self.vehicles[i].destinations[j].arrival_time + instance.nodes[current_node].service_duration

    def calculate_routes_capacities(self, instance: ProblemInstance) -> None:
        for i, _ in enumerate(self.vehicles):
            temporary_capacity = 0.0
            for j in range(1, len(self.vehicles[i].destinations) - 1):
                node_number = self.vehicles[i].destinations[j].node.number
                temporary_capacity += instance.nodes[node_number].demand
            self.vehicles[i].current_capacity = temporary_capacity

    def calculate_length_of_routes(self, instance: ProblemInstance) -> None:
        for i, _ in enumerate(self.vehicles):
            temporary_distance = 0.0
            for j, _ in enumerate(self.vehicles[i].destinations):
                previous_node = self.vehicles[i].destinations[j - 1].node.number
                current_node = self.vehicles[i].destinations[j].node.number
                temporary_distance += instance.MMOEASA_distances[previous_node][current_node]
            self.vehicles[i].route_distance = temporary_distance

    def objective_function(self, instance: ProblemInstance) -> Union[float, float]:
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
                if self.vehicle[i].current_capacity < minimum_cargo:
                    minimum_cargo = self.vehicle[i].current_capacity
                if self.vehicle[i].current_capacity > maximum_cargo:
                    maximum_cargo = self.vehicle[i].route_distance
            #self.distance_unbalance = maximum_distance - minimum_distance
            self.cargo_unbalance = maximum_cargo - minimum_cargo
        
        return self.total_distance, self.cargo_unbalance

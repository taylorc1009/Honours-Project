from typing import List
from MMOEASA.hypervolumes import Hypervolume_total_distance, Hypervolume_cargo_unbalance, update_Hypervolumes
from MMOEASA.constants import MMOEASA_INFINITY
from vehicle import Vehicle
from problemInstance import ProblemInstance
from destination import Destination

class Solution():
    feasible: bool=True
    total_distance: float=None
    #distance_unbalance: float=None
    cargo_unbalance: float=None

    T: float=None
    T_cooling: float=None
    #t: float=None

    def __init__(self, _id: int=None, order_of_destinations: List[Destination]=list(), vehicles: List[Vehicle]=list()) -> None:
        self.id: int=_id
        self.order_of_destinations: List[Destination]=order_of_destinations
        self.vehicles: List[Vehicle]=vehicles

    def calculate_nodes_time_windows(self, instance: ProblemInstance) -> None:
        for i in enumerate(self.vehicles):
            for j in range(1, self.vehicles[i].destinations):
                previous_node = self.vehicles[i].destinations[j - 1].node.number
                current_node = self.vehicles[i].destinations[j].node.number
                self.vehicles[i].destinations[j].arrival_time = self.vehicles[i].destinations[j - 1] + instance.distances[previous_node][current_node]
                if self.vehicles[i].destinations[j].arrival_time < instance.nodes[current_node].ready_time:
                    self.vehicles[i].destinations[j].wait_time = instance.nodes[current_node].ready_time - self.vehicles[i].destinations[j].arrival_time
                    self.vehicles[i].destinations[j].arrival_time = instance.nodes[current_node].ready_time
                self.vehicles[i].destinations[j].departure_time = self.vehicles[i].destinations[j].arrival_time + instance.nodes[current_node].service_duration

    def calculate_routes_capacities(self, instance: ProblemInstance) -> None:
        for i in enumerate(self.vehicles):
            temporary_capacity = 0.0
            for j in range(1, self.vehicles[i].destinations - 1):
                node_number = self.vehicles[i].destinations[j].node.number
                temporary_capacity += instance.nodes[node_number].demand
            self.vehicles[i].current_capacity = temporary_capacity

    def calculate_length_of_routes(self, instance: ProblemInstance) -> None:
        for i in enumerate(self.vehicles):
            temporary_distance = 0.0
            for j in enumerate(self.vehicles[i].destinations):
                previous_node = self.vehicles[i].destinations[j - 1].node.number
                current_node = self.vehicles[i].destinations[j].node.number
                temporary_distance += instance.distances[previous_node][current_node]
            self.vehicles[i].route_distance = temporary_distance

    def objective_function(self, instance: ProblemInstance) -> None:
        vehicle = 0
        while vehicle < len(self.vehicles) and self.feasible:
            self.total_distance += self.vehicles[vehicle].route_distance

            for i in range(1, self.vehicles[i].destinations):
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

            for i in enumerate(self.vehicles):
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

            update_Hypervolumes(
                total_distance=self.total_distance if self.total_distance > Hypervolume_total_distance[0] else 0.0,
                #distance_unbalance=self.distance_unbalance if self.distance_unbalance > Hypervolume_distance_unbalance else 0.0,
                cargo_unbalance=self.cargo_unbalance if self.cargo_unbalance > Hypervolume_cargo_unbalance[0] else 0.0
            )

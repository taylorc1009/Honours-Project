import copy
from typing import List, Dict
from Ombuki.constants import INT_MAX
from vehicle import Vehicle
from problemInstance import ProblemInstance

class Solution:
    def __init__(self, _id: int=None, vehicles: List[Vehicle]=None, feasible: bool=True, total_distance: float=0.0, num_vehicles: int=0, rank: int=INT_MAX) -> None:
        self.id: int=int(_id)
        self.vehicles: List[Vehicle]=vehicles
        self.feasible: bool=feasible
        self.total_distance: float=float(total_distance)
        self.num_vehicles: int=int(len(vehicles) if vehicles else num_vehicles) # the reason this objective is a variable instead of just using "len(vehicles)" is because if the solution is invalid, it needs to be set to a very high number
        self.rank: int=int(rank)

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

    def objective_function(self, instance: ProblemInstance):
        vehicle = 0
        self.total_distance = 0.0
        self.num_vehicles = len(self.vehicles)
        self.feasible = True  # set the solution as feasible temporarily

        while vehicle < len(self.vehicles) and self.feasible:
            self.total_distance += self.vehicles[vehicle].route_distance

            for destination in self.vehicles[vehicle].get_customers_visited():
                node_number = destination.node.number
                if destination.arrival_time > instance.nodes[node_number].due_date or self.vehicles[vehicle].current_capacity > instance.capacity_of_vehicles:
                    self.feasible = False
                    self.total_distance = INT_MAX
                    self.num_vehicles = INT_MAX
                    break
            vehicle += 1

    def __deepcopy__(self, memodict: Dict=None):
        return Solution(_id=self.id, vehicles=[copy.deepcopy(v) for v in self.vehicles], feasible=self.feasible, total_distance=self.total_distance)

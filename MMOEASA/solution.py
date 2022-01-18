import copy
from typing import List, Tuple, Dict
from MMOEASA.constants import MMOEASA_INFINITY
from vehicle import Vehicle
from problemInstance import ProblemInstance

class Solution:
    feasible: bool=True

    T_default: float=0.0
    T: float=0.0
    T_cooling: float=0.0

    total_distance: float=0.0
    #distance_unbalance: float=None
    cargo_unbalance: float=0.0

    def __init__(self, _id: int=None, vehicles: List[Vehicle]=None) -> None:
        self.id: int=int(_id)
        self.vehicles: List[Vehicle]=vehicles

    def __str__(self) -> str:
        return f"{self.id=}, {self.feasible=}, {self.T_default=}, {self.T=}, {self.T_cooling=}, {self.total_distance=}, {self.cargo_unbalance=}, {len(self.vehicles)=}, {[str(v) for v in self.vehicles]}"

    def calculate_nodes_time_windows(self, instance: ProblemInstance) -> None:
        for i, _ in enumerate(self.vehicles):
            self.vehicles[i].calculate_destinations_time_windows(instance)

    def calculate_vehicles_loads(self, instance: ProblemInstance) -> None:
        for i, _ in enumerate(self.vehicles):
            self.vehicles[i].calculate_vehicle_load(instance)

    def calculate_length_of_routes(self, instance: ProblemInstance) -> None:
        for i, _ in enumerate(self.vehicles):
            self.vehicles[i].calculate_length_of_route(instance)

    def objective_function(self, instance: ProblemInstance) -> Tuple[float, float]:
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
                    maximum_cargo = self.vehicles[i].current_capacity
            #self.distance_unbalance = maximum_distance - minimum_distance
            self.cargo_unbalance = maximum_cargo - minimum_cargo

            # these values are potentially the next Hypervolumes;
            # if they're greater than any previously recorded total distances and unbalances in the vehicles' cargo, then they will be set as the new Hypervolumes by the function "update_Hypervolumes" in "mmoeasa.py"
            # but if, and only if, the solution is feasible...
            return self.total_distance, self.cargo_unbalance
        return 0.0, 0.0 # ... and if the solution isn't feasible, then return zero values so that the previously recorded Hypervolumes aren't changed

    def __deepcopy__(self, memodict: Dict=None):
        obj_copy = Solution(_id=self.id, vehicles=[copy.deepcopy(v) for v in self.vehicles])
        obj_copy.feasible = self.feasible
        obj_copy.T_default = self.T_default
        obj_copy.T = self.T
        obj_copy.T_cooling = self.T_cooling
        obj_copy.total_distance = self.total_distance
        obj_copy.cargo_unbalance = self.cargo_unbalance

        return obj_copy

        """ this does not work due to the following error: "RecursionError: maximum recursion depth exceeded while calling a Python object"
                obj_copy=copy.deepcopy(self)
                obj_copy.vehicles = copy.deepcopy(self.vehicles)
                for i, _ in enumerate(self.vehicles):
                    obj_copy.vehicles[i].destinations = copy.deepcopy(self.vehicles[i].destinations)
                    for j, _ in enumerate(self.vehicles[i].destinations):
                        obj_copy.vehicles[i].destinations[j].node = copy.deepcopy(self.vehicles[i].destinations[j].node)"""

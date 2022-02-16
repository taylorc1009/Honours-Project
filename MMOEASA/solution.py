import copy
from typing import List, Dict
from MMOEASA.constants import MMOEASA_INFINITY
from vehicle import Vehicle
from problemInstance import ProblemInstance
from solution import Solution

class MMOEASASolution(Solution):
    def __init__(self, _id: int=None, vehicles: List[Vehicle]=None, feasible: bool=True, T_default: float=0.0, T: float=0.0, T_cooling: float=0.0, total_distance: float=0.0, distance_unbalance: float=0.0, cargo_unbalance: float=0.0) -> None:
        super(MMOEASASolution, self).__init__(_id=_id, vehicles=vehicles, feasible=feasible, total_distance=total_distance)
        self.T_default: float=float(T_default)
        self.T: float=float(T)
        self.T_cooling: float=float(T_cooling)
        self.distance_unbalance: float=float(distance_unbalance)
        self.cargo_unbalance: float=float(cargo_unbalance)

    def __str__(self) -> str:
        return f"id={self.id}, feasible={self.feasible}, T_default={self.T_default}, T={self.T}, T_cooling={self.T_cooling}, total_distance={self.total_distance}, distance_unbalance={self.distance_unbalance}, cargo_unbalance={self.cargo_unbalance}, {len(self.vehicles)=}, {[(i, str(v)) for i, v in enumerate(self.vehicles)]}"

    def objective_function(self, instance: ProblemInstance) -> None:
        vehicle = 0
        self.total_distance = 0.0
        self.feasible = True # set the solution as feasible temporarily

        while vehicle < len(self.vehicles) and self.feasible:
            self.total_distance += self.vehicles[vehicle].route_distance

            for destination in self.vehicles[vehicle].get_customers_visited():
                if destination.arrival_time > instance.nodes[destination.node.number].due_date or self.vehicles[vehicle].current_capacity > instance.capacity_of_vehicles:
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

            for vehicle in self.vehicles:
                # these cannot be converted to "if ... elif" because we may miss, for example, our "maximum_distance" as on the first iteration it will also be less than "MMOEASA_INFINITY" ("minimum_distance")
                if vehicle.route_distance < minimum_distance:
                    minimum_distance = vehicle.route_distance
                if vehicle.route_distance > maximum_distance:
                    maximum_distance = vehicle.route_distance
                if vehicle.current_capacity < minimum_cargo:
                    minimum_cargo = vehicle.current_capacity
                if vehicle.current_capacity > maximum_cargo:
                    maximum_cargo = vehicle.current_capacity
            self.distance_unbalance = maximum_distance - minimum_distance
            self.cargo_unbalance = maximum_cargo - minimum_cargo

    def __deepcopy__(self, memodict: Dict=None):
        return MMOEASASolution(_id=self.id, vehicles=[copy.deepcopy(v) for v in self.vehicles], feasible=self.feasible, T_default=self.T_default, T=self.T, T_cooling=self.T_cooling, total_distance=self.total_distance, distance_unbalance=self.distance_unbalance, cargo_unbalance=self.cargo_unbalance)

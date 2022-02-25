import copy
from typing import List, Dict
from constants import INT_MAX
from vehicle import Vehicle
from problemInstance import ProblemInstance
from solution import Solution

class OmbukiSolution(Solution):
    def __init__(self, _id: int=None, vehicles: List[Vehicle]=None, feasible: bool=True, total_distance: float=0.0, num_vehicles: int=0, rank: int=INT_MAX) -> None:
        super(OmbukiSolution, self).__init__(_id=_id, vehicles=vehicles, feasible=feasible, total_distance=total_distance, rank=rank) # initialise every solution's temperature (in Ombuki) to 100 and don't modify it later so that Simulated Annealing isn't used when MMOEASA's acceptance criterion, "MO_Metropolis", is being utilised
        self.num_vehicles: int=int(num_vehicles) # the reason this objective is a variable instead of just using "len(vehicles)" is because if the solution is invalid, it needs to be set to a very high number

    def __str__(self) -> str:
        return f"id={self.id}, feasible={self.feasible}, total_distance={self.total_distance}, num_vehicles={self.num_vehicles}"#, {[(i, str(v)) for i, v in enumerate(self.vehicles)]}"

    def objective_function(self, instance: ProblemInstance):
        vehicle = 0
        self.total_distance = 0.0
        self.num_vehicles = len(self.vehicles)
        self.feasible = True  # set the solution as feasible temporarily

        while vehicle < len(self.vehicles) and self.feasible:
            self.total_distance += self.vehicles[vehicle].route_distance

            for destination in self.vehicles[vehicle].get_customers_visited():
                if destination.arrival_time > instance.nodes[destination.node.number].due_date or self.vehicles[vehicle].current_capacity > instance.capacity_of_vehicles:
                    self.feasible = False
                    self.total_distance = INT_MAX
                    self.num_vehicles = INT_MAX
                    break
            vehicle += 1

    def __deepcopy__(self, memodict: Dict=None):
        return OmbukiSolution(_id=self.id, vehicles=[copy.deepcopy(v) for v in self.vehicles], feasible=self.feasible, total_distance=self.total_distance, num_vehicles=self.num_vehicles, rank=self.rank)

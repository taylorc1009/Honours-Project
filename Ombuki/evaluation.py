from Ombuki.ombukiSolution import OmbukiSolution
from problemInstance import ProblemInstance
from MMOEASA.mmoeasa import TWIH
from typing import Tuple, List

def TWIH_ref_point(instance: ProblemInstance) -> Tuple[float, float]:
    solution = TWIH(instance)

    solution.calculate_length_of_routes(instance)
    solution.total_distance = sum([vehicle.route_distance for vehicle in solution.vehicles])

    return solution.total_distance * 10, len(solution.vehicles) * 10

def calculate_median_Hypervolumes(ND_solutions: List[OmbukiSolution], TWIH_Hypervolumes: Tuple[float, float]) -> float:
    prev_TD, prev_NV = ref_TD, ref_NV = TWIH_Hypervolumes[0], TWIH_Hypervolumes[0]
    area = 0.0

    for ND in sorted([solution for solution in ND_solutions], key=lambda x: x.total_distance):
        area += (prev_TD - ND.total_distance) * (ref_NV - ND.num_vehicles)
        prev_TD, prev_NV = ND.total_distance, ND.num_vehicles

    return area / (ref_TD * ref_NV)
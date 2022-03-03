from Ombuki.ombukiSolution import OmbukiSolution
from problemInstance import ProblemInstance
from typing import Tuple, List

def TWIH_ref_point(instance: ProblemInstance) -> Tuple[float, float]:
    return 10000.0, instance.amount_of_vehicles

def calculate_median_Hypervolumes(ND_solutions: List[OmbukiSolution], TWIH_Hypervolumes: Tuple[float, float]) -> float:
    prev_TD, prev_NV = ref_TD, ref_NV = TWIH_Hypervolumes[0], TWIH_Hypervolumes[0]
    area = 0.0

    for ND in sorted([solution for solution in ND_solutions], key=lambda x: x.total_distance, reverse=True):
        area += (prev_TD - ND.total_distance) * (ref_NV - ND.num_vehicles)
        prev_TD, prev_NV = ND.total_distance, ND.num_vehicles

    return (area / (ref_TD * ref_NV)) * 100
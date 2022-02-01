from typing import List, Tuple
from MMOEASA.solution import Solution

def calculate_median_Hypervolumes(ND_solutions: List[Solution], TWIH_Hypervolumes: Tuple[float, float, float]) -> float:
    prev_TD, prev_DU, prev_CU = ref_TD, ref_DU, ref_CU = TWIH_Hypervolumes[0], TWIH_Hypervolumes[1], TWIH_Hypervolumes[2]
    area = 0.0

    for ND in sorted([solution for solution in ND_solutions], key=lambda x: x.total_distance):
        area += (prev_TD - ND.total_distance) * (ref_CU - ND.cargo_unbalance)
        prev_TD, prev_DU, prev_CU = ND.total_distance, ND.distance_unbalance, ND.cargo_unbalance

    return area / (ref_TD * ref_CU) # TODO: this is currently giving a "float division by zero" exception; why?

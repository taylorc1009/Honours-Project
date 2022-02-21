from problemInstance import ProblemInstance
from MMOEASA.mmoeasa import TWIH
from MMOEASA.constants import INFINITY
from mmoeasaSolution import MMOEASASolution
from typing import Tuple, List

def TWIH_ref_point(instance: ProblemInstance) -> Tuple[float, float, float]:
    solution = TWIH(instance)
    minimum_distance, maximum_distance, minimum_cargo, maximum_cargo = INFINITY, 0, INFINITY, 0

    solution.calculate_length_of_routes(instance)

    solution.total_distance = sum([vehicle.route_distance for vehicle in solution.vehicles])

    for vehicle in solution.vehicles:
        if vehicle.route_distance < minimum_distance:
            minimum_distance = vehicle.route_distance
        if vehicle.route_distance > maximum_distance:
            maximum_distance = vehicle.route_distance
        if vehicle.current_capacity < minimum_cargo:
            minimum_cargo = vehicle.current_capacity
        if vehicle.current_capacity > maximum_cargo:
            maximum_cargo = vehicle.current_capacity
    solution.distance_unbalance = maximum_distance - minimum_distance
    solution.cargo_unbalance = maximum_cargo - minimum_cargo

    return solution.total_distance * 10, solution.distance_unbalance * 10, solution.cargo_unbalance * 10

def calculate_median_Hypervolumes(ND_solutions: List[MMOEASASolution], TWIH_Hypervolumes: Tuple[float, float, float]) -> float:
    prev_TD, prev_DU, prev_CU = ref_TD, ref_DU, ref_CU = TWIH_Hypervolumes[0], TWIH_Hypervolumes[1], TWIH_Hypervolumes[2]
    area = 0.0

    for ND in sorted([solution for solution in ND_solutions], key=lambda x: x.total_distance):
        area += (prev_TD - ND.total_distance) * (ref_CU - ND.cargo_unbalance)
        prev_TD, prev_DU, prev_CU = ND.total_distance, ND.distance_unbalance, ND.cargo_unbalance

    return area / (ref_TD * ref_CU) # TODO: this is currently giving a "float division by zero" exception; why?
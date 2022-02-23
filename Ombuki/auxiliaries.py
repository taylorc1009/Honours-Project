from numpy import random
from constants import INT_MAX
from typing import Set, List, Union
from MMOEASA.mmoeasaSolution import MMOEASASolution
from Ombuki.ombukiSolution import OmbukiSolution

def rand(start: int, end: int, exclude_values: Set[int]=None) -> int:
    # '+ 1' to make the random number generator inclusive of the "end" value
    offset = 1 if end < INT_MAX else 0
    random_val = random.randint(start, end + offset)
    while exclude_values is not None and random_val in exclude_values:
        random_val = random.randint(start, end + offset)
    return random_val

def is_nondominated(old_solution: OmbukiSolution, new_solution: OmbukiSolution) -> bool:
    return (new_solution.total_distance < old_solution.total_distance and new_solution.num_vehicles <= old_solution.num_vehicles) or (new_solution.total_distance <= old_solution.total_distance and new_solution.num_vehicles < old_solution.num_vehicles)

def is_nondominated_by_any(population: List[OmbukiSolution], subject_solution: Union[int, OmbukiSolution]) -> bool:
    is_int = isinstance(subject_solution, int)
    for i, solution in enumerate(population):
        if not i == (subject_solution if is_int else subject_solution.id) and not is_nondominated(solution, population[subject_solution] if is_int else subject_solution):
            return False
    return True

def mmoeasa_is_nondominated(Parent: MMOEASASolution, Child: MMOEASASolution) -> bool:
    return (Child.total_distance < Parent.total_distance and Child.cargo_unbalance <= Parent.cargo_unbalance) or (Child.total_distance <= Parent.total_distance and Child.cargo_unbalance < Parent.cargo_unbalance)

def mmoeasa_is_nondominated_by_any(population: List[MMOEASASolution], subject_solution: int) -> bool:
    for i, solution in enumerate(population):
        if not i == subject_solution and not mmoeasa_is_nondominated(solution, population[subject_solution]):
            return False
    return True

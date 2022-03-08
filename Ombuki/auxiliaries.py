from numpy import random
from common import INT_MAX
from typing import Set, List, Union, Callable
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

def mmoeasa_is_nondominated(parent: MMOEASASolution, child: MMOEASASolution) -> bool:
    return (child.total_distance < parent.total_distance and child.cargo_unbalance <= parent.cargo_unbalance) or (child.total_distance <= parent.total_distance and child.cargo_unbalance < parent.cargo_unbalance)

def get_nondominated_set(unranked_solutions: List[Union[OmbukiSolution, MMOEASASolution]], nondominated_check: Callable[[Union[OmbukiSolution, MMOEASASolution], Union[OmbukiSolution, MMOEASASolution]], bool]) -> Set[int]:
    nondominated_ids = set([s.id for s in unranked_solutions])

    for s, solution in enumerate(unranked_solutions[:len(unranked_solutions) - 1]):
        for solution_auxiliary in unranked_solutions[s + 1:]:
            if nondominated_check(solution, solution_auxiliary) and solution.id in nondominated_ids:
                nondominated_ids.remove(solution.id)
            elif nondominated_check(solution_auxiliary, solution) and solution_auxiliary.id in nondominated_ids:
                nondominated_ids.remove(solution_auxiliary.id)

    return nondominated_ids

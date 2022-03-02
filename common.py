import time
from typing import Final, Set
from numpy import random

INT_MAX: Final[int]=2147483647

def rand(start: int, end: int, exclude_values: Set[int]=None) -> int:
    # '+ 1' to make the random number generator inclusive of the "end" value
    offset = 1 if end < INT_MAX else 0
    random_val = random.randint(start, end + offset)
    while exclude_values is not None and random_val in exclude_values:
        random_val = random.randint(start, end + offset)
    return random_val

def check_seconds_termination_condition(start: float, TC: int):
    return (time.time() - start) > TC

def check_iterations_termination_condition(iterations: int, TC: int):
    return iterations > TC

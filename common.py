from typing import Final, List
from numpy import random

INT_MAX: Final[int]=2147483647

def rand(start: int, end: int, exclude_values: List[int]=None) -> int:
    # '+ 1' to make the random number generator inclusive of the "end" value
    offset = 1 if end < INT_MAX else 0
    random_val = random.randint(start, end + offset)
    while exclude_values is not None and random_val in exclude_values:
        random_val = random.randint(start, end + offset)
    return random_val
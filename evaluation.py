import os
from MMOEASA.evaluation import TWIH_ref_point as MMOEASA_ref_point, calculate_median_Hypervolumes as MMOEASA_median_hypervolumes
from Ombuki.evaluation import TWIH_ref_point as Ombuki_ref_point, calculate_median_Hypervolumes as Ombuki_median_hypervolumes
from Ombuki.ombukiSolution import OmbukiSolution
from MMOEASA.mmoeasaSolution import MMOEASASolution
from typing import List, Union
from problemInstance import ProblemInstance

def calculate_area(problem_instance: ProblemInstance, nondominated_set: List[Union[MMOEASASolution, OmbukiSolution]], algorithm: str, acceptance_criterion: str):
    area = 0.0
    if len(nondominated_set) > 0:
        if acceptance_criterion.upper() == "MMOEASA":
            area = MMOEASA_median_hypervolumes(nondominated_set, MMOEASA_ref_point(problem_instance))
        elif acceptance_criterion.upper() == "OMBUKI":
            area = Ombuki_median_hypervolumes(nondominated_set, Ombuki_ref_point(problem_instance))

        area = round(area, 2)

    print(f"{os.linesep}Graph area occupied: {area}%")

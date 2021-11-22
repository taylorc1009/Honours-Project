from typing import List

# the Hypervolumes are lists because lists are mutable and can therefore be changed from another file
# the lists should only ever store one float value; if used correctly with the "update_Hypervolumes" function below, doing so should be easy
Hypervolume_total_distance: List[float]=[0.0]
#Hypervolume_distance_unbalance: List[float]=[0.0]
Hypervolume_cargo_unbalance: List[float]=[0.0]

def update_Hypervolumes(total_distance: float=0.0, distance_unbalance: float=0.0, cargo_unbalance: float=0.0) -> None:
    if total_distance is not 0.0:
        Hypervolume_total_distance.clear()
        Hypervolume_total_distance.append(total_distance)
    """if distance_unbalance is not 0.0:
        Hypervolume_distance_unbalance.clear()
        Hypervolume_distance_unbalance.append(total_distance)"""
    if cargo_unbalance is not 0.0:
        Hypervolume_cargo_unbalance.clear()
        Hypervolume_cargo_unbalance.append(total_distance)
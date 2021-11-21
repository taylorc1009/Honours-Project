from solution import Solution
from ..problemInstance import ProblemInstance
from typing import List

# the Hypervolumes are lists because lists are mutable and can therefore be changed from another file
# the lists should only ever store one float value; if used correctly with the "update_Hypervolumes" function below, doing so should be easy
Hypervolume_total_distance: List[float]=[0.0]
#Hypervolume_distance_unbalance: List[float]=[0.0]
Hypervolume_cargo_unbalance: List[float]=[0.0]

def update_Hypervolumes(total_distance: float=0.0, distance_unbalance: float=0.0, cargo_unbalance: float=0.0):
    if total_distance is not 0.0:
        Hypervolume_total_distance.clear()
        Hypervolume_total_distance.append(total_distance)
    """if distance_unbalance is not 0.0:
        Hypervolume_distance_unbalance.clear()
        Hypervolume_distance_unbalance.append(total_distance)"""
    if cargo_unbalance is not 0.0:
        Hypervolume_cargo_unbalance.clear()
        Hypervolume_cargo_unbalance.append(total_distance)

def solution_visits_destination(destination: int, instance: ProblemInstance, I: Solution) -> bool:
    for j in range(0, instance.amountOfVehicles):
        if len(I.vehicles[j].destinations) - 2 >= 1:
            for k in len(I.vehicles[j].destinations):
                if I.vehicles[j].destinations[k].node.number == instance.destinations[destination].node.number: # directly get the destination number from the list of destinations in case there's a mismatch between the destination number and the for loop iterator (although there shouldn't)
                    return True
    return False

def verify_nodes_are_inserted(I: Solution, instance: ProblemInstance) -> None:
    for i in range(1, len(instance.nodes)):
        if not solution_visits_destination(i, instance, I):
            inserted, vehicle = False, 0
            while vehicle < instance.amount_of_vehicles and not inserted:
                length_of_route = len(I.vehicles[vehicle].destinations) - 2
                final_destination = I.vehicles[vehicle].destinations[length_of_route].node.number
                
                I.vehicles[vehicle].destinations[length_of_route + 1].node = instance.nodes[i]
                I.vehicles[vehicle].current_capacity += instance.destinations[i].node.demand

                I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time = I.vehicles[vehicle].destinations[length_of_route].departure_time + instance.MMOEASA_distances[final_destination][i]
                I.vehicles[vehicle].destinations[length_of_route + 1].wait_time = 0.0
                if I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time < instance.destinations[i].ready_time:
                    I.vehicles[vehicle].destinations[length_of_route + 1].wait_time = instance.destinations[i].ready_time - I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time
                    I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time = instance.destinations[i].ready_time
                
                if I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time <= instance.destinations[i].due_date:
                    I.vehicles[vehicle].destinations[length_of_route + 1].departure_time = instance.destinations[i].serve_time + I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time

                    I.calculate_route_lengths()

                    inserted = True
                elif I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time > instance.destinations[i].due_date or I.vehicles[vehicle].current_capacity > instance.capacity_of_vehicles:
                    del I.vehicles[vehicle].destinations[length_of_route + 1]
                    vehicle += 1

    vehicle = 0
    for i in range(I.vehicles):
        I.vehicles[vehicle].destinations.append(instance.destinations[0])

        length_of_route = len(I.vehicles[i].destinations) - 2
        final_destination = I.vehicles[vehicle].destinations[length_of_route].number

        I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time = I.vehicles[vehicle].destinations[length_of_route + 1].departure_time + instance.MMOEASA_distances[final_destination][0]
        I.vehicles[vehicle].destinations[length_of_route + 1].departure_time = I.vehicles[vehicle].destinations[length_of_route + 1].departure_time + instance.MMOEASA_distances[final_destination][0]
        I.vehicles[vehicle].destinations[length_of_route + 1].wait_time = 0.0

    return inserted

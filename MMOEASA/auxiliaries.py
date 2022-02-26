from typing import List, Union
from common import INT_MAX
from MMOEASA.mmoeasaSolution import MMOEASASolution
from Ombuki.ombukiSolution import OmbukiSolution
from problemInstance import ProblemInstance
from vehicle import Vehicle
from destination import Destination

def is_nondominated(Parent: MMOEASASolution, Child: MMOEASASolution) -> bool:
    return (Child.total_distance < Parent.total_distance and Child.cargo_unbalance <= Parent.cargo_unbalance) or (Child.total_distance <= Parent.total_distance and Child.cargo_unbalance < Parent.cargo_unbalance)

def is_nondominated_by_any(nondominated_set: List[MMOEASASolution], subject_solution: MMOEASASolution) -> bool:
    i = 0
    for solution in nondominated_set:
        if not is_nondominated(solution, subject_solution):
            nondominated_set[i] = solution
            i += 1
    if i != len(nondominated_set):
        del nondominated_set[i:]
        return True
    return False

def ombuki_is_nondominated(old_solution: OmbukiSolution, new_solution: OmbukiSolution) -> bool:
    return (new_solution.total_distance < old_solution.total_distance and new_solution.num_vehicles <= old_solution.num_vehicles) or (new_solution.total_distance <= old_solution.total_distance and new_solution.num_vehicles < old_solution.num_vehicles)

def ombuki_is_nondominated_by_any(nondominated_set: List[OmbukiSolution], subject_solution: OmbukiSolution) -> bool:
    i = 0
    for solution in nondominated_set:
        if not ombuki_is_nondominated(solution, subject_solution):
            nondominated_set[i] = solution
            i += 1
    if i != len(nondominated_set):
        del nondominated_set[i:]
        return True
    return False

def insert_unvisited_node(I: Union[MMOEASASolution, OmbukiSolution], instance: ProblemInstance, node: int) -> Union[MMOEASASolution, OmbukiSolution]:
    inserted = False
    vehicle = 0
    infeasible_vehicle, lowest_delay = -1, float(INT_MAX)

    while vehicle < len(I.vehicles) and not inserted:
        if I.vehicles[vehicle].current_capacity + instance.nodes[node].demand < instance.capacity_of_vehicles:
            position = I.vehicles[vehicle].get_num_of_customers_visited() + 1
            I.vehicles[vehicle].destinations.insert(position, Destination(instance.nodes[node]))
            I.vehicles[vehicle].calculate_destination_time_window(instance, position - 1, position)

            if I.vehicles[vehicle].destinations[position].arrival_time <= instance.nodes[node].due_date:
                inserted = True
                break
            elif not len(I.vehicles) < instance.amount_of_vehicles and I.vehicles[vehicle].destinations[position].wait_time < lowest_delay:
                infeasible_vehicle = vehicle
                lowest_delay = I.vehicles[vehicle].destinations[position].wait_time

            I.vehicles[vehicle].destinations.pop(position)
        if not inserted:
            vehicle += 1

    if not inserted: # in this case, the unvisited node doesn't fit into any of the existing routes, so it needs a new vehicle
        if len(I.vehicles) < instance.amount_of_vehicles:
            new_vehicle = Vehicle.create_route(instance, node=instance.nodes[node])
            I.vehicles.append(new_vehicle)
        else:
            I.vehicles[infeasible_vehicle].destinations.insert(len(I.vehicles[infeasible_vehicle].destinations) - 1, Destination(node=instance.nodes[node]))
            vehicle = infeasible_vehicle

        # these seem unnecessary as the crossover operator invokes all of these methods once it's finished inserting all of the unvisited nodes, but they're needed so that an other invocation of "insert_unvisited_nodes()" will have the correct time windows when determining where to insert an unvisited node
        I.vehicles[vehicle].calculate_destinations_time_windows(instance)
        I.vehicles[vehicle].calculate_vehicle_load(instance)
        I.vehicles[vehicle].calculate_length_of_route(instance)
    else:
        num_customers = I.vehicles[vehicle].get_num_of_customers_visited()
        I.vehicles[vehicle].calculate_destination_time_window(instance, num_customers, num_customers + 1)
        I.vehicles[vehicle].current_capacity += instance.nodes[node].demand
        I.vehicles[vehicle].route_distance += instance.get_distance(node, 0)

    return I

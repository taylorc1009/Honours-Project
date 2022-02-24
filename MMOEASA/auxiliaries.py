from typing import List, Union
from numpy import random
from constants import INT_MAX
from MMOEASA.mmoeasaSolution import MMOEASASolution
from Ombuki.ombukiSolution import OmbukiSolution
from problemInstance import ProblemInstance
from vehicle import Vehicle
from destination import Destination
import copy

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

def rand(start: int, end: int, exclude_values: List[int]=None) -> int:
    # '+ 1' to make the random number generator inclusive of the "end" value
    offset = 1 if end < INT_MAX else 0
    random_val = random.randint(start, end + offset)
    while exclude_values is not None and random_val in exclude_values:
        random_val = random.randint(start, end + offset)
    return random_val

def insert_unvisited_node(I: Union[MMOEASASolution, OmbukiSolution], instance: ProblemInstance, node: int) -> Union[MMOEASASolution, OmbukiSolution]:
    inserted = False
    vehicle = 0
    infeasible_vehicle, lowest_delay = -1, float(INT_MAX)

    while vehicle < len(I.vehicles) and not inserted:
        customers_on_route = I.vehicles[vehicle].get_num_of_customers_visited()
        final_customer = I.vehicles[vehicle].destinations[customers_on_route].node.number
        vehicle_backup = copy.deepcopy(I.vehicles[vehicle])

        I.vehicles[vehicle].destinations[customers_on_route + 1].node = instance.nodes[node]
        I.vehicles[vehicle].current_capacity += instance.nodes[node].demand

        I.vehicles[vehicle].destinations[customers_on_route + 1].arrival_time = I.vehicles[vehicle].destinations[customers_on_route].departure_time + instance.get_distance(final_customer, node)
        I.vehicles[vehicle].destinations[customers_on_route + 1].wait_time = 0.0
        if I.vehicles[vehicle].destinations[customers_on_route + 1].arrival_time < instance.nodes[node].ready_time:
            I.vehicles[vehicle].destinations[customers_on_route + 1].wait_time = instance.nodes[node].ready_time - I.vehicles[vehicle].destinations[customers_on_route + 1].arrival_time
            I.vehicles[vehicle].destinations[customers_on_route + 1].arrival_time = instance.nodes[node].ready_time

        if I.vehicles[vehicle].destinations[customers_on_route + 1].arrival_time <= instance.nodes[node].due_date:
            I.vehicles[vehicle].destinations[customers_on_route + 1].departure_time = instance.nodes[node].service_duration + I.vehicles[vehicle].destinations[customers_on_route + 1].arrival_time
            I.calculate_length_of_routes(instance)
            inserted = True
        elif I.vehicles[vehicle].destinations[customers_on_route + 1].arrival_time > instance.nodes[node].due_date or I.vehicles[vehicle].current_capacity > instance.capacity_of_vehicles:
            arrival_delay = I.vehicles[vehicle].destinations[customers_on_route + 1].arrival_time - instance.nodes[node].due_date
            if not len(I.vehicles) < instance.amount_of_vehicles and arrival_delay < lowest_delay and not I.vehicles[vehicle].current_capacity > instance.capacity_of_vehicles:
                infeasible_vehicle = vehicle
                lowest_delay = I.vehicles[vehicle].destinations[customers_on_route + 1].arrival_time - instance.nodes[node].due_date
            I.vehicles[vehicle] = vehicle_backup
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
        I.vehicles[vehicle] = reinitialize_return_to_depot(I.vehicles[vehicle], instance)

    return I

def reinitialize_return_to_depot(vehicle: Vehicle, instance: ProblemInstance) -> Vehicle:
    if not vehicle.destinations[-1].node.number == 0:
        vehicle.destinations.append(Destination(node=instance.nodes[0]))

    customers_on_route = vehicle.get_num_of_customers_visited()
    final_customer = vehicle.destinations[customers_on_route].node.number

    vehicle.destinations[customers_on_route + 1].arrival_time = vehicle.destinations[customers_on_route + 1].departure_time + instance.get_distance(final_customer, 0)
    vehicle.destinations[customers_on_route + 1].departure_time = vehicle.destinations[customers_on_route + 1].departure_time + instance.get_distance(final_customer, 0)
    vehicle.destinations[customers_on_route + 1].wait_time = 0.0
    
    return vehicle
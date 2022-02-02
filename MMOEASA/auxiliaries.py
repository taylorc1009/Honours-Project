from typing import List
from numpy import random
from MMOEASA.constants import INT_MAX
from MMOEASA.solution import Solution
from problemInstance import ProblemInstance
from vehicle import Vehicle
from destination import Destination
import copy

def rand(start: int, end: int, exclude_values: List[int]=None) -> int:
    # '+ 1' to make the random number generator inclusive of the "end" value
    offset = 1 if end < INT_MAX else 0
    random_val = random.randint(start, end + offset)
    while exclude_values is not None and random_val in exclude_values:
        random_val = random.randint(start, end + offset)
    return random_val

def insert_unvisited_node(I: Solution, instance: ProblemInstance, node: int) -> Solution:
    inserted = False
    vehicle = 0

    while vehicle < len(I.vehicles) and not inserted:
        customers_on_route = I.vehicles[vehicle].get_num_of_customers_visited()
        final_customer = I.vehicles[vehicle].destinations[customers_on_route].node.number
        vehicle_backup = copy.deepcopy(I.vehicles[vehicle])

        I.vehicles[vehicle].destinations[customers_on_route + 1].node = instance.nodes[node]
        I.vehicles[vehicle].current_capacity += instance.nodes[node].demand

        I.vehicles[vehicle].destinations[customers_on_route + 1].arrival_time = I.vehicles[vehicle].destinations[customers_on_route].departure_time + instance.MMOEASA_distances[final_customer][node]
        I.vehicles[vehicle].destinations[customers_on_route + 1].wait_time = 0.0
        if I.vehicles[vehicle].destinations[customers_on_route + 1].arrival_time < instance.nodes[node].ready_time:
            I.vehicles[vehicle].destinations[customers_on_route + 1].wait_time = instance.nodes[node].ready_time - I.vehicles[vehicle].destinations[customers_on_route + 1].arrival_time
            I.vehicles[vehicle].destinations[customers_on_route + 1].arrival_time = instance.nodes[node].ready_time
        
        if I.vehicles[vehicle].destinations[customers_on_route + 1].arrival_time <= instance.nodes[node].due_date:
            I.vehicles[vehicle].destinations[customers_on_route + 1].departure_time = instance.nodes[node].service_duration + I.vehicles[vehicle].destinations[customers_on_route + 1].arrival_time
            I.calculate_length_of_routes(instance)
            inserted = True
        elif I.vehicles[vehicle].destinations[customers_on_route + 1].arrival_time > instance.nodes[node].due_date or I.vehicles[vehicle].current_capacity > instance.capacity_of_vehicles:
            I.vehicles[vehicle] = vehicle_backup
            vehicle += 1

    if not inserted: # in this case, the unvisited node doesn't fit into any of the existing routes, so it needs a new vehicle
        destinations = [Destination(node=instance.nodes[0]), Destination(node=instance.nodes[node]), Destination(node=instance.nodes[0])]
        I.vehicles.append(Vehicle(current_capacity=instance.nodes[node].demand, destinations=destinations))

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

    vehicle.destinations[customers_on_route + 1].arrival_time = vehicle.destinations[customers_on_route + 1].departure_time + instance.MMOEASA_distances[final_customer][0]
    vehicle.destinations[customers_on_route + 1].departure_time = vehicle.destinations[customers_on_route + 1].departure_time + instance.MMOEASA_distances[final_customer][0]
    vehicle.destinations[customers_on_route + 1].wait_time = 0.0
    
    return vehicle
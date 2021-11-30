from MMOEASA.solution import Solution
from problemInstance import ProblemInstance
from vehicle import Vehicle
from destination import Destination
import copy

def solution_visits_destination(node: int, instance: ProblemInstance, I: Solution) -> bool:
    for i, _ in enumerate(I.vehicles):
        if I.vehicles[i].getNumOfCustomersVisited() >= 1:
            for j, _ in enumerate(I.vehicles[i].destinations):
                if I.vehicles[i].destinations[j].node.number == instance.nodes[node].number: # directly get the destination number from the list of destinations in case there's a mismatch between the destination number and the for loop iterator (although there shouldn't)
                    return True
    return False

def insert_unvisited_node(I: Solution, instance: ProblemInstance, node: int) -> Solution:
    inserted = False
    vehicle = 0

    while vehicle < len(I.vehicles) and not inserted:
        length_of_route = I.vehicles[vehicle].getNumOfCustomersVisited()
        print(len(I.vehicles[vehicle].destinations), length_of_route, vehicle)
        final_destination = I.vehicles[vehicle].destinations[length_of_route].node.number
        vehicle_backup = copy.deepcopy(I.vehicles[vehicle])

        I.vehicles[vehicle].destinations[length_of_route + 1].node = instance.nodes[node]
        I.vehicles[vehicle].current_capacity += instance.nodes[node].demand

        I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time = I.vehicles[vehicle].destinations[length_of_route].departure_time + instance.MMOEASA_distances[final_destination][node]
        I.vehicles[vehicle].destinations[length_of_route + 1].wait_time = 0.0
        if I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time < instance.nodes[node].ready_time:
            I.vehicles[vehicle].destinations[length_of_route + 1].wait_time = instance.nodes[node].ready_time - I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time
            I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time = instance.nodes[node].ready_time
        
        if I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time <= instance.nodes[node].due_date:
            I.vehicles[vehicle].destinations[length_of_route + 1].departure_time = instance.nodes[node].service_duration + I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time

            I.calculate_lengths_of_routes(instance)

            inserted = True
        elif I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time > instance.nodes[node].due_date or I.vehicles[vehicle].current_capacity > instance.capacity_of_vehicles:
            I.vehicles[vehicle] = vehicle_backup
            vehicle += 1

    if not inserted:
        destinations = [Destination(node=instance.nodes[0]), Destination(node=instance.nodes[node]), Destination(node=instance.nodes[0])]
        I.vehicles.append(Vehicle(number=vehicle, current_capacity=instance.nodes[node].demand, destinations=destinations))
        
        I.vehicles[vehicle].calculate_destinations_time_windows(instance)
        I.vehicles[vehicle].calculate_vehicle_load(instance)
        I.vehicles[vehicle].calculate_length_of_route(instance)

        return I

    I.vehicles[vehicle] = reinitialize_return_to_depot(I.vehicles[vehicle], instance)
    return I

def reinitialize_return_to_depot(vehicle: Vehicle, instance: ProblemInstance) -> Vehicle:
    if not vehicle.destinations[-1].node.number == 0:
        vehicle.destinations.append(Destination(node=instance.nodes[0]))

    length_of_route = vehicle.getNumOfCustomersVisited()
    print(len(vehicle.destinations), length_of_route)
    final_destination = vehicle.destinations[length_of_route].node.number

    print(len(instance.MMOEASA_distances), len(instance.MMOEASA_distances[final_destination]), final_destination)
    vehicle.destinations[length_of_route + 1].arrival_time = vehicle.destinations[length_of_route + 1].departure_time + instance.MMOEASA_distances[final_destination][0]
    vehicle.destinations[length_of_route + 1].departure_time = vehicle.destinations[length_of_route + 1].departure_time + instance.MMOEASA_distances[final_destination][0]
    vehicle.destinations[length_of_route + 1].wait_time = 0.0
    
    return vehicle
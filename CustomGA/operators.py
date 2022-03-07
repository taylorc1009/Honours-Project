import copy
from random import shuffle
from typing import List
from CustomGA.constants import MUTATION_LONGEST_WAIT_PROBABILITY, MUTATION_LONGEST_ROUTE_PROBABILITY
from CustomGA.customGASolution import CustomGASolution
from common import INT_MAX, rand
from problemInstance import ProblemInstance
from vehicle import Vehicle

def set_up_crossover_child(instance: ProblemInstance, parent_one: CustomGASolution, parent_two_vehicle: Vehicle) -> CustomGASolution:
    child_solution = copy.deepcopy(parent_one)

    nodes_to_remove = {d.node.number for d in parent_two_vehicle.get_customers_visited()}
    i = 0
    while i < len(child_solution.vehicles) and nodes_to_remove:
        increment = True
        j = 1
        while j <= child_solution.vehicles[i].get_num_of_customers_visited() and nodes_to_remove:
            destination = child_solution.vehicles[i].destinations[j]
            if destination.node.number in nodes_to_remove:
                nodes_to_remove.remove(destination.node.number)
                child_solution.vehicles[i].current_capacity -= destination.node.demand
                if child_solution.vehicles[i].get_num_of_customers_visited() - 1 > 0:
                    del child_solution.vehicles[i].destinations[j]
                else:
                    increment = False
                    del child_solution.vehicles[i]
                    break  # break, otherwise the while loop will start searching the next vehicle with "j" as the same value; without incrementing "i" and starting "j" at 0
            else:
                j += 1
        if increment:
            i += 1

    child_solution.calculate_nodes_time_windows(instance)
    child_solution.calculate_vehicles_loads(instance)

    return child_solution

def crossover(instance: ProblemInstance, parent_one: CustomGASolution, parent_two_vehicle: Vehicle) -> CustomGASolution:
    crossover_solution = set_up_crossover_child(instance, parent_one, parent_two_vehicle)

    randomized_destinations = list(range(1, len(parent_two_vehicle.destinations) - 1))
    shuffle(randomized_destinations)
    for d in randomized_destinations:
        parent_destination = parent_two_vehicle.destinations[d]
        best_vehicle, best_position = instance.amount_of_vehicles, 1
        shortest_from_previous, shortest_to_next = (float(INT_MAX),) * 2
        highest_wait_time = 0.0
        found_feasible_location = False

        for i, vehicle in enumerate(crossover_solution.vehicles):
            if not vehicle.current_capacity + parent_destination.node.demand > instance.capacity_of_vehicles:
                for j in range(1, len(crossover_solution.vehicles[i].destinations)):
                    #crossover_solution.vehicles[i].destinations.insert(j, copy.deepcopy(parent_destination))
                    #crossover_solution.vehicles[i].calculate_destination_time_window(instance, j - 1, j)

                    distance_from_previous = instance.get_distance(vehicle.destinations[j - 1].node.number, parent_destination.node.number)
                    distance_to_next = instance.get_distance(parent_destination.node.number, vehicle.destinations[j].node.number)

                    simulated_arrival_time = vehicle.destinations[j - 1].departure_time + distance_from_previous
                    if simulated_arrival_time < parent_destination.node.ready_time:
                        simulated_arrival_time = parent_destination.node.ready_time
                    simulated_departure_time = simulated_arrival_time + parent_destination.node.service_duration

                    if not (simulated_arrival_time > parent_destination.node.due_date or simulated_departure_time + distance_to_next > vehicle.destinations[j].node.due_date) \
                            and ((distance_from_previous < shortest_from_previous and distance_to_next <= shortest_to_next) or (distance_from_previous <= shortest_from_previous and distance_to_next < shortest_to_next)):
                        best_vehicle, best_position, shortest_from_previous, shortest_to_next = i, j, distance_from_previous, distance_to_next
                        found_feasible_location = True
                    elif not found_feasible_location and crossover_solution.vehicles[i].destinations[j - 1].wait_time > highest_wait_time:
                        best_vehicle, best_position, highest_wait_time = i, j - 1, crossover_solution.vehicles[i].destinations[j - 1].wait_time

                    #del crossover_solution.vehicles[i].destinations[j]

        if not found_feasible_location and len(crossover_solution.vehicles) < instance.amount_of_vehicles:
            best_vehicle = len(crossover_solution.vehicles)
            crossover_solution.vehicles.append(Vehicle.create_route(instance, parent_destination.node))
        else:
            crossover_solution.vehicles[best_vehicle].destinations.insert(best_position, copy.deepcopy(parent_destination))

        crossover_solution.vehicles[best_vehicle].calculate_vehicle_load(instance)
        crossover_solution.vehicles[best_vehicle].calculate_destinations_time_windows(instance)
        crossover_solution.vehicles[best_vehicle].calculate_length_of_route(instance)

    crossover_solution.objective_function(instance)
    return crossover_solution

def select_random_vehicle(solution: CustomGASolution, customers_required: int=2) -> int:
    random_vehicle = -1
    exclude_values = set()
    while not random_vehicle >= 0:
        random_vehicle = rand(0, len(solution.vehicles) - 1, exclude_values=exclude_values)
        if not solution.vehicles[random_vehicle].get_num_of_customers_visited() >= customers_required:
            exclude_values.add(random_vehicle)
            random_vehicle = -1
    return random_vehicle

def select_route_with_longest_wait(solution: CustomGASolution) -> int:
    longest_waiting_vehicle = -1
    longest_total_wait = 0.0
    if rand(1, 100) < MUTATION_LONGEST_WAIT_PROBABILITY:
        for v, vehicle in enumerate(solution.vehicles):
            if vehicle.get_num_of_customers_visited() > 1:
                total_wait = 0.0
                for destination in vehicle.get_customers_visited():
                    total_wait += destination.wait_time
                    if total_wait > longest_total_wait:
                        longest_waiting_vehicle = v
                        longest_total_wait = total_wait
    if not longest_waiting_vehicle >= 0:
        longest_waiting_vehicle = select_random_vehicle(solution)
    return longest_waiting_vehicle

def TWBS_mutation(instance: ProblemInstance, solution: CustomGASolution) -> CustomGASolution: #	Time-Window-based Sort Mutator
    longest_waiting_vehicle = select_route_with_longest_wait(solution)

    solution.vehicles[longest_waiting_vehicle].destinations[1:-1] = sorted(solution.vehicles[longest_waiting_vehicle].get_customers_visited(), key=lambda d: d.node.ready_time)

    solution.vehicles[longest_waiting_vehicle].calculate_destinations_time_windows(instance)
    solution.vehicles[longest_waiting_vehicle].calculate_length_of_route(instance)
    solution.objective_function(instance)

    return solution

def swap(l: List, index_one: int, index_two: int):
    l[index_one], l[index_two] = l[index_two], l[index_one]

def TWBSw_mutation(instance: ProblemInstance, solution: CustomGASolution) -> CustomGASolution: # Time-Window-based Swap Mutator
    longest_waiting_vehicle = select_route_with_longest_wait(solution)

    for d in range(1, solution.vehicles[longest_waiting_vehicle].get_num_of_customers_visited()):
        if solution.vehicles[longest_waiting_vehicle].destinations[d].node.ready_time > solution.vehicles[longest_waiting_vehicle].destinations[d + 1].node.ready_time:
            swap(solution.vehicles[longest_waiting_vehicle].destinations, d, d + 1)
            break

    solution.vehicles[longest_waiting_vehicle].calculate_destinations_time_windows(instance)
    solution.vehicles[longest_waiting_vehicle].calculate_length_of_route(instance)
    solution.objective_function(instance)

    return solution

def swap_high_wait_time_destinations(instance: ProblemInstance, solution: CustomGASolution, just_once: bool=False) -> CustomGASolution:
    longest_waiting_vehicle = select_route_with_longest_wait(solution)

    destination = 1
    while destination <= solution.vehicles[longest_waiting_vehicle].get_num_of_customers_visited() - 1:
        if solution.vehicles[longest_waiting_vehicle].destinations[destination].wait_time > solution.vehicles[longest_waiting_vehicle].destinations[destination + 1].wait_time:
            swap(solution.vehicles[longest_waiting_vehicle].destinations, destination, destination + 1)
            for _ in range(2):
                solution.vehicles[longest_waiting_vehicle].calculate_destination_time_window(instance, destination - 1, destination)
                destination += 1
            if just_once:
                break
        else:
            destination += 1

    d = len(solution.vehicles[longest_waiting_vehicle].destinations) - 1
    solution.vehicles[longest_waiting_vehicle].calculate_destination_time_window(instance, d - 1, d)
    solution.vehicles[longest_waiting_vehicle].calculate_length_of_route(instance)
    solution.objective_function(instance)

    return solution

def WTBS_mutation(instance: ProblemInstance, solution: CustomGASolution) -> CustomGASolution: # Wait-Time-based Swap Mutator
    return swap_high_wait_time_destinations(instance, solution)

def SWTBS_mutation(instance: ProblemInstance, solution: CustomGASolution) -> CustomGASolution: # Single Wait-Time-based Swap Mutator
    return swap_high_wait_time_destinations(instance, solution, just_once=True)

def swap_long_distance_destinations(instance: ProblemInstance, solution: CustomGASolution, just_once: bool=False) -> CustomGASolution:
    longest_route_length = 0
    furthest_travelling_vehicle = -1
    if rand(1, 100) < MUTATION_LONGEST_ROUTE_PROBABILITY:
        for v, vehicle in enumerate(solution.vehicles):
            if vehicle.route_distance > longest_route_length and vehicle.get_num_of_customers_visited() > 2:
                furthest_travelling_vehicle = v
                longest_route_length = vehicle.route_distance
    if not furthest_travelling_vehicle >= 0:
        furthest_travelling_vehicle = select_random_vehicle(solution, customers_required=3)

    destination = 1
    while destination <= solution.vehicles[furthest_travelling_vehicle].get_num_of_customers_visited() - 2:
        if instance.get_distance(solution.vehicles[furthest_travelling_vehicle].destinations[destination].node.number, solution.vehicles[furthest_travelling_vehicle].destinations[destination + 1].node.number) > instance.get_distance(solution.vehicles[furthest_travelling_vehicle].destinations[destination].node.number, solution.vehicles[furthest_travelling_vehicle].destinations[destination + 2].node.number):
            swap(solution.vehicles[furthest_travelling_vehicle].destinations, destination + 1, destination + 2)
            if just_once:
                break
        destination += 1

    solution.vehicles[furthest_travelling_vehicle].calculate_length_of_route(instance)
    solution.vehicles[furthest_travelling_vehicle].calculate_destinations_time_windows(instance)
    solution.objective_function(instance)

    return solution

def DBS_mutation(instance: ProblemInstance, solution: CustomGASolution) -> CustomGASolution: # Distance-based Swap Mutator
    return swap_long_distance_destinations(instance, solution)

def SDBS_mutation(instance: ProblemInstance, solution: CustomGASolution) -> CustomGASolution: # Single Distance-based Swap Mutator
    return swap_long_distance_destinations(instance, solution, just_once=True)

def move_destination_to_fit_window(instance: ProblemInstance, solution: CustomGASolution, reverse: bool=False) -> CustomGASolution:
    random_vehicle = select_random_vehicle(solution)

    sorted_destinations = sorted(solution.vehicles[random_vehicle].get_customers_visited(), key=lambda d: d.node.ready_time)
    destinations = list(enumerate(solution.vehicles[random_vehicle].get_customers_visited(), 1))
    if reverse:
        destinations = reversed(destinations)
    for d, destination in destinations:
        if destination.node.number != sorted_destinations[d - 1].node.number:
            solution.vehicles[random_vehicle].destinations.insert(d, solution.vehicles[random_vehicle].destinations.pop(d))
            break

    solution.vehicles[random_vehicle].calculate_destinations_time_windows(instance)
    solution.vehicles[random_vehicle].calculate_length_of_route(instance)
    solution.objective_function(instance)

    return solution

def TWBMF_mutation(instance: ProblemInstance, solution: CustomGASolution) -> CustomGASolution: # Time-Window-based Move Forward Mutator
    return move_destination_to_fit_window(instance, solution)

def TWBPB_mutation(instance: ProblemInstance, solution: CustomGASolution) -> CustomGASolution: # Time-Window-based Push-back Mutator
    return move_destination_to_fit_window(instance, solution, reverse=True)

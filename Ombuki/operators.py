import copy
from random import shuffle
from typing import Dict, List
from Ombuki.constants import INT_MAX, MUTATION_REVERSAL_LENGTH
from Ombuki.auxiliaries import rand, is_nondominated
from Ombuki.solution import Solution
from threading import Thread, currentThread
from destination import Destination
from problemInstance import ProblemInstance
from vehicle import Vehicle

def t_crossover(instance: ProblemInstance, solution: Solution, parent_vehicle: Vehicle, result: Dict[str, Solution]):
    nodes_to_remove = set([d.node.number for d in parent_vehicle.get_customers_visited()])
    for i, vehicle in enumerate(solution.vehicles):
        j = 1
        while j <= vehicle.get_num_of_customers_visited():
            destination = solution.vehicles[i].destinations[j]
            if destination.node.number in nodes_to_remove:
                solution.vehicles[i].current_capacity -= destination.node.demand
                del solution.vehicles[i].destinations[j]
            else:
                j += 1

    solution.calculate_nodes_time_windows(instance)

    randomized_destinations = list(range(len(parent_vehicle.destinations)))
    shuffle(randomized_destinations)
    for d in randomized_destinations:
        parent_destination = parent_vehicle.destinations[d]
        best_vehicle, best_position = -1, 0
        shortest_from_previous, shortest_to_next = (float(INT_MAX),) * 2

        for i, vehicle in enumerate(solution.vehicles):
            if not vehicle.current_capacity + parent_destination.node.demand > instance.capacity_of_vehicles:
                for j in range(1, len(solution.vehicles[i].destinations)):
                    solution.vehicles[i].destinations.insert(j, parent_destination)
                    solution.vehicles[i].calculate_destination_time_window(instance, j - 1, j)

                    distance_from_previous = instance.get_distance(vehicle.destinations[j - 1].node.number, vehicle.destinations[j].node.number)
                    distance_to_next = instance.get_distance(vehicle.destinations[j].node.number, vehicle.destinations[j + 1].node.number)

                    if not (vehicle.destinations[j - 1].departure_time + distance_from_previous > vehicle.destinations[j].node.due_date or vehicle.destinations[j].departure_time + distance_to_next > vehicle.destinations[j + 1].node.due_date):
                        if (distance_from_previous < shortest_from_previous and distance_to_next <= shortest_to_next) or (distance_from_previous <= shortest_from_previous and distance_to_next < shortest_to_next):
                            best_vehicle, best_position, shortest_from_previous, shortest_to_next = i, j, distance_from_previous, distance_to_next

                    del solution.vehicles[i].destinations[j]
        if best_vehicle >= 0 and best_position > 0:
            solution.vehicles[best_vehicle].destinations.insert(best_position, copy.deepcopy(parent_destination))
            """for k in range(j, len(vehicle.destinations)):
                solution.vehicles[i].calculate_destination_time_window(instance, k - 1, k)"""
            solution.vehicles[best_vehicle].calculate_vehicle_load(instance)
            solution.vehicles[best_vehicle].calculate_destinations_time_windows(instance)
            solution.vehicles[best_vehicle].calculate_length_of_route(instance)
            solution.objective_function(instance)
        elif len(solution.vehicles) < instance.amount_of_vehicles:
            solution.vehicles.append(Vehicle.create_route(instance, copy.deepcopy(parent_destination.node)))
            solution.vehicles[-1].calculate_vehicle_load(instance)
            solution.vehicles[-1].calculate_destinations_time_windows(instance)
            solution.vehicles[-1].calculate_length_of_route(instance)
            solution.objective_function(instance)
        else:
            # do something to accommodate the infeasible solution
            continue

    result[currentThread().getName()] = solution

def crossover(instance: ProblemInstance, parent_one: Solution, parent_two: Solution) -> Solution:
    parent_one_vehicle = parent_one.vehicles[rand(0, len(parent_one.vehicles) - 1)]
    parent_two_vehicle = parent_two.vehicles[rand(0, len(parent_two.vehicles) - 1)]
    parent_two.id = parent_one.id # parent two will be the selection tournament winner, so the ID of parent_one will be the current index of "population" in the main algorithm

    # threads cannot return values, so they need to be given a mutable type that can be given the values we'd like to return; in this instance, a list is used
    thread_results: Dict[str, Solution] = {"child_one": None, "child_two": None}
    child_one_thread = Thread(name="child_one", target=t_crossover, args=(instance, parent_one, parent_two_vehicle, thread_results))
    child_two_thread = Thread(name="child_two", target=t_crossover, args=(instance, parent_two, parent_one_vehicle, thread_results))
    child_one_thread.start()
    child_two_thread.start()
    child_one_thread.join()
    child_two_thread.join()

    return thread_results["child_one"] if is_nondominated(thread_results["child_one"], thread_results["child_two"]) else thread_results["child_two"]

def get_next_vehicles_destinations(solution: Solution, vehicle: int, first_destination: int, remaining_destinations: int):
    num_customers = solution.vehicles[vehicle].get_num_of_customers_visited()
    position = (num_customers + 1) - first_destination
    if position < remaining_destinations and remaining_destinations > 1:
        return solution.vehicles[vehicle].destinations[first_destination:num_customers+1] + get_next_vehicles_destinations(solution, vehicle + 1, 1, remaining_destinations - position)
    else:
        return solution.vehicles[vehicle].destinations[first_destination:first_destination+remaining_destinations]

def set_next_vehicles_destinations(solution: Solution, vehicle: int, first_destination: int, remaining_destinations: int, reversed_destinations: List[Destination]):
    num_customers = solution.vehicles[vehicle].get_num_of_customers_visited()
    position = (num_customers + 1) - first_destination
    if position < remaining_destinations and remaining_destinations > 1:
        solution.vehicles[vehicle].destinations[first_destination:num_customers+1] = reversed_destinations[0:position]
        del reversed_destinations[0:position]
        set_next_vehicles_destinations(solution, vehicle + 1, 1, remaining_destinations - position, reversed_destinations)
    else:
        solution.vehicles[vehicle].destinations[first_destination:first_destination+remaining_destinations] = reversed_destinations

def mutation(instance: ProblemInstance, solution: Solution) -> Solution:
    num_nodes_to_swap = rand(2, MUTATION_REVERSAL_LENGTH)
    first_reversal_node = rand(1, len(instance.nodes) - num_nodes_to_swap)

    vehicle_num = -1
    num_destinations_tracker = 0
    for i, vehicle in enumerate(solution.vehicles):
        if not num_destinations_tracker + vehicle.get_num_of_customers_visited() > first_reversal_node:
            num_destinations_tracker += vehicle.get_num_of_customers_visited()
        else:
            vehicle_num = i
            break

    first_destination = first_reversal_node - num_destinations_tracker
    reversed_destinations = get_next_vehicles_destinations(solution, vehicle_num, first_destination, num_nodes_to_swap)
    reversed_destinations = list(reversed(reversed_destinations))
    set_next_vehicles_destinations(solution, vehicle_num, first_destination, num_nodes_to_swap, reversed_destinations)

    solution.vehicles[vehicle_num].calculate_vehicle_load(instance)
    solution.vehicles[vehicle_num].calculate_destinations_time_windows(instance)
    solution.vehicles[vehicle_num].calculate_length_of_route(instance)
    solution.objective_function(instance)
    return solution
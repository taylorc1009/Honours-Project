import copy
from random import shuffle
from typing import List, Union
from Ombuki.constants import INT_MAX
from Ombuki.auxiliaries import rand, is_nondominated
from Ombuki.solution import Solution
from threading import Thread
from problemInstance import ProblemInstance
from vehicle import Vehicle

def t_crossover(instance: ProblemInstance, solution: Solution, parent_vehicle: Vehicle, result: List[Union[List[Solution], int]]):
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

    #solution.calculate_vehicles_loads(instance)
    solution.calculate_nodes_time_windows(instance)
    #solution.calculate_length_of_routes(instance)

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

    result[0][result[1]] = solution

def crossover(instance: ProblemInstance, parent_one: Solution, parent_two: Solution) -> Solution:
    parent_one_vehicle = parent_one.vehicles[rand(0, len(parent_one.vehicles) - 1)]
    parent_two_vehicle = parent_two.vehicles[rand(0, len(parent_two.vehicles) - 1)]

    # threads cannot return values, so they need to be given a mutable type that can be given the values we'd like to return; in this instance, a list is used

    thread_results: List[Solution] = [None, None]
    child_one_thread = Thread(target=t_crossover, args=(instance, parent_one, parent_two_vehicle, [thread_results, 0]))
    child_two_thread = Thread(target=t_crossover, args=(instance, parent_two, parent_one_vehicle, [thread_results, 1]))
    child_one_thread.start()
    child_two_thread.start()
    child_one_thread.join()
    child_two_thread.join()

    return thread_results[0] if is_nondominated(thread_results[0], thread_results[1]) else thread_results[1]

def mutation(solution: Solution) -> Solution:
    pass
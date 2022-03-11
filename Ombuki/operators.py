import copy
from random import shuffle
from typing import Dict, List, Union
from Ombuki.constants import MUTATION_REVERSAL_LENGTH
from Ombuki.auxiliaries import rand, is_nondominated, mmoeasa_is_nondominated
from Ombuki.ombukiSolution import OmbukiSolution
from MMOEASA.mmoeasaSolution import MMOEASASolution
from threading import Thread, currentThread
from destination import Destination
from problemInstance import ProblemInstance
from vehicle import Vehicle
from common import INT_MAX

def set_up_crossover_child(instance: ProblemInstance, parent_one: Union[OmbukiSolution, MMOEASASolution], parent_two_vehicle: Vehicle) -> OmbukiSolution:
    crossover_solution = copy.deepcopy(parent_one)

    nodes_to_remove = set([d.node.number for d in parent_two_vehicle.get_customers_visited()])
    i = 0
    while i < len(crossover_solution.vehicles) and nodes_to_remove:
        increment = True
        j = 1
        while j <= crossover_solution.vehicles[i].get_num_of_customers_visited() and nodes_to_remove:
            destination = crossover_solution.vehicles[i].destinations[j]
            if destination.node.number in nodes_to_remove:
                nodes_to_remove.remove(destination.node.number)
                crossover_solution.vehicles[i].current_capacity -= destination.node.demand
                if crossover_solution.vehicles[i].get_num_of_customers_visited() - 1 > 0:
                    del crossover_solution.vehicles[i].destinations[j]
                else:
                    increment = False
                    del crossover_solution.vehicles[i]
                    break # break, otherwise the while loop will start searching the next vehicle with "j" as the same value; without incrementing "i" and starting "j" at 0
            else:
                j += 1
        if increment:
            i += 1

    crossover_solution.calculate_nodes_time_windows(instance)
    crossover_solution.calculate_vehicles_loads(instance)

    return crossover_solution

def original_crossover_thread(instance: ProblemInstance, solution: Union[OmbukiSolution, MMOEASASolution], parent_vehicle: Vehicle, result: Dict[str, Union[OmbukiSolution, MMOEASASolution]]) -> None:
    crossover_solution = set_up_crossover_child(instance, solution, parent_vehicle)

    randomized_destinations = list(range(1, len(parent_vehicle.destinations) - 1))
    shuffle(randomized_destinations)
    for d in randomized_destinations:
        parent_destination = parent_vehicle.destinations[d]
        best_vehicle, best_position = INT_MAX, 0
        shortest_from_previous, shortest_to_next = (float(INT_MAX),) * 2
        found_feasible_location = False

        for i, vehicle in enumerate(crossover_solution.vehicles):
            if not vehicle.current_capacity + parent_destination.node.demand > instance.capacity_of_vehicles:
                for j in range(1, len(crossover_solution.vehicles[i].destinations)):
                    distance_from_previous = instance.get_distance(vehicle.destinations[j - 1].node.number, parent_destination.node.number)
                    distance_to_next = instance.get_distance(parent_destination.node.number, vehicle.destinations[j].node.number)

                    simulated_arrival_time = vehicle.destinations[j - 1].departure_time + distance_from_previous
                    if simulated_arrival_time < parent_destination.node.ready_time:
                        simulated_arrival_time = parent_destination.node.ready_time
                    simulated_departure_time = simulated_arrival_time + parent_destination.node.service_duration

                    if not (simulated_arrival_time > parent_destination.node.due_date or simulated_departure_time + distance_to_next > vehicle.destinations[j].node.due_date) \
                            and (distance_from_previous < shortest_from_previous and distance_to_next <= shortest_to_next) or (distance_from_previous <= shortest_from_previous and distance_to_next < shortest_to_next):
                        best_vehicle, best_position, shortest_from_previous, shortest_to_next = i, j, distance_from_previous, distance_to_next
                        found_feasible_location = True

        if not found_feasible_location:
            best_vehicle = len(crossover_solution.vehicles)
            crossover_solution.vehicles.append(Vehicle.create_route(instance, parent_destination.node))
        else:
            crossover_solution.vehicles[best_vehicle].destinations.insert(best_position, copy.deepcopy(parent_destination))

        crossover_solution.vehicles[best_vehicle].calculate_vehicle_load(instance)
        crossover_solution.vehicles[best_vehicle].calculate_destinations_time_windows(instance)
        crossover_solution.vehicles[best_vehicle].calculate_length_of_route(instance)

    crossover_solution.objective_function(instance)
    result[currentThread().getName()] = crossover_solution

def modified_crossover_thread(instance: ProblemInstance, solution: Union[OmbukiSolution, MMOEASASolution], parent_vehicle: Vehicle, result: Dict[str, Union[OmbukiSolution, MMOEASASolution]]) -> None:
    crossover_solution = set_up_crossover_child(instance, solution, parent_vehicle)

    randomized_destinations = list(range(1, len(parent_vehicle.destinations) - 1))
    shuffle(randomized_destinations)
    for d in randomized_destinations:
        parent_destination = parent_vehicle.destinations[d]
        best_vehicle, best_position = -1, 0
        shortest_from_previous, shortest_to_next, infeasible_shortest_from_previous, infeasible_shortest_to_next = (float(INT_MAX),) * 4
        found_feasible_location = False

        for i, vehicle in enumerate(crossover_solution.vehicles):
            if not vehicle.current_capacity + parent_destination.node.demand > instance.capacity_of_vehicles:
                for j in range(1, len(crossover_solution.vehicles[i].destinations)):
                    distance_from_previous = instance.get_distance(vehicle.destinations[j - 1].node.number, parent_destination.node.number)
                    distance_to_next = instance.get_distance(parent_destination.node.number, vehicle.destinations[j].node.number)

                    simulated_arrival_time = vehicle.destinations[j - 1].departure_time + distance_from_previous
                    if simulated_arrival_time < parent_destination.node.ready_time:
                        simulated_arrival_time = parent_destination.node.ready_time
                    simulated_departure_time = simulated_arrival_time + parent_destination.node.service_duration

                    if not (simulated_arrival_time > parent_destination.node.due_date or simulated_departure_time + distance_to_next > vehicle.destinations[j].node.due_date) \
                            and (distance_from_previous < shortest_from_previous and distance_to_next <= shortest_to_next) or (distance_from_previous <= shortest_from_previous and distance_to_next < shortest_to_next):
                        best_vehicle, best_position, shortest_from_previous, shortest_to_next = i, j, distance_from_previous, distance_to_next
                        found_feasible_location = True
                    elif not found_feasible_location and (distance_from_previous < infeasible_shortest_from_previous and distance_to_next <= infeasible_shortest_to_next) or (distance_from_previous <= infeasible_shortest_from_previous and distance_to_next < infeasible_shortest_to_next):
                        best_vehicle, best_position, infeasible_shortest_from_previous, infeasible_shortest_to_next = i, j, distance_from_previous, distance_to_next

        if not found_feasible_location:
            if len(crossover_solution.vehicles) < instance.amount_of_vehicles:
                best_vehicle = len(crossover_solution.vehicles)
                crossover_solution.vehicles.append(Vehicle.create_route(instance, parent_destination.node))
            else:
                sorted_with_index = sorted(crossover_solution.vehicles, key=lambda veh: instance.get_distance(veh.destinations[-2].node.number, parent_destination.node.number))
                for infeasible_vehicle in sorted_with_index:
                    if infeasible_vehicle.current_capacity + parent_destination.node.demand < instance.capacity_of_vehicles:
                        infeasible_vehicle.destinations.insert(infeasible_vehicle.get_num_of_customers_visited() + 1, copy.deepcopy(parent_destination))
                        break
        else:
            crossover_solution.vehicles[best_vehicle].destinations.insert(best_position, copy.deepcopy(parent_destination))

        crossover_solution.vehicles[best_vehicle].calculate_vehicle_load(instance)
        crossover_solution.vehicles[best_vehicle].calculate_destinations_time_windows(instance)
        crossover_solution.vehicles[best_vehicle].calculate_length_of_route(instance)

    crossover_solution.objective_function(instance)
    result[currentThread().getName()] = crossover_solution

def crossover(instance: ProblemInstance, parent_one: Union[OmbukiSolution, MMOEASASolution], parent_two: Union[OmbukiSolution, MMOEASASolution], use_original: bool) -> Union[OmbukiSolution, MMOEASASolution]:
    parent_one_vehicle = parent_one.vehicles[rand(0, len(parent_one.vehicles) - 1)]
    parent_two_vehicle = parent_two.vehicles[rand(0, len(parent_two.vehicles) - 1)]

    # threads cannot return values, so they need to be given a mutable type that can be given the values we'd like to return; in this instance, a list is used
    thread_results: Dict[str, Union[OmbukiSolution, MMOEASASolution]] = {"child_one": None, "child_two": None}
    child_one_thread = Thread(name="child_one", target=original_crossover_thread if use_original else modified_crossover_thread, args=(instance, parent_one, parent_two_vehicle, thread_results))
    child_two_thread = Thread(name="child_two", target=original_crossover_thread if use_original else modified_crossover_thread, args=(instance, parent_two, parent_one_vehicle, thread_results))
    child_one_thread.start()
    child_two_thread.start()
    child_one_thread.join()
    child_two_thread.join()

    thread_results["child_two"].id = thread_results["child_one"].id
    if instance.acceptance_criterion == "MMOEASA":
        return thread_results["child_one"] if mmoeasa_is_nondominated(thread_results["child_one"], thread_results["child_two"]) else thread_results["child_two"]
    return thread_results["child_one"] if is_nondominated(thread_results["child_one"], thread_results["child_two"]) else thread_results["child_two"]

def get_next_vehicles_destinations(solution: Union[OmbukiSolution, MMOEASASolution], vehicle: int, first_destination: int, remaining_destinations: int) -> List[Destination]:
    if not remaining_destinations:
        return list()
    num_customers = solution.vehicles[vehicle].get_num_of_customers_visited()
    if num_customers < first_destination + remaining_destinations:
        return solution.vehicles[vehicle].destinations[first_destination:num_customers + 1] + get_next_vehicles_destinations(solution, vehicle + 1, 1, remaining_destinations - ((num_customers + 1) - first_destination))
    else:
        return solution.vehicles[vehicle].destinations[first_destination:first_destination + remaining_destinations]

def set_next_vehicles_destinations(solution: Union[OmbukiSolution, MMOEASASolution], vehicle: int, first_destination: int, remaining_destinations: int, reversed_destinations: List[Destination]) -> None:
    if not (remaining_destinations and reversed_destinations):
        return
    num_customers = solution.vehicles[vehicle].get_num_of_customers_visited()
    if num_customers < first_destination + remaining_destinations:
        num_customers_inclusive = (num_customers + 1) - first_destination
        solution.vehicles[vehicle].destinations[first_destination:num_customers + 1] = reversed_destinations[:num_customers_inclusive]
        del reversed_destinations[:num_customers_inclusive]
        set_next_vehicles_destinations(solution, vehicle + 1, 1, remaining_destinations - num_customers_inclusive, reversed_destinations)
    else:
        solution.vehicles[vehicle].destinations[first_destination:first_destination + remaining_destinations] = reversed_destinations
        reversed_destinations.clear()

def mutation(instance: ProblemInstance, solution: Union[OmbukiSolution, MMOEASASolution]) -> Union[OmbukiSolution, MMOEASASolution]:
    num_nodes_to_swap = rand(2, MUTATION_REVERSAL_LENGTH)
    first_reversal_node = rand(1, (len(instance.nodes) - 1) - num_nodes_to_swap)

    vehicle_num = -1
    num_destinations_tracker = 0
    for i, vehicle in enumerate(solution.vehicles):
        if not num_destinations_tracker + vehicle.get_num_of_customers_visited() > first_reversal_node:
            num_destinations_tracker += vehicle.get_num_of_customers_visited()
        else:
            vehicle_num = i
            break

    first_destination = (first_reversal_node - num_destinations_tracker) + 1

    # the reason that the get and set functions are called recursively is because the mutation operator specified by Ombuki can swap customers across vehicles
    # therefore, the first call of the recursive functions can get/set the first one/two customers from one vehicle, then any remaining customers in the next vehcile
    reversed_destinations = get_next_vehicles_destinations(solution, vehicle_num, first_destination, num_nodes_to_swap)
    reversed_destinations = list(reversed(reversed_destinations))
    set_next_vehicles_destinations(solution, vehicle_num, first_destination, num_nodes_to_swap, reversed_destinations)

    solution.vehicles[vehicle_num].calculate_vehicle_load(instance)
    solution.vehicles[vehicle_num].calculate_destinations_time_windows(instance)
    solution.vehicles[vehicle_num].calculate_length_of_route(instance)
    solution.objective_function(instance)
    return solution
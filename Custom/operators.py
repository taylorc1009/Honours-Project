import copy
import time
from typing import Dict, Set
from Custom.customSolution import CustomSolution
from destination import Destination
from problemInstance import ProblemInstance
from common import rand, INT_MAX

class CrossoverPositionStats:
    def __init__(self):
        self.distance_from_previous = float(INT_MAX)
        self.distance_to_next = float(INT_MAX)

    def update_record(self, distance_from_previous: float, distance_to_next: float):
        self.distance_from_previous = float(distance_from_previous)
        self.distance_to_next = float(distance_to_next)

def crossover_evaluation(instance: ProblemInstance, crossover_solution: CustomSolution, nodes_to_insert: Set[int], results: Dict[int, CrossoverPositionStats], iteration: int) -> CustomSolution:
    if not iteration:
        return crossover_solution
    crossover_solution_copy = None

    for node in list(nodes_to_insert):
        shortest_from_previous, shortest_to_next = results[node].distance_from_previous, results[node].distance_to_next

        for v, vehicle in enumerate(crossover_solution.vehicles):
            if vehicle.current_capacity + node <= instance.capacity_of_vehicles:
                for d, destination in enumerate(vehicle.destinations[1:], 1):
                    distance_from_previous = instance.get_distance(vehicle.destinations[d - 1].node.number, node)
                    distance_to_next = instance.get_distance(node, destination.node.number)

                    simulated_arrival_time = vehicle.destinations[d - 1].departure_time + distance_from_previous
                    if not (simulated_arrival_time > instance.nodes[node].demand or simulated_arrival_time + distance_to_next > destination.node.due_date) \
                        and ((distance_from_previous < shortest_from_previous and distance_to_next <= shortest_to_next)
                        or (distance_from_previous <= shortest_from_previous and distance_to_next < shortest_to_next)):

                        crossover_solution_copy = copy.deepcopy(crossover_solution)
                        crossover_solution_copy.vehicles[v].destinations.insert(d, Destination(node=instance.nodes[node]))
                        for d_aux in range(d, crossover_solution_copy.vehicles[v].get_num_of_customers_visited() + 1):
                            crossover_solution_copy.vehicles[v].calculate_destination_time_window(instance, d_aux - 1, d_aux)
                        crossover_solution_copy.vehicles[v].current_capacity += instance.nodes[node].demand

                        crossover_solution_copy = crossover_evaluation(instance, crossover_solution_copy, nodes_to_insert.difference({node}), results, iteration - 1)
                        if crossover_solution_copy:
                            shortest_from_previous, shortest_to_next = distance_from_previous, shortest_to_next
                            results[node].update_record(distance_from_previous, distance_to_next)

    return crossover_solution_copy

def crossover(instance: ProblemInstance, parent_one: CustomSolution, parent_two: CustomSolution) -> CustomSolution:
    crossover_solution = copy.deepcopy(parent_one)
    parent_two_destinations = parent_two.vehicles[rand(0, len(parent_two.vehicles) - 1)].get_customers_visited()
    nodes_to_remove = set([d.node.number for d in parent_two_destinations])
    nodes_to_insert = copy.deepcopy(nodes_to_remove)

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

    results = {destination.node.number: CrossoverPositionStats() for destination in parent_two_destinations}
    """thread_pool = list()
    for i, destination in enumerate(parent_two_customers):
        thread_pool.append(Thread(name=str(destination.node.number), target=crossover_evaluation, args=(instance, copy.deepcopy(crossover_solution), parent_two_customers, i, results, len(parent_two_customers))))
        thread_pool[-1].start()
    for crossover_thread in thread_pool:
        crossover_thread.join()"""
    start = time.time()
    crossover_solution_copy = copy.deepcopy(crossover_solution)
    crossover_solution = crossover_evaluation(instance, crossover_solution_copy, nodes_to_insert, results, len(nodes_to_insert))
    copy_is = crossover_solution_copy is crossover_solution

    """results = sorted(results, key=lambda r: r.order)
    for result in results:
        crossover_solution.vehicles[result.vehicle].destinations.insert(result.position, Destination(node=instance.nodes[result.node_number]))"""

    print(f"{round(time.time() - start, 1)}s", copy_is)
    crossover_solution.calculate_length_of_routes(instance)
    crossover_solution.calculate_nodes_time_windows(instance)
    crossover_solution.calculate_vehicles_loads(instance)
    crossover_solution.objective_function(instance)

    return crossover_solution
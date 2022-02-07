import copy
import random
from typing import List
from problemInstance import ProblemInstance
from Ombuki.solution import Solution
from vehicle import Vehicle
from destination import Destination
from Ombuki.auxiliaries import rand
from numpy import arange, round
from Ombuki.constants import INT_MAX

def generate_random_solution(instance: ProblemInstance) -> Solution:
    solution = Solution(_id=0, vehicles=list())

    for i in arange(1, len(instance.nodes)):
        infeasible_vehicles = set()
        inserted = False
        while not inserted:
            vehicle = rand(0, instance.amount_of_vehicles - 1, exclude_values=infeasible_vehicles) # generate a random number between 1 and max vehicles instead of 1 to current num of vehicles; to keep the original probability of inserting the node to a new vehicle
            if vehicle < len(solution.vehicles) and solution.vehicles[vehicle].current_capacity + instance.nodes[i].demand <= instance.capacity_of_vehicles:
                solution.vehicles[vehicle].destinations.insert(len(solution.vehicles[vehicle].destinations) - 1, Destination(node=instance.nodes[i]))
                solution.vehicles[vehicle].current_capacity += instance.nodes[i].demand
                inserted = True
            elif len(infeasible_vehicles) == len(solution.vehicles):
                solution.vehicles.append(Vehicle.create_route(instance, node=instance.nodes[i]))
                solution.vehicles[-1].current_capacity = instance.nodes[i].demand
                inserted = True
            else:
                infeasible_vehicles.add(vehicle)

    return solution

def generate_greedy_solution(instance: ProblemInstance) -> Solution:
    solution = Solution(_id=0, vehicles=[Vehicle.create_route(instance)])
    unvisited_nodes = list(arange(1, len(instance.nodes)))
    vehicle = 0

    while unvisited_nodes:
        node = instance.nodes[random.sample(unvisited_nodes, 1)[0]]
        solution.vehicles[vehicle].destinations.insert(len(solution.vehicles[vehicle].destinations) - 1, Destination(node=node))
        unvisited_nodes.remove(node.number)

        while not solution.vehicles[vehicle].current_capacity > instance.capacity_of_vehicles:
            closest_node = None
            distance_of_closest = float(INT_MAX)
            for u_node in unvisited_nodes:
                distance = node.get_distance(instance.nodes[u_node])
                if distance < distance_of_closest:
                    closest_node = u_node
                    distance_of_closest = distance
            if closest_node and not solution.vehicles[vehicle].current_capacity + instance.nodes[closest_node].demand > instance.capacity_of_vehicles:
                solution.vehicles[vehicle].destinations.insert(len(solution.vehicles[vehicle].destinations) - 1, Destination(node=instance.nodes[closest_node]))
                solution.vehicles[vehicle].current_capacity += instance.nodes[closest_node].demand
                node = solution.vehicles[vehicle].destinations[-2].node
                unvisited_nodes.remove(closest_node)
            else:
                if closest_node:
                    vehicle += 1
                    solution.vehicles.append(Vehicle.create_route(instance))
                break

    return solution

def is_nondominated(old_solution: Solution, new_solution: Solution) -> bool:
    return (new_solution.total_distance < old_solution.total_distance and len(new_solution.vehicles) <= len(old_solution.vehicles)) or (new_solution.total_distance <= old_solution.total_distance and len(new_solution.vehicles) < len(old_solution.vehicles))

def pareto_rank(population: List[Solution], ) -> None:
    curr_rank = 1
    N = len(population)
    m = N
    unranked_solutions = set(arange(0, N))

    while N > 0:
        best_solution = None
        for i in unranked_solutions:
            if best_solution:
                if is_nondominated(population[i], best_solution):
                    population[i].rank = curr_rank
            else:
                best_solution = population[i]
        for i in arange(0, m):
            if is_nondominated(population[i], best_solution):
                population[i].rank = curr_rank
                unranked_solutions.remove(population[i].id)

def transform_to_feasible_network(instance: ProblemInstance, solution: Solution) -> Solution:
    feasible_solution = Solution(_id=solution.id, vehicles=[Vehicle.create_route(instance, solution.vehicles[0].destinations[1].node)])

    feasible_solution.vehicles[0].destinations[1].arrival_time = feasible_solution.vehicles[0].destinations[1].node.get_distance(feasible_solution.vehicles[0].destinations[0].node)
    if feasible_solution.vehicles[0].destinations[1].arrival_time < feasible_solution.vehicles[0].destinations[1].node.ready_time:
        feasible_solution.vehicles[0].destinations[1].wait_time = feasible_solution.vehicles[0].destinations[1].node.ready_time
        feasible_solution.vehicles[0].destinations[1].arrival_time = feasible_solution.vehicles[0].destinations[1].node.ready_time
    feasible_solution.vehicles[0].destinations[1].departure_time = feasible_solution.vehicles[0].destinations[1].arrival_time + feasible_solution.vehicles[0].destinations[1].node.service_duration

    f_vehicle = 0
    for vehicle in solution.vehicles:
        for destination in vehicle.get_customers_visited()[1 if vehicle is solution.vehicles[0] else 0:]:
            inserted = False

            while not inserted:
                if feasible_solution.vehicles[f_vehicle].current_capacity + destination.node.demand <= instance.capacity_of_vehicles and feasible_solution.vehicles[f_vehicle].destinations[-2].departure_time + feasible_solution.vehicles[f_vehicle].destinations[-2].node.get_distance(destination.node) <= destination.node.due_date:
                    feasible_solution.vehicles[f_vehicle].destinations.insert(len(feasible_solution.vehicles[f_vehicle].destinations) - 1, copy.deepcopy(destination))
                    inserted = True
                elif f_vehicle == instance.amount_of_vehicles - 1:
                    f_vehicle = 0
                else:
                    if len(feasible_solution.vehicles) < instance.amount_of_vehicles:
                        feasible_solution.vehicles.append(Vehicle.create_route(instance, destination.node))
                        inserted = True
                    f_vehicle += 1

            feasible_solution.vehicles[f_vehicle].destinations[-2].arrival_time = feasible_solution.vehicles[f_vehicle].destinations[-3].departure_time + feasible_solution.vehicles[f_vehicle].destinations[-3].node.get_distance(feasible_solution.vehicles[f_vehicle].destinations[-2].node)
            if feasible_solution.vehicles[f_vehicle].destinations[-2].arrival_time < feasible_solution.vehicles[f_vehicle].destinations[-2].node.ready_time:
                feasible_solution.vehicles[f_vehicle].destinations[-2].wait_time = feasible_solution.vehicles[f_vehicle].destinations[-2].node.ready_time - feasible_solution.vehicles[f_vehicle].destinations[-2].arrival_time
                feasible_solution.vehicles[f_vehicle].destinations[-2].arrival_time = feasible_solution.vehicles[f_vehicle].destinations[-2].node.ready_time
            else:
                feasible_solution.vehicles[f_vehicle].destinations[-2].wait_time = 0.0
            feasible_solution.vehicles[f_vehicle].destinations[-2].departure_time = feasible_solution.vehicles[f_vehicle].destinations[-2].arrival_time + destination.node.service_duration

    return feasible_solution

def relocate_final_destinations(instance: ProblemInstance, solution: Solution) -> Solution:
    f_solution = copy.deepcopy(solution)

    for i in arange(0, len(f_solution.vehicles)):
        f_solution.vehicles[i + 1 if i < len(f_solution.vehicles) - 1 else 0].destinations.insert(1, f_solution.vehicles[i].destinations[-2])
        del f_solution.vehicles[i].destinations[-2] # can't delete an empty route here as each iteration of the loop only moves one destination to the next route; it never leaves one route empty

    f_solution.calculate_vehicles_loads(instance)
    f_solution.calculate_length_of_routes(instance)
    f_solution.calculate_nodes_time_windows(instance)
    f_solution.objective_function(instance)

    return f_solution if f_solution.feasible and is_nondominated(solution, f_solution) else solution

def routing_scheme(instance: ProblemInstance, solution: Solution) -> Solution:
    feasible_solution = transform_to_feasible_network(instance, solution)
    feasible_solution = relocate_final_destinations(instance, feasible_solution)

    return feasible_solution

def Ombuki(instance: ProblemInstance, population_size: int, generation_span: int, crossover: float, mutation: float) -> List[Solution]:
    population: List[Solution] = list()
    #pareto_optimal: List[Solution] = list()

    num_greedy_solutions = round(float(population_size * 0.1))
    for i in arange(0, num_greedy_solutions).astype(int):
        greedy_solution = generate_greedy_solution(instance)
        greedy_solution.id = i
        population.insert(i, greedy_solution)
    for i in arange(num_greedy_solutions, population_size).astype(int):
        random_solution = generate_random_solution(instance)
        random_solution.id = i
        population.insert(i, random_solution)

    for _ in arange(0, generation_span):
        for i in arange(0, population_size):
            population[i] = routing_scheme(instance, population[i])
            pareto_rank(population)

    return population

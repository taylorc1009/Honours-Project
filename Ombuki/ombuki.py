import copy
import random
from typing import List, Tuple
from problemInstance import ProblemInstance
from Ombuki.solution import Solution
from vehicle import Vehicle
from destination import Destination
from Ombuki.auxiliaries import rand
from numpy import arange, round
from Ombuki.constants import INT_MAX, TOURNAMENT_SIZE, TOURNAMENT_PROBABILITY, GREEDY_PERCENT


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
    return (new_solution.total_distance < old_solution.total_distance and new_solution.num_vehicles <= old_solution.num_vehicles) or (new_solution.total_distance <= old_solution.total_distance and new_solution.num_vehicles < old_solution.num_vehicles)

def pareto_rank(population: List[Solution]) -> None:
    curr_rank = 1
    unranked_solutions = list(arange(0, len(population)))

    while unranked_solutions:
        best_solution = None

        for i in unranked_solutions:
            if best_solution:
                if is_nondominated(best_solution, population[i]):
                    best_solution = population[i]
                    population[i].rank = curr_rank
                    for j in [j for j, solution in enumerate(population) if solution.rank == curr_rank]:
                        population[j].rank = INT_MAX
                elif not is_nondominated(population[i], best_solution):
                    population[i].rank = curr_rank
            else:
                best_solution = population[i]
                population[i].rank = curr_rank

        for i in unranked_solutions:
            if population[i].rank == curr_rank:
                unranked_solutions.remove(population[i].id)
        curr_rank += 1

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

def relocate_final_destinations(instance: ProblemInstance, solution: Solution) -> Tuple[Solution, bool]:
    f_solution = copy.deepcopy(solution)

    for i in arange(0, len(f_solution.vehicles)):
        f_solution.vehicles[i + 1 if i < len(f_solution.vehicles) - 1 else 0].destinations.insert(1, f_solution.vehicles[i].destinations[-2])
        del f_solution.vehicles[i].destinations[-2] # can't delete an empty route here as each iteration of the loop only moves one destination to the next route; it never leaves one route empty

    f_solution.calculate_vehicles_loads(instance)
    f_solution.calculate_length_of_routes(instance)
    f_solution.calculate_nodes_time_windows(instance)
    f_solution.objective_function(instance)

    return (f_solution, True) if f_solution.feasible and is_nondominated(solution, f_solution) else (solution, False)

def routing_scheme(instance: ProblemInstance, solution: Solution) -> Solution:
    feasible_solution = transform_to_feasible_network(instance, solution)
    feasible_solution, relocated = relocate_final_destinations(instance, feasible_solution)

    if not relocated:
        solution.calculate_vehicles_loads(instance)
        solution.calculate_length_of_routes(instance)
        solution.calculate_nodes_time_windows(instance)
        solution.objective_function(instance)

    return feasible_solution

def selection_tournament(population: List[Solution]) -> int:
    rank_one_solutions = list(filter(lambda s: s.rank == 1, population))
    tournament_set = random.sample(rank_one_solutions, TOURNAMENT_SIZE)

    if rand(1, 100) < TOURNAMENT_PROBABILITY:
        best_solution = population[tournament_set[0].id]
        for solution in tournament_set:
            if is_nondominated(best_solution, population[solution.id]):
                best_solution = population[solution.id]
        return best_solution.id
    else:
        return tournament_set[rand(0, TOURNAMENT_SIZE - 1)].id

def crossover_probability(instance: ProblemInstance, solution: Solution, probability: int) -> Tuple[Solution, bool]:
    if rand(1, 100) < probability:
        solution_copy = copy.deepcopy(solution)

        return solution_copy, False
    return solution, True

def mutation_probability(instance: ProblemInstance, solution: Solution, probability: int, pending_copy: bool) -> Solution:
    if rand(1, 100) < probability:
        solution_copy = copy.deepcopy(solution) if pending_copy else solution

        return solution_copy
    return solution

def Ombuki(instance: ProblemInstance, population_size: int, generation_span: int, crossover: int, mutation: int) -> List[Solution]:
    population: List[Solution] = list()
    #pareto_optimal: List[Solution] = list()

    num_greedy_solutions = round(float(population_size * GREEDY_PERCENT))
    for i in arange(0, num_greedy_solutions).astype(int):
        greedy_solution = generate_greedy_solution(instance)
        greedy_solution.id = i
        greedy_solution.calculate_vehicles_loads(instance)
        greedy_solution.calculate_length_of_routes(instance)
        greedy_solution.calculate_nodes_time_windows(instance)
        greedy_solution.objective_function(instance)
        population.insert(i, greedy_solution)
    for i in arange(num_greedy_solutions, population_size).astype(int):
        random_solution = generate_random_solution(instance)
        random_solution.id = i
        random_solution.calculate_vehicles_loads(instance)
        random_solution.calculate_length_of_routes(instance)
        random_solution.calculate_nodes_time_windows(instance)
        random_solution.objective_function(instance)
        population.insert(i, random_solution)
    pareto_rank(population)

    for _ in arange(0, generation_span):
        winning_parent = selection_tournament(population)
        for i in arange(0, population_size):
            population[i] = routing_scheme(instance, population[i])
            pareto_rank(population)
            population[i], pending_copy = crossover_probability(instance, population[i], crossover)
            population[i] = mutation_probability(instance, population[i], mutation, pending_copy)

    return population

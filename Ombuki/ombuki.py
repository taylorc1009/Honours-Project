import copy
import random
from typing import List, Tuple
from problemInstance import ProblemInstance
from Ombuki.solution import Solution
from vehicle import Vehicle
from destination import Destination
from Ombuki.auxiliaries import rand
from numpy import arange, round, random
from Ombuki.constants import INT_MAX, TOURNAMENT_SIZE, TOURNAMENT_PROBABILITY, GREEDY_PERCENT


def generate_random_solution(instance: ProblemInstance) -> Solution:
    solution = Solution(_id=0, vehicles=list())

    for i in range(1, len(instance.nodes)):
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
        node = instance.nodes[random.choice(unvisited_nodes)]
        solution.vehicles[vehicle].destinations.insert(len(solution.vehicles[vehicle].destinations) - 1, Destination(node=node))
        solution.vehicles[vehicle].current_capacity = node.demand
        unvisited_nodes.remove(node.number)

        while not solution.vehicles[vehicle].current_capacity > instance.capacity_of_vehicles:
            closest_node = None
            distance_of_closest = float(INT_MAX)
            for u_node in unvisited_nodes:
                distance = instance.get_distance(node.number, u_node)
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
                    solution.vehicles.append(Vehicle.create_route(instance))
                    vehicle += 1
                break

    return solution

def is_nondominated(old_solution: Solution, new_solution: Solution) -> bool:
    return (new_solution.total_distance < old_solution.total_distance and new_solution.num_vehicles <= old_solution.num_vehicles) or (new_solution.total_distance <= old_solution.total_distance and new_solution.num_vehicles < old_solution.num_vehicles)

def is_nondominated_by_any(population: List[Solution], subject_solution: int) -> bool:
    for i, solution in enumerate(population):
        if not i == subject_solution and not is_nondominated(solution, population[subject_solution]):
            return False
    return True

def pareto_rank(population: List[Solution]) -> None:
    curr_rank = 1
    unranked_solutions = list(arange(0, len(population)))

    while unranked_solutions:
        for i in unranked_solutions:
            if is_nondominated_by_any(population, i):
                population[i].rank = curr_rank
                unranked_solutions.remove(population[i].id)
        curr_rank += 1

def attempt_feasible_network_transformation(instance: ProblemInstance, solution: Solution) -> Solution:
    feasible_solution = Solution(_id=solution.id, vehicles=[Vehicle.create_route(instance, solution.vehicles[0].destinations[1].node)])
    feasible_solution.vehicles[0].current_capacity += solution.vehicles[0].destinations[1].node.demand
    feasible_solution.vehicles[0].calculate_destination_time_window(instance, 0, 1)
    """feasible_solution.vehicles[0].destinations[1].arrival_time = instance.get_distance(0, feasible_solution.vehicles[0].destinations[1].node.number)
    if feasible_solution.vehicles[0].destinations[1].arrival_time < feasible_solution.vehicles[0].destinations[1].node.ready_time:
        feasible_solution.vehicles[0].destinations[1].wait_time = feasible_solution.vehicles[0].destinations[1].node.ready_time
        feasible_solution.vehicles[0].destinations[1].arrival_time = feasible_solution.vehicles[0].destinations[1].node.ready_time
    feasible_solution.vehicles[0].destinations[1].departure_time = feasible_solution.vehicles[0].destinations[1].arrival_time + feasible_solution.vehicles[0].destinations[1].node.service_duration"""

    f_vehicle = 0
    for vehicle in solution.vehicles:
        for destination in vehicle.get_customers_visited()[1 if vehicle is solution.vehicles[0] else 0:]:
            feasible_insertion = False
            vehicle_reset = False
            first_attempted_vehicle = f_vehicle

            while not feasible_insertion:
                if feasible_solution.vehicles[f_vehicle].current_capacity + destination.node.demand <= instance.capacity_of_vehicles and feasible_solution.vehicles[f_vehicle].destinations[-2].departure_time + instance.get_distance(feasible_solution.vehicles[f_vehicle].destinations[-2].node.number, destination.node.number) <= destination.node.due_date:
                    feasible_solution.vehicles[f_vehicle].destinations.insert(len(feasible_solution.vehicles[f_vehicle].destinations) - 1, copy.deepcopy(destination))
                    feasible_insertion = True
                elif f_vehicle == instance.amount_of_vehicles - 1:
                    if not vehicle_reset:
                        f_vehicle = 0
                        vehicle_reset = True
                    else: # at this point, no feasible vehicle insertion was found, so select the vehicle with the nearest final destination where capacity constraints are not violated; therefore, this solution is now infeasible
                        sorted_by_last_destination = sorted(feasible_solution.vehicles, key=lambda v: instance.get_distance(v.destinations[-2].node.number, destination.node.number))
                        for i, infeasible_vehicle in enumerate(sorted_by_last_destination):
                            if not infeasible_vehicle.current_capacity + destination.node.demand > instance.capacity_of_vehicles:
                                sorted_by_last_destination[i].destinations.insert(len(feasible_solution.vehicles[f_vehicle].destinations) - 1, copy.deepcopy(destination))
                                break
                        break
                        """nearest_destination = solution.vehicles[0].destinations[-2].node.number
                        for infeasible_vehicle in solution.vehicles[1:]:
                            if instance.get_distance(infeasible_vehicle.destinations[-2].node.number, destination.node.number) < instance.get_distance(nearest_destination.):"""
                else:
                    if len(feasible_solution.vehicles) < instance.amount_of_vehicles:
                        feasible_solution.vehicles.append(Vehicle.create_route(instance, destination.node))
                        feasible_insertion = True
                    f_vehicle += 1

            feasible_solution.vehicles[f_vehicle].current_capacity += destination.node.demand
            feasible_solution.vehicles[f_vehicle].calculate_destination_time_window(instance, -3, -2)
            """feasible_solution.vehicles[f_vehicle].destinations[-2].arrival_time = feasible_solution.vehicles[f_vehicle].destinations[-3].departure_time + instance.get_distance(feasible_solution.vehicles[f_vehicle].destinations[-3].node.number, feasible_solution.vehicles[f_vehicle].destinations[-2].node.number)
            if feasible_solution.vehicles[f_vehicle].destinations[-2].arrival_time < feasible_solution.vehicles[f_vehicle].destinations[-2].node.ready_time:
                feasible_solution.vehicles[f_vehicle].destinations[-2].wait_time = feasible_solution.vehicles[f_vehicle].destinations[-2].node.ready_time - feasible_solution.vehicles[f_vehicle].destinations[-2].arrival_time
                feasible_solution.vehicles[f_vehicle].destinations[-2].arrival_time = feasible_solution.vehicles[f_vehicle].destinations[-2].node.ready_time
            else:
                feasible_solution.vehicles[f_vehicle].destinations[-2].wait_time = 0.0
            feasible_solution.vehicles[f_vehicle].destinations[-2].departure_time = feasible_solution.vehicles[f_vehicle].destinations[-2].arrival_time + destination.node.service_duration"""

            if not feasible_insertion:
                f_vehicle = first_attempted_vehicle

    return feasible_solution

def relocate_final_destinations(instance: ProblemInstance, solution: Solution) -> Tuple[Solution, bool]:
    f_solution = copy.deepcopy(solution)

    for i in range(0, len(f_solution.vehicles)):
        f_solution.vehicles[i + 1 if i < len(f_solution.vehicles) - 1 else 0].destinations.insert(1, f_solution.vehicles[i].destinations[-2])
        del f_solution.vehicles[i].destinations[-2] # can't delete an empty route here as each iteration of the loop only moves one destination to the next route; it never leaves one route empty

    f_solution.calculate_vehicles_loads(instance)
    f_solution.calculate_length_of_routes(instance)
    f_solution.calculate_nodes_time_windows(instance)
    f_solution.objective_function(instance)

    return (f_solution, True) if f_solution.feasible and is_nondominated(solution, f_solution) else (solution, False)

def routing_scheme(instance: ProblemInstance, solution: Solution) -> Solution:
    feasible_solution = attempt_feasible_network_transformation(instance, solution)
    feasible_solution, relocated = relocate_final_destinations(instance, feasible_solution)

    if not relocated:
        feasible_solution.calculate_vehicles_loads(instance)
        feasible_solution.calculate_length_of_routes(instance)
        feasible_solution.calculate_nodes_time_windows(instance)
        feasible_solution.objective_function(instance)

    return feasible_solution

def selection_tournament(population: List[Solution]) -> int:
    rank_one_solutions = list(filter(lambda s: s.rank == 1, population))
    tournament_set = random.choice(rank_one_solutions, TOURNAMENT_SIZE) if rank_one_solutions else random.choice(population, TOURNAMENT_SIZE)

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

    num_greedy_solutions = int(round(float(population_size * GREEDY_PERCENT)))
    for i in range(0, num_greedy_solutions):
        greedy_solution = generate_greedy_solution(instance)
        greedy_solution.id = i
        greedy_solution.calculate_vehicles_loads(instance)
        greedy_solution.calculate_length_of_routes(instance)
        greedy_solution.calculate_nodes_time_windows(instance)
        greedy_solution.objective_function(instance)
        population.insert(i, greedy_solution)
    for i in range(num_greedy_solutions, population_size):
        random_solution = generate_random_solution(instance)
        random_solution.id = i
        random_solution.calculate_vehicles_loads(instance)
        random_solution.calculate_length_of_routes(instance)
        random_solution.calculate_nodes_time_windows(instance)
        random_solution.objective_function(instance)
        population.insert(i, random_solution)
    #pareto_rank(population)

    for _ in range(0, generation_span):
        winning_parent = selection_tournament(population)
        for i in range(0, population_size):
            population[i] = routing_scheme(instance, population[i])
            pareto_rank(population)
            population[i], pending_copy = crossover_probability(instance, population[i], crossover)
            population[i] = mutation_probability(instance, population[i], mutation, pending_copy)

    return population

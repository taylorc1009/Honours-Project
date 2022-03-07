import copy
import time
from typing import List, Union, Dict, Tuple
from Ombuki.operators import crossover, mutation
from MMOEASA.mmoeasaSolution import MMOEASASolution
from problemInstance import ProblemInstance
from Ombuki.ombukiSolution import OmbukiSolution
from vehicle import Vehicle
from destination import Destination
from Ombuki.auxiliaries import rand, is_nondominated, is_nondominated_by_any, mmoeasa_is_nondominated, mmoeasa_is_nondominated_by_any
from numpy import arange, round, random
from Ombuki.constants import TOURNAMENT_SET_SIZE, TOURNAMENT_PROBABILITY_SELECT_BEST, GREEDY_PERCENT
from common import INT_MAX, check_iterations_termination_condition, check_seconds_termination_condition
from MMOEASA.mmoeasa import mo_metropolis

initialiser_execution_time: int=0
feasible_initialisations: int=0
crossover_invocations: int=0
crossover_successes: int=0
mutation_invocations: int=0
mutation_successes: int=0

def generate_random_solution(instance: ProblemInstance) -> Union[OmbukiSolution, MMOEASASolution]:
    solution = OmbukiSolution(_id=0, vehicles=list()) if instance.acceptance_criterion == "Ombuki" else MMOEASASolution(_id=0, vehicles=list())

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

def generate_greedy_solution(instance: ProblemInstance) -> Union[OmbukiSolution, MMOEASASolution]:
    solution = OmbukiSolution(_id=0, vehicles=[Vehicle.create_route(instance)]) if instance.acceptance_criterion == "Ombuki" else MMOEASASolution(_id=0, vehicles=[Vehicle.create_route(instance)])
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

def pareto_rank(instance: ProblemInstance, population: List[Union[OmbukiSolution, MMOEASASolution]]) -> int:
    curr_rank = 1
    unranked_solutions = list(range(0, len(population)))
    num_rank_ones = 0

    while unranked_solutions:
        could_assign_rank = False
        for i in unranked_solutions:
            if instance.acceptance_criterion == "MMOEASA":
                if mmoeasa_is_nondominated_by_any(population, i):
                    population[i].rank = curr_rank
                    if curr_rank == 1:
                        num_rank_ones += 1
                    unranked_solutions.remove(population[i].id)
                    could_assign_rank = True
            elif is_nondominated_by_any(population, i):
                population[i].rank = curr_rank
                if curr_rank == 1:
                    num_rank_ones += 1
                unranked_solutions.remove(population[i].id)
                could_assign_rank = True
        if not could_assign_rank:
            for i in unranked_solutions:
                population[i].rank = curr_rank
            if curr_rank == 1:
                num_rank_ones += len(unranked_solutions)
            break
        curr_rank += 1

    return num_rank_ones

def attempt_feasible_network_transformation(instance: ProblemInstance, solution: Union[OmbukiSolution, MMOEASASolution]) -> Union[OmbukiSolution, MMOEASASolution]:
    vehicles = [Vehicle.create_route(instance, solution.vehicles[0].destinations[1].node)]
    feasible_solution = OmbukiSolution(_id=solution.id, vehicles=vehicles) if instance.acceptance_criterion == "Ombuki" else MMOEASASolution(_id=solution.id, vehicles=vehicles)
    feasible_solution.vehicles[0].current_capacity += solution.vehicles[0].destinations[1].node.demand
    feasible_solution.vehicles[0].calculate_destination_time_window(instance, 0, 1)

    f_vehicle = 0
    for vehicle in solution.vehicles:
        for destination in vehicle.get_customers_visited()[1 if vehicle is solution.vehicles[0] else 0:]:
            if feasible_solution.vehicles[f_vehicle].current_capacity + destination.node.demand <= instance.capacity_of_vehicles and feasible_solution.vehicles[f_vehicle].destinations[-2].departure_time + instance.get_distance(feasible_solution.vehicles[f_vehicle].destinations[-2].node.number, destination.node.number) <= destination.node.due_date:
                feasible_solution.vehicles[f_vehicle].destinations.insert(len(feasible_solution.vehicles[f_vehicle].destinations) - 1, copy.deepcopy(destination))
            else:
                feasible_solution.vehicles.append(Vehicle.create_route(instance, destination.node))
                f_vehicle += 1

            feasible_solution.vehicles[f_vehicle].current_capacity += destination.node.demand
            feasible_solution.vehicles[f_vehicle].calculate_destination_time_window(instance, -3, -2)

    return feasible_solution

def relocate_final_destinations(instance: ProblemInstance, solution: Union[OmbukiSolution, MMOEASASolution]) -> Union[OmbukiSolution, MMOEASASolution]:
    f_solution = copy.deepcopy(solution)

    for i in range(0, len(f_solution.vehicles)):
        f_solution.vehicles[i + 1 if i < len(f_solution.vehicles) - 1 else 0].destinations.insert(1, f_solution.vehicles[i].destinations[-2])
        del f_solution.vehicles[i].destinations[-2] # can't delete an empty route here as each iteration of the loop only moves one destination to the next route; it never leaves one route empty

    f_solution.calculate_vehicles_loads(instance)
    f_solution.calculate_length_of_routes(instance)
    f_solution.calculate_nodes_time_windows(instance)
    f_solution.objective_function(instance)

    if instance.acceptance_criterion == "MMOEASA":
        return f_solution if mmoeasa_is_nondominated(solution, f_solution) else solution
    return f_solution if is_nondominated(solution, f_solution) else solution

def routing_scheme(instance: ProblemInstance, solution: Union[OmbukiSolution, MMOEASASolution]) -> Union[OmbukiSolution, MMOEASASolution]:
    feasible_solution = attempt_feasible_network_transformation(instance, solution)
    relocated_solution = relocate_final_destinations(instance, feasible_solution)

    if relocated_solution is feasible_solution:
        feasible_solution.calculate_vehicles_loads(instance)
        feasible_solution.calculate_length_of_routes(instance)
        feasible_solution.calculate_nodes_time_windows(instance)
        feasible_solution.objective_function(instance)

    return relocated_solution

def selection_tournament(instance: ProblemInstance, population: List[Union[OmbukiSolution, MMOEASASolution]]) -> int:
    best_solutions = list(filter(lambda s: s.rank == 1, population))
    if not best_solutions: # in this instance, the initialising population has been given and no solutions have been ranked yet, so work with any feasible solutions
        best_solutions = list(filter(lambda s: s.feasible, population))

    if best_solutions:
        tournament_set = random.choice(best_solutions, TOURNAMENT_SET_SIZE)
    else:
        tournament_set = random.choice(population, TOURNAMENT_SET_SIZE)

    if rand(1, 100) < TOURNAMENT_PROBABILITY_SELECT_BEST:
        best_solution = population[tournament_set[0].id]
        for solution in tournament_set:
            if instance.acceptance_criterion == "MMOEASA":
                if mmoeasa_is_nondominated(best_solution, population[solution.id]):
                    best_solution = population[solution.id]
            elif is_nondominated(best_solution, population[solution.id]):
                best_solution = population[solution.id]
        return best_solution.id
    else:
        return tournament_set[rand(0, TOURNAMENT_SET_SIZE - 1)].id

def crossover_probability(instance: ProblemInstance, iterator_parent: Union[OmbukiSolution, MMOEASASolution], tournament_parent: Union[OmbukiSolution, MMOEASASolution], probability: int) -> Union[OmbukiSolution, MMOEASASolution]:
    if rand(1, 100) < probability:
        global crossover_invocations, crossover_successes
        crossover_invocations += 1

        crossover_solution = crossover(instance, iterator_parent, tournament_parent)

        if instance.acceptance_criterion == "MMOEASA":
            if mmoeasa_is_nondominated(iterator_parent, crossover_solution):
                crossover_successes += 1
        elif is_nondominated(iterator_parent, crossover_solution):
            crossover_successes += 1
        return crossover_solution
    return iterator_parent

def mutation_probability(instance: ProblemInstance, solution: Union[OmbukiSolution, MMOEASASolution], probability: int, pending_copy: bool) -> Union[OmbukiSolution, MMOEASASolution]:
    if rand(1, 100) < probability:
        global mutation_invocations, mutation_successes
        mutation_invocations += 1

        mutated_solution = mutation(instance, copy.deepcopy(solution) if pending_copy else solution)

        if instance.acceptance_criterion == "MMOEASA":
            if mmoeasa_is_nondominated(solution, mutated_solution):
                mutation_successes += 1
                return mutated_solution
        elif is_nondominated(solution, mutated_solution):
            mutation_successes += 1
            return mutated_solution
    return solution

def Ombuki(instance: ProblemInstance, population_size: int, termination_condition: int, termination_type: str, crossover: int, mutation: int) -> Tuple[List[Union[OmbukiSolution, MMOEASASolution]], Dict[str, int]]:
    population: List[Union[OmbukiSolution, MMOEASASolution]] = list()

    global initialiser_execution_time, feasible_initialisations
    initialiser_execution_time = time.time()
    num_greedy_solutions = int(round(float(population_size * GREEDY_PERCENT)))
    for i in range(0, num_greedy_solutions):
        greedy_solution = generate_greedy_solution(instance)
        greedy_solution.id = i
        greedy_solution.calculate_vehicles_loads(instance)
        greedy_solution.calculate_length_of_routes(instance)
        greedy_solution.calculate_nodes_time_windows(instance)
        greedy_solution.objective_function(instance)
        if greedy_solution.feasible:
            feasible_initialisations += 1
        population.insert(i, greedy_solution)
    for i in range(num_greedy_solutions, population_size):
        random_solution = generate_random_solution(instance)
        random_solution.id = i
        random_solution.calculate_vehicles_loads(instance)
        random_solution.calculate_length_of_routes(instance)
        random_solution.calculate_nodes_time_windows(instance)
        random_solution.objective_function(instance)
        if random_solution.feasible:
            feasible_initialisations += 1
        population.insert(i, random_solution)
    initialiser_execution_time = round((time.time() - initialiser_execution_time) * 1000, 3)

    start = time.time()
    terminate = False
    iterations = 0
    while not terminate:
        winning_parent = selection_tournament(instance, population)
        for i, solution in enumerate(population):
            if not population[i].feasible:
                population[i] = routing_scheme(instance, solution)

            result = crossover_probability(instance, solution, population[winning_parent], crossover)
            result = mutation_probability(instance, result, mutation, result is solution)

            if not population[i].feasible:
                population[i] = result
            elif result.feasible:
                if instance.acceptance_criterion == "MMOEASA":
                    population[i], _ = mo_metropolis(instance, solution, result, 100.0)
                elif is_nondominated(population[i], result):
                    population[i] = result
        num_rank_ones = pareto_rank(instance, population)
        iterations += 1

        if termination_type == "iterations":
            terminate = check_iterations_termination_condition(iterations, termination_condition, num_rank_ones)
        elif termination_type == "seconds":
            terminate = check_seconds_termination_condition(start, termination_condition, num_rank_ones)

    # because MMOEASA only returns a non-dominated set with a size equal to the population size, and Ombuki doesn't have a non-dominated set with a restricted size, the algorithm needs to select (unbiasly) a fixed amount of rank 1 solutions for a fair evaluation
    nondominated_set = list()
    for solution in population:
        if solution.rank == 1 and solution.feasible:
            nondominated_set.append(solution)
            if len(nondominated_set) == 20:
                break

    global crossover_invocations, crossover_successes, mutation_invocations, mutation_successes
    statistics = {
        "initialiser_execution_time": f"{initialiser_execution_time} milliseconds",
        "feasible_initialisations": feasible_initialisations,
        "crossover_invocations": crossover_invocations,
        "crossover_successes": crossover_successes,
        "mutation_invocations": mutation_invocations,
        "mutation_successes": mutation_successes
    }

    return nondominated_set, statistics

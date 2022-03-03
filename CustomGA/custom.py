import copy
import time
import random
from typing import List, Dict, Tuple
from common import rand, check_iterations_termination_condition, check_seconds_termination_condition, INT_MAX
from random import shuffle
from destination import Destination
from problemInstance import ProblemInstance
from CustomGA.customGASolution import CustomGASolution
from CustomGA.operators import crossover, TWBS_mutation, TWBSw_mutation, WTBS_mutation, SWTBS_mutation, DBS_mutation, SDBS_mutation, TWBMF_mutation, TWBPB_mutation
from CustomGA.constants import TOURNAMENT_SET_SIZE, TOURNAMENT_PROBABILITY_SELECT_BEST
from vehicle import Vehicle
from numpy import ceil, random

initialiser_execution_time: int=0
feasible_initialisations: int=0
crossover_invocations: int=0
crossover_successes: int=0
mutation_invocations: int=0
mutation_successes: int=0

def DTWIH(instance: ProblemInstance) -> CustomGASolution:
    sorted_nodes = sorted([node for _, node in instance.nodes.items() if node.number], key=lambda n: n.ready_time)
    num_routes = int(ceil(instance.amount_of_vehicles / 2))
    solution = CustomGASolution(_id=0, vehicles=[Vehicle.create_route(instance) for _ in range(0, num_routes)])
    additional_vehicles = 0

    while sorted_nodes:
        range_of_sorted_nodes = num_routes if num_routes < len(sorted_nodes) else len(sorted_nodes)
        nodes_to_insert = sorted_nodes[:range_of_sorted_nodes]
        shuffle(nodes_to_insert)
        for i in range(range_of_sorted_nodes):
            index = i
            if solution.vehicles[index].current_capacity + nodes_to_insert[i].demand <= instance.capacity_of_vehicles:
                solution.vehicles[index].destinations.insert(len(solution.vehicles[index].destinations) - 1, Destination(node=nodes_to_insert[i]))
            else:
                # TODO: try picking the best location in an existing vehicle?
                index = (num_routes - 1) + additional_vehicles
                if solution.vehicles[index].current_capacity + nodes_to_insert[i].demand > instance.capacity_of_vehicles:
                    solution.vehicles.append(Vehicle.create_route(instance, nodes_to_insert[i]))
                    additional_vehicles += 1
                    index += 1
                else:
                    solution.vehicles[index].destinations.insert(len(solution.vehicles[index].destinations) - 1, Destination(node=nodes_to_insert[i]))
            solution.vehicles[index].current_capacity += nodes_to_insert[i].demand
        del sorted_nodes[:range_of_sorted_nodes]

    solution.calculate_nodes_time_windows(instance)
    solution.calculate_length_of_routes(instance)
    solution.objective_function(instance)

    return solution

def is_nondominated(old_solution: CustomGASolution, new_solution: CustomGASolution) -> bool:
    return (new_solution.total_distance < old_solution.total_distance and new_solution.num_vehicles <= old_solution.num_vehicles) or (new_solution.total_distance <= old_solution.total_distance and new_solution.num_vehicles < old_solution.num_vehicles)

def is_nondominated_by_any(population: List[CustomGASolution], subject_solution: int) -> bool:
    for s, solution in enumerate(population):
        if s != subject_solution and not is_nondominated(solution, population[subject_solution]):
            return False
    return True

def pareto_rank(population: List[CustomGASolution]) -> int:
    curr_rank = 1
    unranked_solutions = list(range(len(population)))
    num_rank_ones = 0

    while unranked_solutions:
        could_assign_rank = False
        for i in unranked_solutions:
            if is_nondominated_by_any(population, i):
                population[i].rank = curr_rank
                if curr_rank == 1:
                    num_rank_ones += 1
                unranked_solutions.remove(population[i].id)
                could_assign_rank = True
        if not could_assign_rank:
            for i in unranked_solutions:
                population[i].rank = INT_MAX
            break
        curr_rank += 1

    return num_rank_ones

def selection_tournament(population: List[CustomGASolution]) -> int:
    best_solutions = list(filter(lambda s: s.rank == 1, population))
    if not best_solutions:  # in this instance, the initialising population has been given and no solutions have been ranked yet, so work with any feasible solutions
        best_solutions = list(filter(lambda s: s.feasible, population))

    if best_solutions:
        tournament_set = random.choice(best_solutions, TOURNAMENT_SET_SIZE)
    else:
        tournament_set = random.choice(population, TOURNAMENT_SET_SIZE)

    if rand(1, 100) < TOURNAMENT_PROBABILITY_SELECT_BEST:
        best_solution = population[tournament_set[0].id]
        for solution in tournament_set:
            if is_nondominated(best_solution, population[solution.id]):
                best_solution = population[solution.id]
        return best_solution.id
    else:
        return tournament_set[rand(0, TOURNAMENT_SET_SIZE - 1)].id

def try_crossover(instance, parent_one: CustomGASolution, parent_two: CustomGASolution, crossover_probability) -> CustomGASolution:
    if rand(1, 100) < crossover_probability:
        global crossover_invocations, crossover_successes
        crossover_invocations += 1

        crossover_solution = crossover(instance, parent_one, parent_two.vehicles[rand(0, len(parent_two.vehicles) - 1)])

        if is_nondominated(parent_one, crossover_solution):
            crossover_successes += 1
        return crossover_solution
    return parent_one

def try_mutation(instance, solution: CustomGASolution, mutation_probability: int) -> CustomGASolution:
    if rand(1, 100) < mutation_probability:
        global mutation_invocations, mutation_successes
        mutation_invocations += 1

        mutated_solution = copy.deepcopy(solution)
        probability = rand(1, 8)

        if probability == 1:
            mutated_solution = TWBS_mutation(instance, mutated_solution) # Time-Window-based Sort Mutator
        elif probability == 2:
            mutated_solution = TWBSw_mutation(instance, mutated_solution) # Time-Window-based Swap Mutator
        elif probability == 3:
            mutated_solution = WTBS_mutation(instance, mutated_solution) # Wait-Time-based Swap Mutator
        elif probability == 4:
            mutated_solution = SWTBS_mutation(instance, mutated_solution) # Single Wait-Time-based Swap Mutator
        elif probability == 5:
            mutated_solution = DBS_mutation(instance, mutated_solution) # Distance-based Swap Mutator
        elif probability == 6:
            mutated_solution = SDBS_mutation(instance, mutated_solution) # Single Distance-based Swap Mutator
        elif probability == 7:
            mutated_solution = TWBMF_mutation(instance, mutated_solution) # Time-Window-based Move Forward Mutator
        elif probability == 8:
            mutated_solution = TWBPB_mutation(instance, mutated_solution) # Time-Window-based Push-back Mutator

        if is_nondominated(solution, mutated_solution):
            mutation_successes += 1
            return mutated_solution
        else:
            return solution
    return solution

def CustomGA(instance: ProblemInstance, population_size: int, termination_condition: int, termination_type: str, crossover_probability: int, mutation_probability: int) -> Tuple[List[CustomGASolution], Dict[str, int]]:
    population: List[CustomGASolution] = list()

    global initialiser_execution_time, feasible_initialisations
    initialiser_execution_time = time.time()
    for i in range(0, population_size):
        population.insert(i, DTWIH(instance))
        population[i].id = i
        if population[i].feasible:
            feasible_initialisations += 1
    initialiser_execution_time = round((time.time() - initialiser_execution_time) * 1000, 3)

    start = time.time()
    terminate = False
    iterations = 0
    while not terminate:
        crossover_parent_two = selection_tournament(population)
        for s, solution in enumerate(population):
            child = try_crossover(instance, solution, population[crossover_parent_two], crossover_probability)
            child = try_mutation(instance, child, mutation_probability)

            dominates_parent = is_nondominated(solution, child)
            if not solution.feasible or dominates_parent:
                population[s] = child
        num_rank_ones = pareto_rank(population)
        iterations += 1

        if termination_type == "iterations":
            terminate = check_iterations_termination_condition(iterations, termination_condition, num_rank_ones)
        elif termination_type == "seconds":
            terminate = check_seconds_termination_condition(start, termination_condition, num_rank_ones)

    # because MMOEASA only returns a non-dominated set with a size equal to the population size, and Ombuki doesn't have a non-dominated set with a restricted size, the algorithm needs to select (unbiasly) a fixed amount of rank 1 solutions for a fair evaluation
    nondominated_set = list()
    for solution in population:
        if solution.rank == 1:
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

import copy
import time
import random
from typing import List, Dict, Tuple
from common import rand
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

    for offset in range(0, num_routes):
        range_of_sorted_nodes = num_routes if num_routes < len(sorted_nodes) else len(sorted_nodes)
        for i in range(0, range_of_sorted_nodes):
            if solution.vehicles[i].current_capacity + sorted_nodes[i].demand <= instance.capacity_of_vehicles:
                solution.vehicles[i].destinations.insert(offset + 1, Destination(node=sorted_nodes[i]))
                solution.vehicles[i].current_capacity += sorted_nodes[i].demand
            else:
                # TODO: try picking the best location in an existing vehicle?
                index = (num_routes - 1) + additional_vehicles
                if solution.vehicles[index].current_capacity + sorted_nodes[i].demand > instance.capacity_of_vehicles:
                    solution.vehicles.append(Vehicle.create_route(instance, sorted_nodes[i]))
                    additional_vehicles += 1
                else:
                    solution.vehicles[index].destinations.insert(len(solution.vehicles[index].destinations), Destination(node=sorted_nodes[i]))
        del sorted_nodes[:num_routes]

    solution.calculate_nodes_time_windows(instance)
    solution.calculate_length_of_routes(instance)
    solution.objective_function(instance)

    return solution

def is_nondominated(old_solution: CustomGASolution, new_solution: CustomGASolution) -> bool:
    return (new_solution.total_distance < old_solution.total_distance and new_solution.num_vehicles <= old_solution.num_vehicles) or (new_solution.total_distance <= old_solution.total_distance and new_solution.num_vehicles < old_solution.num_vehicles)

def is_nondominated_by_any(population: List[CustomGASolution], subject_solution: int) -> bool:
    for s, solution in enumerate(population):
        if s != subject_solution and not is_nondominated(population[subject_solution], solution):
            return False
    return True

def pareto_rank(population: List[CustomGASolution]) -> None:
    curr_rank = 1
    unranked_solutions = list(range(0, len(population)))

    while unranked_solutions:
        could_assign_rank = False
        for i in unranked_solutions:
            if is_nondominated_by_any(population, i):
                population[i].rank = curr_rank
                unranked_solutions.remove(population[i].id)
                could_assign_rank = True
        if not could_assign_rank:
            for i in unranked_solutions:
                population[i].rank = curr_rank
            break
        curr_rank += 1

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

def CustomGA(instance: ProblemInstance, population_size: int, termination_condition: int, crossover_probability: int, mutation_probability: int) -> Tuple[List[CustomGASolution], Dict[str, int]]:
    population: List[CustomGASolution] = list()

    global initialiser_execution_time, feasible_initialisations
    initialiser_execution_time = time.time()
    DTWIH_solution = DTWIH(instance)
    if DTWIH_solution.feasible:
        feasible_initialisations += 1
    for i in range(0, population_size):
        population.insert(i, copy.deepcopy(DTWIH_solution))
        population[i].id = i
    del DTWIH_solution
    initialiser_execution_time = round(time.time() - initialiser_execution_time, 2)

    start = time.time()
    for i in range(termination_condition):
        crossover_parent_two = selection_tournament(population)
        for s, solution in enumerate(population):
            child = try_crossover(instance, solution, population[crossover_parent_two], crossover_probability)
            child = try_mutation(instance, child, mutation_probability)

            dominates_parent = is_nondominated(population[s], child)
            if not solution.feasible or dominates_parent:
                population[s] = child
                if dominates_parent:
                    print(f"solution {s} dominated")
        pareto_rank(population)
        if not i % (termination_condition / 10):
            print(f"iterations={i}, time={round(time.time() - start, 1)}s")

    # because MMOEASA only returns a non-dominated set with a size equal to the population size, and Ombuki doesn't have a non-dominated set with a restricted size, the algorithm needs to select (unbiasly) a fixed amount of rank 1 solutions for a fair evaluation
    nondominated_set = list()
    for solution in population:
        if solution.rank == 1:
            nondominated_set.append(solution)
            if len(nondominated_set) == 20:
                break

    global crossover_invocations, crossover_successes, mutation_invocations, mutation_successes
    statistics = {
        "initialiser_execution_time": f"{initialiser_execution_time}s",
        "feasible_initialisations": feasible_initialisations,
        "crossover_invocations": crossover_invocations,
        "crossover_successes": crossover_successes,
        "mutation_invocations": mutation_invocations,
        "mutation_successes": mutation_successes
    }

    return nondominated_set, statistics

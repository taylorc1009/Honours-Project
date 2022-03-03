import copy
import time
from MMOEASA.auxiliaries import is_nondominated, is_nondominated_by_any, ombuki_is_nondominated_by_any
from MMOEASA.operators import mutation1, mutation2, mutation3, mutation4, mutation5, mutation6, mutation7, mutation8, mutation9, mutation10, crossover1
from MMOEASA.constants import MAX_SIMULTANEOUS_MUTATIONS
from Ombuki.auxiliaries import is_nondominated as ombuki_is_nondominated
from MMOEASA.mmoeasaSolution import MMOEASASolution
from Ombuki.ombukiSolution import OmbukiSolution
from problemInstance import ProblemInstance
from destination import Destination
from vehicle import Vehicle
from common import INT_MAX, rand, check_iterations_termination_condition, check_seconds_termination_condition
from typing import List, Tuple, Union, Dict
from numpy import sqrt, exp

initialiser_execution_time: int=0
feasible_initialisations: int=0
crossover_invocations: int=0
crossover_successes: int=0
mutation_invocations: int=0
mutation_successes: int=0

def TWIH(instance: ProblemInstance) -> Union[MMOEASASolution, OmbukiSolution]:
    sorted_nodes = sorted([value for _, value in instance.nodes.items()], key=lambda x: x.ready_time)

    solution = MMOEASASolution(_id=0, vehicles=list()) if instance.acceptance_criterion == "MMOEASA" else OmbukiSolution(_id=0, vehicles=list())
    s = 0 # list of destinations iterator

    for _ in range(0, instance.amount_of_vehicles - 1):
        if s >= len(instance.nodes) - 1:
            break
        if sorted_nodes[s].number == 0:
            s += 1

        vehicle = Vehicle.create_route(instance)

        while s < len(instance.nodes) and vehicle.current_capacity + sorted_nodes[s].demand < instance.capacity_of_vehicles:
            vehicle.destinations.insert(len(vehicle.destinations) - 1, Destination(node=sorted_nodes[s]))
            vehicle.current_capacity += float(sorted_nodes[s].demand)
            s += 1

        solution.vehicles.append(vehicle)

    solution.calculate_nodes_time_windows(instance)
    solution.calculate_vehicles_loads(instance)
    solution.calculate_length_of_routes(instance)
    solution.objective_function(instance)

    return solution

def calculate_cooling(i: int, temperature_max: float, temperature_min: float, temperature_stop: float, population_size: int, termination_condition: int) -> float:
    jump_temperatures = (temperature_max - temperature_min) / float(population_size - 1) if population_size > 1 else 0.0
    temperature_aux = temperature_max - float(i) * jump_temperatures
    error = float(INT_MAX)
    max_error = 0.005 * float(termination_condition)
    cooling_rate = 0.995
    auxiliary_iterations = 0.0

    while abs(error) > max_error and not auxiliary_iterations > termination_condition: # the original MMOEASA "Calculate_cooling" doesn't have the second condition, but mine (without it) gets an infinite loop (use the "print"s below to see)
        #print(abs(error), maxError, cooling_rate, auxiliary_iterations)
        temperature = temperature_aux
        auxiliary_iterations = 0.0

        while temperature > temperature_stop:
            temperature *= cooling_rate
            auxiliary_iterations += 1.0

        #print(termination_condition, auxiliary_iterations)
        error = float(termination_condition) - auxiliary_iterations
        cooling_rate = cooling_rate + (0.05 / float(termination_condition)) if error > 0.0 else cooling_rate - (0.05 / float(termination_condition))

    return cooling_rate

def crossover(instance: ProblemInstance, I: Union[MMOEASASolution, OmbukiSolution], population: List[Union[MMOEASASolution, OmbukiSolution]], P_crossover: int) -> Union[MMOEASASolution, OmbukiSolution]:
    if rand(1, 100) <= P_crossover:
        global crossover_invocations
        crossover_invocations += 1

        return crossover1(instance, copy.deepcopy(I), population)
    return I

def mutation(instance: ProblemInstance, I: Union[MMOEASASolution, OmbukiSolution], P_mutation: int, pending_copy: bool) -> Tuple[Union[MMOEASASolution, OmbukiSolution], bool]:
    if rand(1, 100) <= P_mutation:
        global mutation_invocations
        mutation_invocations += 1

        solution_copy = copy.deepcopy(I) if pending_copy else I
        probability = rand(1, 100)

        if 1 <= probability <= 10:
            return mutation1(instance, solution_copy), True
        elif 11 <= probability <= 20:
            return mutation2(instance, solution_copy), True
        elif 21 <= probability <= 30:
            return mutation3(instance, solution_copy), True
        elif 31 <= probability <= 40:
            return mutation4(instance, solution_copy), True
        elif 41 <= probability <= 50:
            return mutation5(instance, solution_copy), True
        elif 51 <= probability <= 60:
            return mutation6(instance, solution_copy), True
        elif 61 <= probability <= 70:
            return mutation7(instance, solution_copy), True
        elif 71 <= probability <= 80:
            return mutation8(instance, solution_copy), True
        elif 81 <= probability <= 90:
            return mutation9(instance, solution_copy), True
        elif 91 <= probability <= 100:
            return mutation10(instance, solution_copy), True
    return I, False

def euclidean_distance_dispersion(instance: ProblemInstance, x1: float, y1: float, x2: float, y2: float) -> float:
    return sqrt(((x2 - x1) / 2 * instance.Hypervolume_total_distance) ** 2 + ((y2 - y1) / 2 * instance.Hypervolume_cargo_unbalance) ** 2)

def mo_metropolis(instance: ProblemInstance, parent: MMOEASASolution, child: MMOEASASolution, temperature: float) -> Tuple[MMOEASASolution, bool]:
    if is_nondominated(parent, child):
        return child, True
    elif temperature <= 0.00001:
        return parent, False
    else:
        d_df = euclidean_distance_dispersion(instance, child.total_distance, child.cargo_unbalance, parent.total_distance, parent.cargo_unbalance)
        random_val = rand(0, INT_MAX) / INT_MAX
        d_pt_pt = d_df / temperature ** 2
        pt_exp = exp(-1.0 * d_pt_pt)

        if random_val < pt_exp:
            return child, not (child.cargo_unbalance == parent.cargo_unbalance and child.total_distance == parent.total_distance)
        else:
            return parent, False

def MMOEASA(instance: ProblemInstance, population_size: int, multi_starts: int, termination_condition: int, termination_type: str, crossover_probability: int, mutation_probability: int, temperature_max: float, temperature_min: float, temperature_stop: float) -> Tuple[List[Union[OmbukiSolution, MMOEASASolution]], Dict[str, int]]:
    population: List[Union[MMOEASASolution, OmbukiSolution]] = list()
    nondominated_set: List[Union[MMOEASASolution, OmbukiSolution]] = list()

    global initialiser_execution_time, feasible_initialisations, crossover_successes, mutation_successes
    initialiser_execution_time = time.time()
    TWIH_solution = TWIH(instance)
    if TWIH_solution.feasible:
        feasible_initialisations += 1
    for i in range(population_size):
        population.insert(i, copy.deepcopy(TWIH_solution))
        population[i].id = i
        if instance.acceptance_criterion == "MMOEASA":
            population[i].default_temperature = temperature_max - float(i) * ((temperature_max - temperature_min) / float(population_size - 1))
            population[i].cooling_rate = calculate_cooling(i, temperature_max, temperature_min, temperature_stop, population_size, termination_condition)
    del TWIH_solution
    initialiser_execution_time = round((time.time() - initialiser_execution_time) * 1000, 3)

    start = time.time()
    terminate = False
    iterations = 0
    #current_multi_start = 0
    while not terminate:#current_multi_start < MS:
        if instance.acceptance_criterion == "MMOEASA":
            for s in range(len(population)):
                population[s].temperature = population[s].default_temperature

        while (instance.acceptance_criterion == "MMOEASA" and population[0].temperature > temperature_stop and not terminate) or not terminate:
            for s, solution in enumerate(population):
                #selection_tournament = rand(1, population_size * (2 if len(nondominated_set) > 1 else 1))
                solution_copy = crossover(instance, solution, population, crossover_probability)#population if selection_tournament <= population_size else nondominated_set, P_crossover)
                crossover_occurred = solution_copy is not solution
                mutations = 0
                for _ in range(0, rand(1, MAX_SIMULTANEOUS_MUTATIONS)):
                    solution_copy, mutation_occurred = mutation(instance, solution_copy, mutation_probability, solution_copy is solution)
                    if mutation_occurred:
                        mutations += 1

                child_dominated, dominated_any = False, False
                if instance.acceptance_criterion == "Ombuki":
                    child_dominated = ombuki_is_nondominated(solution, solution_copy)
                    if child_dominated or not population[s].feasible:
                        if crossover_occurred:
                            crossover_successes += 1
                        if mutations > 0:
                            mutation_successes += mutations
                        population[s] = solution_copy
                        dominated_any = ombuki_is_nondominated_by_any(nondominated_set, population[s])
                else:
                    population[s], child_dominated = mo_metropolis(instance, solution, solution_copy, solution.temperature)
                    if child_dominated:
                        if crossover_occurred:
                            crossover_successes += 1
                        if mutations > 0:
                            mutation_successes += mutations
                        dominated_any = is_nondominated_by_any(nondominated_set, population[s])

                if dominated_any or (child_dominated and len(nondominated_set) < population_size):
                    nondominated_set.append(copy.deepcopy(population[s]))
                    """should_write = False # use the debugger to edit the value in "should_write" if you'd like a solution to be written to a CSV
                    if should_write:
                        MMOEASA_write_solution_for_validation(population[s], instance.capacity_of_vehicles)"""

                if instance.acceptance_criterion == "MMOEASA":
                    population[s].temperature *= population[s].cooling_rate
            iterations += 1

            if termination_type == "iterations":
                terminate = check_iterations_termination_condition(iterations, termination_condition * multi_starts, len(nondominated_set))
            elif termination_type == "seconds":
                terminate = check_seconds_termination_condition(start, termination_condition, len(nondominated_set))

    global crossover_invocations, mutation_invocations
    statistics = {
        "initialiser_execution_time": f"{initialiser_execution_time} milliseconds",
        "feasible_initialisations": feasible_initialisations,
        "crossover_invocations": crossover_invocations,
        "crossover_successes": crossover_successes,
        "mutation_invocations": mutation_invocations,
        "mutation_successes": mutation_successes
    }

    return nondominated_set, statistics

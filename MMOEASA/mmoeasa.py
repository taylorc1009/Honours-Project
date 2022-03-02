import copy
import time
from MMOEASA.auxiliaries import is_nondominated, is_nondominated_by_any, ombuki_is_nondominated_by_any
from MMOEASA.operators import Mutation1, Mutation2, Mutation3, Mutation4, Mutation5, Mutation6, Mutation7, Mutation8, Mutation9, Mutation10, Crossover1
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
    D_i = 0 # list of destinations iterator

    for _ in range(0, instance.amount_of_vehicles - 1):
        if D_i >= len(instance.nodes) - 1:
            break
        if sorted_nodes[D_i].number == 0:
            D_i += 1

        vehicle = Vehicle.create_route(instance)

        while D_i < len(instance.nodes) and vehicle.current_capacity + sorted_nodes[D_i].demand < instance.capacity_of_vehicles:
            vehicle.destinations.insert(len(vehicle.destinations) - 1, Destination(node=sorted_nodes[D_i]))
            vehicle.current_capacity += float(sorted_nodes[D_i].demand)
            D_i += 1

        solution.vehicles.append(vehicle)

    return solution

def TWIH_initialiser(instance: ProblemInstance) -> Union[MMOEASASolution, OmbukiSolution]:
    solution = TWIH(instance)

    solution.calculate_nodes_time_windows(instance)
    solution.calculate_vehicles_loads(instance)
    solution.calculate_length_of_routes(instance)
    solution.objective_function(instance)

    return solution

def Calculate_cooling(i: int, T_max: float, T_min: float, T_stop: float, p: int, TC: int) -> float:
    jump_temperatures = (T_max - T_min) / float(p - 1) if p > 1 else 0.0
    T_2 = T_max - float(i) * jump_temperatures
    error = float(INT_MAX)
    maxError = 0.005 * float(TC)
    T_cooling = 0.995
    auxiliary_iterations = 0.0

    while abs(error) > maxError and not auxiliary_iterations > TC: # TODO: the original MMOEASA "Calculate_cooling" doesn't have the second condition, but mine (without it) gets an infinite loop (use the "print"s below to see)
        #print(abs(error), maxError, T_cooling, auxiliary_iterations)
        T_1 = T_2
        auxiliary_iterations = 0.0

        while T_1 > T_stop:
            T_1 *= T_cooling
            auxiliary_iterations += 1.0

        #print(TC, auxiliary_iterations)
        error = float(TC) - auxiliary_iterations
        T_cooling = T_cooling + (0.05 / float(TC)) if error > 0.0 else T_cooling - (0.05 / float(TC))

    return T_cooling

def Crossover(instance: ProblemInstance, I: Union[MMOEASASolution, OmbukiSolution], P: List[Union[MMOEASASolution, OmbukiSolution]], P_crossover: int) -> Union[MMOEASASolution, OmbukiSolution]:
    if rand(1, 100) <= P_crossover:
        global crossover_invocations
        crossover_invocations += 1

        return Crossover1(instance, copy.deepcopy(I), P)
    return I

def Mutation(instance: ProblemInstance, I: Union[MMOEASASolution, OmbukiSolution], P_mutation: int, pending_copy: bool) -> Tuple[Union[MMOEASASolution, OmbukiSolution], bool]:
    if rand(1, 100) <= P_mutation:
        global mutation_invocations
        mutation_invocations += 1

        I_c = copy.deepcopy(I) if pending_copy else I
        probability = rand(1, 100)

        if 1 <= probability <= 10:
            return Mutation1(instance, I_c), True
        elif 11 <= probability <= 20:
            return Mutation2(instance, I_c), True
        elif 21 <= probability <= 30:
            return Mutation3(instance, I_c), True
        elif 31 <= probability <= 40:
            return Mutation4(instance, I_c), True
        elif 41 <= probability <= 50:
            return Mutation5(instance, I_c), True
        elif 51 <= probability <= 60:
            return Mutation6(instance, I_c), True
        elif 61 <= probability <= 70:
            return Mutation7(instance, I_c), True
        elif 71 <= probability <= 80:
            return Mutation8(instance, I_c), True
        elif 81 <= probability <= 90:
            return Mutation9(instance, I_c), True
        elif 91 <= probability <= 100:
            return Mutation10(instance, I_c), True
    return I, False

def Euclidean_distance_dispersion(instance: ProblemInstance, x1: float, y1: float, x2: float, y2: float) -> float:
    return sqrt(((x2 - x1) / 2 * instance.Hypervolume_total_distance) ** 2 + ((y2 - y1) / 2 * instance.Hypervolume_cargo_unbalance) ** 2)

def MO_Metropolis(instance: ProblemInstance, Parent: MMOEASASolution, Child: MMOEASASolution, T: float) -> Tuple[MMOEASASolution, bool]:  # TODO: change back to " -> MMOEASASolution" return type once debugging of MO_Metropolis has finished
    if is_nondominated(Parent, Child):
        return Child, True
    elif T <= 0.00001:
        return Parent, False
    else:
        d_df = Euclidean_distance_dispersion(instance, Child.total_distance, Child.cargo_unbalance, Parent.total_distance, Parent.cargo_unbalance)
        random_val = rand(0, INT_MAX) / INT_MAX
        d_pt_pt = d_df / T ** 2
        pt_exp = exp(-1.0 * d_pt_pt)

        if random_val < pt_exp:
            return Child, not (Child.cargo_unbalance == Parent.cargo_unbalance and Child.total_distance == Parent.total_distance)
        else:
            return Parent, False

def MMOEASA(instance: ProblemInstance, p: int, MS: int, TC: int, TC_type: str, P_crossover: int, P_mutation: int, T_max: float, T_min: float, T_stop: float) -> Tuple[List[Union[OmbukiSolution, MMOEASASolution]], Dict[str, int]]:
    P: List[Union[MMOEASASolution, OmbukiSolution]] = list()
    ND: List[Union[MMOEASASolution, OmbukiSolution]] = list()

    global initialiser_execution_time, feasible_initialisations, crossover_successes, mutation_successes
    initialiser_execution_time = time.time()
    TWIH_solution = TWIH_initialiser(instance)
    if TWIH_solution.feasible:
        feasible_initialisations += 1
    for i in range(p):
        P.insert(i, copy.deepcopy(TWIH_solution))
        P[i].id = i
        if instance.acceptance_criterion == "MMOEASA":
            P[i].T_default = T_max - float(i) * ((T_max - T_min) / float(p - 1))
            P[i].T_cooling = Calculate_cooling(i, T_max, T_min, T_stop, p, TC)
    del TWIH_solution
    initialiser_execution_time = round((time.time() - initialiser_execution_time) * 1000, 3)

    start = time.time()
    terminate = False
    iterations = 0
    #current_multi_start = 0
    while not terminate:#current_multi_start < MS:
        if instance.acceptance_criterion == "MMOEASA":
            for i in range(len(P)):
                P[i].T = P[i].T_default

        while (instance.acceptance_criterion == "MMOEASA" and P[0].T > T_stop and not terminate) or not terminate:
            for i, I in enumerate(P):
                #selection_tournament = rand(1, p * (2 if len(ND) > 1 else 1))
                I_c = Crossover(instance, I, P, P_crossover)#P if selection_tournament <= p else ND, P_crossover)
                crossover_occurred = I_c is not I
                mutations = 0
                for _ in range(0, rand(1, MAX_SIMULTANEOUS_MUTATIONS)):
                    I_c, mutation_occurred = Mutation(instance, I_c, P_mutation, I_c is I)
                    if mutation_occurred:
                        mutations += 1

                child_dominated, dominated_any = False, False
                if instance.acceptance_criterion == "Ombuki":
                    child_dominated = ombuki_is_nondominated(I, I_c)
                    if child_dominated or not P[i].feasible:
                        if crossover_occurred:
                            crossover_successes += 1
                        if mutations > 0:
                            mutation_successes += mutations
                        P[i] = I_c
                        dominated_any = ombuki_is_nondominated_by_any(ND, P[i])
                else:
                    P[i], child_dominated = MO_Metropolis(instance, I, I_c, I.T)
                    if child_dominated:
                        if crossover_occurred:
                            crossover_successes += 1
                        if mutations > 0:
                            mutation_successes += mutations
                        dominated_any = is_nondominated_by_any(ND, P[i])

                if dominated_any or (child_dominated and len(ND) < p):
                    ND.append(copy.deepcopy(P[i]))
                    print(f"{len(ND)=}, {iterations=}, time={round(time.time() - start, 1)}s")

                    """should_write = False # use the debugger to edit the value in "should_write" if you'd like a solution to be written to a CSV
                    if should_write:
                        MMOEASA_write_solution_for_validation(P[i], instance.capacity_of_vehicles)"""

                if instance.acceptance_criterion == "MMOEASA":
                    P[i].T *= P[i].T_cooling
            iterations += 1
            """if not iterations % (TC / 10):
                if instance.acceptance_criterion == "MMOEASA":
                    print(f"{iterations=}, {P[0].T=}, time={round(time.time() - start, 1)}s")
                else:
                    print(f"{iterations=}, time={round(time.time() - start, 1)}s")"""

            if TC_type == "iterations":
                terminate = check_iterations_termination_condition(iterations, TC)
            elif TC_type == "seconds":
                terminate = check_seconds_termination_condition(start, TC)

        ##if instance.acceptance_criterion == "MMOEASA":
        #current_multi_start += 1
        #iterations = 0
        ##if iterations < TC:
        print("multi-start occurred")

    global crossover_invocations, mutation_invocations
    statistics = {
        "initialiser_execution_time": f"{initialiser_execution_time} milliseconds",
        "feasible_initialisations": feasible_initialisations,
        "crossover_invocations": crossover_invocations,
        "crossover_successes": crossover_successes,
        "mutation_invocations": mutation_invocations,
        "mutation_successes": mutation_successes
    }

    return ND, statistics

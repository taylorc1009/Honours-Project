import copy
import time
from MMOEASA.auxiliaries import rand
from MMOEASA.operators import Mutation1, Mutation2, Mutation3, Mutation4, Mutation5, Mutation6, Mutation7, Mutation8, Mutation9, Mutation10, Crossover1
from MMOEASA.constants import INT_MAX, MMOEASA_MAX_SIMULTANEOUS_MUTATIONS, MMOEASA_INFINITY
from MMOEASA.solution import Solution
from problemInstance import ProblemInstance
from destination import Destination
from vehicle import Vehicle
from typing import List, Tuple
from numpy import sqrt, exp
from data import write_solution_for_validation

Hypervolume_total_distance: float=0.0
Hypervolume_distance_unbalance: float=0.0 # currently, the distance unbalance objective is unused in the objective function, but this may change
Hypervolume_cargo_unbalance: float=0.0

def update_Hypervolumes(HV_TD: float, HV_DU: float, HV_CU: float) -> None:
    global Hypervolume_total_distance, Hypervolume_distance_unbalance, Hypervolume_cargo_unbalance
    Hypervolume_total_distance = float(HV_TD)
    Hypervolume_distance_unbalance = float(HV_DU)
    Hypervolume_cargo_unbalance = float(HV_CU)

    print(f"Hypervolumes modified: TD={Hypervolume_total_distance}, DU={Hypervolume_distance_unbalance}, CU={Hypervolume_cargo_unbalance}")

def TWIH(instance: ProblemInstance) -> Solution:
    sorted_nodes = sorted([value for _, value in instance.nodes.items()], key=lambda x: x.ready_time)

    solution = Solution(_id=0, vehicles=list())
    D_i = 0 # list of destinations iterator

    for i in range(0, instance.amount_of_vehicles - 1):
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

def TWIH_initialiser(instance: ProblemInstance) -> Solution:
    solution = TWIH(instance)

    solution.calculate_nodes_time_windows(instance)
    solution.calculate_vehicles_loads(instance)
    solution.calculate_length_of_routes(instance)
    solution.objective_function(instance)

    return solution

def TWIH_ref_point(instance: ProblemInstance) -> Tuple[float, float, float]:
    solution = TWIH(instance)
    minimum_distance, maximum_distance, minimum_cargo, maximum_cargo = MMOEASA_INFINITY, 0, MMOEASA_INFINITY, 0

    solution.calculate_length_of_routes(instance)

    solution.total_distance = sum([vehicle.route_distance for vehicle in solution.vehicles])

    for vehicle in solution.vehicles:
        if vehicle.route_distance < minimum_distance:
            minimum_distance = vehicle.route_distance
        if vehicle.route_distance > maximum_distance:
            maximum_distance = vehicle.route_distance
        if vehicle.current_capacity < minimum_cargo:
            minimum_cargo = vehicle.current_capacity
        if vehicle.current_capacity > maximum_cargo:
            maximum_cargo = vehicle.current_capacity
    solution.distance_unbalance = maximum_distance - minimum_distance
    solution.cargo_unbalance = maximum_cargo - minimum_cargo

    return solution.total_distance * 2, solution.distance_unbalance * 2, solution.cargo_unbalance * 2

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

def Crossover(instance: ProblemInstance, I: Solution, P: List[Solution], P_crossover: int) -> Tuple[Solution, bool]:
    if rand(1, 100) <= P_crossover:
        I_c = Crossover1(instance, copy.deepcopy(I), P)
        return I_c, False
    return I, True

def Mutation(instance: ProblemInstance, I: Solution, P_mutation: int, pending_copy: bool) -> Tuple[Solution, bool]:
    if rand(1, 100) <= P_mutation:
        I_c = copy.deepcopy(I) if pending_copy else I
        probability = rand(1, 100)

        if 1 <= probability <= 10:
            I_c = Mutation1(instance, I_c)
        elif 11 <= probability <= 20:
            I_c = Mutation2(instance, I_c)
        elif 21 <= probability <= 30:
            I_c = Mutation3(instance, I_c)
        elif 31 <= probability <= 40:
            I_c = Mutation4(instance, I_c)
        elif 41 <= probability <= 50:
            I_c = Mutation5(instance, I_c)
        elif 51 <= probability <= 60:
            I_c = Mutation6(instance, I_c)
        elif 61 <= probability <= 70:
            I_c = Mutation7(instance, I_c)
        elif 71 <= probability <= 80:
            I_c = Mutation8(instance, I_c)
        elif 81 <= probability <= 90:
            I_c = Mutation9(instance, I_c)
        elif 91 <= probability <= 100:
            I_c = Mutation10(instance, I_c)

        return I_c, False
    return I, pending_copy

def Euclidean_distance_dispersion(x1: float, y1: float, x2: float, y2: float) -> float:
    global Hypervolume_total_distance, Hypervolume_cargo_unbalance
    return sqrt(((x2 - x1) / 2 * Hypervolume_total_distance) ** 2 + ((y2 - y1) / 2 * Hypervolume_cargo_unbalance) ** 2)

def Child_dominates(Parent: Solution, Child: Solution) -> bool:
    return (Child.total_distance < Parent.total_distance and Child.cargo_unbalance <= Parent.cargo_unbalance) or (Child.total_distance <= Parent.total_distance and Child.cargo_unbalance < Parent.cargo_unbalance)

def MO_Metropolis(Parent: Solution, Child: Solution, T: float) -> Tuple[Solution, bool]:  # TODO: change back to " -> Solution" return type once debugging of MO_Metropolis has finished
    if Child_dominates(Parent, Child):
        return Child, True
    elif T <= 0.00001:
        return Parent, False
    else:
        d_df = Euclidean_distance_dispersion(Child.total_distance, Child.cargo_unbalance, Parent.total_distance, Parent.cargo_unbalance)
        random_val = rand(0, INT_MAX - 1) / INT_MAX
        d_pt_pt = d_df / T ** 2
        pt_exp = exp(-1 * d_pt_pt)

        if random_val < pt_exp:
            return Child, not (Child.cargo_unbalance == Parent.cargo_unbalance and Child.total_distance == Parent.total_distance)
        else:
            return Parent, False

def is_nondominated(I: Solution, ND: List[Solution]) -> bool:
    if ND:
        nondominated = ND[-1] # the only non-dominated solution we need to check is the solution at the end of the non-dominated set; the last non-dominated solution will dominate every preceding solution
        return (I.total_distance < nondominated.total_distance and I.cargo_unbalance <= nondominated.cargo_unbalance) or (I.total_distance <= nondominated.total_distance and I.cargo_unbalance < nondominated.cargo_unbalance)
    else:
        return I.feasible

def MMOEASA(instance: ProblemInstance, p: int, MS: int, TC: int, P_crossover: int, P_mutation: int, T_max: float, T_min: float, T_stop: float, Hypervolumes: List[float]) -> List[Solution]:
    P: List[Solution] = list()
    ND: List[Solution] = list()
    iterations = 0
    update_Hypervolumes(*Hypervolumes)

    prev_ND_id = 0

    TWIH_solution = TWIH_initialiser(instance)
    for i in range(p):
        P.insert(i, copy.deepcopy(TWIH_solution))
        P[i].id = i
        P[i].T_default = T_max - float(i) * ((T_max - T_min) / float(p - 1))
        P[i].T_cooling = Calculate_cooling(i, T_max, T_min, T_stop, p, TC)
    del TWIH_solution

    start = time.time()
    current_multi_start = 0
    while current_multi_start < MS and not iterations >= TC:
        for i, _ in enumerate(P):
            P[i].T = P[i].T_default

        while P[0].T > T_stop and not iterations >= TC:
            for i, I in enumerate(P):
                I_c, pending_copy = Crossover(instance, I, P, P_crossover)
                for _ in range(0, rand(1, MMOEASA_MAX_SIMULTANEOUS_MUTATIONS)):
                    I_c, pending_copy = Mutation(instance, I_c, P_mutation, pending_copy)
                P[i], parent_changed = MO_Metropolis(I, I_c, I.T)

                if is_nondominated(P[i], ND): # this should be something like "if P[i] is unique and not dominated by all elements in the Non-Dominated set, then add it to ND and sort ND"
                    if len(ND) >= p:
                        ND.pop(0)
                    ND.append(copy.deepcopy(P[i]))
                    print(f"{len(ND)=}, ND={i}, {iterations=}, time={round(time.time() - start, 1)}s")
                    prev_ND_id = i

                    should_write = False
                    if should_write: # use the debugger to edit the value in "should_write" if you'd like a solution to be written to a CSV
                        write_solution_for_validation(P[i], instance.capacity_of_vehicles)
                elif parent_changed and i == prev_ND_id:
                    print(f"ND solution ({prev_ND_id}) changed in P ({iterations=}, time={round(time.time() - start, 1)}s)")

                P[i].T *= P[i].T_cooling
            iterations += 1
            if not iterations % (TC / 10):
                print(f"{iterations=}, {P[0].T=}, time={round(time.time() - start, 1)}s")

        current_multi_start += 1
        if iterations < TC:
            print("multi-start occurred")
    return ND
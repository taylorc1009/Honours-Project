import copy
from MMOEASA.auxiliaries import rand
from MMOEASA.operators import Mutation1, Mutation2, Mutation3, Mutation4, Mutation5, Mutation6, Mutation7, Mutation8, Mutation9, Mutation10, Crossover1
from MMOEASA.constants import INT_MAX, MMOEASA_MAX_SIMULTANEOUS_MUTATIONS
from MMOEASA.solution import Solution
from problemInstance import ProblemInstance
from destination import Destination
from vehicle import Vehicle
from typing import List
from numpy import sqrt, exp

Hypervolume_total_distance: float=0.0
Hypervolume_distance_unbalance: float=0.0
Hypervolume_cargo_unbalance: float=0.0

def update_Hypervolumes(potentialHV_TD: float=0.0, potentialHV_DU: float=0.0, potentialHV_CU: float=0.0) -> None:
    global Hypervolume_total_distance, Hypervolume_distance_unbalance, Hypervolume_cargo_unbalance
    if float(potentialHV_TD) > Hypervolume_total_distance:
        Hypervolume_total_distance = float(potentialHV_TD)
    if float(potentialHV_DU) > Hypervolume_distance_unbalance:
        Hypervolume_distance_unbalance = float(potentialHV_DU)
    if float(potentialHV_CU) > Hypervolume_cargo_unbalance:
        Hypervolume_cargo_unbalance = float(potentialHV_CU)

def TWIH(instance: ProblemInstance) -> Solution:
    sorted_nodes = sorted([value for _, value in instance.nodes.items()], key=lambda x: x.ready_time)

    solution = Solution(_id=0, vehicles=list())
    D_i = 1 # list of destinations iterator

    for i in range(0, instance.amount_of_vehicles - 1):
        if D_i >= len(instance.nodes) - 1:
            break
        if sorted_nodes[D_i].number == 0:
            continue

        vehicle = Vehicle(i, destinations=list())
        vehicle.destinations.append(Destination(node=sorted_nodes[0])) # have the route start at the depot

        while D_i < len(instance.nodes) and vehicle.current_capacity + sorted_nodes[D_i].demand < instance.capacity_of_vehicles:
            vehicle.destinations.append(Destination(node=sorted_nodes[D_i]))
            vehicle.current_capacity += sorted_nodes[D_i].demand
            D_i += 1
        
        vehicle.destinations.append(Destination(node=sorted_nodes[0])) # have the route end at the depot
        solution.vehicles.append(vehicle)

    solution.calculate_nodes_time_windows(instance)
    solution.calculate_vehicles_loads(instance)
    solution.calculate_length_of_routes(instance)
    potentialHV_TD, potentialHV_CU = solution.objective_function(instance)

    update_Hypervolumes(potentialHV_TD=potentialHV_TD, potentialHV_CU=potentialHV_CU)

    return solution

def Calculate_cooling(i: int, T_max: float, T_min: float, T_stop: float, p: int, TC: int) -> float:
    jump_temperatures = (T_max - T_min)/(float(p) - 1.0) if p > 1 else 0.0
    T_2 = T_max - (float(i) * jump_temperatures)
    error = float(INT_MAX)
    maxError = 0.005 * float(TC)
    T_cooling = 0.995
    auxiliary_iterations = 0.0

    while abs(error) > maxError and not auxiliary_iterations > TC: # the original MMOEASA "Calculate_cooling" doesn't have the second condition, but mines (without it) gets an infinite loop (use the "print"s below to see)
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

def Crossover(instance: ProblemInstance, I: Solution, P: List[Solution], P_crossover: int) -> Solution:
    if rand(1, 100) <= P_crossover:
        I_c, potentialHV_TD, potentialHV_CU = Crossover1(instance, I, P)
        update_Hypervolumes(potentialHV_TD=potentialHV_TD, potentialHV_CU=potentialHV_CU)
        return I_c
    return I

def Mutation(instance: ProblemInstance, I: Solution, P_mutation: int, probability: int) -> Solution:
    if rand(1, 100) <= P_mutation:
        I_m = I
        potentialHV_TD, potentialHV_CU = 0.0, 0.0

        if 1 <= probability <= 10:
            I_m, potentialHV_TD, potentialHV_CU = Mutation1(instance, I)
        elif 11 <= probability <= 20:
            I_m, potentialHV_TD, potentialHV_CU = Mutation2(instance, I)
        elif 21 <= probability <= 30:
            I_m, potentialHV_TD, potentialHV_CU = Mutation3(instance, I)
        elif 31 <= probability <= 40:
            I_m, potentialHV_TD, potentialHV_CU = Mutation4(instance, I)
        elif 41 <= probability <= 50:
            Mutation5()
        elif 51 <= probability <= 60:
            Mutation6()
        elif 61 <= probability <= 70:
            Mutation7()
        elif 71 <= probability <= 80:
            Mutation8()
        elif 81 <= probability <= 90:
            Mutation9()
        elif 91 <= probability <= 100:
            Mutation10()
        
        update_Hypervolumes(potentialHV_TD=potentialHV_TD, potentialHV_CU=potentialHV_CU)
        return I_m
    return I

def Euclidean_distance_dispersion(x1: float, y1: float, x2: float, y2: float):
    global Hypervolume_total_distance, Hypervolume_cargo_unbalance
    return sqrt(((x2 - x1) / 2 * Hypervolume_total_distance) ** 2 + ((y2 - y1) / 2 * Hypervolume_cargo_unbalance) ** 2)

def Child_dominates(Parent: Solution, Child: Solution) -> bool:
    return True if (Child.total_distance < Parent.total_distance and Child.cargo_unbalance <= Parent.cargo_unbalance) or (Child.total_distance <= Parent.total_distance and Child.cargo_unbalance < Parent.cargo_unbalance) else False

def MO_Metropolis(Parent: Solution, Child: Solution, T: float) -> Solution:
    if Child_dominates(Parent, Child):
        return Child
    elif T <= 0.00001:
        return Parent
    else:
        d_df = Euclidean_distance_dispersion(Child.total_distance, Child.cargo_unbalance, Parent.total_distance, Parent.cargo_unbalance)
        random_val = rand(0, INT_MAX - 1) / INT_MAX
        d_pt_pt = d_df / T ** 2
        pt_exp = exp(-1 * d_pt_pt)

        if random_val < pt_exp:
            return Child
        else:
            return Parent

def is_nondominated(I: Solution, ND: List[Solution]) -> bool:
    for nondominated in ND:
        if (I.total_distance < nondominated.total_distance and I.cargo_unbalance <= nondominated.cargo_unbalance) or (I.total_distance <= nondominated.total_distance and I.cargo_unbalance < nondominated.cargo_unbalance):
            continue
        else:
            return False
    return True

def MMOEASA(instance: ProblemInstance, p: int, MS: int, TC: int, P_crossover: int, P_mutation: int, T_max: float, T_min: float, T_stop: float) -> List[Solution]:
    P: List[Solution]=list()
    ND: List[Solution]=list()
    iterations = 0

    # temporary Hypervolume initialization
    #global Hypervolume_total_distance, Hypervolume_distance_unbalance, Hypervolume_cargo_unbalance
    #Hypervolume_total_distance = 2378.924 if instance.name == "R101.txt" and not len(instance.nodes) < 100 else 1
    #Hypervolume_distance_unbalance = 113.491 if instance.name == "R101.txt" and not len(instance.nodes) < 100 else 1
    #Hypervolume_cargo_unbalance = 171.000 if instance.name == "R101.txt" and not len(instance.nodes) < 100 else 1

    TWIH_initialiser = TWIH(instance)
    for i in range(p):
        TWIH_initialiser.id = i
        P.insert(i, copy.deepcopy(TWIH_initialiser))
        P[i].T_default = T_max - float(i) * ((T_max - T_min) / float(p) - 1.0)
        P[i].T_cooling = Calculate_cooling(i, T_max, T_min, T_stop, p, TC)
    del TWIH_initialiser
        
    current_multi_start = 1
    while current_multi_start <= MS and not iterations >= TC:
        for i, _ in enumerate(P):
            P[i].T = P[i].T_default
        
        while P[0].T > T_stop and not iterations >= TC:
            for i, I in enumerate(P):
                I_c = Crossover(instance, I, P, P_crossover)
                I_m = I_c
                for j in range(0, rand(1, MMOEASA_MAX_SIMULTANEOUS_MUTATIONS)):
                    I_m = Mutation(instance, I_m, P_mutation, rand(1, 30)) # TODO: remember to change 30 to 100 once all 10 mutation operators have been implemented
                P[i] = MO_Metropolis(I, I_m, I.T)
                
                if is_nondominated(P[i], ND): # this should be something like "if P[i] is unique and not dominated by all elements in the Non-Dominated set, then add it to ND and sort ND"
                    if len(ND) >= p:
                        ND.pop(0)
                    ND.append(P[i])
                
                P[i].T *= P[i].T_cooling
                print(f"len(ND)={len(ND)}")
            iterations += 1
        current_multi_start += 1
    return ND
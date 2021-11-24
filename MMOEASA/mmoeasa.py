from MMOEASA.auxiliaries import verify_nodes_are_inserted, reinitialize_depot_return
from MMOEASA.hypervolumes import Hypervolume_total_distance, Hypervolume_cargo_unbalance
from MMOEASA.operators import Mutation1, Mutation2, Mutation3, Mutation4, Mutation5, Mutation6, Mutation7, Mutation8, Mutation9, Mutation10, Crossover1
from MMOEASA.constants import INT_MAX
from MMOEASA.solution import Solution
from problemInstance import ProblemInstance
from destination import Destination
from vehicle import Vehicle
from typing import List
from numpy import random, sqrt, exp

#Hypervolume_total_distance, Hypervolume_distance_unbalance, Hypervolume_cargo_unbalance = 1, 1, 1

def TWIH(instance: ProblemInstance, solution_id: int) -> Solution:
    sorted_nodes = sorted([value for _, value in instance.nodes.items()], key=lambda x: x.ready_time)

    solution = Solution(
        _id=solution_id,
        #order_of_destinations=[Destination(node=node) for node in sorted_nodes],
        vehicles=list()
    )
    D_i = 1 # list of destinations iterator

    for i in range(0, instance.amount_of_vehicles - 1):
        if D_i >= len(instance.nodes) - 1:
            break
        if sorted_nodes[D_i].number == 0:
            continue

        vehicle = Vehicle(i, destinations=list())
        vehicle.destinations.append(Destination(node=sorted_nodes[0])) # have the route start at the depot

        while vehicle.current_capacity + sorted_nodes[D_i].demand < instance.capacity_of_vehicles and D_i < len(instance.nodes) - 1:
            vehicle.destinations.append(Destination(node=sorted_nodes[D_i]))
            vehicle.current_capacity += sorted_nodes[D_i].demand
            #instance.destinations[solution.orderOfDestinations[D_i].number].assignedVehicle = vehicle
            D_i += 1
        
        vehicle.destinations.append(Destination(node=sorted_nodes[0])) # have the route end at the depot
        solution.vehicles.append(vehicle)

    for i in range(1, len(instance.nodes)):
        verify_nodes_are_inserted(solution, instance, i)
    reinitialize_depot_return(solution, instance)

    solution.calculate_nodes_time_windows(instance)
    solution.calculate_routes_capacities(instance)
    solution.calculate_length_of_routes(instance)
    solution.objective_function(instance)

    #for vehicle in solution.vehicles:
    #    print(f"{vehicle.number}, {[destination.number for destination in vehicle.destinations]}")

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

def Cooling(P: List[Solution], T_stop: float) -> bool:
    for I in P:
        if I.T <= T_stop:
            return False
    return True

def Crossover(instance: ProblemInstance, I: Solution, P: List[Solution], P_crossover: int) -> Solution:
    return Crossover1(instance, I, P) if random.randint(1, 100) <= P_crossover else I

def Mutation(instance: ProblemInstance, I: Solution, P_mutation: int, probability: int) -> Solution:
    I_m = I

    if random.randint(1, 100) <= P_mutation:
        if probability >= 1 and probability <= 10:
            Mutation1(instance, I_m)
        elif probability >= 11 and probability <= 20:
            Mutation2()
        elif probability >= 21 and probability <= 30:
            Mutation3()
        elif probability >= 31 and probability <= 40:
            Mutation4()
        elif probability >= 41 and probability <= 50:
            Mutation5()
        elif probability >= 51 and probability <= 60:
            Mutation6()
        elif probability >= 61 and probability <= 70:
            Mutation7()
        elif probability >= 71 and probability <= 80:
            Mutation8()
        elif probability >= 81 and probability <= 90:
            Mutation9()
        elif probability >= 91 and probability <= 100:
            Mutation10()
    
    return I_m

def Euclidean_distance_dispersion(x1: int, y1: int, x2: int, y2: int):
    return sqrt(((x2 - x1) / 2 * Hypervolume_total_distance[0]) ** 2 + ((y2 - y1) / 2 * Hypervolume_cargo_unbalance[0]) ** 2)

def Child_dominates(Parent: Solution, Child: Solution) -> bool:
    return True if Child.total_distance < Parent.total_distance and Child.cargo_unbalance <= Parent.cargo_unbalance or Child.total_distance <= Parent.total_distance and Child.cargo_unbalance < Parent.cargo_unbalance else False

def MO_Metropolis(Parent: Solution, Child: Solution, T: float) -> Solution:
    if Child_dominates(Parent, Child):
        return Child
    elif T <= 0.00001:
        return Parent
    else:
        d_df = Euclidean_distance_dispersion(Child.total_distance, Child.cargo_unbalance, Parent.total_distance, Parent.cargo_unbalance)
        random_val = random.randint(0, INT_MAX) / INT_MAX
        d_pt_pt = d_df / T ** 2
        pt_exp = exp(-1 * d_pt_pt)

        if random_val < pt_exp:
            return Child
        else:
            return Parent

def is_nondominated(I: Solution, ND: List[Solution]) -> bool:
    for nondominated in ND:
        if I.total_distance < nondominated.total_distance and I.cargo_unbalance <= nondominated.cargo_unbalance or I.total_distance <= nondominated.total_distance and I.cargo_unbalance < nondominated.cargo_unbalance:
            continue
        else:
            return False
    return True

def MMOEASA(instance: ProblemInstance, p: int, MS: int, TC: int, P_crossover: int, P_mutation: int, T_max: float, T_min: float, T_stop: float) -> List[Solution]:
    #for i, I in enumerate(instance.destinations, start=1):
    P: List[Solution]=list()
    ND: List[Solution]=list()

    terminate = False
    iterations = 0

    # temporary Hypervolume initialization
    #Hypervolume_total_distance = 2378.924 if instance.name == "r101.txt" and not len(instance.destinations) < 100 else 1
    ##Hypervolume_distance_unbalance = 113.491 if instance.name == "r101.txt" and not len(instance.destinations) < 100 else 1
    #Hypervolume_cargo_unbalance = 171.000 if instance.name == "r101.txt" and not len(instance.destinations) < 100 else 1

    for i in range(p):
        P.insert(i, TWIH(instance, i))
        P[i].T_default = T_max - float(i) * ((T_max - T_min) / float(p) - 1.0)
        P[i].T_cooling = Calculate_cooling(i, T_max, T_min, T_stop, p, TC)
    
    for i in P:
        print(i.id)
        
    current_multi_start = 1
    while current_multi_start <= MS and not terminate:
        for j, _ in enumerate(P):
            P[j].T = P[j].T_default
            print(j, P[j].T)
        
        while P[0].T > T_stop and not terminate:#Cooling(P[j], T_stop) and not terminate:
            if iterations == TC:
                terminate = True

            for j, I in enumerate(P):
                #if j > 0: # I added this because I need to give Crossover and Mutation two parents; the pseudocode says to only give them one but if I do that then I don't have two parents to use in crossover/mutation
                I_c = Crossover(instance, I, P, P_crossover)
                I_m = Mutation(instance, I_c, P_mutation, random.randint(1, 100))
                P[j] = MO_Metropolis(I, I_m, I.T)
                
                if is_nondominated(P[j], ND): # this should be something like "if P[j] is unique and not dominated by all elements in the Non-Dominated set, then add it to ND and sort ND"
                    ND.append(P[j])
                
                P[j].T *= P[j].T_cooling
            iterations += 1
            print(P[0].T, current_multi_start)
        current_multi_start += 1
    
    return ND
from operators import Mutation1, Mutation2, Mutation3, Mutation4, Mutation5, Mutation6, Mutation7, Mutation8, Mutation9, Mutation10, Crossover1
from problemInstance import ProblemInstance
from vehicle import Vehicle
from typing import List, Dict
from numpy import random

class Solution():
    #T: float=None
    #T_cooling: Dict[int, float]=dict()
    #t: float=None

    def __init__(self, orderOfDestinations: List[int]=list(), vehicles: List[Vehicle]=list()):
        self.orderOfDestinations = orderOfDestinations
        self.vehicles = vehicles

def TWIH(instance: ProblemInstance):
    solution = Solution(
        orderOfDestinations=sorted([value for _, value in instance.destinations.items()], key=lambda x: x.readyTime),
        vehicles=list()
    )
    D_i = 1 # list of destinations iterator

    for i in range(0, instance.amountOfVehicles - 1):
        if D_i >= len(instance.destinations) - 1:
            break
        if solution.orderOfDestinations[D_i].number == 0:
            continue

        vehicle = Vehicle(i, instance.capacityOfVehicles, destinations=list())
        vehicle.destinations.append(solution.orderOfDestinations[0]) # have the route start at the depot

        while vehicle.currentCapacity + solution.orderOfDestinations[D_i].demand < vehicle.maxCapacity and D_i < len(instance.destinations) - 1:
            vehicle.destinations.append(solution.orderOfDestinations[D_i])
            vehicle.currentCapacity += solution.orderOfDestinations[D_i].demand
            instance.destinations[solution.orderOfDestinations[D_i].number].assignedVehicle = vehicle
            D_i += 1
        
        vehicle.destinations.append(solution.orderOfDestinations[0]) # have the route end at the depot
        solution.vehicles.append(vehicle)

    #for vehicle in solution.vehicles:
    #    print(f"{vehicle.number}, {[destination.number for destination in vehicle.destinations]}")

    return solution

def Calculate_cooling(destination: int, T_max: float, T_min: float, T_stop: float, p: int, TC: int):
    jumpTemperatures = 0
    if p > 1:
        jumpTemperatures = (T_max - T_min)/(p - 1)
    
    T_2 = T_max - destination * jumpTemperatures
    error = 0
    maxError = 0.005 * TC
    T_cooling = 0.995

    while abs(error) > maxError:
        T_1 = T_2
        auxiliaryIterations = 0

        while T_1 > T_stop:
            T_1 *= T_cooling
            auxiliaryIterations += 1
        
        error = TC - auxiliaryIterations
        T_cooling = (T_cooling + 0.05 / TC) if error > 0 else (T_cooling - 0.05 / TC)
    
    return T_cooling

def Cooling(P: List[Solution], T_stop: float) -> bool:
    for I in P:
        if I.t <= T_stop:
            return False
    return True

def Crossover(I: Solution, P_crossover: int):
    if random.randint(1, 100) <= P_crossover:
        Crossover1()

def Mutation(I: Solution, P_mutation: int, probability: int):
    if random.randint(1, 100) <= P_mutation:
        if probability >= 1 and probability <= 10:
            Mutation1()
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

def MO_Metropolis(I: Solution, I_m: Solution, T: float):
    pass

def MMOEASA(instance: ProblemInstance, p: int, MS: int, TC: int, P_crossover: int, P_mutation: int, T_min: float, T_max: float, T_stop: float) -> List[Solution]:
    #for i, I in enumerate(instance.destinations, start=1):
    P: List[Solution]=list()
    ND: List[Solution]=list()

    for i in range(p):
        P.insert(i, TWIH(instance))
    
    for i in range(p):
        #for I in instance.destinations.keys:
            #P[i].T = T_min + i * ((T_max - T_min) / p - 1)
            #P[i].T_cooling[I] = Calculate_cooling(I, T_max, T_min, T_stop, p, TC)
            #instance.destinations[I].T = T_min + i * ((T_max - T_min) / p - 1)
            #instance.destinations[I].T_cooling = Calculate_cooling(I, T_max, T_min, T_stop, p, TC)
        
        current_multi_start = 1;
        while (current_multi_start <= MS):
            #for j in enumerate(P):
                #P[j].t = P[j].T
            
            for I in instance.destinations.keys:
                instance.destinations[I].T = T_min + i * ((T_max - T_min) / p - 1)
                instance.destinations[I].T_cooling = Calculate_cooling(I, T_max, T_min, T_stop, p, TC)
            
            while Cooling(P, T_stop):
                for j, I in enumerate(P):
                    if j > 0: # I added this because I need to give Crossover and Mutation two parents; the pseudocode says to only give them one but if I do that then I don't have two parents to use in crossover/mutation
                        I_c = Crossover(I, P[j - 1], P_crossover)
                        I_m = Mutation(I_c, P_mutation, random.randint(1, 100))
                        P[j] = MO_Metropolis(I, I_m, I.T)
                    
                    if True:
                        ND.append(P[j])
                    
                    P[j].t *= P[j].T_cooling
            current_multi_start += 1
    return ND
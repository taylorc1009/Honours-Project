from mmoeasa import Solution, MO_Metropolis
from constants import MMOEASA_POPULATION_SIZE
from auxiliaries import verify_nodes_are_inserted
from ..problemInstance import ProblemInstance
from typing import List
from numpy import random

def rand(start: int, end: int, exclude_values: List[int]=list()):
    random_val = random.randint(start, end)
    while random_val in exclude_values:
        random_val = random.randint(start, end)
    return random_val

def shift_left(I: Solution, vehicle: int, destination: int, displacement: int=1):
    for i in range(I.vehicles[vehicle].getIndexOfDestination(destination), len(I.vehicles[vehicle].destinations)):
        I.vehicles[vehicle].destinations[i].node = I.vehicles[vehicle].destinations[i + displacement].node

def shift_right(I: Solution, vehicle: int, destination: int, displacement: int=1):
    for i in range(len(I.vehicles[vehicle].destinations), I.vehicles[vehicle].getIndexOfDestination(destination), -1):
        I.vehicles[vehicle].destinations[i].node = I.vehicles[vehicle].destinations[i - displacement].node

def move_destination(instance: ProblemInstance, I: Solution, vehicle_1: int, origin: int, vehicle_2: int, destination: int):
    num_nodes = len(instance.nodes)
    
    origin_node = I.vehicles[vehicle_1].destinations[origin].node
    destination_node = I.vehicles[vehicle_2].destinations[destination].node

    if vehicle_1 == vehicle_2:
        omd_absolute = abs(origin - destination)

        if omd_absolute == 1:
            I.vehicles[vehicle_2].destinations[destination].node = origin_node
            I.vehicles[vehicle_1].destinations[origin].node = destination_node
        elif omd_absolute > 1:
            shift_right(I, vehicle_2, destination)
            I.vehicles[vehicle_2].destinations[destination].node = origin_node

            if origin > destination:
                shift_left(I, vehicle_1, origin + 1)
            elif origin < destination:
                shift_left(I, vehicle_1, origin)
    else:
        if len(I.vehicles[vehicle_2].destinations) - 2 <= 0: # "- 2" to discount the two depot entries
            I.vehicles[vehicle_2].destinations[0].node = instance.node[0]
            I.vehicles[vehicle_2].destinations[1].node = origin_node.node
            I.vehicles[vehicle_2].destinations[2].node = instance.node[0]

            if len(I.vehicles[vehicle_2].destinations) > 3:
                for i in range(3, len(I.vehicles[vehicle_2].destinations)):
                    del I.vehicles[vehicle_2].destinations[i]
            
            shift_left(num_nodes, I, vehicle_1, origin)
        elif len(I.vehicles[vehicle_1].destinations) - 2 == 0:
            shift_right(num_nodes, I, vehicle_2, destination)

            I.vehicles[vehicle_2].destinations[destination].node = origin_node
            shift_left(num_nodes, I, vehicle_1, origin)
    
    I.calculate_nodes_time_windows(instance)
    I.calculate_routes_capacities(instance)
    I.calculate_length_of_routes(instance)
    I.objective_function(instance)

def Mutation1(instance: ProblemInstance, I: Solution) -> Solution:
    I_m = I

    vehicle_randomize = rand(0, len(I_m.vehicles) - 1)
    while len(I_m.vehicles[vehicle_randomize].destinations) < 2:
        vehicle_randomize = rand(0, len(I_m.vehicles) - 1)
    
    origin_position = rand(0, len(I_m.vehicles[vehicle_randomize].destinations))
    destination_position = rand(0, len(I_m.vehicles[vehicle_randomize].destinations), exclude_values=[origin_position])
    #while origin_position == destination_position:
        #destination_position = rand(0, len(I_m.vehicles[vehicle_randomize].destinations))

    move_destination(instance, I_m, vehicle_randomize, origin_position, vehicle_randomize, destination_position)
    
    if MO_Metropolis(MMOEASA_POPULATION_SIZE, I_m, I, I_m.T):
        return I_m
    return I

def Mutation2():
    pass

def Mutation3():
    pass

def Mutation4():
    pass

def Mutation5():
    pass

def Mutation6():
    pass

def Mutation7():
    pass

def Mutation8():
    pass

def Mutation9():
    pass

def Mutation10():
    pass

def Crossover1(instance: ProblemInstance, I: Solution, P: List[Solution]):
    I_c = I

    routes_to_safeguard = list()

    for i in enumerate(I_c.vehicles):
        if rand(0, 100) < 50:
            routes_to_safeguard.append(i)
        else:
            #I.vehicles[i].clearAssignedDestinations()
            I_c.vehicles[i].destinations.clear()
            i -= 1

    for i in range(len(I_c.vehicles), -1, -1):
        if i in routes_to_safeguard:
            for j in enumerate(I_c.vehicles):
                if j not in routes_to_safeguard:
                    #I.vehicles[j].clearAssignedDestinations()
                    I_c.vehicles[j].destinations = I_c.vehicles[i].destinations
                    routes_to_safeguard.append(j)
                    #I.vehicles[i].clearAssignedDestinations()
                    del I_c.vehicles[i]
                    del routes_to_safeguard[i]
                    break
    
    random_solution = rand(0, len(P), exclude_values=[I_c.id])
    routes_inserted = len(routes_to_safeguard)

    for i in enumerate(P[random_solution].vehicles):
        if len(P[random_solution].vehicles[i].destinations) - 2 >= 1:
            insertion_possible = True
            for j in range(1, len(P[random_solution].vehicles[i].destinations) - 1): # start at one and end one before the end of the list to discount depot nodes
                for k in enumerate(I_c.vehicles):
                    if len(I_c.vehicles[k].destinations) - 2 >= 1:
                        for l in range(1, len(I_c.vehicles[k].destinations) - 1):
                            if I_c.vehicles[k].destinations[l].node.number == P[random_solution].vehicles[i].destinations[j].node.number:
                                insertion_possible = False
            if insertion_possible and routes_inserted < instance.amountOfVehicles:
                I_c.vehicles[routes_inserted].destinations = P[random_solution].vehicles[i].destinations
                routes_inserted += 1
    
    verify_nodes_are_inserted(I, instance)

    I.calculate_number_of_routes()
    calculate_time_window_paths()
    calculate_route_cargo()
    calculate_length_of_routes()
    objective_function()


    return I if I_c.total_distance < 0 else MO_Metropolis(I, I_c, I.T)
from mmoeasa import Solution, MO_Metropolis
from constants import MMOEASA_POPULATION_SIZE
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
    
    calculate_number_of_routes()
    calculate_time_window_paths()
    calculate_route_cargo()
    calculate_length_of_routes()
    objective_function()

def Mutation1(instance: ProblemInstance, I: Solution) -> Solution:
    I_m = I

    vehicle_randomize = rand(0, len(I_m.vehicles) - 1)
    while len(I_m.vehicles[vehicle_randomize].destinations) < 2:
        vehicle_randomize = rand(0, len(I_m.vehicles) - 1)
    
    origin_position = rand(0, len(I_m.vehicles[vehicle_randomize].destinations))
    destination_position = rand(0, len(I_m.vehicles[vehicle_randomize].destinations), exclude_values=list(origin_position))
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

def solution_visits_destination(destination: int, instance: ProblemInstance, I: Solution) -> bool:
    for j in range(0, instance.amountOfVehicles):
        if len(I.vehicles[j].destinations) - 2 >= 1:
            for k in len(I.vehicles[j].destinations):
                if I.vehicles[j].destinations[k].node.number == instance.destinations[destination].node.number: # directly get the destination number from the list of destinations in case there's a mismatch between the destination number and the for loop iterator (although there shouldn't)
                    return True
    return False

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
    
    random_solution = rand(0, len(P), exclude_values=list(I_c.id))
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
    
    for i in range(1, len(instance.destinations)):
        if not solution_visits_destination(i, instance, I):
            inserted, vehicle = False, 0
            while vehicle < instance.amount_of_vehicles and inserted < 0:
                length_of_route = len(I_c.vehicles[vehicle].destinations) - 2
                final_destination = I_c.vehicles[vehicle].destinations[length_of_route].node.number
                
                I_c.vehicles[vehicle].destinations[length_of_route + 1].node = instance.nodes[i]
                I_c.vehicles[vehicle].current_capacity += instance.destinations[i].node.demand

                I_c.vehicles[vehicle].destinations[length_of_route + 1].arrival_time = I_c.vehicles[vehicle].destinations[length_of_route].departure_time + instance.MMOEASA_distances[final_destination][i]
                I_c.vehicles[vehicle].destinations[length_of_route + 1].wait_time = 0.0
                if I_c.vehicles[vehicle].destinations[length_of_route + 1].arrival_time < instance.destinations[i].ready_time:
                    I_c.vehicles[vehicle].destinations[length_of_route + 1].wait_time = instance.destinations[i].ready_time - I_c.vehicles[vehicle].destinations[length_of_route + 1].arrival_time
                    I_c.vehicles[vehicle].destinations[length_of_route + 1].arrival_time = instance.destinations[i].ready_time
                
                if I_c.vehicles[vehicle].destinations[length_of_route + 1].arrival_time <= instance.destinations[i].due_date:
                    I_c.vehicles[vehicle].destinations[length_of_route + 1].departure_time = instance.destinations[i].serve_time + I_c.vehicles[vehicle].destinations[length_of_route + 1].arrival_time

                    calculate_route_lengths()

                    inserted = True
                elif I_c.vehicles[vehicle].destinations[length_of_route + 1].arrival_time > instance.destinations[i].due_date or I_c.vehicles[vehicle].current_capacity > instance.capacity_of_vehicles:
                    del I_c.vehicles[vehicle].destinations[length_of_route + 1]
                    vehicle += 1
    
    for i in range(I_c.vehicles):
        I_c.vehicles[vehicle].destinations.append(instance.destinations[0])

        length_of_route = len(I_c.vehicles[i].destinations) - 2
        final_destination = I_c.vehicles[vehicle].destinations[length_of_route].number

        I_c.vehicles[vehicle].destinations[length_of_route + 1].arrival_time = I_c.vehicles[vehicle].destinations[length_of_route + 1].departure_time + instance.MMOEASA_distances[final_destination][0]
        I_c.vehicles[vehicle].destinations[length_of_route + 1].departure_time = I_c.vehicles[vehicle].destinations[length_of_route + 1].departure_time + instance.MMOEASA_distances[final_destination][0]
        I_c.vehicles[vehicle].destinations[length_of_route + 1].wait_time = 0.0

    calculate_number_of_routes()
    calculate_time_window_paths()
    calculate_route_cargo()
    calculate_length_of_routes()
    objective_function()


    return I if I_c.total_distance < 0 else MO_Metropolis(I, I_c, I.T)
from mmoeasa import Solution, MO_Metropolis
from constants import MMOEASA_INFINITY, INT_MAX, MMOEASA_POPULATION_SIZE
from ..problemInstance import ProblemInstance
from numpy import random, exp

def rand(start: int, end: int):
    return random.randint(start, end)

def shift_left(I: Solution, vehicle: int, destination: int, displacement: int=1):
    for i in range(I.vehicles[vehicle].getIndexOfDestination(destination), len(I.vehicles[vehicle].destinations)):
        I.vehicles[vehicle].destinations[i] = I.vehicles[vehicle].destinations[i + displacement]

def shift_right(I: Solution, vehicle: int, destination: int, displacement: int=1):
    for i in range(len(I.vehicles[vehicle].destinations), I.vehicles[vehicle].getIndexOfDestination(destination), -1):
        I.vehicles[vehicle].destinations[i] = I.vehicles[vehicle].destinations[i - displacement]

def move_destination(instance: ProblemInstance, I: Solution, vehicle_1: int, origin: int, vehicle_2: int, destination: int):
    num_nodes = len(instance.destinations)
    
    origin_node = I.vehicles[vehicle_1].destinations[origin]
    destination_node = I.vehicles[vehicle_2].destinations[destination]

    if vehicle_1 == vehicle_2:
        o_a_absolute = abs(origin - destination)

        if o_a_absolute == 1:
            I.vehicles[vehicle_2].destinations[destination] = origin_node
            I.vehicles[vehicle_1].destinations[origin] = destination_node
        elif o_a_absolute > 1:
            shift_right(I, vehicle_2, destination)
            I.vehicles[vehicle_2].destinations[destination] = origin_node

            if origin > destination:
                shift_left(I, vehicle_1, origin + 1)
            elif origin < destination:
                shift_left(I, vehicle_1, origin)
    else:
        if len(I.vehicles[vehicle_2].destinations) - 2 <= 0: # "- 2" to discount the two depot entries
            I.vehicles[vehicle_2].destinations[0] = instance.destinations[0]
            I.vehicles[vehicle_2].destinations[1] = origin_node
            I.vehicles[vehicle_2].destinations[2] = instance.destinations[0]

            if len(I.vehicles[vehicle_2].destinations) > 3:
                for i in range(3, len(I.vehicles[vehicle_2].destinations)):
                    I.vehicles[vehicle_2].destinations.remove(i)
            
            shift_left(num_nodes, I, vehicle_1, origin)
        elif len(I.vehicles[vehicle_1].destinations) - 2 == 0:
            shift_right(num_nodes, I, vehicle_2, destination)

            I.vehicles[vehicle_2].destinations[destination] = origin_node
            shift_left(num_nodes, I, vehicle_1, origin)

def Mutation1(instance: ProblemInstance, I: Solution) -> Solution:
    I_m = I

    vehicle_randomize = rand(0, len(I_m.vehicles) - 1)
    while len(I_m.vehicles[vehicle_randomize].destinations) < 2:
        vehicle_randomize = rand(0, len(I_m.vehicles) - 1)
    
    origin_position = rand(0, len(I_m.vehicles[vehicle_randomize].destinations))
    destination_position = rand(0, len(I_m.vehicles[vehicle_randomize].destinations))
    while origin_position == destination_position:
        destination_position = rand(0, len(I_m.vehicles[vehicle_randomize].destinations))

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

def Crossover1():
    pass
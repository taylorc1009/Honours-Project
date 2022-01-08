import copy
from MMOEASA.constants import MMOEASA_INFINITY
from MMOEASA.solution import Solution
from MMOEASA.auxiliaries import insert_unvisited_node, solution_visits_destination, rand
from problemInstance import ProblemInstance
from destination import Destination
from typing import List, Tuple
from vehicle import Vehicle

"""def shift_left(I: Solution, vehicle: int, index: int, displacement: int=1) -> Solution:
    for i in range(index, len(I.vehicles[vehicle].destinations) - 1):
        I.vehicles[vehicle].destinations[i].node = I.vehicles[vehicle].destinations[i + displacement].node
    return I

def shift_right(I: Solution, vehicle: int, index: int, displacement: int=1) -> Solution:
    for i in range(len(I.vehicles[vehicle].destinations) - 1, index, -1):
        I.vehicles[vehicle].destinations[i].node = I.vehicles[vehicle].destinations[i - displacement].node
    return I"""

# TODO: this could be heavily improved using the list's ".insert()" method; the MMOEASA in C needs to move elements the same way they're being moved now as C doesn't have append/pop methods
def move_destination(instance: ProblemInstance, I: Solution, vehicle_1: int, origin: int, vehicle_2: int, destination: int) -> Tuple[Solution, float, float]:
    """origin_node = I.vehicles[vehicle_1].destinations[origin]
    destination_node = I.vehicles[vehicle_2].destinations[destination]"""
    origin_node = I.vehicles[vehicle_1].destinations[origin]
    destination_node = I.vehicles[vehicle_2].destinations[destination]

    if vehicle_1 == vehicle_2:
        omd_absolute = abs(origin - destination)

        if omd_absolute == 1:
            I.vehicles[vehicle_2].destinations[destination] = origin_node
            I.vehicles[vehicle_1].destinations[origin] = destination_node
        elif omd_absolute > 1:
            """I = shift_right(I, vehicle_2, destination)
            I.vehicles[vehicle_2].destinations[destination].node = origin_node

            if origin > destination:
                I = shift_left(I, vehicle_1, origin + 1)
            elif origin < destination:
                I = shift_left(I, vehicle_1, origin)

            # during debugging, I noticed that the final node is not being reset to the depot node (as the following, new line does)
            # the original MMOEASA code doesn't do this either, but I imagine it should?
            # TODO: this may also belong in the "else" section below? Test this theory when more mutators are added
            I.vehicles[vehicle_1].destinations[-1].node = instance.nodes[0]"""
            I.vehicles[vehicle_2].destinations.insert(destination, origin_node)
            del I.vehicles[vehicle_1].destinations[origin + 1 if origin > destination else origin]
    else:
        if I.vehicles[vehicle_2].getNumOfCustomersVisited() <= 0:
            I.vehicles[vehicle_2].destinations = [Destination(node=instance.nodes[0]), origin_node, Destination(node=instance.nodes[0])]
            #I = shift_left(I, vehicle_1, origin)
        else:
            """I = shift_right(I, vehicle_2, destination)
            I.vehicles[vehicle_2].destinations[destination].node = origin_node
            I.vehicles[vehicle_2].destinations.append(Destination(node=instance.nodes[0]))
            I = shift_left(I, vehicle_1, origin)
        del I.vehicles[vehicle_1].destinations[-1]"""
            I.vehicles[vehicle_2].destinations.insert(destination, origin_node)
        del I.vehicles[vehicle_1].destinations[origin]
    
    I.calculate_nodes_time_windows(instance)
    I.calculate_vehicles_loads(instance)
    I.calculate_length_of_routes(instance)
    potentialHV_TD, potentialHV_CU = I.objective_function(instance)

    return I, potentialHV_TD, potentialHV_CU

def get_random_vehicle(I: Solution, exclude_values: List[int]=None, vehicles_required: int=1) -> int:
    random_vehicle = rand(0, len(I.vehicles) - 1, exclude_values=exclude_values)
    while I.vehicles[random_vehicle].getNumOfCustomersVisited() < vehicles_required:
        random_vehicle = rand(0, len(I.vehicles) - 1, exclude_values=exclude_values)
    return random_vehicle

def compare_Hypervolumes(TD_1: float=0.0, TD_2: float=0.0, CU_1: float=0.0, CU_2: float=0.0) -> Tuple[float, float]:
    finalHV_TD = float(TD_1) if float(TD_1) > float(TD_2) else float(TD_2)
    finalHV_CU = float(CU_1) if float(CU_1) > float(CU_2) else float(CU_2)
    return finalHV_TD, finalHV_CU

def Mutation1(instance: ProblemInstance, I_m: Solution) -> Tuple[Solution, float, float]:
    random_vehicle = get_random_vehicle(I_m, vehicles_required=2)
    num_customers = I_m.vehicles[random_vehicle].getNumOfCustomersVisited()
    origin_position = rand(1, num_customers)
    destination_position = rand(1, num_customers, exclude_values=[origin_position])

    I_m, potentialHV_TD, potentialHV_CU = move_destination(instance, I_m, random_vehicle, origin_position, random_vehicle, destination_position)
    
    # I don't think this "if" is necessary as the MMOEASA main algorithm performs the metropolis function anyway
    #if MO_Metropolis(MMOEASA_POPULATION_SIZE, I_m, I, I_m.T):
    return I_m, potentialHV_TD, potentialHV_CU
    #return I

def Mutation2(instance: ProblemInstance, I_m: Solution) -> Tuple[Solution, float, float]:
    potentialHV_TD, potentialHV_CU = 0.0, 0.0

    random_vehicle = get_random_vehicle(I_m, vehicles_required=2)
    num_customers = I_m.vehicles[random_vehicle].getNumOfCustomersVisited()
    origin_position = rand(1, num_customers)

    best_location, fitness_of_best_location = origin_position, MMOEASA_INFINITY
    for i in range(1, num_customers + 1):
        if i != origin_position:
            I_m, tempHV_TD, tempHV_CU = move_destination(instance, I_m, random_vehicle, origin_position, random_vehicle, i)
            potentialHV_TD, potentialHV_CU = compare_Hypervolumes(TD_1=potentialHV_TD, TD_2=tempHV_TD, CU_1=potentialHV_CU, CU_2=tempHV_CU)
            if 0 <= I_m.total_distance < fitness_of_best_location:
                fitness_of_best_location = I_m.total_distance
                best_location = i
            I_m, _, _ = move_destination(instance, I_m, random_vehicle, i, random_vehicle, origin_position)

    if best_location != origin_position:
        I_m, _, _ = move_destination(instance, I_m, random_vehicle, origin_position, random_vehicle, best_location)

    # I don't think this "if" is necessary as the MMOEASA main algorithm performs the metropolis function anyway
    # if MO_Metropolis(MMOEASA_POPULATION_SIZE, I_m, I, I_m.T):
    return I_m, potentialHV_TD, potentialHV_CU
    # return I

def Mutation3(instance: ProblemInstance, I_m: Solution) -> Tuple[Solution, float, float]:
    random_origin_vehicle = get_random_vehicle(I_m)
    origin_position = rand(1, I_m.vehicles[random_origin_vehicle].getNumOfCustomersVisited())

    random_destination_vehicle = get_random_vehicle(I_m, exclude_values=[random_origin_vehicle])
    destination_position = rand(1, I_m.vehicles[random_destination_vehicle].getNumOfCustomersVisited())

    I_m, potentialHV_TD, potentialHV_CU = move_destination(instance, I_m, random_origin_vehicle, origin_position, random_destination_vehicle, destination_position)

    return I_m, potentialHV_TD, potentialHV_CU

def Mutation4(instance: ProblemInstance, I_m: Solution) -> Tuple[Solution, float, float]:
    potentialHV_TD, potentialHV_CU = 0.0, 0.0

    random_origin_vehicle = get_random_vehicle(I_m)
    origin_position = rand(1, I_m.vehicles[random_origin_vehicle].getNumOfCustomersVisited())

    random_destination_vehicle = get_random_vehicle(I_m, exclude_values=[random_origin_vehicle])

    best_location, fitness_of_best_location = -1, MMOEASA_INFINITY
    for i in range(1, I_m.vehicles[random_destination_vehicle].getNumOfCustomersVisited() + 1):
        I_m, tempHV_TD, tempHV_CU = move_destination(instance, I_m, random_origin_vehicle, origin_position, random_destination_vehicle, i)
        potentialHV_TD, potentialHV_CU = compare_Hypervolumes(TD_1=potentialHV_TD, TD_2=tempHV_TD, CU_1=potentialHV_CU, CU_2=tempHV_CU)
        if 0 <= I_m.total_distance < fitness_of_best_location:
            fitness_of_best_location = I_m.total_distance
            best_location = i
        I_m, _, _ = move_destination(instance, I_m, random_destination_vehicle, i, random_origin_vehicle, origin_position)

    if best_location >= 0:
        I_m, _, _ = move_destination(instance, I_m, random_origin_vehicle, origin_position, random_destination_vehicle, best_location)

    return I_m, potentialHV_TD, potentialHV_CU

def Mutation5(instance: ProblemInstance, I_m: Solution) -> Tuple[Solution, float, float]:
    random_origin_vehicle = get_random_vehicle(I_m)
    origin_position = rand(1, I_m.vehicles[random_origin_vehicle].getNumOfCustomersVisited())

    random_destination_vehicle = get_random_vehicle(I_m, exclude_values=[random_origin_vehicle])
    destination_position = rand(1, I_m.vehicles[random_destination_vehicle].getNumOfCustomersVisited())

    I_m, potentialHV_TD, potentialHV_CU = move_destination(instance, I_m, random_origin_vehicle, origin_position, random_destination_vehicle, destination_position)
    I_m, tempHV_TD, tempHV_CU = move_destination(instance, I_m, random_destination_vehicle, destination_position + 1, random_origin_vehicle, origin_position)

    potentialHV_TD, potentialHV_CU = compare_Hypervolumes(TD_1=potentialHV_TD, TD_2=tempHV_TD, CU_1=potentialHV_CU, CU_2=tempHV_CU)

    return I_m, potentialHV_TD, potentialHV_CU

def Mutation6(instance: ProblemInstance, I_m: Solution) -> Tuple[Solution, float, float]:
    potentialHV_TD, potentialHV_CU = 0.0, 0.0

    random_origin_vehicle = get_random_vehicle(I_m)
    origin_position = rand(1, I_m.vehicles[random_origin_vehicle].getNumOfCustomersVisited())

    best_vehicle, best_location, fitness_of_best_location = -1, -1, MMOEASA_INFINITY
    for destination_vehicle in range(0, len(I_m.vehicles)):
        if not random_origin_vehicle == destination_vehicle:
            num_customers = I_m.vehicles[destination_vehicle].getNumOfCustomersVisited()
            if num_customers > 0:
                for i in range(1, num_customers + 1):
                    I_m, tempHV_TD, tempHV_CU = move_destination(instance, I_m, random_origin_vehicle, origin_position, destination_vehicle, i)
                    potentialHV_TD, potentialHV_CU = compare_Hypervolumes(TD_1=potentialHV_TD, TD_2=tempHV_TD, CU_1=potentialHV_CU, CU_2=tempHV_CU)
                    if 0 <= I_m.total_distance < fitness_of_best_location:
                        fitness_of_best_location = I_m.total_distance
                        best_vehicle = destination_vehicle
                        best_location = i
                    I_m, _, _ = move_destination(instance, I_m, destination_vehicle, i, random_origin_vehicle, origin_position)

    if best_location >= 0:
        I_m, _, _ = move_destination(instance, I_m, random_origin_vehicle, origin_position, best_vehicle, best_location)

    return I_m, potentialHV_TD, potentialHV_CU

def Mutation7(instance: ProblemInstance, I_m: Solution) -> Tuple[Solution, float, float]:
    potentialHV_TD, potentialHV_CU = 0.0, 0.0

    random_origin_vehicle = get_random_vehicle(I_m)
    origin_position = rand(1, I_m.vehicles[random_origin_vehicle].getNumOfCustomersVisited())

    best_vehicle, best_location, smallest_time_window_difference = -1, -1, MMOEASA_INFINITY
    for destination_vehicle in range(0, len(I_m.vehicles)):
        if not random_origin_vehicle == destination_vehicle:
            num_customers = I_m.vehicles[destination_vehicle].getNumOfCustomersVisited()
            if num_customers > 0:
                for i in range(1, num_customers + 2): # TODO: MMOEASA does +2 to include the depot-return node in this mutation; is this correct and does it work?
                    I_m, tempHV_TD, tempHV_CU = move_destination(instance, I_m, random_origin_vehicle, origin_position, destination_vehicle, i)
                    potentialHV_TD, potentialHV_CU = compare_Hypervolumes(TD_1=potentialHV_TD, TD_2=tempHV_TD, CU_1=potentialHV_CU, CU_2=tempHV_CU)
                    time_window_difference = abs(I_m.vehicles[random_origin_vehicle].destinations[origin_position].arrival_time - I_m.vehicles[destination_vehicle].destinations[i].arrival_time)
                    if I_m.total_distance >= 0 and time_window_difference < smallest_time_window_difference:
                        smallest_time_window_difference = time_window_difference
                        best_vehicle = destination_vehicle
                        best_location = i
                    I_m, _, _ = move_destination(instance, I_m, destination_vehicle, i, random_origin_vehicle, origin_position)

    if best_location >= 0:
        I_m, _, _ = move_destination(instance, I_m, random_origin_vehicle, origin_position, best_vehicle, best_location)

    return I_m, potentialHV_TD, potentialHV_CU

def Mutation8(instance: ProblemInstance, I_m: Solution) -> Tuple[Solution, float, float]:
    potentialHV_TD, potentialHV_CU = 0.0, 0.0

    if len(I_m.vehicles) < instance.amount_of_vehicles:
        random_vehicle = get_random_vehicle(I_m, vehicles_required=2)
        origin_position = rand(1, I_m.vehicles[random_vehicle].getNumOfCustomersVisited())

        destinations = [Destination(node=instance.nodes[0]), *I_m.vehicles[random_vehicle].destinations[origin_position:-1], Destination(node=instance.nodes[0])]
        I_m.vehicles.append(Vehicle(destinations=destinations))
        del I_m.vehicles[random_vehicle].destinations[origin_position:-1]

        I_m.calculate_nodes_time_windows(instance)
        I_m.calculate_vehicles_loads(instance)
        I_m.calculate_length_of_routes(instance)
        potentialHV_TD, potentialHV_CU = I_m.objective_function(instance)

    return I_m, potentialHV_TD, potentialHV_CU

def Mutation9(instance: ProblemInstance, I_m: Solution) -> Tuple[Solution, float, float]:
    potentialHV_TD, potentialHV_CU = 0.0, 0.0

    if len(I_m.vehicles) < instance.amount_of_vehicles:
        random_vehicle = get_random_vehicle(I_m, vehicles_required=2)
        origin_position = rand(1, I_m.vehicles[random_vehicle].getNumOfCustomersVisited())

        destinations = [Destination(node=instance.nodes[0]), I_m.vehicles[random_vehicle].destinations[origin_position], Destination(node=instance.nodes[0])]
        I_m.vehicles.append(Vehicle(destinations=destinations))
        del I_m.vehicles[random_vehicle].destinations[origin_position]

        I_m.calculate_nodes_time_windows(instance)
        I_m.calculate_vehicles_loads(instance)
        I_m.calculate_length_of_routes(instance)
        potentialHV_TD, potentialHV_CU = I_m.objective_function(instance)

    return I_m, potentialHV_TD, potentialHV_CU

def Mutation10() -> Tuple[Solution, float, float]:
    pass

def vehicle_insertion_possible(I_c: Solution, P: List[Solution], random_solution: int, i: int) -> bool:
    for j in range(1, len(P[random_solution].vehicles[i].destinations) - 1): # start at one and end one before the end of the list to discount depot nodes
        for k, _ in enumerate(I_c.vehicles):
            if I_c.vehicles[k].getNumOfCustomersVisited() >= 1:
                for l in range(1, len(I_c.vehicles[k].destinations) - 1):
                    if I_c.vehicles[k].destinations[l].node.number == P[random_solution].vehicles[i].destinations[j].node.number: # make sure "I_c" does not already visit a node from "P[random_solution].vehicles[i]"
                        return False
    return True

def Crossover1(instance: ProblemInstance, I_c: Solution, P: List[Solution]) -> Tuple[Solution, float, float]:
    routes_to_safeguard = list()
    i = 0
    while i < len(I_c.vehicles): # use a while loop here instead of a for loop as a Python for loop iterator cannot be decremented
        if rand(0, 100) < 50:
            routes_to_safeguard.append(i)
            i += 1 # only increment the for loop in this case; if it's incremented in the "else" block then a vehicle will be skipped (because the "else" removes one vehicle from the list)
        else:
            del I_c.vehicles[i]
            #i -= 1

    """ this block of code from the original MMOEASA (written in C) appears to be unnecessary here as it's only moving the last vehicle in the list to an earlier point in the list
    for i in range(len(I_c.vehicles) - 1, -1, -1):
        if i in routes_to_safeguard:
            for j, _ in enumerate(I_c.vehicles):
                if j not in routes_to_safeguard:
                    I_c.vehicles[j] = I_c.vehicles[i]
                    routes_to_safeguard.append(j)
                    del I_c.vehicles[i]
                    routes_to_safeguard.remove(i)
                    break"""
    
    random_solution = rand(0, len(P) - 1, exclude_values=[I_c.id])

    for i, _ in enumerate(P[random_solution].vehicles):
        if P[random_solution].vehicles[i].getNumOfCustomersVisited() >= 1:
            if vehicle_insertion_possible(I_c, P, random_solution, i) and len(I_c.vehicles) < instance.amount_of_vehicles:
                I_c.vehicles.append(copy.deepcopy(P[random_solution].vehicles[i]))

    for i in range(1, len(instance.nodes)):
        if not solution_visits_destination(i, instance, I_c):
            I_c = insert_unvisited_node(I_c, instance, i)

    I_c.calculate_nodes_time_windows(instance)
    I_c.calculate_vehicles_loads(instance)
    I_c.calculate_length_of_routes(instance)
    potentialHV_TD, potentialHV_CU = I_c.objective_function(instance)

    # I don't think this line is necessary as the MMOEASA main algorithm performs the metropolis function anyway
    #return I if I_c.total_distance < 0 else MO_Metropolis(I, I_c, I.T)

    return I_c, potentialHV_TD, potentialHV_CU
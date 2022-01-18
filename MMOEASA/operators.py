import copy
from MMOEASA.constants import MMOEASA_INFINITY
from MMOEASA.solution import Solution
from MMOEASA.auxiliaries import insert_unvisited_node, rand
from problemInstance import ProblemInstance
from destination import Destination
from typing import List, Tuple, Set
from vehicle import Vehicle

def move_destination(instance: ProblemInstance, I: Solution, vehicle_1: int, origin: int, vehicle_2: int, destination: int) -> Tuple[Solution, float, float]:
    origin_node = I.vehicles[vehicle_1].destinations[origin]

    if vehicle_1 == vehicle_2:
        omd_absolute = abs(origin - destination)

        if omd_absolute == 1:
            I.vehicles[vehicle_1].destinations[origin] = I.vehicles[vehicle_2].destinations[destination]
            I.vehicles[vehicle_2].destinations[destination] = origin_node
        elif omd_absolute > 1:
            I.vehicles[vehicle_2].destinations.insert(destination, origin_node)
            del I.vehicles[vehicle_1].destinations[origin + 1 if origin > destination else origin]
    else:
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
    return max(TD_1, TD_2), max(CU_1, CU_2)

def Mutation1(instance: ProblemInstance, I_m: Solution) -> Tuple[Solution, float, float]:
    random_vehicle = get_random_vehicle(I_m, vehicles_required=2)
    num_customers = I_m.vehicles[random_vehicle].getNumOfCustomersVisited()
    origin_position = rand(1, num_customers)
    destination_position = rand(1, num_customers, exclude_values=[origin_position])

    I_m, potentialHV_TD, potentialHV_CU = move_destination(instance, I_m, random_vehicle, origin_position, random_vehicle, destination_position)

    return I_m, potentialHV_TD, potentialHV_CU

def Mutation2(instance: ProblemInstance, I_m: Solution) -> Tuple[Solution, float, float]:
    potentialHV_TD, potentialHV_CU = 0.0, 0.0

    random_vehicle = get_random_vehicle(I_m, vehicles_required=2)
    num_customers = I_m.vehicles[random_vehicle].getNumOfCustomersVisited()
    origin_position = rand(1, num_customers)

    best_location, fitness_of_best_location = origin_position, MMOEASA_INFINITY
    for i in range(1, num_customers + 1):
        if not i == origin_position:
            I_m, tempHV_TD, tempHV_CU = move_destination(instance, I_m, random_vehicle, origin_position, random_vehicle, i)
            potentialHV_TD, potentialHV_CU = compare_Hypervolumes(TD_1=potentialHV_TD, TD_2=tempHV_TD, CU_1=potentialHV_CU, CU_2=tempHV_CU)

            if 0 <= I_m.total_distance < fitness_of_best_location:
                fitness_of_best_location = I_m.total_distance
                best_location = i
            I_m, _, _ = move_destination(instance, I_m, random_vehicle, i, random_vehicle, origin_position + 1 if origin_position > i else origin_position)

    if not best_location == origin_position:
        I_m, _, _ = move_destination(instance, I_m, random_vehicle, origin_position, random_vehicle, best_location)

    return I_m, potentialHV_TD, potentialHV_CU

def Mutation3(instance: ProblemInstance, I_m: Solution) -> Tuple[Solution, float, float]:
    random_origin_vehicle = get_random_vehicle(I_m)
    origin_position = rand(1, I_m.vehicles[random_origin_vehicle].getNumOfCustomersVisited())

    random_destination_vehicle = get_random_vehicle(I_m, exclude_values=[random_origin_vehicle])
    destination_position = rand(1, I_m.vehicles[random_destination_vehicle].getNumOfCustomersVisited())

    I_m, potentialHV_TD, potentialHV_CU = move_destination(instance, I_m, random_origin_vehicle, origin_position, random_destination_vehicle, destination_position)

    if not I_m.vehicles[random_origin_vehicle].getNumOfCustomersVisited():
        del I_m.vehicles[random_origin_vehicle]

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
        if not I_m.vehicles[random_origin_vehicle].getNumOfCustomersVisited():
            del I_m.vehicles[random_origin_vehicle]

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
        if not I_m.vehicles[random_origin_vehicle].getNumOfCustomersVisited():
            del I_m.vehicles[random_origin_vehicle]

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
        if not I_m.vehicles[random_origin_vehicle].getNumOfCustomersVisited():
            del I_m.vehicles[random_origin_vehicle]

    return I_m, potentialHV_TD, potentialHV_CU

def Mutation8(instance: ProblemInstance, I_m: Solution) -> Tuple[Solution, float, float]:
    potentialHV_TD, potentialHV_CU = 0.0, 0.0

    if len(I_m.vehicles) < instance.amount_of_vehicles:
        random_vehicle = get_random_vehicle(I_m, vehicles_required=2)
        origin_position = rand(1, I_m.vehicles[random_vehicle].getNumOfCustomersVisited())

        destinations = [Destination(node=instance.nodes[0]), *I_m.vehicles[random_vehicle].destinations[origin_position:-1], Destination(node=instance.nodes[0])]
        I_m.vehicles.append(Vehicle(destinations=destinations))

        if origin_position == 1:
            del I_m.vehicles[random_vehicle]
        else:
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
        num_customers = I_m.vehicles[random_vehicle].getNumOfCustomersVisited()
        origin_position = rand(1, num_customers)

        destinations = [Destination(node=instance.nodes[0]), I_m.vehicles[random_vehicle].destinations[origin_position], Destination(node=instance.nodes[0])]
        I_m.vehicles.append(Vehicle(destinations=destinations))

        if num_customers == 1:
            del I_m.vehicles[random_vehicle]
        else:
            del I_m.vehicles[random_vehicle].destinations[origin_position]

        I_m.calculate_nodes_time_windows(instance)
        I_m.calculate_vehicles_loads(instance)
        I_m.calculate_length_of_routes(instance)
        potentialHV_TD, potentialHV_CU = I_m.objective_function(instance)

    return I_m, potentialHV_TD, potentialHV_CU

def Mutation10(instance: ProblemInstance, I_m: Solution) -> Tuple[Solution, float, float]:
    potentialHV_TD, potentialHV_CU = 0.0, 0.0

    random_origin_vehicle = get_random_vehicle(I_m)

    infeasible_node_reallocations = 0
    for _ in range(1, I_m.vehicles[random_origin_vehicle].getNumOfCustomersVisited() + 1):
        origin_position = 1 + infeasible_node_reallocations
        node_reallocated = False
        destination_vehicle = 0

        while destination_vehicle < len(I_m.vehicles) and not node_reallocated:
            num_customers_destination = I_m.vehicles[destination_vehicle].getNumOfCustomersVisited()

            if not random_origin_vehicle == destination_vehicle and num_customers_destination >= 1:
                for destination_position in range(1, num_customers_destination + 1):
                    I_m, tempHV_TD, tempHV_CU = move_destination(instance, I_m, random_origin_vehicle, origin_position, destination_vehicle, destination_position)

                    if I_m.total_distance > MMOEASA_INFINITY / 2:
                        I_m, _, _ = move_destination(instance, I_m, destination_vehicle, destination_position, random_origin_vehicle, origin_position)
                    else:
                        potentialHV_TD, potentialHV_CU = compare_Hypervolumes(TD_1=potentialHV_TD, TD_2=tempHV_TD, CU_1=potentialHV_CU, CU_2=tempHV_CU)
                        node_reallocated = True
                        break
            destination_vehicle += 1
        if not node_reallocated:
            infeasible_node_reallocations += 1

    if not infeasible_node_reallocations:
        del I_m.vehicles[random_origin_vehicle]

    return I_m, potentialHV_TD, potentialHV_CU

def vehicle_insertion_possible(unvisited_nodes: Set[int], new_vehicle: Vehicle) -> Tuple[bool, Set[int]]:
    nodes_to_insert = set([d.node.number for d in new_vehicle.getCustomersVisited()])
    return len(unvisited_nodes.difference(nodes_to_insert)) == len(unvisited_nodes) - len(nodes_to_insert), nodes_to_insert

def Crossover1(instance: ProblemInstance, I_c: Solution, P: List[Solution]) -> Tuple[Solution, float, float]:
    I_c.vehicles = [v for v in I_c.vehicles if rand(1, 100) < 50]
    
    random_solution = rand(0, len(P) - 1, exclude_values=[I_c.id])

    unvisited_nodes = set(range(1, len(instance.nodes))).difference([d.node.number for v in I_c.vehicles for d in v.getCustomersVisited()])

    for i, _ in enumerate(P[random_solution].vehicles):
        if P[random_solution].vehicles[i].getNumOfCustomersVisited() >= 1:
            insertion_possible, new_nodes = vehicle_insertion_possible(unvisited_nodes, P[random_solution].vehicles[i])

            if insertion_possible and len(I_c.vehicles) < instance.amount_of_vehicles:
                I_c.vehicles.append(copy.deepcopy(P[random_solution].vehicles[i]))
                unvisited_nodes.difference_update(new_nodes)

                if not unvisited_nodes:
                    break

    for node_number in unvisited_nodes:
        I_c = insert_unvisited_node(I_c, instance, node_number)

    I_c.calculate_nodes_time_windows(instance)
    I_c.calculate_vehicles_loads(instance)
    I_c.calculate_length_of_routes(instance)
    potentialHV_TD, potentialHV_CU = I_c.objective_function(instance)

    return I_c, potentialHV_TD, potentialHV_CU

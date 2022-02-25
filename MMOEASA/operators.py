import copy
from MMOEASA.constants import INFINITY
from MMOEASA.mmoeasaSolution import MMOEASASolution
from Ombuki.ombukiSolution import OmbukiSolution
from MMOEASA.auxiliaries import insert_unvisited_node, rand
from problemInstance import ProblemInstance
from typing import List, Tuple, Set, Union
from vehicle import Vehicle

def move_destination(instance: ProblemInstance, I: Union[MMOEASASolution, OmbukiSolution], vehicle_1: int, origin: int, vehicle_2: int, destination: int) -> Union[MMOEASASolution, OmbukiSolution]:
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
    I.objective_function(instance)

    return I

def get_random_vehicle(I: Union[MMOEASASolution, OmbukiSolution], exclude_values: List[int]=None, vehicles_required: int=1) -> int:
    random_vehicle = rand(0, len(I.vehicles) - 1, exclude_values=exclude_values)
    while I.vehicles[random_vehicle].get_num_of_customers_visited() < vehicles_required:
        random_vehicle = rand(0, len(I.vehicles) - 1, exclude_values=exclude_values)
    return random_vehicle

def Mutation1(instance: ProblemInstance, I_c: Union[MMOEASASolution, OmbukiSolution]) -> Union[MMOEASASolution, OmbukiSolution]:
    random_vehicle = get_random_vehicle(I_c, vehicles_required=2)
    num_customers = I_c.vehicles[random_vehicle].get_num_of_customers_visited()
    origin_position = rand(1, num_customers)
    destination_position = rand(1, num_customers, exclude_values=[origin_position])

    I_c = move_destination(instance, I_c, random_vehicle, origin_position, random_vehicle, destination_position)

    return I_c

def Mutation2(instance: ProblemInstance, I_c: Union[MMOEASASolution, OmbukiSolution]) -> Union[MMOEASASolution, OmbukiSolution]:
    random_vehicle = get_random_vehicle(I_c, vehicles_required=2)
    num_customers = I_c.vehicles[random_vehicle].get_num_of_customers_visited()
    origin_position = rand(1, num_customers)

    best_location, fitness_of_best_location = origin_position, INFINITY
    for i in range(1, num_customers + 1):
        if not i == origin_position:
            I_c = move_destination(instance, I_c, random_vehicle, origin_position, random_vehicle, i)

            if 0 <= I_c.total_distance < fitness_of_best_location:
                fitness_of_best_location = I_c.total_distance
                best_location = i
            I_c = move_destination(instance, I_c, random_vehicle, i, random_vehicle, origin_position + 1 if origin_position > i else origin_position)

    if not best_location == origin_position:
        I_c = move_destination(instance, I_c, random_vehicle, origin_position, random_vehicle, best_location)

    return I_c

def Mutation3(instance: ProblemInstance, I_c: Union[MMOEASASolution, OmbukiSolution]) -> Union[MMOEASASolution, OmbukiSolution]:
    random_origin_vehicle = get_random_vehicle(I_c)
    origin_position = rand(1, I_c.vehicles[random_origin_vehicle].get_num_of_customers_visited())

    random_destination_vehicle = get_random_vehicle(I_c, exclude_values=[random_origin_vehicle])
    destination_position = rand(1, I_c.vehicles[random_destination_vehicle].get_num_of_customers_visited())

    I_c = move_destination(instance, I_c, random_origin_vehicle, origin_position, random_destination_vehicle, destination_position)

    if not I_c.vehicles[random_origin_vehicle].get_num_of_customers_visited():
        del I_c.vehicles[random_origin_vehicle]

    return I_c

def Mutation4(instance: ProblemInstance, I_c: Union[MMOEASASolution, OmbukiSolution]) -> Union[MMOEASASolution, OmbukiSolution]:
    random_origin_vehicle = get_random_vehicle(I_c)
    origin_position = rand(1, I_c.vehicles[random_origin_vehicle].get_num_of_customers_visited())

    random_destination_vehicle = get_random_vehicle(I_c, exclude_values=[random_origin_vehicle])

    best_location, fitness_of_best_location = -1, INFINITY
    for i in range(1, I_c.vehicles[random_destination_vehicle].get_num_of_customers_visited() + 1):
        I_c = move_destination(instance, I_c, random_origin_vehicle, origin_position, random_destination_vehicle, i)

        if 0 <= I_c.total_distance < fitness_of_best_location:
            fitness_of_best_location = I_c.total_distance
            best_location = i
        I_c = move_destination(instance, I_c, random_destination_vehicle, i, random_origin_vehicle, origin_position)

    if best_location >= 0:
        I_c = move_destination(instance, I_c, random_origin_vehicle, origin_position, random_destination_vehicle, best_location)
        if not I_c.vehicles[random_origin_vehicle].get_num_of_customers_visited():
            del I_c.vehicles[random_origin_vehicle]

    return I_c

def Mutation5(instance: ProblemInstance, I_c: Union[MMOEASASolution, OmbukiSolution]) -> Union[MMOEASASolution, OmbukiSolution]:
    random_origin_vehicle = get_random_vehicle(I_c)
    origin_position = rand(1, I_c.vehicles[random_origin_vehicle].get_num_of_customers_visited())

    random_destination_vehicle = get_random_vehicle(I_c, exclude_values=[random_origin_vehicle])
    destination_position = rand(1, I_c.vehicles[random_destination_vehicle].get_num_of_customers_visited())

    I_c = move_destination(instance, I_c, random_origin_vehicle, origin_position, random_destination_vehicle, destination_position)
    I_c = move_destination(instance, I_c, random_destination_vehicle, destination_position + 1, random_origin_vehicle, origin_position)

    return I_c

def Mutation6(instance: ProblemInstance, I_c: Union[MMOEASASolution, OmbukiSolution]) -> Union[MMOEASASolution, OmbukiSolution]:
    random_origin_vehicle = get_random_vehicle(I_c)
    origin_position = rand(1, I_c.vehicles[random_origin_vehicle].get_num_of_customers_visited())

    best_vehicle, best_location, fitness_of_best_location = -1, -1, INFINITY
    for destination_vehicle in range(0, len(I_c.vehicles)):
        if not random_origin_vehicle == destination_vehicle:
            num_customers = I_c.vehicles[destination_vehicle].get_num_of_customers_visited()

            if num_customers > 0:
                for i in range(1, num_customers + 1):
                    I_c = move_destination(instance, I_c, random_origin_vehicle, origin_position, destination_vehicle, i)

                    if 0 <= I_c.total_distance < fitness_of_best_location:
                        fitness_of_best_location = I_c.total_distance
                        best_vehicle = destination_vehicle
                        best_location = i
                    I_c = move_destination(instance, I_c, destination_vehicle, i, random_origin_vehicle, origin_position)

    if best_location >= 0:
        I_c = move_destination(instance, I_c, random_origin_vehicle, origin_position, best_vehicle, best_location)
        if not I_c.vehicles[random_origin_vehicle].get_num_of_customers_visited():
            del I_c.vehicles[random_origin_vehicle]

    return I_c

def Mutation7(instance: ProblemInstance, I_c: Union[MMOEASASolution, OmbukiSolution]) -> Union[MMOEASASolution, OmbukiSolution]:
    random_origin_vehicle = get_random_vehicle(I_c)
    origin_position = rand(1, I_c.vehicles[random_origin_vehicle].get_num_of_customers_visited())

    best_vehicle, best_location, smallest_time_window_difference = -1, -1, INFINITY
    for destination_vehicle in range(0, len(I_c.vehicles)):
        if not random_origin_vehicle == destination_vehicle:
            num_customers = I_c.vehicles[destination_vehicle].get_num_of_customers_visited()

            if num_customers > 0:
                for i in range(1, num_customers + 2): # TODO: MMOEASA does +2 to include the depot-return node in this mutation; is this correct and does it work?
                    I_c = move_destination(instance, I_c, random_origin_vehicle, origin_position, destination_vehicle, i)
                    time_window_difference = abs(I_c.vehicles[random_origin_vehicle].destinations[origin_position].arrival_time - I_c.vehicles[destination_vehicle].destinations[i].arrival_time)

                    if I_c.total_distance >= 0 and time_window_difference < smallest_time_window_difference:
                        smallest_time_window_difference = time_window_difference
                        best_vehicle = destination_vehicle
                        best_location = i
                    I_c = move_destination(instance, I_c, destination_vehicle, i, random_origin_vehicle, origin_position)

    if best_location >= 0:
        I_c = move_destination(instance, I_c, random_origin_vehicle, origin_position, best_vehicle, best_location)
        if not I_c.vehicles[random_origin_vehicle].get_num_of_customers_visited():
            del I_c.vehicles[random_origin_vehicle]

    return I_c

def Mutation8(instance: ProblemInstance, I_c: Union[MMOEASASolution, OmbukiSolution]) -> Union[MMOEASASolution, OmbukiSolution]:
    if len(I_c.vehicles) < instance.amount_of_vehicles:
        random_vehicle = get_random_vehicle(I_c, vehicles_required=2)
        origin_position = rand(1, I_c.vehicles[random_vehicle].get_num_of_customers_visited())

        I_c.vehicles.append(Vehicle.create_route(instance, I_c.vehicles[random_vehicle].destinations[origin_position:-1]))

        if origin_position == 1:
            del I_c.vehicles[random_vehicle]
        else:
            del I_c.vehicles[random_vehicle].destinations[origin_position:-1]

        I_c.calculate_nodes_time_windows(instance)
        I_c.calculate_vehicles_loads(instance)
        I_c.calculate_length_of_routes(instance)
        I_c.objective_function(instance)

    return I_c

def Mutation9(instance: ProblemInstance, I_c: Union[MMOEASASolution, OmbukiSolution]) -> Union[MMOEASASolution, OmbukiSolution]:
    if len(I_c.vehicles) < instance.amount_of_vehicles:
        random_vehicle = get_random_vehicle(I_c, vehicles_required=2)
        num_customers = I_c.vehicles[random_vehicle].get_num_of_customers_visited()
        origin_position = rand(1, num_customers)

        I_c.vehicles.append(Vehicle.create_route(instance, I_c.vehicles[random_vehicle].destinations[origin_position].node))

        if num_customers == 1:
            del I_c.vehicles[random_vehicle]
        else:
            del I_c.vehicles[random_vehicle].destinations[origin_position]

        I_c.calculate_nodes_time_windows(instance)
        I_c.calculate_vehicles_loads(instance)
        I_c.calculate_length_of_routes(instance)
        I_c.objective_function(instance)

    return I_c

def Mutation10(instance: ProblemInstance, I_c: Union[MMOEASASolution, OmbukiSolution]) -> Union[MMOEASASolution, OmbukiSolution]:
    random_origin_vehicle = get_random_vehicle(I_c)

    infeasible_node_reallocations = 0
    for _ in range(1, I_c.vehicles[random_origin_vehicle].get_num_of_customers_visited() + 1):
        origin_position = 1 + infeasible_node_reallocations
        node_reallocated = False
        destination_vehicle = 0

        while destination_vehicle < len(I_c.vehicles) and not node_reallocated:
            num_customers_destination = I_c.vehicles[destination_vehicle].get_num_of_customers_visited()

            if not random_origin_vehicle == destination_vehicle and num_customers_destination >= 1:
                for destination_position in range(1, num_customers_destination + 1):
                    I_c = move_destination(instance, I_c, random_origin_vehicle, origin_position, destination_vehicle, destination_position)

                    if I_c.total_distance > INFINITY / 2:
                        I_c = move_destination(instance, I_c, destination_vehicle, destination_position, random_origin_vehicle, origin_position)
                    else:
                        node_reallocated = True
                        break
            destination_vehicle += 1
        if not node_reallocated:
            infeasible_node_reallocations += 1

    if not infeasible_node_reallocations:
        del I_c.vehicles[random_origin_vehicle]

    return I_c

def vehicle_insertion_possible(unvisited_nodes: Set[int], new_vehicle: Vehicle) -> Tuple[bool, Set[int]]:
    nodes_to_insert = set([d.node.number for d in new_vehicle.get_customers_visited()])
    return len(unvisited_nodes.difference(nodes_to_insert)) == len(unvisited_nodes) - len(nodes_to_insert), nodes_to_insert

def Crossover1(instance: ProblemInstance, I_c: Union[MMOEASASolution, OmbukiSolution], P: List[Union[MMOEASASolution, OmbukiSolution]]) -> Union[MMOEASASolution, OmbukiSolution]:
    I_c.vehicles = [v for v in I_c.vehicles if rand(1, 100) < 50]
    
    random_solution = rand(0, len(P) - 1, exclude_values=[I_c.id])

    unvisited_nodes = set(range(1, len(instance.nodes))).difference([d.node.number for v in I_c.vehicles for d in v.get_customers_visited()])

    for i, _ in enumerate(P[random_solution].vehicles):
        if P[random_solution].vehicles[i].get_num_of_customers_visited() >= 1:
            insertion_possible, new_nodes = vehicle_insertion_possible(unvisited_nodes, P[random_solution].vehicles[i])

            if insertion_possible and len(I_c.vehicles) < instance.amount_of_vehicles:
                I_c.vehicles.append(copy.deepcopy(P[random_solution].vehicles[i]))
                unvisited_nodes.difference_update(new_nodes)

                if not unvisited_nodes:
                    break

    for node_number in unvisited_nodes:
        I_c = insert_unvisited_node(I_c, instance, node_number)

    """ these commented-out calculations shouldn't be needed as "insert_unvisited_node" does them
    even if "insert_unvisited_node" isn't used, they aren't needed as the for loop above will be inserting vehicles with these values already calculated
    
    I_c.calculate_nodes_time_windows(instance)
    I_c.calculate_vehicles_loads(instance)
    I_c.calculate_length_of_routes(instance)"""
    I_c.objective_function(instance)

    return I_c

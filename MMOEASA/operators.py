import copy
from MMOEASA.constants import INFINITY
from MMOEASA.mmoeasaSolution import MMOEASASolution
from Ombuki.ombukiSolution import OmbukiSolution
from MMOEASA.auxiliaries import insert_unvisited_node
from common import rand
from problemInstance import ProblemInstance
from typing import List, Tuple, Set, Union
from vehicle import Vehicle

def move_destination(instance: ProblemInstance, solution: Union[MMOEASASolution, OmbukiSolution], vehicle_1: int, origin: int, vehicle_2: int, destination: int) -> Union[MMOEASASolution, OmbukiSolution]:
    origin_node = solution.vehicles[vehicle_1].destinations[origin]

    if vehicle_1 == vehicle_2:
        omd_absolute = abs(origin - destination)

        if omd_absolute == 1:
            solution.vehicles[vehicle_1].destinations[origin] = solution.vehicles[vehicle_2].destinations[destination]
            solution.vehicles[vehicle_2].destinations[destination] = origin_node
        elif omd_absolute > 1:
            solution.vehicles[vehicle_2].destinations.insert(destination, origin_node)
            del solution.vehicles[vehicle_1].destinations[origin + 1 if origin > destination else origin]
    else:
        solution.vehicles[vehicle_2].destinations.insert(destination, origin_node)
        del solution.vehicles[vehicle_1].destinations[origin]

    solution.calculate_nodes_time_windows(instance)
    solution.calculate_vehicles_loads(instance)
    solution.calculate_length_of_routes(instance)
    solution.objective_function(instance)

    return solution

def get_random_vehicle(solution: Union[MMOEASASolution, OmbukiSolution], exclude_values: Set[int]=None, vehicles_required: int=1) -> int:
    random_vehicle = rand(0, len(solution.vehicles) - 1, exclude_values=exclude_values)
    while solution.vehicles[random_vehicle].get_num_of_customers_visited() < vehicles_required:
        random_vehicle = rand(0, len(solution.vehicles) - 1, exclude_values=exclude_values)
    return random_vehicle

def mutation1(instance: ProblemInstance, solution: Union[MMOEASASolution, OmbukiSolution]) -> Union[MMOEASASolution, OmbukiSolution]:
    random_vehicle = get_random_vehicle(solution, vehicles_required=2)
    num_customers = solution.vehicles[random_vehicle].get_num_of_customers_visited()
    origin_position = rand(1, num_customers)
    destination_position = rand(1, num_customers, exclude_values={origin_position})

    solution = move_destination(instance, solution, random_vehicle, origin_position, random_vehicle, destination_position)

    return solution

def mutation2(instance: ProblemInstance, solution: Union[MMOEASASolution, OmbukiSolution]) -> Union[MMOEASASolution, OmbukiSolution]:
    random_vehicle = get_random_vehicle(solution, vehicles_required=2)
    num_customers = solution.vehicles[random_vehicle].get_num_of_customers_visited()
    origin_position = rand(1, num_customers)

    best_location, fitness_of_best_location = origin_position, INFINITY
    for i in range(1, num_customers + 1):
        if not i == origin_position:
            solution = move_destination(instance, solution, random_vehicle, origin_position, random_vehicle, i)

            if 0 <= solution.total_distance < fitness_of_best_location:
                fitness_of_best_location = solution.total_distance
                best_location = i
            solution = move_destination(instance, solution, random_vehicle, i, random_vehicle, origin_position + 1 if origin_position > i else origin_position)

    if not best_location == origin_position:
        solution = move_destination(instance, solution, random_vehicle, origin_position, random_vehicle, best_location)

    return solution

def mutation3(instance: ProblemInstance, solution: Union[MMOEASASolution, OmbukiSolution]) -> Union[MMOEASASolution, OmbukiSolution]:
    random_origin_vehicle = get_random_vehicle(solution)
    origin_position = rand(1, solution.vehicles[random_origin_vehicle].get_num_of_customers_visited())

    random_destination_vehicle = get_random_vehicle(solution, exclude_values={random_origin_vehicle})
    destination_position = rand(1, solution.vehicles[random_destination_vehicle].get_num_of_customers_visited())

    solution = move_destination(instance, solution, random_origin_vehicle, origin_position, random_destination_vehicle, destination_position)

    if not solution.vehicles[random_origin_vehicle].get_num_of_customers_visited():
        del solution.vehicles[random_origin_vehicle]

    return solution

def mutation4(instance: ProblemInstance, solution: Union[MMOEASASolution, OmbukiSolution]) -> Union[MMOEASASolution, OmbukiSolution]:
    random_origin_vehicle = get_random_vehicle(solution)
    origin_position = rand(1, solution.vehicles[random_origin_vehicle].get_num_of_customers_visited())

    random_destination_vehicle = get_random_vehicle(solution, exclude_values={random_origin_vehicle})

    best_location, fitness_of_best_location = -1, INFINITY
    for i in range(1, solution.vehicles[random_destination_vehicle].get_num_of_customers_visited() + 1):
        solution = move_destination(instance, solution, random_origin_vehicle, origin_position, random_destination_vehicle, i)

        if 0 <= solution.total_distance < fitness_of_best_location:
            fitness_of_best_location = solution.total_distance
            best_location = i
        solution = move_destination(instance, solution, random_destination_vehicle, i, random_origin_vehicle, origin_position)

    if best_location >= 0:
        solution = move_destination(instance, solution, random_origin_vehicle, origin_position, random_destination_vehicle, best_location)
        if not solution.vehicles[random_origin_vehicle].get_num_of_customers_visited():
            del solution.vehicles[random_origin_vehicle]

    return solution

def mutation5(instance: ProblemInstance, solution: Union[MMOEASASolution, OmbukiSolution]) -> Union[MMOEASASolution, OmbukiSolution]:
    random_origin_vehicle = get_random_vehicle(solution)
    origin_position = rand(1, solution.vehicles[random_origin_vehicle].get_num_of_customers_visited())

    random_destination_vehicle = get_random_vehicle(solution, exclude_values={random_origin_vehicle})
    destination_position = rand(1, solution.vehicles[random_destination_vehicle].get_num_of_customers_visited())

    solution = move_destination(instance, solution, random_origin_vehicle, origin_position, random_destination_vehicle, destination_position)
    solution = move_destination(instance, solution, random_destination_vehicle, destination_position + 1, random_origin_vehicle, origin_position)

    return solution

def mutation6(instance: ProblemInstance, solution: Union[MMOEASASolution, OmbukiSolution]) -> Union[MMOEASASolution, OmbukiSolution]:
    random_origin_vehicle = get_random_vehicle(solution)
    origin_position = rand(1, solution.vehicles[random_origin_vehicle].get_num_of_customers_visited())

    best_vehicle, best_location, fitness_of_best_location = -1, -1, INFINITY
    for destination_vehicle in range(0, len(solution.vehicles)):
        if not random_origin_vehicle == destination_vehicle:
            num_customers = solution.vehicles[destination_vehicle].get_num_of_customers_visited()

            if num_customers > 0:
                for i in range(1, num_customers + 1):
                    solution = move_destination(instance, solution, random_origin_vehicle, origin_position, destination_vehicle, i)

                    if 0 <= solution.total_distance < fitness_of_best_location:
                        fitness_of_best_location = solution.total_distance
                        best_vehicle = destination_vehicle
                        best_location = i
                    solution = move_destination(instance, solution, destination_vehicle, i, random_origin_vehicle, origin_position)

    if best_location >= 0:
        solution = move_destination(instance, solution, random_origin_vehicle, origin_position, best_vehicle, best_location)
        if not solution.vehicles[random_origin_vehicle].get_num_of_customers_visited():
            del solution.vehicles[random_origin_vehicle]

    return solution

def mutation7(instance: ProblemInstance, solution: Union[MMOEASASolution, OmbukiSolution]) -> Union[MMOEASASolution, OmbukiSolution]:
    random_origin_vehicle = get_random_vehicle(solution)
    origin_position = rand(1, solution.vehicles[random_origin_vehicle].get_num_of_customers_visited())

    best_vehicle, best_location, smallest_time_window_difference = -1, -1, INFINITY
    for destination_vehicle in range(0, len(solution.vehicles)):
        if not random_origin_vehicle == destination_vehicle:
            num_customers = solution.vehicles[destination_vehicle].get_num_of_customers_visited()

            if num_customers > 0:
                for i in range(1, num_customers + 2): # TODO: MMOEASA does +2 to include the depot-return node in this mutation; is this correct and does it work?
                    solution = move_destination(instance, solution, random_origin_vehicle, origin_position, destination_vehicle, i)
                    time_window_difference = abs(solution.vehicles[random_origin_vehicle].destinations[origin_position].arrival_time - solution.vehicles[destination_vehicle].destinations[i].arrival_time)

                    if solution.total_distance >= 0 and time_window_difference < smallest_time_window_difference:
                        smallest_time_window_difference = time_window_difference
                        best_vehicle = destination_vehicle
                        best_location = i
                    solution = move_destination(instance, solution, destination_vehicle, i, random_origin_vehicle, origin_position)

    if best_location >= 0:
        solution = move_destination(instance, solution, random_origin_vehicle, origin_position, best_vehicle, best_location)
        if not solution.vehicles[random_origin_vehicle].get_num_of_customers_visited():
            del solution.vehicles[random_origin_vehicle]

    return solution

def mutation8(instance: ProblemInstance, solution: Union[MMOEASASolution, OmbukiSolution]) -> Union[MMOEASASolution, OmbukiSolution]:
    if len(solution.vehicles) < instance.amount_of_vehicles:
        random_vehicle = get_random_vehicle(solution, vehicles_required=2)
        origin_position = rand(1, solution.vehicles[random_vehicle].get_num_of_customers_visited())

        solution.vehicles.append(Vehicle.create_route(instance, solution.vehicles[random_vehicle].destinations[origin_position:-1]))

        if origin_position == 1:
            del solution.vehicles[random_vehicle]
        else:
            del solution.vehicles[random_vehicle].destinations[origin_position:-1]

        solution.calculate_nodes_time_windows(instance)
        solution.calculate_vehicles_loads(instance)
        solution.calculate_length_of_routes(instance)
        solution.objective_function(instance)

    return solution

def mutation9(instance: ProblemInstance, solution: Union[MMOEASASolution, OmbukiSolution]) -> Union[MMOEASASolution, OmbukiSolution]:
    if len(solution.vehicles) < instance.amount_of_vehicles:
        random_vehicle = get_random_vehicle(solution, vehicles_required=2)
        num_customers = solution.vehicles[random_vehicle].get_num_of_customers_visited()
        origin_position = rand(1, num_customers)

        solution.vehicles.append(Vehicle.create_route(instance, solution.vehicles[random_vehicle].destinations[origin_position].node))

        if num_customers == 1:
            del solution.vehicles[random_vehicle]
        else:
            del solution.vehicles[random_vehicle].destinations[origin_position]

        solution.calculate_nodes_time_windows(instance)
        solution.calculate_vehicles_loads(instance)
        solution.calculate_length_of_routes(instance)
        solution.objective_function(instance)

    return solution

def mutation10(instance: ProblemInstance, solution: Union[MMOEASASolution, OmbukiSolution]) -> Union[MMOEASASolution, OmbukiSolution]:
    random_origin_vehicle = get_random_vehicle(solution)

    infeasible_node_reallocations = 0
    for _ in range(1, solution.vehicles[random_origin_vehicle].get_num_of_customers_visited() + 1):
        origin_position = 1 + infeasible_node_reallocations
        node_reallocated = False
        destination_vehicle = 0

        while destination_vehicle < len(solution.vehicles) and not node_reallocated:
            num_customers_destination = solution.vehicles[destination_vehicle].get_num_of_customers_visited()

            if not random_origin_vehicle == destination_vehicle and num_customers_destination >= 1:
                for destination_position in range(1, num_customers_destination + 1):
                    solution = move_destination(instance, solution, random_origin_vehicle, origin_position, destination_vehicle, destination_position)

                    if solution.total_distance > INFINITY / 2:
                        solution = move_destination(instance, solution, destination_vehicle, destination_position, random_origin_vehicle, origin_position)
                    else:
                        node_reallocated = True
                        break
            destination_vehicle += 1
        if not node_reallocated:
            infeasible_node_reallocations += 1

    if not infeasible_node_reallocations:
        del solution.vehicles[random_origin_vehicle]

    return solution

def vehicle_insertion_possible(unvisited_nodes: Set[int], new_vehicle: Vehicle) -> Tuple[bool, Set[int]]:
    nodes_to_insert = set([d.node.number for d in new_vehicle.get_customers_visited()])
    return len(unvisited_nodes.difference(nodes_to_insert)) == len(unvisited_nodes) - len(nodes_to_insert), nodes_to_insert

def crossover1(instance: ProblemInstance, solution: Union[MMOEASASolution, OmbukiSolution], P: List[Union[MMOEASASolution, OmbukiSolution]]) -> Union[MMOEASASolution, OmbukiSolution]:
    solution.vehicles = [v for v in solution.vehicles if rand(1, 100) < 50]
    
    random_solution = rand(0, len(P) - 1, exclude_values={solution.id})

    unvisited_nodes = set(range(1, len(instance.nodes))).difference([d.node.number for v in solution.vehicles for d in v.get_customers_visited()])

    for i, _ in enumerate(P[random_solution].vehicles):
        if P[random_solution].vehicles[i].get_num_of_customers_visited() >= 1:
            insertion_possible, new_nodes = vehicle_insertion_possible(unvisited_nodes, P[random_solution].vehicles[i])

            if insertion_possible and len(solution.vehicles) < instance.amount_of_vehicles:
                solution.vehicles.append(copy.deepcopy(P[random_solution].vehicles[i]))
                unvisited_nodes.difference_update(new_nodes)

                if not unvisited_nodes:
                    break

    for node_number in unvisited_nodes:
        solution = insert_unvisited_node(solution, instance, node_number)

    """ these commented-out calculations shouldn't be needed as "insert_unvisited_node" does them
    even if "insert_unvisited_node" isn't used, they aren't needed as the for loop above will be inserting vehicles with these values already calculated
    
    solution.calculate_nodes_time_windows(instance)
    solution.calculate_vehicles_loads(instance)
    solution.calculate_length_of_routes(instance)"""
    solution.objective_function(instance)

    return solution

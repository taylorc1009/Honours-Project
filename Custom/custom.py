from typing import List
from destination import Destination
from problemInstance import ProblemInstance
from Custom.customSolution import CustomSolution
from vehicle import Vehicle
from numpy import ceil

def DTWIH(instance: ProblemInstance) -> CustomSolution:
    sorted_nodes = sorted([node for _, node in instance.nodes.items() if node.number], key=lambda n: n.ready_time)
    num_routes = int(ceil(instance.amount_of_vehicles / 2))
    solution = CustomSolution(_id=0, vehicles=[Vehicle.create_route(instance) for _ in range(0, num_routes)])
    additional_vehicles = 0

    for offset in range(0, num_routes):
        range_of_sorted_nodes = num_routes if num_routes < len(sorted_nodes) else len(sorted_nodes)
        for i in range(0, range_of_sorted_nodes):
            if solution.vehicles[i].current_capacity + sorted_nodes[i].demand <= instance.capacity_of_vehicles:
                solution.vehicles[i].destinations.insert(offset + 1, Destination(node=sorted_nodes[i]))
                solution.vehicles[i].current_capacity += sorted_nodes[i].demand
            else:
                # TODO: try picking the best location in an existing vehicle?
                index = (num_routes - 1) + additional_vehicles
                if solution.vehicles[index].current_capacity + sorted_nodes[i].demand > instance.capacity_of_vehicles:
                    solution.vehicles.append(Vehicle.create_route(instance, sorted_nodes[i]))
                    additional_vehicles += 1
                else:
                    solution.vehicles[index].destinations.insert(len(solution.vehicles[index].destinations), Destination(node=sorted_nodes[i]))
        del sorted_nodes[:num_routes]

    solution.calculate_nodes_time_windows(instance)
    solution.calculate_length_of_routes(instance)
    solution.objective_function(instance)

    return solution

def Custom(instance: ProblemInstance, population_size: int, termination_condition: int, crossover_probability: int, mutation_probability: int) -> List[CustomSolution]:
    nondominated_set: List[CustomSolution] = list()

    DTWIH_solution = DTWIH(instance)

    return nondominated_set
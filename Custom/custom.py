import copy
from typing import List
from common import rand
from destination import Destination
from problemInstance import ProblemInstance
from Custom.customSolution import CustomSolution
from Custom.operators import crossover, mutation
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

def try_crossover(instance, parent_one: CustomSolution, parent_two: CustomSolution, crossover_probability) -> CustomSolution:
    if rand(1, 100) < crossover_probability:
        return crossover(instance, parent_one, parent_two.vehicles[rand(0, len(parent_two.vehicles) - 1)])
    return parent_one

def try_mutation(instance, solution: CustomSolution, mutation_probability: int) -> CustomSolution:
    if rand(1, 100) < mutation_probability:
        return mutation(instance, solution)
    return solution

def Custom(instance: ProblemInstance, population_size: int, termination_condition: int, crossover_probability: int, mutation_probability: int) -> List[CustomSolution]:
    population: List[CustomSolution] = list()

    DTWIH_solution = DTWIH(instance)
    for i in range(0, population_size):
        population.insert(i, copy.deepcopy(DTWIH_solution))
        population[i].id = i

    for i in range(termination_condition):
        for solution in population:
            child = try_crossover(instance, solution, None, crossover_probability)
            child = try_mutation(instance, solution, mutation_probability)

    return
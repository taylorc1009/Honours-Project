import random
from typing import List
from problemInstance import ProblemInstance
from Ombuki.solution import Solution
from vehicle import Vehicle
from destination import Destination
from Ombuki.auxiliaries import rand
from numpy import arange, round
from Ombuki.constants import INT_MAX

def generate_random_solution(instance: ProblemInstance) -> Solution:
    solution = Solution(_id=0, vehicles=list())

    for i in arange(1, len(instance.nodes)):
        infeasible_vehicles = set()
        inserted = False
        while not inserted:
            vehicle = rand(0, instance.amount_of_vehicles - 1, exclude_values=infeasible_vehicles) # generate a random number between 1 and max vehicles instead of 1 to current num of vehicles; to keep the original probability of inserting the node to a new vehicle
            if vehicle < len(solution.vehicles) and solution.vehicles[vehicle].current_capacity + instance.nodes[i].demand <= instance.capacity_of_vehicles:
                solution.vehicles[vehicle].destinations.append(Destination(node=instance.nodes[i]))
                solution.vehicles[vehicle].current_capacity += instance.nodes[i].demand
                inserted = True
            elif len(infeasible_vehicles) == len(solution.vehicles):
                solution.vehicles.append(Vehicle(destinations=[Destination(node=instance.nodes[i])]))
                solution.vehicles[-1].current_capacity = instance.nodes[i].demand
                inserted = True
            else:
                infeasible_vehicles.add(vehicle)

    return solution

def generate_greedy_solution(instance: ProblemInstance) -> Solution:
    solution = Solution(_id=0, vehicles=[Vehicle(destinations=list())])
    unvisited_nodes = list(arange(1, len(instance.nodes)))
    vehicle = 0

    while unvisited_nodes:
        node = random.sample(unvisited_nodes, 1)[0]
        destination = Destination(node=instance.nodes[node])
        solution.vehicles[vehicle].destinations.append(destination)
        unvisited_nodes.remove(node)

        while not solution.vehicles[vehicle].current_capacity > instance.capacity_of_vehicles:
            closest_node = None
            distance_of_closest = float(INT_MAX)
            for node in unvisited_nodes:
                distance = destination.node.get_distance(instance.nodes[node])
                if distance < distance_of_closest:
                    closest_node = node
                    distance_of_closest = distance
            if closest_node and not solution.vehicles[vehicle].current_capacity + instance.nodes[closest_node].demand > instance.capacity_of_vehicles:
                solution.vehicles[vehicle].destinations.append(Destination(node=instance.nodes[closest_node]))
                solution.vehicles[vehicle].current_capacity += instance.nodes[closest_node].demand
                unvisited_nodes.remove(closest_node)
            else:
                if closest_node:
                    vehicle += 1
                    solution.vehicles.append(Vehicle(destinations=list()))
                break

    return solution

def Ombuki(instance: ProblemInstance, population_size: int, span: int, crossover: float, mutation: float) -> List[Solution]:
    P: List[Solution] = list()
    ND: List[Solution] = list()

    num_greedy_solutions = round(float(population_size * 0.1))
    for i in arange(0, num_greedy_solutions).astype(int):
        greedy_solution = generate_greedy_solution(instance)
        greedy_solution.id = i
        P.insert(i, greedy_solution)
    for i in arange(num_greedy_solutions, population_size).astype(int):
        random_solution = generate_random_solution(instance)
        random_solution.id = i
        P.insert(i, random_solution)

    return ND

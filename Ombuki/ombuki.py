from typing import List
from numpy import ceil
from problemInstance import ProblemInstance
from solution import Solution
from auxiliaries import rand

def generate_initial_solution(instance: ProblemInstance) -> Solution:
    num_nodes = len(instance.nodes) - 1
    num_greedy_nodes = ceil(float(num_nodes * 0.1))
    num_random_nodes = num_nodes - num_greedy_nodes

    greedy_nodes = set()
    for _ in range(0, num_greedy_nodes):
        greedy_nodes.add(instance.nodes[rand(1, num_nodes + 1, exclude_values=greedy_nodes)].number)

    for i in range(1, num_nodes + 2):
        if i in greedy_nodes:
            # do greedy procedure
            pass
        else:
            vehicle = rand(1, instance.amount_of_vehicles)

def Ombuki(instance: ProblemInstance, p: int, span: int, crossover: float, mutation: float) -> List[Solution]:
    P: List[Solution] = list()
    ND: List[Solution] = list()

    initial_solution = generate_initial_solution(instance)

    return ND
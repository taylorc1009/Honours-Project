import copy
from destination import Destination
from typing import List, Dict, Union
from problemInstance import ProblemInstance
from node import Node

class Vehicle:
    def __init__(self, current_capacity: int=0, destinations: List[Destination]=None, route_distance: float=0.0) -> None:
        self.current_capacity: int=int(current_capacity)
        self.destinations: List[Destination]=destinations
        self.route_distance: float=float(route_distance)

    def __str__(self) -> str:
        return f"Vehicle(current_capacity={self.current_capacity}, route_distance={self.route_distance}, {len(self.destinations)=}, {[(i, str(d)) for i, d in enumerate(self.destinations)]})"

    def get_customers_visited(self) -> List[Destination]:
        return self.destinations[1:-1] # to do this, we assume that every depot departure and return is initialised correctly (at index 0 and n - 1) which we can do as any route that isn't in this format is incorrect
        #return list(filter(lambda d: (d.node.number != 0), self.destinations)) # this is an alternative to hoping that the list of destinations begins and ends at 0

    def get_num_of_customers_visited(self) -> int:
        return len(self.destinations) - 2 # to do this, we assume that every depot departure and return is initialised correctly (at index 0 and n - 1) which we can do as any route that isn't in this format is incorrect
        #return len(list(filter(lambda d: (d.node.number != 0), self.destinations))) # this is an alternative to hoping that the list of destinations begins and ends at 0

    # TODO: you probably don't need to give these methods the problem instance as each Node object holds the values you're looking for (such as the "ready_time") and they're all in "self.destinations"
    def calculate_destinations_time_windows(self, instance: ProblemInstance) -> None:
        for i in range(1, len(self.destinations)):
            previous_node = self.destinations[i - 1].node.number
            current_node = self.destinations[i].node.number
            self.destinations[i].arrival_time = self.destinations[i - 1].departure_time + instance.MMOEASA_distances[previous_node][current_node]
            if self.destinations[i].arrival_time < instance.nodes[current_node].ready_time: # if the vehicle arrives before "ready_time" then it will have to wait for that moment before serving the node
                self.destinations[i].wait_time = instance.nodes[current_node].ready_time - self.destinations[i].arrival_time
                self.destinations[i].arrival_time = instance.nodes[current_node].ready_time
            else:
                self.destinations[i].wait_time = 0.0
            self.destinations[i].departure_time = self.destinations[i].arrival_time + instance.nodes[current_node].service_duration

    def calculate_vehicle_load(self, instance: ProblemInstance):
        temporary_capacity = 0.0
        for i in range(1, len(self.destinations) - 1):
            node_number = self.destinations[i].node.number
            temporary_capacity += instance.nodes[node_number].demand
        self.current_capacity = temporary_capacity

    def calculate_length_of_route(self, instance: ProblemInstance):
        temporary_distance = 0.0
        for i in range(1, len(self.destinations)):
            previous_node = self.destinations[i - 1].node.number
            current_node = self.destinations[i].node.number
            temporary_distance += instance.MMOEASA_distances[previous_node][current_node]
        self.route_distance = temporary_distance

    def __deepcopy__(self, memodict: Dict=None):
        return Vehicle(current_capacity=self.current_capacity, route_distance=self.route_distance, destinations=[copy.deepcopy(d) for d in self.destinations])

    @classmethod
    def create(cls, instance: ProblemInstance, node: Union[Node, List[Node]]=None):
        destinations = [Destination(node=node) for node in node] if isinstance(node, list) else [Destination(node=node)]
        return cls(destinations=[instance.nodes[0], *destinations, instance.nodes[0]])

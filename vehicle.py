from destination import Destination
from typing import List
from problemInstance import ProblemInstance

class Vehicle():
    route_distance: float=None
    
    def __init__(self, number: int, current_capacity: int=0, destinations: List[Destination]=list()) -> None:
        #self.number: int=number
        self.current_capacity: int=current_capacity
        self.destinations: List[Destination]=destinations

    def __str__(self) -> str:
        return f"{self.current_capacity}, {[destination.node.number for destination in self.destinations]}"

    def getNumOfCustomersVisited(self) -> int:
        return len(list(filter(lambda d: (d.node.number != 0), self.destinations)))
    
    def getIndexOfNode(self, node_number: int) -> int:
        for i, d in enumerate(self.destinations):
            if d.node.number == node_number:
                return i
        return None
        #return next(filter(lambda d: (d.node.number == node_number), self.destinations), 0) # does this work and is it better than the for loop above?

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

    """ this funcion is supposed to change "assignedVehicle" of every destination in "self.destinations" to "None", which would allow for quicker calculations of unvisited nodes, but this is very hard to track
    def clearAssignedDestinations(self) -> None:
        for i in enumerate(self.destinations):
            self.destinations[i].assignedVehicle = None
        self.destinations.clear()"""
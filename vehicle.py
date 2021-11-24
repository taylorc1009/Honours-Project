from destination import Destination
from typing import List

class Vehicle():
    route_distance: float=None
    
    def __init__(self, number: int, current_capacity: int=0, destinations: List[Destination]=list()) -> None:
        self.number: int=number
        self.current_capacity: int=current_capacity
        self.destinations: List[Destination]=destinations

    def __str__(self) -> str:
        return f"{self.number}, {self.current_capacity}, {[destination.node.number for destination in self.destinations]}"
    
    def getIndexOfDestinationByNode(self, node_number: int) -> int:
        #for i, d in enumerate(self.destinations):
            #if d.number == destination:
                #return i

        return next(filter(lambda d: (d.node.number == node_number), self.destinations), None) # does this work and is it better than the for loop above?

    """ this funcion is supposed to change "assignedVehicle" of every destination in "self.destinations" to "None", which would allow for quicker calculations of unvisited nodes, but this is very hard to track
    def clearAssignedDestinations(self) -> None:
        for i in enumerate(self.destinations):
            self.destinations[i].assignedVehicle = None
        self.destinations.clear()"""
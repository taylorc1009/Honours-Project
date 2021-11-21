from destination import Destination
from typing import List

class Vehicle():
    route_distance: float=None
    
    def __init__(self, number: int, current_capacity: int=0, destinations: List[Destination]=list()) -> None:
        self.number: int=number
        self.current_capacity: int=current_capacity
        self.destinations: List[Destination]=destinations

    def __str__(self) -> str:
        return f"{self.number}, {self.max_capacity}, {self.current_capacity}, {[destination.node.number for destination in self.destinations]}"
    
    def getIndexOfDestination(self, destination: int) -> int:
        #for i, d in enumerate(self.destinations):
            #if d.number == destination:
                #return i

        if filter(lambda d: (d.number == destination), self.destinations): # does this work and is it better than the for loop above?
            return True
        return None

    """ this funcion is supposed to change "assignedVehicle" of every destination in "self.destinations" to "None", which would allow for quicker calculations of unvisited nodes, but this is very hard to track
    def clearAssignedDestinations(self) -> None:
        for i in enumerate(self.destinations):
            self.destinations[i].assignedVehicle = None
        self.destinations.clear()"""
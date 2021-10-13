class ProblemInstance():
    def __init__(self, name, amountOfVehicles, capacityOfVehicles, destinations=[]):
        self.name = name
        self.amountOfVehicles = amountOfVehicles
        self.capacityOfVehicles = capacityOfVehicles
        self.destinations = destinations

    def __str__(self) -> str:
        return f"{self.name}, {self.amountOfVehicles}, {self.capacityOfVehicles}, {[dest.__str__() for dest in self.destinations]}"
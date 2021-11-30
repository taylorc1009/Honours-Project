from MMOEASA.solution import Solution
from problemInstance import ProblemInstance
from destination import Destination



def solution_visits_destination(node: int, instance: ProblemInstance, I: Solution) -> bool:
    for i, _ in enumerate(I.vehicles):
        if I.vehicles[i].getNumOfCustomersVisited() >= 1:
            for j, _ in enumerate(I.vehicles[i].destinations):
                if I.vehicles[i].destinations[j].node.number == instance.nodes[node].number: # directly get the destination number from the list of destinations in case there's a mismatch between the destination number and the for loop iterator (although there shouldn't)
                    return True
    return False

def verify_nodes_are_inserted(I: Solution, instance: ProblemInstance, node: int) -> Solution:
    inserted = False
    vehicle = 0

    while vehicle < len(I.vehicles) and not inserted:
        length_of_route = I.vehicles[vehicle].getNumOfCustomersVisited()
        final_destination = I.vehicles[vehicle].destinations[length_of_route].node.number
        
        I.vehicles[vehicle].destinations[length_of_route + 1].node = instance.nodes[node]
        I.vehicles[vehicle].current_capacity += instance.nodes[node].demand

        I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time = I.vehicles[vehicle].destinations[length_of_route].departure_time + instance.MMOEASA_distances[final_destination][node]
        I.vehicles[vehicle].destinations[length_of_route + 1].wait_time = 0.0
        if I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time < instance.nodes[node].ready_time:
            I.vehicles[vehicle].destinations[length_of_route + 1].wait_time = instance.nodes[node].ready_time - I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time
            I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time = instance.nodes[node].ready_time
        
        if I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time <= instance.nodes[node].due_date:
            I.vehicles[vehicle].destinations[length_of_route + 1].departure_time = instance.nodes[node].service_duration + I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time

            I.calculate_length_of_routes(instance)

            inserted = True
        elif I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time > instance.nodes[node].due_date or I.vehicles[vehicle].current_capacity > instance.capacity_of_vehicles:
            del I.vehicles[vehicle].destinations[length_of_route + 1]
            vehicle += 1

    return I

def reinitialize_depot_return(I: Solution, instance: ProblemInstance) -> Solution:
    vehicle = 0

    for i in range(len(I.vehicles)):
        I.vehicles[vehicle].destinations.append(Destination(node=instance.nodes[0]))

        length_of_route = I.vehicles[i].getNumOfCustomersVisited() - 1
        final_destination = I.vehicles[vehicle].destinations[length_of_route].node.number

        I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time = I.vehicles[vehicle].destinations[length_of_route + 1].departure_time + instance.MMOEASA_distances[final_destination][0]
        I.vehicles[vehicle].destinations[length_of_route + 1].departure_time = I.vehicles[vehicle].destinations[length_of_route + 1].departure_time + instance.MMOEASA_distances[final_destination][0]
        I.vehicles[vehicle].destinations[length_of_route + 1].wait_time = 0.0
    
    return I
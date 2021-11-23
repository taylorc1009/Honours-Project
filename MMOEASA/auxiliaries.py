from MMOEASA.solution import Solution
from problemInstance import ProblemInstance

def solution_visits_destination(node: int, instance: ProblemInstance, I: Solution) -> bool:
    for j in range(0, instance.amount_of_vehicles - 1):
        print(j)
        if len(I.vehicles[j].destinations) - 2 >= 1:
            for k in len(I.vehicles[j].destinations):
                if I.vehicles[j].destinations[k].node.number == instance.nodes[node].number: # directly get the destination number from the list of destinations in case there's a mismatch between the destination number and the for loop iterator (although there shouldn't)
                    return True
    return False

def verify_nodes_are_inserted(I: Solution, instance: ProblemInstance, node: int) -> None:
    inserted, vehicle = False, 0
    while vehicle < instance.amount_of_vehicles and not inserted:
        length_of_route = len(I.vehicles[vehicle].destinations) - 2
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

def reinitialize_depot_return(I: Solution, instance: ProblemInstance):
    vehicle = 0
    for i in range(I.vehicles):
        I.vehicles[vehicle].destinations.append(instance.nodes[0])

        length_of_route = len(I.vehicles[i].destinations) - 2
        final_destination = I.vehicles[vehicle].destinations[length_of_route].number

        I.vehicles[vehicle].destinations[length_of_route + 1].arrival_time = I.vehicles[vehicle].destinations[length_of_route + 1].departure_time + instance.MMOEASA_distances[final_destination][0]
        I.vehicles[vehicle].destinations[length_of_route + 1].departure_time = I.vehicles[vehicle].destinations[length_of_route + 1].departure_time + instance.MMOEASA_distances[final_destination][0]
        I.vehicles[vehicle].destinations[length_of_route + 1].wait_time = 0.0
import copy
from random import shuffle
from Custom.customSolution import CustomSolution
from common import INT_MAX
from problemInstance import ProblemInstance
from vehicle import Vehicle

def set_up_crossover_child(instance: ProblemInstance, parent_one: CustomSolution, parent_two_vehicle: Vehicle) -> CustomSolution:
    child_solution = copy.deepcopy(parent_one)

    nodes_to_remove = set([d.node.number for d in parent_two_vehicle.get_customers_visited()])
    i = 0
    while i < len(child_solution.vehicles) and nodes_to_remove:
        increment = True
        j = 1
        while j <= child_solution.vehicles[i].get_num_of_customers_visited() and nodes_to_remove:
            destination = child_solution.vehicles[i].destinations[j]
            if destination.node.number in nodes_to_remove:
                nodes_to_remove.remove(destination.node.number)
                child_solution.vehicles[i].current_capacity -= destination.node.demand
                if child_solution.vehicles[i].get_num_of_customers_visited() - 1 > 0:
                    del child_solution.vehicles[i].destinations[j]
                else:
                    increment = False
                    del child_solution.vehicles[i]
                    break  # break, otherwise the while loop will start searching the next vehicle with "j" as the same value; without incrementing "i" and starting "j" at 0
            else:
                j += 1
        if increment:
            i += 1

    child_solution.calculate_nodes_time_windows(instance)
    child_solution.calculate_vehicles_loads(instance)

    return child_solution

def crossover(instance: ProblemInstance, parent_one: CustomSolution, parent_two_vehicle: Vehicle) -> CustomSolution:
    crossover_solution = set_up_crossover_child(instance, parent_one, parent_two_vehicle)

    randomized_destinations = list(range(1, len(parent_two_vehicle.destinations) - 1))
    shuffle(randomized_destinations)
    for d in randomized_destinations:
        parent_destination = parent_two_vehicle.destinations[d]
        best_vehicle, best_position = -1, 0
        shortest_from_previous, shortest_to_next = (float(INT_MAX),) * 2
        found_feasible_location = False

        for i, vehicle in enumerate(crossover_solution.vehicles):
            if not vehicle.current_capacity + parent_destination.node.demand > instance.capacity_of_vehicles:
                for j in range(1, len(crossover_solution.vehicles[i].destinations)):
                    crossover_solution.vehicles[i].destinations.insert(j, parent_destination)
                    crossover_solution.vehicles[i].calculate_destination_time_window(instance, j - 1, j)

                    distance_from_previous = instance.get_distance(vehicle.destinations[j - 1].node.number, vehicle.destinations[j].node.number)
                    distance_to_next = instance.get_distance(vehicle.destinations[j].node.number, vehicle.destinations[j + 1].node.number)

                    if not (vehicle.destinations[j - 1].departure_time + distance_from_previous > vehicle.destinations[j].node.due_date or vehicle.destinations[j].departure_time + distance_to_next > vehicle.destinations[j + 1].node.due_date):
                        if (distance_from_previous < shortest_from_previous and distance_to_next <= shortest_to_next) or (distance_from_previous <= shortest_from_previous and distance_to_next < shortest_to_next):
                            best_vehicle, best_position, shortest_from_previous, shortest_to_next = i, j, distance_from_previous, distance_to_next
                            found_feasible_location = True
                        elif not found_feasible_location: # until a feasible location is found, record the best infeasible location as it will be needed in case no feasible location is found
                            best_vehicle, best_position, shortest_from_previous, shortest_to_next = i, j, distance_from_previous, distance_to_next

                    del crossover_solution.vehicles[i].destinations[j]

        if not found_feasible_location and len(crossover_solution.vehicles) < instance.amount_of_vehicles:
            best_vehicle = len(crossover_solution.vehicles)
            crossover_solution.vehicles.append(Vehicle.create_route(instance, copy.deepcopy(parent_destination.node)))
        else:
            crossover_solution.vehicles[best_vehicle].destinations.insert(best_position, copy.deepcopy(parent_destination))

        crossover_solution.vehicles[best_vehicle].calculate_vehicle_load(instance)
        crossover_solution.vehicles[best_vehicle].calculate_destinations_time_windows(instance)
        crossover_solution.vehicles[best_vehicle].calculate_length_of_route(instance)
        crossover_solution.objective_function(instance)

    return crossover_solution
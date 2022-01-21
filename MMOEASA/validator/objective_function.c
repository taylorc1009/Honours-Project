#include <string.h>
#include "data.h"

void free_Solution(struct Solution* solution) {
    for (int v = 0; v < solution->vehicles->size; v++) {
        struct Vehicle* vehicle = (struct Vehicle*)solution->vehicles->at(solution->vehicles, v);
        for (int d = 0; d < vehicle->destinations->size; d++) {
            struct Destination* destination = (struct Destination*)vehicle->destinations->at(vehicle->destinations, d);

            free(destination->node);
            free(destination);
        }
        vehicle->destinations->clear(vehicle->destinations);
        free(vehicle);
    }
    solution->vehicles->clear(solution->vehicles);
    free(solution);
}

void objective_function(struct Solution* restrict I, const int amount_of_vehicles, const int capacity_of_vehicles)
{
    float minimum_distance, maximum_distance, minimum_cargo, maximum_cargo;
    I->total_distance = 0;
    int v = 0;

    do {
        struct Vehicle* vehicle = (struct Vehicle*)I->vehicles->at(I->vehicles, v);
        I->total_distance += vehicle->route_distance;
        printf("hi %f, %f\n", vehicle->current_capacity, vehicle->route_distance);
        for (int d = 1; d <= vehicle->destinations->size; d++) {
            printf("hi %d\n", vehicle->destinations->size);
            struct Destination* destination = (struct Destination*)vehicle->destinations->at(vehicle->destinations, d);
            if (destination->arrival_time > destination->node->due_date || vehicle->current_capacity > capacity_of_vehicles) {
                I->feasible = false;
                I->total_distance = INFINITY;
                I->distance_unbalance = INFINITY;
                I->cargo_unbalance = INFINITY;
                break;
            }
        }

        v++;
    } while(v < amount_of_vehicles && I->feasible);

    if (I->feasible)
    {
        minimum_distance = INFINITY;
        maximum_distance = 0;
        minimum_cargo = INFINITY;
        maximum_cargo = 0;

        for (v = 0; v < amount_of_vehicles; v++)
        {
            struct Vehicle* vehicle = (struct Vehicle*)I->vehicles->at(I->vehicles, v);
            if (vehicle->destinations->size >= 1)
            {
                if(vehicle->route_distance < minimum_distance)
                    minimum_distance = vehicle->route_distance;
                if(vehicle->route_distance > maximum_distance)
                    maximum_distance= vehicle->route_distance;
                if(vehicle->current_capacity < minimum_cargo)
                    minimum_cargo = vehicle->current_capacity;
                if(vehicle->current_capacity > maximum_cargo)
                    maximum_cargo = vehicle->current_capacity;
            }
        }

        I->distance_unbalance = maximum_distance - minimum_distance;
        I->cargo_unbalance = maximum_cargo - minimum_cargo;
    }
}

int main(int argc, char** argv) {
    if (3 <= argc <= 4) {
        char* filename = NULL;
        int offset = 0;
        if (argc > 3) {
            filename = argv[1]; // "read_csv" can accept a null filename as it will default to "solution.csv" if this is so
            offset = 1;
        }
        
        struct Solution* solution = read_csv(.file=filename);

        if (solution) {
            objective_function(solution, strtol(argv[1 + offset], (char**)NULL, 10), strtol(argv[2 + offset], (char**)NULL, 10));
    
            printf("feasable: %s\nobjectives:\n - total distance = %f\n - distance unbalance = %f\n - cargo unbalance = %f", solution->feasible ? "true" : "false", solution->total_distance, solution->distance_unbalance, solution->cargo_unbalance);
            free_Solution(solution);
        }
    }
    else
        printf("(!) incorrect amount of arguments found: %d\nusage: objective_function [filename] (number of vehicles) (capacity of vehicles)", argc);
    
    return 0;
}
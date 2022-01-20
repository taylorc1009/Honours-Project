#include <stdio.h>
#include "types.h"

void objective_function(struct Solution* restrict I, const int amount_of_vehicles, const int capacity_of_vehicles)
{
    bool feasible = true;
    float minimum_distance, maximum_distance, minimum_cargo, maximum_cargo;
    I->total_distance = 0;
    int v = 0;

    do
    {
        struct Vehicle* vehicle = (struct Vehicle*)I->vehicles->at(I->vehicles, v);
        I->total_distance += vehicle->route_distance;

        for (int d = 1; d <= vehicle->destinations->size; d++)   
        {
            struct Destination* destination = (struct Destination*)vehicle->destinations->at(vehicle->destinations, d);
            if (destination->arrival_time > destination->node->due_date || vehicle->current_capacity > capacity_of_vehicles)
            {
                feasible = false;
                I->total_distance = INFINITY;
                I->distance_unbalance = INFINITY;
                I->cargo_unbalance = INFINITY;
                break;
            }
        }

        v++;
    } while(v < amount_of_vehicles && feasible);

    if (feasible)
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
    if (argc < 2)
        return 0;
    
    FILE* file;

    if (file = fopen(argv[1], "rb")) {
        fseek(file, 0, SEEK_END);
        long len = (long)ftell(file);
        if (len > 0) {
            rewind(file);

        }
        else
            fclose(file);
    }
    
    return 0;
}
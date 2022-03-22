# My Edinburgh Napier University Honours Project

My Honours Project is aimed at investigating the performance of different methods of solving the Capacitated Vehicle Routing Problem with Time Windows (CVRPTW). The problem entails finding the most efficient combination of routes that multiple vehicles can take to deliver to every customer present in a set of customers. The edition of the VRP I'm investigating (the CVRPTW) is different because it constrains the capacity of each vehicle (and, therefore, the amount of packages each vehicle can carry) and the time windows in which each customer should receive their delivery. Such constraints and complexities make the CVRPTW [NP-Hard](https://en.wikipedia.org/wiki/NP-hardness).

The project investigates evolutionary algorithms (EA), heuristics, and EA-heuristic hybrids that solve the problem by aiming to find the combinations of routes that require the lowest cost to carry out. In other words, the cost is my objective function. Factors that to contribute to the cost of a solution are the amount of vehicles required and the total distance of each route. Any capacity and time window violations will render a solution infeasible and therefore, the solution will be rejected.

## How to execute the application (tutorial for Windows):
1. Install Python version 3.9,
2. Open the Windows command line and `cd` to the project root,
3. Create a virtual environment in the root folder of application;
   1. Using `python3.9 -m venv venv`,
4. Activate the virtual environment;
   1. Using `venv\Scripts\activate`,
5. Install the necessary packages;
   1. Using `pip install -r requirements.txt`,
6. Execute the application;
   1. Using `main.py` as the entry point,
   2. `main.py [ -h | --help ]` can provide further instructions,
   3. The file `compile.bat` can compile the app into a single executable.

## How to externally validate solutions:
1. Use the function `MMOEASA_write_solution_for_validation` from `data.py` in the Python application to output a solution to a CSV,
2. Compile the C application in `../MMOEASA/validator`;
   1. Using either the Makefile or CMake
3. Execute the application `objective_function.exe`;
   1. If you wish to use a different CSV file, give the application the file name as a command line argument,
   2. `objective_function [filename].csv`
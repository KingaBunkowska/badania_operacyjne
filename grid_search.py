from tqdm import tqdm
import inspect
from example_function_file import defined_functions
from evolutionary_functions import defined_functions as df
from genetic_algorithm import Solution, evolutionary_algorithm
from itertools import product
from taskplanner import generate_tasks, generate_input_matrices, Employee, Task
from main import solve

grid_params = {
    "no_generations": [100, 250, 500],
    "breed_function": [*defined_functions["breed"], *df["breed"]],
    "mutate_function": [*defined_functions["mutate"], *df["mutate"]], 
    "select_function": defined_functions["select"],
}

def grid_search(T, Z, p, L, grid_params):
    num_tasks = len(T[0])
    num_employees = len(T)

    Solution.initialize(T, Z, p, L, num_employees, num_tasks)

    param_names = list(grid_params.keys())
    param_values = list(grid_params.values())
    combinations = list(product(*param_values))

    best_solution = None
    best_params = None

    results  = {}
    
    starting_population = [Solution(solve(*Solution.get_data_and_config())) for _ in range(250)]

    for combination in tqdm(combinations, desc="Combinations"):
        params = dict(zip(param_names, combination))
        solution = evolutionary_algorithm(starting_population, **params)

        if best_solution is None or best_solution.f > solution.f:
            best_solution = solution
            best_params = params

        results[params.values()] = solution.get_detailed_f()

    return best_solution, best_params, results

def clean_params(params):
    keys_with_functions = ["breed_function", "mutate_function", "select_function"]
    for key in keys_with_functions:
        params[key] = inspect.getmodule(params[key]).__name__ + ": "+ params[key].__name__
    return params

if __name__ == "__main__":
    employees = [
        Employee([1, 3, 4, 10], 3, [3, 10], [1, 3, 4]),
        Employee([1], 5, [0, 99], [1]),
        Employee([x for x in range(10)], 0, [0, 5], []),
        Employee([], 10, [0, 99], [x for x in range(10)]),
    ]

    tasks = generate_tasks(50)

    T, Z, p = generate_input_matrices(employees, tasks)
    L = 40

    solution, params, results = grid_search(T, Z, p, L, grid_params)

    print("\n".join(str(row) for row in solution.R))
    print(solution.f)
    print(clean_params(params))
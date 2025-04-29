from tqdm import tqdm
from example_function_file import defined_functions
from genetic_algorithm import Solution, evolutionary_algorithm
from itertools import product
from taskplanner import generate_tasks, generate_input_matrices, Employee, Task

grid_params = {
    "breed_function": defined_functions["breed"],
    "mutate_function": defined_functions["mutate"], 
    "select_function": defined_functions["select"],
    "no_generations": [1, 10, 100],
    "population_size": [2, 20, 100],
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

    for combination in tqdm(combinations, desc="Combinations"):
        params = dict(zip(param_names, combination))
        solution = evolutionary_algorithm(**params)

        if best_solution is None or best_solution.f > solution.f:
            best_solution = solution
            best_params = params

        results[params.values()] = solution

    return best_solution, best_params, results

def clean_params(params):
    params["breed_function"] = params["breed_function"].__name__
    params["mutate_function"] = params["mutate_function"].__name__
    params["select_function"] = params["select_function"].__name__
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

    solution, params, _ = grid_search(T, Z, p, L, grid_params)

    print("\n".join(str(row) for row in solution.R))
    print(solution.f)
    print(clean_params(params))
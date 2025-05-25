import copy
import multiprocessing

from tqdm import tqdm
from example_function_file import defined_functions as example_functions
from dominance_hierarchy_functions import defined_functions as dominance_hierarchy_functions
from evolutionary_functions import defined_functions as evolutionary_functions
from lukasz_function import defined_functions as lukasz_functions
from maciek_function_file import defined_functions_maciek as maciek_functions
from genetic_algorithm import Solution, evolutionary_algorithm, functions_to_names
from itertools import product
from taskplanner import generate_tasks, generate_input_matrices, Employee, Task
from main import solve
from uuid import uuid1


grid_params = {
    "no_generations": [50, 100],
    "breed_function": functions_to_names([
        *example_functions["breed"],
        *evolutionary_functions["breed"],
        *dominance_hierarchy_functions["breed"],
        *lukasz_functions["breed"],
        *maciek_functions["breed"],
    ]),
    "mutate_function": functions_to_names([
        *example_functions["mutate"],
        *evolutionary_functions["mutate"],
        *dominance_hierarchy_functions["mutate"],
        *lukasz_functions["mutate"],
        *maciek_functions["mutate"],
    ]),
    "select_function": functions_to_names([
        *example_functions["select"],
        *evolutionary_functions["select"],
        *dominance_hierarchy_functions["select"],
        *lukasz_functions["select"],
        *maciek_functions["select"],
    ]),
}

def run_grid_search(params):
    (process_name, T, Z, p, L, param_names, param_combinations) = params

    with open(f"{process_name}_{uuid1()}.txt", "w") as fin:
        num_tasks = len(T[0])
        num_employees = len(T)

        Solution.initialize(T, Z, p, L, num_employees, num_tasks)

        best_solution = None
        best_params = None

        results  = {}

        starting_population = [Solution(solve(*Solution.get_data_and_config())) for _ in range(200)]

        def format_f(detailed_f):
            return [float(x) for x in detailed_f]

        for combination in tqdm(param_combinations, desc=process_name):
            params = dict(zip(param_names, combination))
            solution = evolutionary_algorithm(starting_population, **params)

            fin.write(f"{format_f(solution.get_detailed_f())} ; {params}\n")

            if best_solution is None or best_solution.f > solution.f:
                best_solution = copy.deepcopy(solution)
                best_params = copy.deepcopy(params)
                print()
                print(float(best_solution.f))
                print(best_params)
                print()
                print()

            results[params.values()] = format_f(solution.get_detailed_f())

        fin.write(f"[[ BEST ]] {format_f(best_solution.get_detailed_f())} ; {best_params}\n")

def equal_split(data, n_chunks):
    chunk_size = len(data) // n_chunks

    start = 0
    for _ in range(n_chunks-1):
        yield data[start:start+chunk_size]
        start += chunk_size
    yield data[start:]

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

    num_parallel = 8

    combinations_chunks = equal_split(list(product(*grid_params.values())), num_parallel)
    pool = multiprocessing.Pool(num_parallel)

    param_names = list(grid_params.keys())

    pool.map(run_grid_search, ((f"process_{i+1}", T, Z, p, L, param_names, chunk) for (i, chunk) in enumerate(combinations_chunks)))

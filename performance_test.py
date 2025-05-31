from load_from_file import load_full_file, generate_and_save
from genetic_algorithm import evolutionary_algorithm, Solution, get_evaluator_fn
from taskplanner import solve
from dominance_hierarchy_functions import dominant_solution_breed_swap_employees, dominant_solution_mutate
from example_function_file import select_children
from lukasz_function import mutation, breed
from maciek_function_file import shuffle_mutation, select_children_by_age


import inspect
import numpy as np
import random
import time

def set_random_seed(seed):
    random.seed(seed)
    np.random.seed(seed)


def function_to_name(f):
    return f"{inspect.getmodule(f).__name__}.{f.__name__}"

params_1 = {
    "breed_function": function_to_name(dominant_solution_breed_swap_employees),
    "mutate_function": function_to_name(mutation),
    "select_function": function_to_name(select_children),
    "no_generations": 100
}

params_2 = {
    "breed_function": function_to_name(breed),
    "mutate_function": function_to_name(shuffle_mutation),
    "select_function": function_to_name(select_children_by_age),
    "no_generations": 100
}

def test(result_path, title):
    times = []
    parameters = []
    for i in range(21,35):
        print(f"Iteration {i}")
        path = f"test_performance2\\test{i}.txt"

        generate_and_save(path, 40, i*3, 10)
        
        L, employe_list, task_list, T, Z = load_full_file(path)
        p = [task.priority for task in task_list]

        Solution.initialize(T, Z, p, L, len(employe_list), len(task_list))
        starting_population = [Solution(solve(*Solution.get_data_and_config())) for _ in range(100)]
        set_random_seed(i)
        start = time.time()
        sol = evolutionary_algorithm(
                starting_population,
                **params_1
            )
        stop = time.time()
        print(stop - start)
        times.append(stop - start)
        parameters.append(i*3)
        


    with open(result_path, "w") as file:
        file.write(f"{title}\n")
        file.write(f"{times}\n")
        file.write(f"{parameters}")

test("result3.txt", "Performance test 10 employees increasing tasks number")

from load_from_file import load_full_file
from dominance_hierarchy_functions import dominant_solution_breed_swap_employees
from example_function_file import select_children
from genetic_algorithm import evolutionary_algorithm, Solution, get_evaluator_fn
from lukasz_function import mutation
from taskplanner import solve
import inspect
import numpy as np

def function_to_name(f):
    return f"{inspect.getmodule(f).__name__}.{f.__name__}"

params = {
    "breed_function": function_to_name(dominant_solution_breed_swap_employees),
    "mutate_function": function_to_name(mutation),
    "select_function": function_to_name(select_children),
    "no_generations": 200
}


def test(path):
    L, employe_list, task_list, T, Z = load_full_file(path)
    p = [task.priority for task in task_list]
    random_results = [[] for _ in range(5)]
    best_effort_results = [[] for _ in range(5)]

    R = solve(T, Z, L, len(employe_list), len(task_list))

    evaluation_fn = get_evaluator_fn(30, 1, 3000, 20)

    for i, x in enumerate(evaluation_fn(T, Z, p, R)):
        random_results[i].append(x)

    Solution.initialize(T, Z, p, L, len(employe_list), len(task_list))
    starting_population = [Solution(solve(*Solution.get_data_and_config())) for _ in range(100)]
    sol = evolutionary_algorithm(
            starting_population,
            **params
        )
    for i, x in enumerate(evaluation_fn(T, Z, p, sol.R)):
        best_effort_results[i].append(x)
    
    time = np.array(T) * np.array(sol.R)
    print(np.sum(time, axis=1))
    check_task = np.sum(sol.R, axis=0)
    print(check_task)
    print(sol.R)


    return best_effort_results



print(test("validate.txt"))





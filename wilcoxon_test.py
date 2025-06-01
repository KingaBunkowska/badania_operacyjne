from load_from_file import load_full_file
from genetic_algorithm import evolutionary_algorithm, Solution, get_evaluator_fn
from taskplanner import solve
from dominance_hierarchy_functions import dominant_solution_breed_swap_employees, dominant_solution_mutate
from example_function_file import select_children
from lukasz_function import mutation


from scipy.stats import wilcoxon
import inspect
import numpy as np
import random

def set_random_seed(seed):
    random.seed(seed)
    np.random.seed(seed)


def function_to_name(f):
    return f"{inspect.getmodule(f).__name__}.{f.__name__}"

params_best = {
    "breed_function": function_to_name(dominant_solution_breed_swap_employees),
    "mutate_function": function_to_name(mutation),
    "select_function": function_to_name(select_children),
    "no_generations": 100
}

params = {
    "breed_function": function_to_name(dominant_solution_breed_swap_employees),
    "mutate_function": function_to_name(dominant_solution_mutate),
    "select_function": function_to_name(select_children),
    "no_generations": 100
}

def test():
    random_mutation = []
    dominant_mutation = []
    for i in range(1,31):
        print(f"Iteration {i}")
        path = f"test\\test{i}.txt"
        
        L, employe_list, task_list, T, Z = load_full_file(path)

        p = [task.priority for task in task_list]

        evaluation_fn = get_evaluator_fn(30, 1, 3000, 20)

        Solution.initialize(T, Z, p, L, len(employe_list), len(task_list))
        starting_population = [Solution(solve(*Solution.get_data_and_config())) for _ in range(100)]
        set_random_seed(i)
        print("random mutation")
        sol = evolutionary_algorithm(
                starting_population,
                **params_best
            )
        
        random_mutation.append(sol.f)
        
        set_random_seed(i)
        print("dominant mutation")
        sol = evolutionary_algorithm(
                starting_population,
                **params
            )
        
        dominant_mutation.append(sol.f)

    with open("result.txt", "w") as file:
        file.write(f"{random_mutation}")
        file.write(f"{dominant_mutation}")

    stat, p_value = wilcoxon(random_mutation, dominant_mutation)

    print(f"Statystyka testu Wilcoxona: {stat}")
    print(f"P-wartość: {p_value}")

    if p_value < 0.05:
        print("Różnica między algorytmami jest statystycznie istotna (p < 0.05).")
    else:
        print("Brak statystycznie istotnej różnicy między algorytmami (p >= 0.05).")

test()
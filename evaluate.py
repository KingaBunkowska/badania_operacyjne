from tqdm import tqdm

from dominance_hierarchy_functions import dominant_solution_breed_swap_employees
from example_function_file import select_children
from genetic_algorithm import evolutionary_algorithm, Solution, get_evaluator_fn
from lukasz_function import mutation
from taskplanner import Employee, generate_tasks, generate_input_matrices, solve
import matplotlib.pyplot as plt


def run_once():
    L = 40
    num_tasks = 40
    employees = [
        Employee([1, 3, 4, 10], 3, [3, 10], [1, 3, 4]),
        Employee([1], 5, [0, 99], [1]),
        Employee([x for x in range(10)], 0, [0, 5], []),
        Employee([], 10, [0, 99], [x for x in range(10)]),
    ]
    tasks = generate_tasks(num_tasks)
    T, Z, p = generate_input_matrices(employees, tasks)
    R = solve(T, Z, L, len(employees), num_tasks)

    print("Difficulty:")
    print([task.difficulty for task in tasks])
    print("T:")
    print(*T, sep='\n')
    print("Z:")
    print(*Z, sep='\n')
    print("R:")
    print(*R, sep='\n')

    for j, employee in enumerate(employees):
        print(f"Employee #{j}:")
        print(round(sum([T[j][i] * R[j][i] for i in range(num_tasks)]), 2))


def run_evaluate():
    L = 40
    num_tasks = 40
    employees = [
        Employee([1, 3, 4, 10], 3, [3, 10], [1, 3, 4]),
        Employee([1], 5, [0, 99], [1]),
        Employee([x for x in range(10)], 0, [0, 5], []),
        Employee([], 10, [0, 99], [x for x in range(10)]),
    ]

    evaluation_fn = get_evaluator_fn(30, 1, 3000, 20)

    random_results = [[] for _ in range(5)]
    best_effort_results = [[] for _ in range(5)]

    N = 100

    def run(T, Z, p):
        R = solve(T, Z, L, len(employees), num_tasks)
        for i, x in enumerate(evaluation_fn(T, Z, p, R)):
            random_results[i].append(x)

        Solution.initialize(T, Z, p, L, 4, num_tasks)
        starting_population = [Solution(solve(*Solution.get_data_and_config())) for _ in range(200)]
        sol = evolutionary_algorithm(
            starting_population,
            dominant_solution_breed_swap_employees,
            mutation,
            select_children,
            100
        )
        for i, x in enumerate(evaluation_fn(T, Z, p, sol.R)):
            best_effort_results[i].append(x)

    for _ in tqdm(range(N)):
        tasks = generate_tasks(num_tasks)
        T, Z, p = generate_input_matrices(employees, tasks)
        run(T, Z, p)

    fig, axes = plt.subplots(2, 3, figsize=(24, 16))
    xs = [x for x in range(N)]
    axes[0][0].scatter(xs, random_results[0], label='random')
    axes[0][0].scatter(xs, best_effort_results[0], label='evolved')
    axes[0][0].set_title('f1')
    axes[0][0].legend()

    axes[0][1].scatter(xs, random_results[1], label='random')
    axes[0][1].scatter(xs, best_effort_results[1], label='evolved')
    axes[0][1].set_title('f2')
    axes[0][1].legend()

    axes[0][2].scatter(xs, random_results[2], label='random')
    axes[0][2].scatter(xs, best_effort_results[2], label='evolved')
    axes[0][2].set_title('f3')
    axes[0][2].legend()

    axes[1][0].scatter(xs, random_results[3], label='random')
    axes[1][0].scatter(xs, best_effort_results[3], label='evolved')
    axes[1][0].set_title('f4')
    axes[1][0].legend()

    axes[1][1].scatter(xs, random_results[4], label='random')
    axes[1][1].scatter(xs, best_effort_results[4], label='evolved')
    axes[1][1].set_title('F')
    axes[1][1].legend()

    axes[1][2].axis('off')
    plt.show()


if __name__ == '__main__':
    run_evaluate()

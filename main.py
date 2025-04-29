from taskplanner import Employee, generate_tasks, generate_input_matrices, solve
import numpy as np
import matplotlib.pyplot as plt


def get_evaluator_fn(alpha, beta, gamma):
    def evaluate(T, Z, p, R):
        time_spent = np.array(T) * np.array(R)
        time_spent_per_employee = np.sum(time_spent, axis=1)
        f1 = np.max(time_spent_per_employee) - np.min(time_spent_per_employee)
        f2 = np.sum(time_spent * (11 - np.array([p])))
        f3 = 1 / (1 + np.sum(np.sqrt(np.sum(np.array(Z) * np.array(R), axis=1))))

        return f1, f2, f3, alpha * f1 + beta * f2 + gamma * f3

    return evaluate


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

    f1s, f2s, f3s, Fs = [], [], [], []
    evaluation_fn = get_evaluator_fn(1, 1, 1)

    num_runs = 50
    for _ in range(num_runs):
        tasks = generate_tasks(num_tasks)
        T, Z, p = generate_input_matrices(employees, tasks)
        R = solve(T, Z, L, len(employees), num_tasks)
        f1, f2, f3, F = evaluation_fn(T, Z, p, R)
        f1s.append(f1)
        f2s.append(f2)
        f3s.append(f3)
        Fs.append(F)

    fig, axes = plt.subplots(2, 2, figsize=(8, 8))
    xs = [x for x in range(num_runs)]
    axes[0][0].scatter(xs, f1s)
    axes[0][0].set_title('f1')

    axes[0][1].scatter(xs, f2s)
    axes[0][1].set_title('f2')

    axes[1][0].scatter(xs, f3s)
    axes[1][0].set_title('f3')

    axes[1][1].scatter(xs, Fs)
    axes[1][1].set_title('F')
    fig.show()


if __name__ == '__main__':
    run_evaluate()

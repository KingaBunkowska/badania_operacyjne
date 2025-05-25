import random
import math
from genetic_algorithm import Solution

def add_mutate(children):
    def find_not_assigned_tasks(child):
        result = []
        for task in range(Solution.num_tasks):
            assigned = False
            for emp in range(Solution.num_employees):
                assigned = assigned or child.R[emp][task]
            if not assigned:
                result.append(task)

        return result
            

    for child in children:
        if random.uniform(0, 1) > 0.90:
            not_assigned_tasks = find_not_assigned_tasks(child)
            task = random.choice(not_assigned_tasks)
            employee_order = list(range(Solution.num_employees))
            random.shuffle(employee_order)

            for emp in employee_order:
                child.R[emp][task] = 1
                if child.is_legal():
                    break
                child.R[emp][task] = 0

    return children

def delete_disliked_mutate(children: list[Solution]):
    for child in children:
        if random.uniform(0, 1) > 0.95:
            emp = random.choice(range(Solution.num_employees))
            task_satisfactions = [Solution.Z[emp][task] if child.R[emp][task] else math.inf for task in range(Solution.num_tasks)]
            idx, _ = min(enumerate(task_satisfactions), key=lambda x: x[1])
            child.R[emp][idx] = 0
    return children

def delete_lowest_priority(children: list[Solution]):
    for child in children:
        if random.uniform(0, 1) > 0.95:
            emp = random.choice(range(Solution.num_employees))
            task_priorities = [Solution.p[task] if child.R[emp][task] else math.inf for task in range(Solution.num_tasks)]
            idx, _ = min(enumerate(task_priorities), key=lambda x: x[1])
            child.R[emp][idx] = 0
    return children

def delete_longest_task(children: list[Solution]):
    for child in children:
        if random.uniform(0, 1) > 0.95:
            emp = random.choice(range(Solution.num_employees))
            task_length = [Solution.T[emp][task] if child.R[emp][task] else math.inf for task in range(Solution.num_tasks)]
            idx, _ = max(enumerate(task_length), key=lambda x: x[1])
            child.R[emp][idx] = 0
    return children


defined_functions = {
    "breed": [],
    "mutate": [add_mutate, delete_disliked_mutate, delete_longest_task, delete_lowest_priority],
    "select": [],
}
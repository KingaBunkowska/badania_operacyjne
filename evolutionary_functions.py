import random
from copy import copy
import math
from genetic_algorithm import Solution

def breed(population):
    def create_child(parent1, parent2):
        child = Solution(copy(parent1.R))
        for employee in range(len(parent2.R)):
            for task in range(len(parent2.R[0])):
                if parent2.R[employee][task] and child.R[employee][task] == 0:
                    child.R[employee][task] = 1
                    if not child.is_legal():
                        child.R[employee][task] = 0

        return child

    children = []

    weights = [1 / pop.f for pop in population]

    for _ in range(len(population)//2):
        [parent1] = random.choices(population, weights=weights, k=1)
        [parent2] = random.choices(population, weights=weights, k=1)

        children.append(create_child(parent1, parent2))
        children.append(create_child(parent2, parent1))
        
    return children

def swap_mutate(children):
    def swap_tasks(child, task1, task2):
        for emp in range(Solution.num_employees):
            child.R[emp][task1] = child.R[emp][task2]

        return child

    for child in children:
        if random.uniform(0, 1) > 0.70:
            for i in range(Solution.num_tasks//50):
                tasks_to_swap = random.sample(range(len(child.R[0])), k=2)
                child = swap_tasks(child, *tasks_to_swap)
                if not child.is_legal():
                    child = swap_tasks(child, *tasks_to_swap[::-1])    
                else:
                    break     

    return children

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

def delete_unliked_mutate(children: list[Solution]):
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

def fusion_mutate(children: list[Solution]):
    mutate_functions = [swap_mutate, add_mutate, delete_unliked_mutate, delete_longest_task, delete_lowest_priority]
    mutated_children = []
    size = len(children) // len(mutate_functions)
    for i, mutate_function in enumerate(mutate_functions):
        mutated_children.extend(mutate_function(children[i*size:i*size+size]))

    return mutated_children
            

defined_functions = {
    "breed": [breed],
    "mutate": [swap_mutate, add_mutate, delete_unliked_mutate, fusion_mutate, delete_longest_task, delete_lowest_priority],
    "select": [],
}
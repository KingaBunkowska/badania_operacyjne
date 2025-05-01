from random import random, choice, shuffle

import numpy as np

from genetic_algorithm import Solution


def crossover_swap_same_employees(parent1, parent2):
    employee_split = list(range(len(parent1.R)))
    shuffle(employee_split)
    child1 = Solution(parent1.R.copy())
    child2 = Solution(parent2.R.copy())
    for e in employee_split[:len(employee_split)//2]:
        child1.R[e], child2.R[e] = child2.R[e], child1.R[e]

    return resolve_conflicts(child1), resolve_conflicts(child2)


def crossover_happy_vs_productive(parent1, parent2):
    employees = list(range(len(parent1.R)))
    shuffle(employees)
    happy, productive = employees[:2]

    h1 = sum([parent1.Z[happy][task] * parent1.R[happy][task] for task in range(len(parent1.R[happy]))])
    h2 = sum([parent2.Z[happy][task] * parent2.R[happy][task] for task in range(len(parent2.R[happy]))])
    p1 = sum([parent1.T[productive][task] * parent1.R[productive][task] for task in range(len(parent1.R[productive]))])
    p2 = sum([parent2.T[productive][task] * parent2.R[productive][task] for task in range(len(parent2.R[productive]))])

    child1 = Solution(parent1.R.copy())
    child2 = Solution(parent2.R.copy())

    if h1 > h2:
        child2.R[happy] = child1.R[happy]
    else:
        child1.R[happy] = child2.R[happy]

    if p1 > p2:
        child2.R[productive] = child1.R[productive]
    else:
        child1.R[productive] = child2.R[productive]

    return resolve_conflicts(child1), resolve_conflicts(child2)


def resolve_conflicts(sol):
    for task in range(len(sol.R[0])):
        assigments = []
        for employee in range(len(sol.R)):
            if sol.R[employee][task] == 1:
                assigments.append(employee)
        # at most 2 employees are assigned to the task
        if len(assigments) > 1:
            sol.R[choice(assigments)][task] = 0
    unassigned_tasks = []
    for task in range(len(sol.R[0])):
        if sum([sol.R[e][task] for e in range(len(sol.R))]) == 0:
            unassigned_tasks.append(task)
    unassigned_tasks.sort(key=lambda task: sol.p[task], reverse=True)
    for task in unassigned_tasks:
        for employee in range(len(sol.R)):
            sol.R[employee][task] = 1
            if sol.is_legal():
                continue
            sol.R[employee][task] = 0
    return sol


def dominant_solution_breed_swap_employees(population: list[Solution]):
    if len(population) < 2:
        raise Exception("Population too small")

    dominance_hierarchy = list(sorted(population, key=lambda p: p.f))
    alpha, beta = dominance_hierarchy[0], dominance_hierarchy[1]

    if len(population) == 2:
        return crossover_swap_same_employees(alpha, beta)

    children = []
    for _ in range(len(population) // 2):
        parent1 = alpha if random() < 0.7 else beta
        parent2 = choice(dominance_hierarchy[2:])
        children.extend(crossover_swap_same_employees(parent1, parent2))

    return children


def dominant_solution_breed_happy_vs_productive(population: list[Solution]):
    if len(population) < 2:
        raise Exception("Population too small")

    dominance_hierarchy = list(sorted(population, key=lambda p: p.f))
    alpha, beta = dominance_hierarchy[0], dominance_hierarchy[1]

    if len(population) == 2:
        return crossover_happy_vs_productive(alpha, beta)

    children = []
    for _ in range(len(population) // 2):
        parent1 = alpha if random() < 0.7 else beta
        parent2 = choice(dominance_hierarchy[2:])
        children.extend(crossover_happy_vs_productive(parent1, parent2))

    return children


def dominant_solution_mutate(population):
    for i in range(len(population)):
        sol = population[i]
        if random() < 0.5:
            continue
        for employee in range(len(sol.R)):
            satisfaction = [sol.Z[employee][task] for task in range(len(sol.R[0]))]
            best_task = np.argmax(satisfaction)
            sol.R[employee][best_task] = 1
        resolve_conflicts(sol)
    return population


def dominant_solution_select(population, children):
    for sol in population:
        sol.age += 1

    dominance_hierarchy = list(sorted(population + list(children), key=lambda p: p.f * ((10 + p.age) / 10)))

    return dominance_hierarchy[:len(population)]


defined_functions = {
    "breed": [dominant_solution_breed_swap_employees, dominant_solution_breed_happy_vs_productive],
    "mutate": [dominant_solution_mutate],
    "select": [dominant_solution_select],
}

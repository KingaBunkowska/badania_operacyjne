import random
from copy import copy
from genetic_algorithm import Solution


def random_delete_breed(population):
    def create_child(parent1, parent2):
        child = Solution(copy(parent1.R))

        for employee in range(len(parent1.R)):
            for task in range(len(parent1.R[0])):
                if parent1.R[employee][task]:
                    child.R[employee][task] = 1 if random.randint(0, 10) >= 9 else 0

        for employee in range(len(parent2.R)):
            for task in range(len(parent2.R[0])):
                if parent2.R[employee][task] and child.R[employee][task] == 0:
                    child.R[employee][task] = 1 if random.randint(0, 10) > 5 else 0
                    if not child.is_legal():
                        child.R[employee][task] = 0

        return child

    children = []

    for _ in range(len(population)//2):
        parent1 = random.choice(population)
        parent2 = random.choice(population)

        children.append(create_child(parent1, parent2))
        children.append(create_child(parent2, parent1))
        
    return children

def random_delete_mutation(children):
    for child in children:
        if random.uniform(0, 1) > 0.99:

            for employee in range(len(child.R)):
                for task in range(len(child.R)):
                    child.R[employee][task] = 0 if random.uniform(0, 1) > 0.9 else child.R[employee][task]

    return children


def select_children(population, children):
    return children


defined_functions = {
    "breed": [random_delete_breed],
    "mutate": [random_delete_mutation],
    "select": [select_children],
}
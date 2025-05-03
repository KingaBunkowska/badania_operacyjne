import random
from copy import copy, deepcopy
from genetic_algorithm import Solution


def remove_task(parent, task):
        for employee in range(len(parent.R)):
            if parent.R[employee][task] == 1:
                parent.R[employee][task] = 0
                return

def legal_child(child):
    if not child.is_legal():
        for employee in range(len(child.R)):
            time_count = 0
            task_dict = dict()
            for task in range(len(child.R[0])):
                if child.R[employee][task] != 0:
                    task_dict[task] = child.T[employee][task]
                    time_count += task_dict[task]

            if time_count > child.L:
                keys = sorted(task_dict, key=lambda k: task_dict[k], reverse=False)
                for key in keys:
                    time_count -= task_dict[key]
                    child.R[employee][key] = 0
                    if time_count <= child.L:
                        break

def breed(population):

    def create_child(parent1, parent2):
        child = Solution(deepcopy(parent1.R))

        swap_task_number = random.randint(1,len(parent1.R[0]))
        employees_number = len(child.R)


        for _ in range(swap_task_number):
            employee_parent1 = random.randrange(0, employees_number)
            employee_parent2 = random.randrange(0, employees_number)

            task_number_1 = random.randrange(0, len(child.R[employee_parent1]))
            task_number_2 = random.randrange(0, len(parent2.R[employee_parent2]))

            remove_task(child, task_number_1)
            remove_task(child, task_number_2)

            new_employee = random.randrange(0, employees_number)

            child.R[new_employee][task_number_2] = 1

        legal_child(child)
        return child

    children = []

    for _ in range(len(population)//2):
        parent1 = random.choice(population)
        parent2 = random.choice(population)

        children.append(create_child(parent1, parent2))
        children.append(create_child(parent2, parent1))
            
    return children

def mutation(children):
    children_number = len(children)

    mutation_number = random.randrange(1, len(children[0].R[0]))
    employee_numbers = len(children[0].R)
    task_numbers = len(children[0].R[0])

    for _ in range(mutation_number):
        
        child_number = random.randrange(0, children_number)
        employee = random.randrange(0, employee_numbers)
        task = random.randrange(0, task_numbers)

        remove_task(children[child_number], task)
        children[child_number].R[employee][task] = 1

    for child_number in range(children_number):
        legal_child(children[child_number])

    return children

def select(population, children):
    n = len(population)
    all = population + children

    all.sort( key = lambda obj: obj.f)

    return all[:n]

         
defined_functions = {
    "breed": [breed],
    "mutate": [mutation],
    "select": [select],
}
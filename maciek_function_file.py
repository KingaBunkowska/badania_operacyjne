import random
from copy import deepcopy
from genetic_algorithm import Solution


def shuffle_breed(population):
    def create_child(parent1, parent2):
        num_employees = len(parent1.R)
        num_tasks = len(parent1.R[0])

        child_R = [[0 for _ in range(num_tasks)] for _ in range(num_employees)]

        for task in range(num_tasks):
            assigned = False
            fallback_candidates = []

            for emp in range(num_employees):
                prefers_parent1 = emp % 2 == 1
                preferred_value = parent1.R[emp][task] if prefers_parent1 else parent2.R[emp][task]
                fallback_value = parent2.R[emp][task] if prefers_parent1 else parent1.R[emp][task]

                if preferred_value == 1 and not assigned:
                    child_R[emp][task] = 1
                    assigned = True
                elif fallback_value == 1:
                    fallback_candidates.append(emp)

            if not assigned and fallback_candidates:
                best_emp = max(fallback_candidates)
                child_R[best_emp][task] = 1

        return Solution(child_R)

    def fix_until_legal(child):
        num_employees = len(child.R)
        num_tasks = len(child.R[0])

        for task in range(num_tasks):
            if child.is_legal():
                break

            for emp in range(num_employees):
                child.R[emp][task] = 0

        return child

    children = []

    for _ in range(len(population)//2):
        parent1 = random.choice(population)
        parent2 = random.choice(population)

        child1 = create_child(parent1, parent2)
        child2 = create_child(parent2, parent1)
        child1 = fix_until_legal(child1)
        child2 = fix_until_legal(child2)
        children.append(child1)
        children.append(child2)

    return children

def repair_mutation(children, max_attempts=1):

    for child in children:
        # if not child.is_legal():
        #     raise Exception("mutation received illegal child")


        num_employees = len(child.R)
        num_tasks = len(child.R[0])

        for task in range(num_tasks):
            assigned = any(child.R[emp][task] == 1 for emp in range(num_employees))

            if not assigned:
                old_state = deepcopy(child.R)
                success = False

                for _ in range(max_attempts):
                    candidate_emp = random.randint(0, num_employees - 1)

                    for emp in range(num_employees):
                        child.R[emp][task] = 0

                    child.R[candidate_emp][task] = 1

                    if child.is_legal():
                        success = True
                        break

                if not success:
                    child.R = old_state
        #
        # if not child.is_legal():
        #     raise Exception("mutation made illegal child")

    return children

def shuffle_mutation(children):
    for child in children:
        num_employees = len(child.R)
        num_tasks = len(child.R[0])

        task = random.randint(0, num_tasks - 1)

        current_emp = None
        for emp in range(num_employees):
            if child.R[emp][task] == 1:
                current_emp = emp
                break

        if current_emp is not None:
            new_emp = (current_emp + 1) % num_employees

            old_state = deepcopy(child.R)

            for emp in range(num_employees):
                child.R[emp][task] = 0
            child.R[new_emp][task] = 1

            if not child.is_legal():
                child.R = old_state

    return children



def select_children_by_age(population, children, max_age=5):
    for individual in population:
        individual.age += 1

    combined = [ind for ind in population + children if ind.age <= max_age]

    population_size = len(population)
    sorted_combined = sorted(combined, key=lambda ind: ind.f)

    return sorted_combined[:population_size]


defined_functions_maciek = {
    "breed": [shuffle_breed],
    "mutate": [repair_mutation, shuffle_mutation],
    "select": [select_children_by_age],
}
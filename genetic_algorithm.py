from main import get_evaluator_fn
from taskplanner import solve

class Solution():
    def __init__(self, R, loss_function=get_evaluator_fn(1, 1, 1), age=0):
        self.age = age
        self.R = R
        self.loss_function = loss_function

    def F(self, data:list):
        return self.loss_function(*data, self.R)
    

def find_best_solution(population, data):
    return max(population, key=lambda obj: obj.f(*data.values()))

def evolutionary_algorithm(
        breed_function, 
        mutate_function, 
        select_function, 
        no_generations: int, 
        population_size: int,
        data: tuple, # T, Z, p
        config: tuple # L, num_employees, num_tasks
        ):
    T, Z, p = data
    L, num_employees, num_tasks = config

    population = [solve(T, Z, L, num_employees, num_tasks) for _ in range(population_size)]

    best_solution = find_best_solution(population)

    for generation in range(no_generations):
        children = breed_function(population)
        children = mutate_function(children)
        best_child = find_best_solution(children, data)
        best_solution = best_solution if best_solution.f(data) > best_child.f(data) else best_child

        population = select_function(population, children)

    return best_solution
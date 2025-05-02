from main import get_evaluator_fn
from taskplanner import solve

class Solution():
    T = Z = p = L = num_employees = num_tasks = None
    def __init__(self, R, loss_function=get_evaluator_fn(10, 1, 100, 10), age=0):
        self.age = age
        self.R = R
        self.loss_function = loss_function

    @property
    def f(self):
        return self.loss_function(self.T, self.Z, self.p, self.R, self.L)[4]
    
    def get_detailed_f(self):
        return self.loss_function(self.T, self.Z, self.p, self.R, self.L)
    
    @classmethod
    def initialize(cls, T, Z, p, L, num_employees, num_tasks):
        cls.T = T
        cls.Z = Z
        cls.p = p
        cls.L = L
        cls.num_employees = num_employees
        cls.num_tasks = num_tasks

    @classmethod
    def get_data_and_config(cls):
        return (cls.T, cls.Z, cls.L, cls.num_employees, cls.num_tasks)
    

    def is_legal(self):
        for emp in range(self.num_employees):
            res_1 = 0

            for task in range(self.num_tasks):
                
                res_1 += self.T[emp][task] * self.R[emp][task]

                if not (0 <= self.Z[emp][task] <= 10):
                    return False
                
                if not (0 <= self.R[emp][task] <= 1):
                    return False
                
                if not (0 <= self.p[task] <= 10):
                    return False

            if not (0 <= res_1 <= self.L):
                return False

        res_5 = 0    

        for task in range(self.num_tasks):
            res_5 = 0
            for emp in range(self.num_employees):
                res_5 += self.R[emp][task]
            
            if not (0 <= res_5 <= 1):
                return False
            
        return True
    

def find_best_solution(population):
    return min(population, key=lambda obj: obj.f)

def evolutionary_algorithm(
        breed_function, 
        mutate_function, 
        select_function, 
        no_generations: int, 
        population_size: int,
        ):

    population = [Solution(solve(*Solution.get_data_and_config())) for _ in range(population_size)]
    best_solution = find_best_solution(population)

    for generation in range(no_generations):
        children = breed_function(population)
        children = mutate_function(children)

        best_child = find_best_solution(children)
        best_solution = best_solution if best_solution.f < best_child.f else best_child

        population = select_function(population, children)


    return best_solution
import importlib
import inspect
import numpy as np


def get_evaluator_fn(alpha, beta, gamma, delta):
    def evaluate(T, Z, p, R, L=40):
        time_spent = np.array(T) * np.array(R)
        time_spent_per_employee = np.sum(time_spent, axis=1)
        f1 = np.max(time_spent_per_employee) - np.min(time_spent_per_employee)
        f2 = np.sum(time_spent * (11 - np.array([p])))
        f3 = 1 / (1 + np.sum(np.sqrt(np.sum(np.array(Z) * np.array(R), axis=1))))
        f4 = np.sum(np.array([L for _ in range(len(T))]) - np.array(time_spent_per_employee))

        return alpha * f1, beta * f2, gamma * f3, delta * f4, alpha * f1 + beta * f2 + gamma * f3 + delta * f4

    return evaluate

class Solution():
    T = Z = p = L = num_employees = num_tasks = None
    alpha = beta = gamma = delta = None
    loss_function = None
    def __init__(self, R, age=0):
        self.age = age
        self.R = R
        self.loss_function = self.__class__.loss_function

    @property
    def f(self):
        return self.loss_function(self.T, self.Z, self.p, self.R, self.L)[4]
    
    def get_detailed_f(self):
        return self.loss_function(self.T, self.Z, self.p, self.R, self.L)
    
    @classmethod
    def initialize(
        cls, 
        T, 
        Z, 
        p, 
        L, 
        num_employees, 
        num_tasks, 
        alpha=10, 
        beta=1, 
        gamma=100,
        delta=10,
    ):
        cls.T = T
        cls.Z = Z
        cls.p = p
        cls.L = L
        cls.num_employees = num_employees
        cls.num_tasks = num_tasks

        cls.alpha = 10
        cls.beta = 1
        cls.gamma = 100
        cls.delta = 10

        cls.loss_function = get_evaluator_fn(alpha, beta, gamma, delta)

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

def functions_to_names(functions):
    return [f"{inspect.getmodule(f).__name__}.{f.__name__}" for f in functions]

def import_function_by_fqn(fqn):
    module, name = fqn.split(".")
    return getattr(importlib.import_module(module), name)

def evolutionary_algorithm(population, **kwargs):
    breed_function = import_function_by_fqn(kwargs["breed_function"])
    mutate_function = import_function_by_fqn(kwargs["mutate_function"])
    select_function = import_function_by_fqn(kwargs["select_function"])

    best_solution = find_best_solution(population)

    for generation in range(kwargs["no_generations"]):
        children = breed_function(population)
        children = mutate_function(children)

        best_child = find_best_solution(children)
        best_solution = best_solution if best_solution.f < best_child.f else best_child

        population = select_function(population, children)

    return best_solution
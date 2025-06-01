import numpy as np
from random import randint, shuffle, sample


class Task:
    def __init__(self, difficulty, category, priority):
        self.difficulty = difficulty
        self.category = category
        self.priority = priority

    def __repr__(self):
        return f"Task({self.difficulty} {self.category})"


class Employee:
    def __init__(self, likes_categories: [int], experience: int, comfortable_difficulty: [int], is_good_at_categories: [int]):
        self.likes_categories = likes_categories
        self.experience = experience
        self.is_good_at_categories = is_good_at_categories
        self.comfortable_difficulty = comfortable_difficulty

    def _is_comfortable_with(self, difficulty: int):
        return self.comfortable_difficulty[0] < difficulty < self.comfortable_difficulty[1]

    def predict_time(self, task: Task):
        loc = max(0, 10 - self.experience - 5 * (task.category in self.is_good_at_categories))
        scale = 4
        return int(round(task.difficulty + abs(np.random.normal(loc, scale))))

    def predict_satisfaction(self, task: Task):
        like_factor = int(task.category in self.likes_categories) \
                      + int(self._is_comfortable_with(task.difficulty))
        loc = 3 + 2 * like_factor
        scale = 2
        return int(round(np.clip(np.random.normal(loc, scale), 0, 10)))
    
    def __repr__(self):
        return f"Employee ({self.experience}) good at: {self.is_good_at_categories}"


def generate_tasks(num_tasks):
    task_difficulties = [max(1, int(x)) for x in list(np.random.normal(8, 8, (num_tasks,)))]
    tasks = [Task(difficulty, randint(0, 10), randint(0, 10)) for difficulty in task_difficulties]
    return tasks

def generate_employees(num_employees):
    categories = range(0, 10)
    employees = []
    for n in range(num_employees):
        level = randint(1, 5)
        number_of_good_categories = np.clip(randint(0, 10) + randint(0, level), 0, 10)
        number_of_liked_categories = min(10 - number_of_good_categories + randint(0, 2), 10)

        liked_categories = sample(categories, number_of_liked_categories)
        good_categories = sample(categories, number_of_liked_categories)
        comfortable_difficulty_start = max(randint(0, 15) - 2*level, 0)
        comfortable_difficulty_diff = randint(0, level**2) + randint(0, 5)
        comfortable_difficulty = (comfortable_difficulty_start, comfortable_difficulty_diff + comfortable_difficulty_start)

        employees.append(Employee(liked_categories, level, comfortable_difficulty, good_categories))
    return employees

def generate_input_matrices(employees, tasks):
    T = []
    Z = []
    p = [task.priority for task in tasks]
    for employee in employees:
        T.append([employee.predict_time(task) for task in tasks])
        Z.append([employee.predict_satisfaction(task) for task in tasks])

    return T, Z, p

def solve(T, Z, L, num_employees, num_tasks):
    tasks_order = [i for i in range(num_tasks)]
    shuffle(tasks_order)
    R = [[0 for _ in range(num_tasks)] for _ in range(num_employees)]
    for j in range(num_employees):
        time_left = L
        while time_left > 0 and len(tasks_order) > 0:
            if T[j][tasks_order[-1]] > time_left:
                break
            task = tasks_order.pop()
            R[j][task] = 1
            time_left -= T[j][task]
    return R
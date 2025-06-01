import ast
from taskplanner import Employee, Task, generate_input_matrices
import random
import numpy as np

def load_and_generate_matrices(path):
    with open(path, 'r') as file:
        first_line = file.readline()
        L = int(first_line)
        employe_list = []
        task_list = []
        for line in file:
            args = ast.literal_eval(line.strip())
            if len(args) == 4:
                employe_list.append(Employee(*args))
            else:
                task_list.append(Task(*args))

        T, Z, p = generate_input_matrices(employe_list, task_list)
        
    with open(path, "a") as file:
        file.write("\n")
        file.write("\n# Matrix T\n")
        for row in T:
            file.write(f"{row}\n")

        file.write("\n# Matrix Z\n")
        for row in Z:
            file.write(f"{row}\n")


    return L, employe_list, task_list

def load_full_file(path):
    with open(path, 'r') as file:
        lines = file.readlines()

    L = int(lines[0].strip())
    employee_list = []
    task_list = []

    i = 1
    while i < len(lines) and not lines[i].startswith("#"):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        args = ast.literal_eval(line)
        if len(args) == 4:
            employee_list.append(Employee(*args))
        else:
            task_list.append(Task(*args))
        i += 1

    while i < len(lines) and not lines[i].startswith("# Matrix T"):
        i += 1
    i += 1  

    T = []
    while i < len(lines) and not lines[i].startswith("# Matrix Z"):
        line = lines[i].strip()
        if line:
            T.append(ast.literal_eval(line))
        i += 1

    i += 1 
    Z = []
    while i < len(lines):
        line = lines[i].strip()
        if line:
            Z.append(ast.literal_eval(line))
        i += 1

    return L, employee_list, task_list, np.array(T), np.array(Z)

    
def generate_employee(category_number=10, difficulties_number=10):
    categories_comfort = random.sample(range(category_number), random.randint(0,category_number))
    experience = random.randint(1, 10)
    difficulty = random.sample(range(difficulties_number), 2)
    categories_like =  random.sample(range(category_number), random.randint(0,category_number))
    difficulty = [min(difficulty), max(difficulty)]
    employee = Employee(categories_like, experience, difficulty, categories_comfort)
    string = f"({categories_like}, {experience}, {difficulty}, {categories_comfort})\n"

    return string, employee

def generate_task(categories_number=10, difficulties_number=10, priorities_number=10):
    difficulty = random.randint(0, difficulties_number)
    category = random.randint(0, categories_number)
    priority = random.randint(0, priorities_number)

    task = Task(difficulty, category, priority)
    string = f"({difficulty}, {category}, {priority})\n"

    return string, task
    
def generate_and_save(path, L, task_number, employee_number):
    employees = []
    save_employess = []
    tasks = []
    save_tasks = []

    for _ in range(employee_number):
        s, e = generate_employee()
        employees.append(e)
        save_employess.append(s)

    for _ in range(task_number):
        s, t = generate_task()
        tasks.append(t)
        save_tasks.append(s)

    T, Z, p = generate_input_matrices(employees, tasks)
        
    with open(path, "w") as file:
        file.write(f"{L}\n")
        for i in range(employee_number):
            file.write(save_employess[i])

        for i in range(task_number):
            file.write(save_tasks[i])

        file.write("\n# Matrix T\n")
        for row in T:
            file.write(f"{row}\n")

        file.write("\n# Matrix Z\n")
        for row in Z:
            file.write(f"{row}\n")


generate_and_save("simple.txt", 40, 5, 2)

import json
import pickle
from pathlib import Path

from dominance_hierarchy_functions import (
    defined_functions as dominance_hierarchy_functions,
)
from evolutionary_functions import defined_functions as evolutionary_functions
from example_function_file import defined_functions as example_functions
from genetic_algorithm import Solution
from lukasz_function import defined_functions as lukasz_functions
from maciek_function_file import defined_functions_maciek as maciek_functions
from main import solve
from taskplanner import Employee, Task, generate_input_matrices


def get_function_dict():
    category_function_dict = {
        "breed_function": [
            *example_functions["breed"],
            *evolutionary_functions["breed"],
            *dominance_hierarchy_functions["breed"],
            *lukasz_functions["breed"],
            *maciek_functions["breed"],
        ],
        "mutate_function": [
            *example_functions["mutate"],
            *evolutionary_functions["mutate"],
            *dominance_hierarchy_functions["mutate"],
            *lukasz_functions["mutate"],
            *maciek_functions["mutate"],
        ],
        "select_function": [
            *example_functions["select"],
            *evolutionary_functions["select"],
            *dominance_hierarchy_functions["select"],
            *lukasz_functions["select"],
            *maciek_functions["select"],
        ],
    }
    return {
        category: {func.__name__: func for func in funcs}
        for category, funcs in category_function_dict.items()
    }

class FileManager():

    def __init__(self, catalog='data_files'):
        self.experiment_catalog = Path(__file__).parent / catalog
        self.data = None
        self.starting_population = None

    def load_config(self, filename="config.json", verbose=True):
        with open(self.experiment_catalog / filename, 'r') as file:
            data = json.load(file)

        required_fields = [
            "no_generations", 
            "starting_population_mode",  # "auto", "from_file"
            "breed_function", 
            "mutate_function", 
            "select_function", 
            "alpha", 
            "beta", 
            "gamma", 
            "delta",
            "L",
        ]

        for required_field in required_fields:
            if required_field not in data.keys():
                raise ValueError(
                    f"Cannot find required field {required_field} \
                    in configuration file {filename}"
                    )

        # check L

        # data load mode
        self.load_data()

        self.L = data["L"]
        num_tasks = len(self.T[0])
        num_employees = len(self.T)
        Solution.initialize(self.T, self.Z, self.p, self.L, num_employees, num_tasks)

        if data["starting_population_mode"] not in ("auto", "from_file"):
            raise ValueError(
                f"Unexpected value of 'starting_population_mode': \
                {data["starting_population_mode"]}. Expected: 'auto' or 'from_file'"
                )

        if data["starting_population_mode"] == "auto":
            if "starting_population_size" not in data.keys():
                raise ValueError("Specify population size when using mode 'auto'")
            if not isinstance(data["starting_population_size"], int) \
                or data["starting_population_size"] < 2:
                raise ValueError("'starting_population_size' must be an integer ≥ 2.")
            
            self.starting_population = [
                Solution(solve(*Solution.get_data_and_config()))
                for _ in range(data["starting_population_size"])
            ]
            print(f"Number of individuals in the initial population: \
                  {len(self.starting_population)}.")

        else: # starting_population_mode = "from_file":
            file_path = data["starting_population_file"]
            if not isinstance(file_path, str) or file_path.endswith(".pkl"):
                raise ValueError(
                    f"Invalid 'starting_population_file': \
                    expected a string ending with '.pkl', got {repr(file_path)}"
                )
            
            with open(file_path, "rb") as f:
                self.starting_population = pickle.load(f)

            for pop in self.starting_population:
                if not isinstance(pop, Solution):
                    raise ValueError(f"Error during parsing file: {file_path}")
            
            if verbose:
                print(
                    f"Number of individuals in the starting population: \
                    {len(self.starting_population)}."
                )

        function_dict = get_function_dict()

        self.breed_function = function_dict["breed_function"].get(data["breed_function"])
        self.mutate_function = function_dict["mutate_function"].get(data["mutate_function"])
        self.select_function = function_dict["select_function"].get(data["select_function"])

        if self.breed_function is None:
            raise ValueError(
                f"Cannot find function {data["breed_function"]}. \
                Try to one of: {', '.join(function_dict["breed_function"].keys())}"
            )
        if self.mutate_function is None:
            raise ValueError(
                f"Cannot find function {data["mutate_function"]}. \
                Try to one of: {', '.join(function_dict["mutate_function"].keys())}"
            )
        if self.select_function is None:
            raise ValueError(
                f"Cannot find function {data["select_function"]}. \
                Try to one of: {', '.join(function_dict["select_function"].keys())}"
            )

        self.data = data

    def get_evolutionary_algorithm_arguments(self):
        return (
            self.starting_population,
            self.breed_function,
            self.mutate_function,
            self.select_function,
            self.data["no_generations"],
        )


    def load_data(self):
        self._load_tasks_employees()

    def _load_tasks_employees(self):
        tasks = load_tasks_from_json(self.experiment_catalog / "tasks.json")
        employees = load_employees_from_json(self.experiment_catalog / "employees.json")

        self.T, self.Z, self.p = generate_input_matrices(employees, tasks)

def save_tasks_to_json(tasks, filepath):
    data = [
        {
            "difficulty": task.difficulty,
            "category": task.category,
            "priority": task.priority
        }
        for task in tasks
    ]
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def validate_task(task_dict):
    if not (0 <= int(task_dict["priority"]) <= 10):
        raise ValueError(f"Task priority must be an integer between 0 and 10; \
                         got {task_dict['priority']}.")

def load_tasks_from_json(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)

    tasks = []
    for i, item in enumerate(data):
        try:
            validate_task(item)
            difficulty = int(item["difficulty"])
            category = int(item["category"])
            priority = int(item["priority"])
            tasks.append(Task(difficulty, category, priority))
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"Invalid task format at index {i}: {e}")
    return tasks

def save_employees_to_json(employees, filepath):
    data = [
        {
            "likes_categories": e.likes_categories,
            "experience": e.experience,
            "comfortable_difficulty": e.comfortable_difficulty,
            "is_good_at_categories": e.is_good_at_categories,
        }
        for e in employees
    ]
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def load_employees_from_json(filepath):
    with open(filepath, 'r') as f:
        raw_data = json.load(f)

    employees = []
    for i, entry in enumerate(raw_data):
        try:
            emp = Employee(
                likes_categories=entry["likes_categories"],
                experience=entry["experience"],
                comfortable_difficulty=entry["comfortable_difficulty"],
                is_good_at_categories=entry["is_good_at_categories"]
            )
            employees.append(emp)
        except ValueError as e:
            raise ValueError(f"Invalid data for employee #{i}: {e}")

    return employees

if __name__ == "__main__":
    # config_path = Path(__file__).parent / "config.json"
    # print(load_config(config_path))

    # tasks = generate_tasks(10)
    # print(tasks)
    # save_tasks_to_json(tasks, "./data_files/tasks.json")
    # tasks_loaded = load_tasks_from_json("./data_files/tasks.json")
    # print(tasks_loaded)

    # employees = [
    #     Employee([1, 3, 4, 10], 3, [3, 10], [1, 3, 4]),
    #     Employee([1], 5, [0, 99], [1]),
    #     Employee([x for x in range(10)], 0, [0, 5], []),
    #     Employee([], 10, [0, 99], [x for x in range(10)]),
    # ]
    # print(employees)

    # save_employees_to_json(employees, "./data_files/employees.json")
    # emp = load_employees_from_json("./data_files/employees.json")
    # print(emp)

    manager = FileManager()
    manager.load_config()
    # manager.load_data()

    from genetic_algorithm import evolutionary_algorithm

    # print(manager.starting_population[0].R)
    # print(manager.get_evolutionary_algorithm_arguments()[0][0].R)

    print(evolutionary_algorithm(*manager.get_evolutionary_algorithm_arguments()).R)

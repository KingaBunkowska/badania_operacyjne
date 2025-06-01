import inspect
import json
from pathlib import Path
import os
import time
from uuid import uuid1

from dominance_hierarchy_functions import (
    defined_functions as dominance_hierarchy_functions,
)
from evolutionary_functions import defined_functions as evolutionary_functions
from example_function_file import defined_functions as example_functions
from genetic_algorithm import Solution
from lukasz_function import defined_functions as lukasz_functions
from maciek_function_file import defined_functions_maciek as maciek_functions
from taskplanner import solve
from taskplanner import Employee, Task, generate_input_matrices, generate_tasks, generate_employees



def get_function_names_dict():
    category_function_names_dict = {
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
        category: {
            func.__name__: f"{inspect.getmodule(func).__name__}.{func.__name__}"
            for func in funcs
        }
        for category, funcs in category_function_names_dict.items()
    }

class FileManager():

    def __init__(self, catalog='data_files'):
        self.experiment_catalog = Path(__file__).parent / catalog
        os.makedirs(os.path.dirname(self.experiment_catalog / catalog), exist_ok=True)
        self.data = None
        self.starting_population = None

    def load_config(self, filename="config.json", verbose=True):
        """
        Loads the configuration file (default: `"config.json"`) from the experiment directory
        provided during Manager initialization.

        The configuration file must be a JSON file containing the following required fields:

        - `no_generations`: number of generations to run the algorithm
        - `starting_population_mode`: strategy for initializing the population; either `"auto"` or `"from_file"`
            * `"auto"` - requires an additional field `starting_population_size` with an integer specifying how many individuals should be generated
            * `"from_file"` - requires an additional field `starting_population_file` with the name of a JSON file (in the experiment directory) containing a list of `R` matrices to be used as the initial population
        - `breed_function`: name of the breeding function to use
        - `mutate_function`: name of the mutation function to use
        - `select_function`: name of the selection function to use
        - `alpha`: weight of the `f1` component of the loss function (even distribution of time among employees)
        - `beta`: weight of the `f2` component of the loss function (spending time on higher-priority tasks)
        - `gamma`: weight of the `f3` component of the loss function (employee satisfaction)
        - `delta`: weight of the `f4` component of the loss function (maximizing employee working time)
        - `L`: employee time budget (hard constraint)
        - `data_load_mode`: how input data is loaded; either `"matrices"` or `"generated"`
            * `"matrices"` - requires files `T.json`, `Z.json`, and `p.json` with the corresponding matrices in the experiment directory.  
            * `"generated"` - requires files `employees.json` and `tasks.json` in the experiment directory.  
                - The `employees.json` file should contain a list of employee objects, where each employee is represented as a dictionary with the following fields:
                    * `likes_categories` - list of category IDs the employee prefers
                    * `experience` - integer representing experience level (the higher, the more experienced)
                    * `comfortable_difficulty` - list representing the range of task difficulties the employee is comfortable with
                    * `is_good_at_categories` - list of category IDs the employee is skilled in
                - The `tasks.json` file should contain a list of task objects, where each task is represented as a dictionary with the following fields:
                    * `difficulty` - integer indicating how difficult the task is (the higher, the more difficult)
                    * `category` - category ID of the task
                    * `priority` - integer from 0 to 10 (the higher, the more important the task)
            * `"auto"` - requires fileds `"num_tasks"` and `"num_employees"` to be provided as positive integers. Mock data will be automatically generated based on these counts.

        If the optional field `save_matrices` is included in the configuration, the files `T.json`, `Z.json`, `p.json`, and `starting_population.json` will be saved inside the log directory. These files can be used to replicate the experiment or to test other methods on the same data.

        """
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
            "data_load_mode" # "matrices", "generated", "auto"
        ]

        self.data = data
        self._validate_required_fields(filename, data, required_fields)

        self._validate_L(data)

        self._validate_data_load_mode(data)

        self.load_data()

        self.L = data["L"]

        num_tasks = len(self.T[0])
        num_employees = len(self.T)
        Solution.initialize(
            self.T, 
            self.Z, 
            self.p, 
            self.L, 
            num_employees, 
            num_tasks, 
            data["alpha"],
            data["beta"],
            data["gamma"],
            data["delta"],
        )

        self._starting_population_logic(verbose, data)

        self.validate_and_transform_function_names(data)

    def validate_and_transform_function_names(self, data):
        function_names_dict = get_function_names_dict()
        self.breed_function_fqn = function_names_dict["breed_function"].get(data["breed_function"])
        self.mutate_function_fqn = function_names_dict["mutate_function"].get(data["mutate_function"])
        self.select_function_fqn = function_names_dict["select_function"].get(data["select_function"])

        if self.breed_function_fqn is None:
            raise ValueError(
                f"Cannot find function {data["breed_function"]}. "
                f"Try one of: {', '.join(function_names_dict["breed_function"].keys())}"
            )
        if self.mutate_function_fqn is None:
            raise ValueError(
                f"Cannot find function {data["mutate_function"]}. "
                f"Try one of: {', '.join(function_names_dict["mutate_function"].keys())}"
            )
        if self.select_function_fqn is None:
            raise ValueError(
                f"Cannot find function {data["select_function"]}. "
                f"Try one of: {', '.join(function_names_dict["select_function"].keys())}"
            )

    def _starting_population_logic(self, verbose, data):
        if data["starting_population_mode"] not in ("auto", "from_file"):
            raise ValueError(
                "Unexpected value of 'starting_population_mode':"
                f"{data["starting_population_mode"]}. Expected: 'auto' or 'from_file'"
                )

        if data["starting_population_mode"] == "auto":
            if "starting_population_size" not in data.keys():
                raise ValueError("Specify population size when using mode 'auto'. Use parameter: 'starting_population_size")
            if (
                not isinstance(data["starting_population_size"], int) 
                or data["starting_population_size"] < 2
            ):
                raise ValueError("'starting_population_size' must be an integer ≥ 2.")
            
            self.starting_population = [
                Solution(solve(*Solution.get_data_and_config()))
                for _ in range(data["starting_population_size"])
            ]
            if verbose:
                print("Number of individuals in the initial population: "
                    f"{len(self.starting_population)}.")

        else: # starting_population_mode = "from_file":
            file_path = data["starting_population_file"]
            if not isinstance(file_path, str) or not file_path.endswith(".json"):
                raise ValueError(
                    "Invalid 'starting_population_file': "
                    f"expected a string ending with '.json', got {repr(file_path)}"
                )
            
            with open(self.experiment_catalog / file_path, "rb") as f:
                self.starting_population = self.load_solutions_from_json("starting_population.json")

            for pop in self.starting_population:
                if not isinstance(pop, Solution):
                    raise ValueError(f"Error during parsing file: {file_path}")
            
            if verbose:
                print(
                    "Number of individuals in the starting population: "
                    f"{len(self.starting_population)}."
                )

    def _validate_data_load_mode(self, data):
        if data["data_load_mode"] not in ("matrices", "generated", "auto"):
            raise ValueError(
                "Unexpected value of 'data_load_mode':"
                f"{data["data_load_mode"]}. Expected: 'matrices', 'generated' or 'auto'"
                )
        
        if data["data_load_mode"] == "auto" and (
            "num_employees" not in data.keys() 
            or not isinstance(data["num_employees"], int) 
            or data["num_employees"] <= 0
        ):
            raise ValueError(
                f"In 'auto' mode, you must provide a 'num_employees' field with a positive integer value."
            )

        if data["data_load_mode"] == "auto" and (
            "num_tasks" not in data.keys() 
            or not isinstance(data["num_tasks"], int) 
            or data["num_tasks"] <= 0
        ):
            raise ValueError(
                f"In 'auto' mode, you must provide a 'num_tasks' field with a positive integer value."
            )


    def _validate_required_fields(self, filename, data, required_fields):
        for required_field in required_fields:
            if required_field not in data.keys():
                raise ValueError(
                    f"Cannot find required field {required_field} "
                    f"in configuration file {filename}"
                    )

    def _validate_L(self, data):
        if not isinstance(data["L"], int) or data["L"] <= 0:
            raise ValueError(
                "L must be integer > 0"
            )

    def get_evolutionary_algorithm_arguments(self):
        return {
            "population": self.starting_population,
            "breed_function": self.breed_function_fqn,
            "mutate_function": self.mutate_function_fqn,
            "select_function": self.select_function_fqn,
            "no_generations": self.data["no_generations"],
        }

    def load_data(self):
        if self.data["data_load_mode"] == "generated":
            self._load_tasks_employees()
        elif self.data["data_load_mode"] == "auto":
            self._generate_data(self.data["num_tasks"], self.data["num_employees"])
        else: # "data_load_mode" = "matrices"
            self._load_T_Z_p()

    def _load_tasks_employees(self):
        tasks = self.load_tasks_from_json("tasks.json")
        employees = self.load_employees_from_json("employees.json")

        self.T, self.Z, self.p = generate_input_matrices(employees, tasks)

    def _load_T_Z_p(self):
        self.T = self.load_matrix_from_json("T.json")
        self.Z = self.load_matrix_from_json("Z.json")
        self.p = self.load_matrix_from_json("p.json")

    def _generate_data(self, num_tasks, num_employees):
        tasks = generate_tasks(num_tasks)
        employees = generate_employees(num_employees)

        self.T, self.Z, self.p = generate_input_matrices(employees, tasks)

    def _validate_task(self, task_dict):
        if not (0 <= int(task_dict["priority"]) <= 10):
            raise ValueError(
                "Task priority must be an integer between 0 and 10; "
                f"got {task_dict['priority']}.")

    def load_tasks_from_json(self, filename="tasks.json"):
        with open(self.experiment_catalog / filename, 'r') as f:
            data = json.load(f)

        tasks = []
        for i, item in enumerate(data):
            try:
                self._validate_task(item)
                difficulty = int(item["difficulty"])
                category = int(item["category"])
                priority = int(item["priority"])
                tasks.append(Task(difficulty, category, priority))
            except (KeyError, ValueError, TypeError) as e:
                raise ValueError(f"Invalid task format at index {i}: {e}")
        return tasks

    def load_employees_from_json(self, filename="employees.json"):
        with open(self.experiment_catalog / filename, 'r') as f:
            raw_data = json.load(f)

        employees = []
        for i, entry in enumerate(raw_data):
            try:
                emp = Employee(
                    **entry
                )
                employees.append(emp)
            except ValueError as e:
                raise ValueError(f"Invalid data for employee #{i}: {e}")

        return employees

    def save_tasks_to_json(self, tasks, filename="tasks.json"):
        data = [
            {
                "difficulty": task.difficulty,
                "category": task.category,
                "priority": task.priority
            }
            for task in tasks
        ]
        with open(self.experiment_catalog / filename, 'w') as f:
            json.dump(data, f, indent=2)

    def save_employees_to_json(self, employees, filename="employees.json"):
        data = [
            {
                "likes_categories": e.likes_categories,
                "experience": e.experience,
                "comfortable_difficulty": e.comfortable_difficulty,
                "is_good_at_categories": e.is_good_at_categories,
            }
            for e in employees
        ]
        with open(self.experiment_catalog / filename, 'w') as f:
            json.dump(data, f, indent=2)

    def load_matrix_from_json(self, filename):
        with open(self.experiment_catalog / filename, "r") as f:
            matrix = json.load(f)

        return matrix

    def save_matrix_to_json(self, filename, matrix, flag="w"):
        with open(self.experiment_catalog / filename, flag) as f:
            json.dump(matrix, f)
            f.write('\n')

    def save_solutions_to_json(self, filename, solutions: list[Solution], flag="w"):
        Rs = [sol.R for sol in solutions]
        with open(self.experiment_catalog / filename, flag) as f:
            json.dump(Rs, f)

    def load_solutions_from_json(self, filename):
        with open(self.experiment_catalog / filename, 'r') as f:
            Rs = json.load(f)
        return [Solution(R) for R in Rs]

class Logger(FileManager):
    def __init__(self, catalog='data_files', experiment_results_catalog=None):
        super().__init__(catalog)
        if experiment_results_catalog is None:
            self.experiment_results_catalog = self._get_next_catalog()
        elif os.path.isdir(self.experiment_catalog / experiment_results_catalog):
            self.experiment_results_catalog = self._get_next_catalog()
            print(f"Catalog already exists. Using {self.experiment_results_catalog} instead.")
        else:
            self.experiment_results_catalog = experiment_results_catalog

        self.experiment_results_full_path = self.experiment_catalog / self.experiment_results_catalog

        os.makedirs(self.experiment_results_full_path)
        self.iter_number = 0
        self.time_of_start = time.time()

        print(f"Logs available in directory: {self.experiment_results_full_path}")

    def _get_next_catalog(self, name="experiment_data"):
        return f"{name}_{uuid1()}"

    def init_time_of_start(self, time):
        self.time_of_start = time

    def log_iteration(self, solution: Solution, fs: list[float], time: int):
        self.save_matrix_to_json(
            self.experiment_results_full_path / "solutions.txt",
            solution.R,
            flag = "a"
        )
        csv_headers = ["iteration", "time_from_start", "f1", "f2", "f3", "f4", "f"]
        headers_str = ",".join(csv_headers)
        csv_values = [self.iter_number, time-self.time_of_start] + list(fs)
        values_str = ",".join(f"{v:.3f}" for v in csv_values)
        with open(self.experiment_results_full_path / "results.csv", "a") as results:
            if self.iter_number == 0:
                results.write(headers_str+"\n")
            results.write(values_str+"\n")
        self.iter_number += 1

    def load_config(self, filename="config.json", verbose=True):
        super().load_config(filename, verbose)
        if "save_matrices" in self.data.keys():
            self._save_matrices()


    def _save_matrices(self):
        self.save_solutions_to_json(f"{self.experiment_results_full_path}/starting_population.json", self.starting_population)
        self.save_matrix_to_json(f"{self.experiment_results_full_path}/T.json", self.T)
        self.save_matrix_to_json(f"{self.experiment_results_full_path}/Z.json", self.Z)
        self.save_matrix_to_json(f"{self.experiment_results_full_path}/p.json", self.p)

if __name__ == "__main__":
    manager = FileManager("data_files")
    manager.save_tasks_to_json(generate_tasks(50))
    manager.save_employees_to_json(generate_employees(10))
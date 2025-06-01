## About this repository

This repository contains the implementation of a genetic algorithm developed as part of the **Operational Research** course (academic year 2024/2025).

The algorithm addresses the task assignment problem for a group of employees, balancing workloads and prioritizing tasks while respecting individual employee preferences and constraints.

---

### Problem Statement

The project solves the problem of assigning tasks to employees, each with a fixed time budget and varying expertise levels. Tasks have priorities, and employees have different preferences and skill levels regarding tasks. The goal is to balance employee workloads while maximizing the priority of assigned tasks and ensuring employee satisfaction.

---

### Mathematical Model (Summary)

- **Tasks:** \(i = 1, $\ldots$, n\)
- **Employees:** \(j = 1, $\ldots$, m\)
- **Variables:**
  - \($T_{ij}$\) — time employee \($j$\) spends on task \($i$\)
  - \($p_i$\) — priority of task \($i$\) (0 to 10)
  - \($L$\) — maximum available working time per employee
  - \($Z_{ij}$\) — satisfaction of employee \($j$\) working on task \($i$\)
  - \($R_{ij}$\) — decision variable indicating assignment (0 or 1)

The model includes constraints on working time limits and task assignments, ensuring feasible and balanced schedules.

The objective function combines four weighted components:

$F = \alpha f_1 + \beta f_2 + \gamma f_3 + \delta f_4$

where:
- $f_1$ — minimizes workload difference between employees
- $f_2$ — minimizes time spent on low-priority tasks
- $f_3$ — maximizes employee satisfaction
- $f_4$ — maximizes employee working time utilization
---

## How to use

#### Installing dependencies
```bash
pip install -r requirements.txt
```
#### Running program
```bash
python main.py [experiment_catalog_name] [log_catalog_name]
```
- `experiment_catalog_name` (optional):
Name of the folder containing experiment data. This folder should be located in the working directory and contain a `config.json` file, along with any other required files.

- `log_catalog_name` (optional):
Name of the folder where logs will be saved. Folder will be located inside experiement catalog. If not present folder will be automaticly generated.


### Experiment Configuration (`config.json`)

Each experiment requires a `config.json` file located in the experiment directory. This configuration file defines all necessary parameters to run the algorithm.

#### Required fields:

- **`no_generations`** – number of generations the algorithm should run.
- **`starting_population_mode`** – how the initial population is created:
  - `"auto"` – requires an additional field `starting_population_size` specifying how many individuals to generate automatically.
  - `"from_file"` – requires `starting_population_file`, a JSON file containing a list of `R` matrices to be used as the starting population.
- **`breed_function`**, **`mutate_function`**, **`select_function`** – names of the functions used for breeding, mutation, and selection.
- **`alpha`**, **`beta`**, **`gamma`**, **`delta`** – weights for the components of the loss function:
  - `f1` – encourages even distribution of time among employees.
  - `f2` – prioritizes tasks with higher importance.
  - `f3` – accounts for employee satisfaction.
  - `f4` – maximizes employee working time.
- **`L`** – time budget per employee (a hard constraint).
- **`data_load_mode`** – how input data is provided:
  - `"matrices"` – requires the presence of `T.json`, `Z.json`, and `p.json` files with the corresponding matrices in the experiment directory.
  - `"generated"` – requires both `employees.json` and `tasks.json` files describing the data structure:
    - **`employees.json`** should be a list of employee objects, each with:
      - `likes_categories`: list of preferred category IDs
      - `experience`: integer representing experience level
      - `comfortable_difficulty`: list defining the acceptable difficulty range
      - `is_good_at_categories`: list of category IDs the employee is skilled in
    - **`tasks.json`** should be a list of task objects, each with:
      - `difficulty`: integer indicating the task’s difficulty
      - `category`: category ID of the task
      - `priority`: integer from 0 to 10 indicating task importance
  - `"auto"` - requires `num_tasks` and `num_employees`. Mock data will be automatically generated based on these counts. 

---

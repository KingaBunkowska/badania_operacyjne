import os
import sys
import time

from genetic_algorithm import evolutionary_algorithm
from file_manager import FileManager, Logger

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Folder name not specified; using default='experiments'")
        folder_name = 'experiments'
        experiment_results_catalog = None
    elif len(sys.argv) < 3:
        folder_name = sys.argv[1]
        experiment_results_catalog = None
    else:
        folder_name = sys.argv[1]
        experiment_results_catalog = sys.argv[2]

    file_manager = Logger(folder_name, experiment_results_catalog)
    file_manager.load_config()

    file_manager.init_time_of_start(time.time())
    best_solution = evolutionary_algorithm(
        logger=file_manager, 
        **file_manager.get_evolutionary_algorithm_arguments()
    )




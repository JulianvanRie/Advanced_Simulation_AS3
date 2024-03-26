from model import BangladeshModel
from model import BangladeshModel
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time
import sys

"""
    Run simulation
    Print output at terminal
"""

# # ---------------------------------------------------------------
#
# # run time 5 x 24 hours; 1 tick 1 minute
# run_length = 100
#
# # run time 1000 ticks
# # run_length = 1000
#
# seed = 1234568
#
#
# sim_model = BangladeshModel(scenario_probabilities={'A': 10, 'B': 20, 'C': 40, 'D': 80},seed=seed)
#
# # Check if the seed is set
# print("SEED " + str(sim_model._seed))
#
# # One run with given steps
# for i in range(run_length):
#     sim_model.step()
#
# # for path in sim_model.path_ids_dict:
# #     print(sim_model.path_ids_dict[path])

start = time.time()
"""
    Run simulation
    Print output at terminal
"""

# ---------------------------------------------------------------
def run_all_scenarios(seeds, run_length, scenarios):
    sys.setrecursionlimit(9999999)
    all_scenario_results = {}
    for scenario_index, scenario in enumerate(scenarios, start=0):
        print(f"Running scenario {scenario_index} with probabilities {scenario}")
        batch_results = {}
        for seed in seeds:
            print("running seed", seed)
            model = BangladeshModel(seed=seed, scenario_probabilities=scenario)
            for i in range(run_length):
                model.step()
            bridges_data = [{"unique_id": bridge.unique_id,
                             "name": bridge.name,
                             'condition': bridge.condition,
                             'length': bridge.length,
                             'total_delay_time': bridge.total_delay_time,
                             "delay_time_per_vehicle": bridge.delay_time,
                             "break_down_chance": bridge.break_down_chance,
                             "breaks_down": bridge.breaks_down} for bridge in model.bridges]
            batch_results[seed] = pd.DataFrame(bridges_data)
        all_scenario_results[f"Scenario_{scenario_index}"] = batch_results
    return all_scenario_results

# Define your scenarios
scenarios = [
    {'A': 0, 'B': 0, 'C': 0, 'D': 0},  # Scenario 0
    {'A': 0, 'B': 0, 'C': 0, 'D': 5},  # Scenario 1
    {'A': 0, 'B': 0, 'C': 0, 'D': 10},  # Scenario 2
    {'A': 0, 'B': 0, 'C': 5, 'D': 10},  # Scenario 3
    {'A': 0, 'B': 0, 'C': 10, 'D': 20},  # Scenario 4
    {'A': 0, 'B': 5, 'C': 10, 'D': 20},  # Scenario 5
    {'A': 0, 'B': 10, 'C': 20, 'D': 40},  # Scenario 6
    {'A': 5, 'B': 10, 'C': 20, 'D': 40},  # Scenario 7
    {'A': 10, 'B': 20, 'C': 40, 'D': 80},  # Scenario 8
    # Add more scenarios as needed
]

# Set your seeds and run length
seeds = range(1, 11)  # 10 seeds for each scenario
# run_length = 5 * 24 * 60  # Example run length
run_length = 7200
# Run all scenarios
all_scenario_results = run_all_scenarios(seeds, run_length, scenarios)

end = time.time()
print('run length', end - start)

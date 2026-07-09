# import csv
# import random
# import time
# import os
# from multiprocessing import Pool, cpu_count
# from collections import defaultdict
# import numpy as np

# def evaluate_ite(c, t, e):
#     """Pure operational tracking for an un-negated ITE node."""
#     return t if c == 1 else e

# def run_single_influence_run(h, m):
#     """
#     Evaluates individual variable contingency for Variable 1 (index 0).
#     Leaves are generated directly without NOT gates.
#     """
#     n_leaves = 3**h
    
#     # Selection pool: 0 to m-1 are variables, m is constant 0, m+1 is constant 1
#     leaves = [random.randrange(m + 2) for _ in range(n_leaves)]
    
#     # 1. Pick a random baseline truth assignment for all m variables
#     assignment_orig = [random.choice([0, 1]) for _ in range(m)]
    
#     # 2. Duplicate and flip ONLY Variable 1 (index 0)
#     assignment_flip = list(assignment_orig)
#     if m > 0:
#         assignment_flip[0] = 1 - assignment_orig[0]
        
#     # 3. Formulate the raw input layer values
#     layer_orig = []
#     layer_flip = []
#     for leaf in leaves:
#         if leaf < m:
#             layer_orig.append(assignment_orig[leaf])
#             layer_flip.append(assignment_flip[leaf])
#         elif leaf == m:
#             layer_orig.append(0)
#             layer_flip.append(0)
#         else:
#             layer_orig.append(1)
#             layer_flip.append(1)
            
#     # 4. Evaluate the ternary structure bottom-up
#     while len(layer_orig) > 1:
#         next_layer_orig = []
#         next_layer_flip = []
#         for i in range(0, len(layer_orig), 3):
#             c_o, t_o, e_o = layer_orig[i:i+3]
#             next_layer_orig.append(evaluate_ite(c_o, t_o, e_o))
            
#             c_f, t_f, e_f = layer_flip[i:i+3]
#             next_layer_flip.append(evaluate_ite(c_f, t_f, e_f))
#         layer_orig = next_layer_orig
#         layer_flip = next_layer_flip
        
#     # 5. Return 1 if flipping Variable 1 altered the global formula outcome
#     return 1 if layer_orig[0] != layer_flip[0] else 0

# def run_batch_influence(args):
#     h, m, batch_size = args
#     hits = 0
#     for _ in range(batch_size):
#         hits += run_single_influence_run(h, m)
#     return (h, m, hits, batch_size)

# if __name__ == "__main__":
#     H_VALUE = 9
#     # M_VALUES = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384]
#     M_VALUES = np.linspace(1,100, 40, dtype=int)
#     # M_VALUES = np.linspace(1,400,20, dtype=int)
#     RUNS = 2000
#     BATCH_SIZE = 100 
    
#     os.makedirs("results/csv", exist_ok=True)
#     OUTPUT_FILE = f"results/csv/variable_influence_transition_h{H_VALUE}_again.csv"

#     tasks = [(H_VALUE, m, BATCH_SIZE) for m in M_VALUES for _ in range(0, RUNS, BATCH_SIZE)]
#     results = defaultdict(lambda: {"hits": 0, "runs": 0})

#     print(f"Executing Influence Simulation on {cpu_count()} CPU cores...")
#     start_time = time.time()

#     with Pool(processes=cpu_count()) as pool:
#         for h, m, hits, runs in pool.imap_unordered(run_batch_influence, tasks):
#             results[m]["hits"] += hits
#             results[m]["runs"] += runs

#     print("\nWriting Phase Transition data to CSV...")
#     with open(OUTPUT_FILE, mode='w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(["m", "individual_influence_probability"])
#         for m in sorted(results.keys()):
#             prob = results[m]["hits"] / results[m]["runs"]
#             writer.writerow([m, prob])
#             print(f"Pool size m={m:3d} | Variable 1 Global Influence: {prob:.5f}")

#     print(f"\nSaved csv to {OUTPUT_FILE} in {time.time() - start_time:.2f} seconds.")


# import csv
# import random
# import time
# import os
# from multiprocessing import Pool, cpu_count
# from collections import defaultdict

# def evaluate_ite(c, t, e):
#     return t if c == 1 else e

# def run_single_influence_run(h, m):
#     n_leaves = 3**h
#     leaves = [random.randrange(m + 2) for _ in range(n_leaves)]
#     assignment_orig = [random.choice([0, 1]) for _ in range(m)]
    
#     assignment_flip = list(assignment_orig)
#     if m > 0:
#         assignment_flip[0] = 1 - assignment_orig[0]
        
#     layer_orig, layer_flip = [], []
#     for leaf in leaves:
#         if leaf < m:
#             layer_orig.append(assignment_orig[leaf])
#             layer_flip.append(assignment_flip[leaf])
#         elif leaf == m:
#             layer_orig.append(0); layer_flip.append(0)
#         else:
#             layer_orig.append(1); layer_flip.append(1)
            
#     while len(layer_orig) > 1:
#         next_layer_orig, next_layer_flip = [], []
#         for i in range(0, len(layer_orig), 3):
#             c_o, t_o, e_o = layer_orig[i:i+3]
#             next_layer_orig.append(evaluate_ite(c_o, t_o, e_o))
#             c_f, t_f, e_f = layer_flip[i:i+3]
#             next_layer_flip.append(evaluate_ite(c_f, t_f, e_f))
#         layer_orig, layer_flip = next_layer_orig, next_layer_flip
        
#     return 1 if layer_orig[0] != layer_flip[0] else 0

# def run_batch_influence(args):
#     h, m, batch_size = args
#     hits = 0
#     for _ in range(batch_size):
#         hits += run_single_influence_run(h, m)
#     return (h, m, hits, batch_size)

# if __name__ == "__main__":
#     HEIGHTS = range(0,11)
#     M_VALUES = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
#     RUNS = 2000
#     BATCH_SIZE = 100
    
#     os.makedirs("results/csv", exist_ok=True)
#     OUTPUT_FILE = "results/csv/pure_variable_scaling_data.csv"
    
#     tasks = [(h, m, BATCH_SIZE) for h in HEIGHTS for m in M_VALUES for _ in range(0, RUNS, BATCH_SIZE)]
#     results = defaultdict(lambda: {"hits": 0, "runs": 0})
    
#     print(f"Running Pure Variable Scaling Simulation using {cpu_count()} cores...")
#     start_time = time.time()
    
#     with Pool(processes=cpu_count()) as pool:
#         for h, m, hits, runs in pool.imap_unordered(run_batch_influence, tasks):
#             results[(h, m)]["hits"] += hits
#             results[(h, m)]["runs"] += runs
            
#     with open(OUTPUT_FILE, mode='w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(["h", "m", "influence_probability"])
#         for (h, m) in sorted(results.keys()):
#             prob = results[(h, m)]["hits"] / results[(h, m)]["runs"]
#             writer.writerow([h, m, prob])
            
#     print(f"Saved dataset cleanly to {OUTPUT_FILE} in {time.time() - start_time:.2f}s.")


import csv
import random
import time
import os
from multiprocessing import Pool, cpu_count
from collections import defaultdict
import numpy as np

def evaluate_ite(c, t, e):
    """Pure operational tracking for an un-negated ITE node."""
    return t if c == 1 else e

def run_single_influence_run(h, m, allow_negations=False):
    """
    Evaluates individual variable contingency for Variable 1 (index 0).
    """
    n_leaves = 3**h
    
    # 1. Pick a random baseline truth assignment for all m variables
    assignment_orig = [random.choice([0, 1]) for _ in range(m)]
    
    # 2. Duplicate and flip ONLY Variable 1 (index 0)
    assignment_flip = list(assignment_orig)
    if m > 0:
        assignment_flip[0] = 1 - assignment_orig[0]
        
    # 3. Formulate the raw input layer values
    layer_orig = []
    layer_flip = []
    
    if allow_negations:
        alphabet_size = 2 * m + 2
        for _ in range(n_leaves):
            leaf = random.randrange(alphabet_size)
            if leaf < 2 * m:
                # Even numbers are positive vars, odd are negative vars
                var_idx = leaf // 2
                is_neg = (leaf % 2 == 1)
                
                val_o = assignment_orig[var_idx]
                val_f = assignment_flip[var_idx]
                
                layer_orig.append(1 - val_o if is_neg else val_o)
                layer_flip.append(1 - val_f if is_neg else val_f)
            elif leaf == 2 * m: # Constant 0
                layer_orig.append(0)
                layer_flip.append(0)
            else:               # Constant 1
                layer_orig.append(1)
                layer_flip.append(1)
    else:
        # YOUR ORIGINAL LOGIC for restricted alphabet
        alphabet_size = m + 2
        for _ in range(n_leaves):
            leaf = random.randrange(alphabet_size)
            if leaf < m:
                layer_orig.append(assignment_orig[leaf])
                layer_flip.append(assignment_flip[leaf])
            elif leaf == m:
                layer_orig.append(0)
                layer_flip.append(0)
            else:
                layer_orig.append(1)
                layer_flip.append(1)
            
    # 4. Evaluate the ternary structure bottom-up
    while len(layer_orig) > 1:
        next_layer_orig = []
        next_layer_flip = []
        for i in range(0, len(layer_orig), 3):
            c_o, t_o, e_o = layer_orig[i:i+3]
            next_layer_orig.append(t_o if c_o == 1 else e_o)
            
            c_f, t_f, e_f = layer_flip[i:i+3]
            next_layer_flip.append(t_f if c_f == 1 else e_f)
        layer_orig = next_layer_orig
        layer_flip = next_layer_flip
        
    # 5. Return 1 if flipping Variable 1 altered the global formula outcome
    return 1 if layer_orig[0] != layer_flip[0] else 0

def run_batch_influence(args):
    h, m, batch_size = args
    hits = 0
    for _ in range(batch_size):
        hits += run_single_influence_run(h, m)
    return (h, m, hits, batch_size)

if __name__ == "__main__":
    H_VALUE = 7
    M_VALUES = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384]
    # M_VALUES = [100,200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000]
    # M_VALUES = np.linspace(1,400,20, dtype=int)
    RUNS = 5000
    BATCH_SIZE = 100 
    
    os.makedirs("results/csv", exist_ok=True)
    OUTPUT_FILE = f"results/csv/variable_influence_transition_h{H_VALUE}.csv"

    tasks = [(H_VALUE, m, BATCH_SIZE) for m in M_VALUES for _ in range(0, RUNS, BATCH_SIZE)]
    results = defaultdict(lambda: {"hits": 0, "runs": 0})

    print(f"Executing Influence Simulation on {cpu_count()} CPU cores...")
    start_time = time.time()

    with Pool(processes=cpu_count()) as pool:
        for h, m, hits, runs in pool.imap_unordered(run_batch_influence, tasks):
            results[m]["hits"] += hits
            results[m]["runs"] += runs

    print("\nWriting Phase Transition data to CSV...")
    with open(OUTPUT_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["m", "individual_influence_probability"])
        for m in sorted(results.keys()):
            prob = results[m]["hits"] / results[m]["runs"]
            writer.writerow([m, prob])
            print(f"Pool size m={m:3d} | Variable 1 Global Influence: {prob:.5f}")

    print(f"\nSaved csv to {OUTPUT_FILE} in {time.time() - start_time:.2f} seconds.")
# # # import csv
# # # import random
# # # import time
# # # from pysat.solvers import Cadical153
# # # from multiprocessing import Pool, cpu_count

# # # # --- PARAMETERS ---
# # # M_FIXED = 3
# # # H_VALUES = [18] # h=5 might be slow (3^5 = 243 leaves)
# # # RUNS = 10
# # # OUTPUT_FILE = f"results/ite_regular_m={M_FIXED}.csv"

# # # def generate_ite_cnf(h, m):
# # #     """Generates a perfectly regular ITE tree: ITE(Subtree, Subtree, Subtree)."""
# # #     C0_SYM, C1_SYM = m + 1, m + 2
# # #     clauses = [[-C0_SYM], [C1_SYM]]
    
# # #     # Layer 0: The actual leaves
# # #     # Every leaf is a symbol from {1..m, Const0, Const1}
# # #     current_layer = [random.randint(1, m + 2) for _ in range(3**h)]
    
# # #     next_aux = m + 3
# # #     # Iteratively build the tree layer by layer
# # #     # At each step, we take THREE sub-trees and make an ITE gate
# # #     while len(current_layer) > 1:
# # #         next_layer = []
# # #         for i in range(0, len(current_layer), 3):
# # #             # c, t, and e are all outputs from the previous layer
# # #             c, t, e = current_layer[i], current_layer[i+1], current_layer[i+2]
            
# # #             v_i = next_aux
# # #             next_aux += 1
# # #             # Standard ITE encoding: v_i <=> (c ? t : e)
# # #             clauses.extend([
# # #                 [-c, -t, v_i], [-c, t, -v_i], 
# # #                 [c, -e, v_i], [c, e, -v_i]
# # #             ])
# # #             next_layer.append(v_i)
# # #         current_layer = next_layer
        
# # #     clauses.append([current_layer[0]]) # Root must be True
# # #     return clauses

# # # def run_single_h(h):
# # #     sat_count = 0
# # #     start_time = time.perf_counter()
# # #     for _ in range(RUNS):
# # #         cnf = generate_ite_cnf(h, M_FIXED)
# # #         with Cadical153(bootstrap_with=cnf) as solver:
# # #             if solver.solve():
# # #                 sat_count += 1
# # #     avg_time = (time.perf_counter() - start_time) / RUNS
# # #     return h, sat_count / RUNS, avg_time

# # # if __name__ == "__main__":
# # #     with open(OUTPUT_FILE, mode='w', newline='') as file:
# # #         writer = csv.writer(file)
# # #         writer.writerow(["h", "m", "pr_satisfiable", "avg_runtime"])
        
# # #         for h in H_VALUES:
# # #             h_res, pr_sat, avg_time = run_single_h(h)
# # #             print(f"h={h} | Pr(SAT)={pr_sat:.4f}")
# # #             writer.writerow([h_res, M_FIXED, pr_sat, avg_time])


# # import csv
# # import random
# # import time
# # from pysat.solvers import Cadical153
# # from multiprocessing import Pool, cpu_count

# # M_FIXED = 3
# # H_VALUES = [1, 3, 5, 7, 9, 11]
# # RUNS = 100
# # OUTPUT_FILE = f"results/ite_regular_m={M_FIXED}.csv"

# # def generate_ite_cnf(h, m):
# #     C0_SYM, C1_SYM = m + 1, m + 2
# #     clauses = [[-C0_SYM], [C1_SYM]]
    
# #     # Layer 0: 3^h leaves
# #     current_layer = [random.randint(1, m + 2) for _ in range(3**h)]
    
# #     next_aux = m + 3
# #     # Every gate takes 3 branches from the layer below.
# #     # No branch is "special"; c, t, and e all come from the same lower-layer pool.
# #     while len(current_layer) > 1:
# #         next_layer = []
# #         for i in range(0, len(current_layer), 3):
# #             c, t, e = current_layer[i:i+3] # Exactly as you intended
# #             v_i = next_aux
# #             next_aux += 1
# #             clauses.extend([[-c, -t, v_i], [-c, t, -v_i], [c, -e, v_i], [c, e, -v_i]])
# #             next_layer.append(v_i)
# #         current_layer = next_layer
        
# #     clauses.append([current_layer[0]])
# #     return clauses

# # def run_single_h(h):
# #     sat_count = 0
# #     start_time = time.perf_counter()
# #     for _ in range(RUNS):
# #         cnf = generate_ite_cnf(h, M_FIXED)
# #         with Cadical153(bootstrap_with=cnf) as solver:
# #             if solver.solve():
# #                 sat_count += 1
# #     avg_time = (time.perf_counter() - start_time) / RUNS
# #     return h, sat_count / RUNS, avg_time

# # if __name__ == "__main__":
# #     with open(OUTPUT_FILE, mode='w', newline='') as file:
# #         writer = csv.writer(file)
# #         writer.writerow(["h", "m", "pr_satisfiable", "avg_runtime"])
# #         with Pool(processes=cpu_count()) as pool:
# #             for h, pr_sat, avg_time in pool.imap(run_single_h, H_VALUES):
# #                 print(f"h={h}: Pr(SAT)={pr_sat}")
# #                 writer.writerow([h, M_FIXED, pr_sat, avg_time])


# import csv
# import random
# import time
# import numpy as np
# from pysat.solvers import Cadical153
# from multiprocessing import Pool, cpu_count
# from collections import defaultdict

# M_FIXED = 1 # Or set this dynamically in run_batch
# H_VALUES = [10, 12, 14, 16]
# RUNS = 100
# BATCH_SIZE = 20
# OUTPUT_FILE = f"results/ite_regular_batch_m={M_FIXED}.csv"

# def generate_ite_cnf(h, m):
#     C0_SYM, C1_SYM = m + 1, m + 2
#     clauses = [[-C0_SYM], [C1_SYM]]
    
#     # Layer 0: 3^h leaves (Variables 1..m or constants)
#     current_layer = [random.randint(1, m + 2) for _ in range(3**h)]
    
#     next_aux = m + 3
#     while len(current_layer) > 1:
#         next_layer = []
#         for i in range(0, len(current_layer), 3):
#             # c, t, and e are ALL sub-trees from the layer below
#             c, t, e = current_layer[i:i+3]
#             v_i = next_aux
#             next_aux += 1
#             # v_i <-> ITE(c, t, e)
#             clauses.extend([[-c, -t, v_i], [-c, t, -v_i], [c, -e, v_i], [c, e, -v_i]])
#             next_layer.append(v_i)
#         current_layer = next_layer
        
#     clauses.append([current_layer[0]])
#     return clauses

# def run_batch(args):
#     h, m, batch_size = args
#     sat_count = 0
#     total_runtime = 0.0
#     for _ in range(batch_size):
#         clauses = generate_ite_cnf(h, m)
#         with Cadical153(bootstrap_with=clauses) as solver:
#             start = time.perf_counter()
#             result = solver.solve()
#             runtime = time.perf_counter() - start
#             if result: sat_count += 1
#             total_runtime += runtime
#     return h, m, sat_count, batch_size, total_runtime

# if __name__ == "__main__":
#     tasks = []
#     for h in H_VALUES:
#         for _ in range(0, RUNS, BATCH_SIZE):
#             tasks.append((h, M_FIXED, BATCH_SIZE))
#     random.shuffle(tasks)

#     results_dict = defaultdict(lambda: {"sat": 0, "runs": 0, "time": 0.0})
    
#     with Pool(processes=cpu_count()) as pool:
#         for h, m, sat, runs, runtime in pool.imap_unordered(run_batch, tasks):
#             results_dict[h]["sat"] += sat
#             results_dict[h]["runs"] += runs
#             results_dict[h]["time"] += runtime

#     with open(OUTPUT_FILE, mode='w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(["h", "m", "pr_satisfiable", "avg_runtime"])
#         for h in sorted(results_dict.keys()):
#             res = results_dict[h]
#             writer.writerow([h, M_FIXED, res["sat"]/res["runs"], res["time"]/res["runs"]])


import csv
import random
import time
import numpy as np
from pysat.solvers import Cadical153
from multiprocessing import Pool, cpu_count
from collections import defaultdict

# --- PARAMETERS ---
H_FIXED = 7
M_FIXED = 0
# We vary the probability of a leaf being a constant from 0.0 to 1.0
P_VALUES = np.linspace(0.0, 1.0, 50) 
RUNS = 500
BATCH_SIZE = 20
OUTPUT_FILE = f"results/ite_bias_transition_h{H_FIXED}_m{M_FIXED}.csv"

def generate_ite_cnf_biased(h, m, p_const):
    """
    p_const: Total probability a leaf is a constant.
    Half of p_const goes to '0', half to '1'.
    The remaining (1 - p_const) is distributed among m variables.
    """
    n_leaves = 3**h
    C0_SYM, C1_SYM = m + 1, m + 2
    
    leaves = []
    for _ in range(n_leaves):
        r = random.random()
        if r < p_const / 2:
            leaves.append(C0_SYM)
        elif r < p_const:
            leaves.append(C1_SYM)
        else:
            leaves.append(random.randint(1, m))
            # leaves.append(C0_SYM if random.random() < 0.5 else C1_SYM)
            
    clauses = [[-C0_SYM], [C1_SYM]]
    current_layer = leaves
    next_aux = m + 3
    
    while len(current_layer) > 1:
        next_layer = []
        for i in range(0, len(current_layer), 3):
            c, t, e = current_layer[i:i+3]
            v_i = next_aux
            next_aux += 1
            clauses.extend([[-c, -t, v_i], [-c, t, -v_i], [c, -e, v_i], [c, e, -v_i]])
            next_layer.append(v_i)
        current_layer = next_layer
        
    clauses.append([current_layer[0]])
    return clauses

def run_batch(args):
    h, m, p_const, batch_size = args
    sat_count = 0
    for _ in range(batch_size):
        cnf = generate_ite_cnf_biased(h, m, p_const)
        with Cadical153(bootstrap_with=cnf) as solver:
            if solver.solve():
                sat_count += 1
    return p_const, sat_count, batch_size

if __name__ == "__main__":
    tasks = []
    for p in P_VALUES:
        for _ in range(0, RUNS, BATCH_SIZE):
            tasks.append((H_FIXED, M_FIXED, p, BATCH_SIZE))
    
    results = defaultdict(lambda: {"sat": 0, "runs": 0})
    
    with Pool(processes=cpu_count()) as pool:
        for p, sat, runs in pool.imap_unordered(run_batch, tasks):
            results[p]["sat"] += sat
            results[p]["runs"] += runs

    with open(OUTPUT_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["p_const", "pr_satisfiable"])
        for p in sorted(results.keys()):
            writer.writerow([p, results[p]["sat"] / results[p]["runs"]])
    
    print(f"Transition experiment complete. Results in {OUTPUT_FILE}")

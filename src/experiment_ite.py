# # import csv
# # import random
# # import time
# # import numpy as np
# # from pysat.solvers import Cadical153
# # from multiprocessing import Pool, cpu_count
# # from collections import defaultdict

# # def generate_ite_cnf(h, m):
# #     n_leaves = 3**h
# #     leaves = [random.randrange(m + 2) for _ in range(n_leaves)]
    
# #     clauses = []
# #     c0, c1 = m + 1, m + 2
# #     clauses.append([-c0])
# #     clauses.append([c1])
    
# #     current_layer = []
# #     for leaf in leaves:
# #         if leaf < m: current_layer.append(leaf + 1)
# #         elif leaf == m: current_layer.append(c0)
# #         else: current_layer.append(c1)
            
# #     next_aux = m + 3
# #     while len(current_layer) > 1:
# #         next_layer = []
# #         for i in range(0, len(current_layer), 3):
# #             c, t, e = current_layer[i:i+3]
# #             v_i = next_aux
# #             next_aux += 1
# #             clauses.extend([[-c, -t, v_i], [-c, t, -v_i], [c, -e, v_i], [c, e, -v_i]])
# #             next_layer.append(v_i)
# #         current_layer = next_layer
        
# #     clauses.append([current_layer[0]])
# #     return clauses

# # H_VALUES = [0, 1, 2, 3, 4]
# # # Alphas represent m / 3^h. 
# # # You might need to experiment to find the exact transition point.
# # ALPHAS = np.linspace(0, 8, 10000) # Adjust range and density as needed

# # RUNS = 100
# # BATCH_SIZE = 10
# # OUTPUT_FILE = f"results/ite_tree_results_{H_VALUES}_{RUNS}.csv"

# # def solve_formula(clauses):
# #     with Cadical153(bootstrap_with=clauses) as solver:
# #         start = time.perf_counter()
# #         result = solver.solve()
# #         runtime = time.perf_counter() - start
# #     return result, runtime

# # def run_batch(args):
# #     h, alpha, batch_size = args
# #     # m = max(1, int(alpha * (3**h))) # Ensure at least 1 variable
# #     m = int(alpha * (3**h))
# #     # m = int(alpha * h)

# #     sat_count = 0
# #     total_runtime = 0.0
# #     for _ in range(batch_size):
# #         clauses = generate_ite_cnf(h, m)
# #         result, runtime = solve_formula(clauses)
# #         if result: sat_count += 1
# #         total_runtime += runtime

# #     return (h, alpha, sat_count, batch_size, total_runtime)

# # if __name__ == "__main__":
# #     tasks = []
# #     for h in H_VALUES:
# #         for alpha in ALPHAS:
# #             for _ in range(0, RUNS, BATCH_SIZE):
# #                 tasks.append((h, alpha, BATCH_SIZE))

# #     results_dict = defaultdict(lambda: {"sat": 0, "runs": 0, "time": 0.0})

# #     with Pool(processes=cpu_count()) as pool:
# #         for h, alpha, sat, runs, runtime in pool.imap_unordered(run_batch, tasks):
# #             key = (h, alpha)
# #             results_dict[key]["sat"] += sat
# #             results_dict[key]["runs"] += runs
# #             results_dict[key]["time"] += runtime

# #     with open(OUTPUT_FILE, mode='w', newline='') as file:
# #         writer = csv.writer(file)
# #         writer.writerow(["h", "alpha", "pr_satisfiable", "avg_runtime"])
# #         for (h, alpha), data in sorted(results_dict.items()):
# #             writer.writerow([h, alpha, data["sat"]/data["runs"], data["time"]/data["runs"]])

# #     print(f"Results saved to {OUTPUT_FILE}")


# import csv
# import random
# import time
# import numpy as np
# from pysat.solvers import Cadical153
# from multiprocessing import Pool, cpu_count
# from collections import defaultdict

# def generate_ite_cnf(h, m):
#     n_leaves = 3**h
#     # m variables (1 to m) + two constants (m+1, m+2)
#     leaves = [random.randrange(m + 2) for _ in range(n_leaves)]
    
#     clauses = []
#     c0, c1 = m + 1, m + 2
#     clauses.append([-c0]) # Constant 0
#     clauses.append([c1])  # Constant 1
    
#     current_layer = []
#     for leaf in leaves:
#         if leaf < m: current_layer.append(leaf + 1)
#         elif leaf == m: current_layer.append(c0)
#         else: current_layer.append(c1)
            
#     next_aux = m + 3
#     while len(current_layer) > 1:
#         next_layer = []
#         for i in range(0, len(current_layer), 3):
#             c, t, e = current_layer[i:i+3]
#             v_i = next_aux
#             next_aux += 1
#             # Standard ITE to CNF: (v <-> (c ? t : e))
#             clauses.extend([[-c, -t, v_i], [-c, t, -v_i], [c, -e, v_i], [c, e, -v_i]])
#             next_layer.append(v_i)
#         current_layer = next_layer
        
#     clauses.append([current_layer[0]]) # Root must be True
#     return clauses

# def solve_formula(clauses):
#     with Cadical153(bootstrap_with=clauses) as solver:
#         start = time.perf_counter()
#         result = solver.solve()
#         runtime = time.perf_counter() - start
#     return result, runtime

# def run_batch(args):
#     h, alpha, batch_size = args
#     num_leaves = 3**h
    
#     # NEW LOGIC: alpha = leaves/m  =>  m = leaves/alpha
#     # If alpha is 0.1, m is large (easy). If alpha is 5, m is small (hard).
#     # m = max(1, int(num_leaves / alpha))
#     m = int(num_leaves / alpha) if alpha > 0 else num_leaves * 10

#     sat_count = 0
#     total_runtime = 0.0
#     for _ in range(batch_size):
#         clauses = generate_ite_cnf(h, m)
#         result, runtime = solve_formula(clauses)
#         if result: sat_count += 1
#         total_runtime += runtime

#     return (h, alpha, sat_count, batch_size, total_runtime)

# if __name__ == "__main__":
#     # h=4 is the 'speed limit', h=0/1 are very small
#     H_VALUES = [6, 7, 8]
#     # alpha > 1 means more leaves than variables
#     ALPHAS = np.linspace(40, 240, 5000) 
    
#     RUNS = 800
#     BATCH_SIZE = 10
#     OUTPUT_FILE = f"results/ite_tree_results_{H_VALUES}_{RUNS}_inverted.csv"

#     tasks = []
#     for h in H_VALUES:
#         for alpha in ALPHAS:
#             for _ in range(0, RUNS, BATCH_SIZE):
#                 tasks.append((h, alpha, BATCH_SIZE))

#     results_dict = defaultdict(lambda: {"sat": 0, "runs": 0, "time": 0.0})

#     with Pool(processes=cpu_count()) as pool:
#         # Note: the unpacking order must match the return of run_batch
#         for h, alpha, sat, runs, runtime in pool.imap_unordered(run_batch, tasks):
#             key = (h, alpha)
#             results_dict[key]["sat"] += sat
#             results_dict[key]["runs"] += runs
#             results_dict[key]["time"] += runtime

#     with open(OUTPUT_FILE, mode='w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(["h", "alpha", "pr_satisfiable", "avg_runtime"])
#         for (h, alpha), data in sorted(results_dict.items()):
#             writer.writerow([h, alpha, data["sat"]/data["runs"], data["time"]/data["runs"]])

#     print(f"Results saved to {OUTPUT_FILE}")


import csv
import random
import time
import numpy as np
from pysat.solvers import Cadical153
from multiprocessing import Pool, cpu_count
from collections import defaultdict

def generate_ite_cnf(h, m):
    n_leaves = 3**h
    # m variables (1 to m) + two constants (m+1, m+2)
    leaves = [random.randrange(m + 2) for _ in range(n_leaves)]
    
    clauses = []
    c0, c1 = m + 1, m + 2
    clauses.append([-c0]) # Constant 0
    clauses.append([c1])  # Constant 1
    
    current_layer = []
    for leaf in leaves:
        if leaf < m: current_layer.append(leaf + 1)
        elif leaf == m: current_layer.append(c0)
        else: current_layer.append(c1)
            
    next_aux = m + 3
    while len(current_layer) > 1:
        next_layer = []
        for i in range(0, len(current_layer), 3):
            c, t, e = current_layer[i:i+3]
            v_i = next_aux
            next_aux += 1
            # Standard ITE to CNF: (v <-> (c ? t : e))
            clauses.extend([[-c, -t, v_i], [-c, t, -v_i], [c, -e, v_i], [c, e, -v_i]])
            next_layer.append(v_i)
        current_layer = next_layer
        
    clauses.append([current_layer[0]]) # Root must be True
    return clauses

def solve_formula(clauses):
    with Cadical153(bootstrap_with=clauses) as solver:
        start = time.perf_counter()
        result = solver.solve()
        runtime = time.perf_counter() - start
    return result, runtime

def run_batch(args):
    h, multiplier, batch_size = args
    # m = multiplier * h
    m = 0

    actual_alpha = (3**h) / m if m > 0 else 0
    sat_count = 0
    total_runtime = 0.0
    for _ in range(batch_size):
        clauses = generate_ite_cnf(h, m)
        result, runtime = solve_formula(clauses)
        if result: sat_count += 1
        total_runtime += runtime

    return (h, actual_alpha, sat_count, batch_size, total_runtime)

if __name__ == "__main__":
    H_VALUES = [1, 2, 3, 4, 5, 7, 10] # Test the "Linear vs Exponential" race
    MULTIPLIER = 5 
    
    RUNS = 1000
    BATCH_SIZE = 20
    OUTPUT_FILE = f"results/ite_tree_results_{MULTIPLIER}_{RUNS}_mlog.csv"

    tasks = []
    for h in H_VALUES:
        for _ in range(0, RUNS, BATCH_SIZE):
            tasks.append((h, MULTIPLIER, BATCH_SIZE))

    results_dict = defaultdict(lambda: {"sat": 0, "runs": 0, "time": 0.0})

    with Pool(processes=cpu_count()) as pool:
        # Note: the unpacking order must match the return of run_batch
        for h, alpha, sat, runs, runtime in pool.imap_unordered(run_batch, tasks):
            key = (h, alpha)
            results_dict[key]["sat"] += sat
            results_dict[key]["runs"] += runs
            results_dict[key]["time"] += runtime

    with open(OUTPUT_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["h", "alpha", "pr_satisfiable", "avg_runtime"])
        for (h, alpha), data in sorted(results_dict.items()):
            writer.writerow([h, alpha, data["sat"]/data["runs"], data["time"]/data["runs"]])

    print(f"Results saved to {OUTPUT_FILE}")

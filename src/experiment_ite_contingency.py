# import csv
# import random
# import time
# from pysat.solvers import Cadical153
# from multiprocessing import Pool, cpu_count
# from collections import defaultdict

# def generate_ite_cnf(h, m):
#     """Generates a regular ternary ITE tree with h levels and m variables."""
#     n_leaves = 3**h
#     # Leaf pool includes variables 1..m and two constants
#     leaves = [random.randrange(m + 2) for _ in range(n_leaves)]
    
#     clauses = []
#     c0, c1 = m + 1, m + 2
#     clauses.append([-c0]) # Constant 0 must be False
#     clauses.append([c1])  # Constant 1 must be True
    
#     current_layer = []
#     for leaf in leaves:
#         if leaf < m:
#             var = leaf + 1
#             # Using your negation logic to introduce conflicts
#             current_layer.append(var if random.random() < 0.5 else -var)
#         elif leaf == m: current_layer.append(c0)
#         else: current_layer.append(c1)
            
#     next_aux = m + 3
#     while len(current_layer) > 1:
#         next_layer = []
#         for i in range(0, len(current_layer), 3):
#             c, t, e = current_layer[i:i+3]
#             v_i = next_aux
#             next_aux += 1
#             # Standard ITE encoding: v_i <-> (c ? t : e)
#             clauses.extend([[-c, -t, v_i], [-c, t, -v_i], [c, -e, v_i], [c, e, -v_i]])
#             next_layer.append(v_i)
#         current_layer = next_layer
        
#     # The 'Root' is the last aux variable created
#     root_var = current_layer[0]
#     return clauses, root_var

# def check_contingency(clauses, root_var):
#     """
#     Tests if the tree is Contingent, Tautological, or UNSAT.
#     """
#     # 1. Can root be True?
#     with Cadical153(bootstrap_with=clauses + [[root_var]]) as s1:
#         can_be_true = s1.solve()
        
#     # 2. Can root be False?
#     with Cadical153(bootstrap_with=clauses + [[-root_var]]) as s2:
#         can_be_false = s2.solve()
        
#     if can_be_true and can_be_false:
#         return "contingent"
#     elif can_be_true:
#         return "tautology"
#     elif can_be_false:
#         return "unsat"
#     else:
#         return "error" # Should not happen in this logic

# def run_batch(args):
#     h, m, batch_size = args
#     stats = {"contingent": 0, "tautology": 0, "unsat": 0}
    
#     for _ in range(batch_size):
#         clauses, root_var = generate_ite_cnf(h, m)
#         state = check_contingency(clauses, root_var)
#         stats[state] += 1

#     return (h, m, stats["contingent"], stats["tautology"], stats["unsat"], batch_size)

# if __name__ == "__main__":
#     # Test m=1 to see if even a single variable loses its power as h grows
#     M_VALUE = 1
#     H_VALUES = range(14, 16)
#     RUNS = 100
#     BATCH_SIZE = 20
#     OUTPUT_FILE = f"results/ite_contingency_test_{M_VALUE}_{RUNS}.csv"

#     tasks = [(h, M_VALUE, BATCH_SIZE) for h in H_VALUES for _ in range(0, RUNS, BATCH_SIZE)]

#     results = defaultdict(lambda: {"con": 0, "tau": 0, "uns": 0, "runs": 0})

#     with Pool(processes=cpu_count()) as pool:
#         for h, m, con, tau, uns, runs in pool.imap_unordered(run_batch, tasks):
#             results[h]["con"] += con
#             results[h]["tau"] += tau
#             results[h]["uns"] += uns
#             results[h]["runs"] += runs

#     with open(OUTPUT_FILE, mode='w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(["h", "pr_contingent", "pr_tautology", "pr_unsat", "pr_sat_total"])
#         for h in sorted(results.keys()):
#             r = results[h]
#             # Pr(SAT) is Contingent + Tautology
#             writer.writerow([h, r["con"]/r["runs"], r["tau"]/r["runs"], r["uns"]/r["runs"], (r["con"]+r["tau"])/r["runs"]])

#     print(f"Results saved to {OUTPUT_FILE}")


import csv
import random
import time
from pysat.solvers import Cadical153
from multiprocessing import Pool, cpu_count
from collections import defaultdict

def run_single_tree_optimized(h, m):
    """Generates and solves an optimized ITE tree entirely inside Cadical."""
    n_leaves = 3**h
    leaves = [random.randrange(m + 2) for _ in range(n_leaves)]
    
    c0, c1 = m + 1, m + 2
    
    # Initialize Cadical solver directly
    solver = Cadical153()
    solver.add_clause([-c0]) # 0 is False
    solver.add_clause([c1])  # 1 is True
    
    current_layer = []
    for leaf in leaves:
        if leaf < m:
            var = leaf + 1
            # current_layer.append(var if random.random() < 0.5 else -var)
            current_layer.append(-var)  # No negation to maximize contingency
        elif leaf == m: 
            current_layer.append(c0)
        else: 
            current_layer.append(c1)
            
    next_aux = m + 3
    
    while len(current_layer) > 1:
        next_layer = []
        for i in range(0, len(current_layer), 3):
            c, t, e = current_layer[i:i+3]
            
            # --- OPTIMIZATION: Short-circuit evaluations with constants ---
            if c == c1:  # If Condition is True, output is always Then branch
                next_layer.append(t)
                continue
            if c == c0:  # If Condition is False, output is always Else branch
                next_layer.append(e)
                continue
            if t == e:   # If Then and Else are identical, Condition doesn't matter
                next_layer.append(t)
                continue
                
            # Standard Tseitin implementation for non-trivial gates
            v_i = next_aux
            next_aux += 1
            
            # Add clauses directly to C solver memory, avoiding Python allocation overhead
            solver.add_clause([-c, -t, v_i])
            solver.add_clause([-c, t, -v_i])
            solver.add_clause([c, -e, v_i])
            solver.add_clause([c, e, -v_i])
            
            next_layer.append(v_i)
        current_layer = next_layer
        
    root_var = current_layer[0]
    
    # Check contingency using assumptions instead of rebuilding the solver
    can_be_true = solver.solve(assumptions=[root_var])
    can_be_false = solver.solve(assumptions=[-root_var])
    
    # Explicit clean up of C memory structures
    solver.delete()
    
    if can_be_true and can_be_false:
        return "contingent"
    elif can_be_true:
        return "tautology"
    else:
        return "unsat"

def run_batch_optimized(args):
    """Batch worker that passes only tiny metadata back and forth across processes."""
    h, m, batch_size = args
    stats = {"contingent": 0, "tautology": 0, "unsat": 0}
    
    for _ in range(batch_size):
        state = run_single_tree_optimized(h, m)
        stats[state] += 1

    # Returns tiny data payloads over IPC, dropping transmission bottlenecks to 0
    return (h, stats["contingent"], stats["tautology"], stats["unsat"], batch_size)

if __name__ == "__main__":
    M_VALUE = 1
    H_VALUES = range(0,12)
    RUNS = 1000
    BATCH_SIZE = 100     # Smaller chunk size prevents worker starvation
    OUTPUT_FILE = f"results/ite_contingency_ooptimized_{M_VALUE}.csv"

    tasks = [(h, M_VALUE, BATCH_SIZE) for h in H_VALUES for _ in range(0, RUNS, BATCH_SIZE)]
    results = defaultdict(lambda: {"con": 0, "tau": 0, "uns": 0, "runs": 0})

    print(f"Starting execution using {cpu_count()} CPU cores...")
    start_time = time.time()

    with Pool(processes=cpu_count()) as pool:
        for h, con, tau, uns, runs in pool.imap_unordered(run_batch_optimized, tasks):
            results[h]["con"] += con
            results[h]["tau"] += tau
            results[h]["uns"] += uns
            results[h]["runs"] += runs
            print(f"Batch completed for h={h}. Total runs logged for this height: {results[h]['runs']}/{RUNS}")

    with open(OUTPUT_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["h", "pr_contingent", "pr_tautology", "pr_unsat", "pr_sat_total"])
        for h in sorted(results.keys()):
            r = results[h]
            writer.writerow([
                h, 
                r["con"]/r["runs"], 
                r["tau"]/r["runs"], 
                r["uns"]/r["runs"], 
                (r["con"]+r["tau"])/r["runs"]
            ])

    print(f"Done! Saved to {OUTPUT_FILE} in {time.time() - start_time:.2f} seconds.")

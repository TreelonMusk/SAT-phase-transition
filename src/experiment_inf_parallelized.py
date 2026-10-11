import csv
import random
import time
import numpy as np
from pysat.solvers import Cadical153
from multiprocessing import Pool, cpu_count
from collections import defaultdict

N_VALUES = [10, 15, 20, 25]  # Smaller system size since tree grows exponentially fas
LEFT_ALPHA = 3.2 #3.8
RIGHT_ALPHA = 5.2 #4.8
ALPHAS = np.linspace(1, 10, 40)
RUNS_LOW = 500
RUNS_HIGH = 10000
BATCH_SIZE = 20
CONF_BUDGET = 100000
OUTPUT_FILE = f"results/ite_transition_{min(N_VALUES)}_{max(N_VALUES)}.csv"

def generate_ite_cnf(n_vars, n_nodes):
    clauses = []
    # 1...n_vars: User variables
    # n_vars + 1: CONST_0, n_vars + 2: CONST_1
    # n_vars + 3+: Auxiliary variables for gates
    CONST_0, CONST_1 = n_vars + 1, n_vars + 2
    state = {'next_aux': n_vars + 3}
    
    clauses.append([-CONST_0]) # Force CONST_0 to False
    clauses.append([CONST_1])  # Force CONST_1 to True
    
    def get_leaf():
        r = random.random()
        if r < 0.1: return CONST_0
        if r < 0.2: return CONST_1
        return random.randint(1, n_vars)

    def add_ite_gate(c, t, e):
        out = state['next_aux']
        state['next_aux'] += 1
        # Tseytin: Out <=> (C ? T : E)
        clauses.extend([
            [-c, -t, out], [-c, t, -out],
            [c, -e, out],  [c, e, -out]
        ])
        return out

    def build_tree(m):
        if m <= 0: return get_leaf()
        # Randomly split remaining m-1 nodes among 3 branches
        parts = [0, 0, 0]
        for _ in range(m - 1): parts[random.randint(0, 2)] += 1
        return add_ite_gate(build_tree(parts[0]), build_tree(parts[1]), build_tree(parts[2]))

    root_var = build_tree(n_nodes)
    clauses.append([root_var]) # Root must be True
    return clauses

def solve_formula(clauses):
    with Cadical153(bootstrap_with=clauses) as solver:
        solver.conf_budget(CONF_BUDGET)
        start = time.perf_counter()
        result = solver.solve()
        runtime = time.perf_counter() - start
    return result, runtime

def run_batch(args):
    n, alpha, batch_size = args
    n_nodes = int(alpha * n)
    sat_count, total_runtime, total_none = 0, 0.0, 0

    for _ in range(batch_size):
        clauses = generate_ite_cnf(n, n_nodes)
        result, runtime = solve_formula(clauses)
        if result: sat_count += 1
        elif result is None: total_none += 1
        total_runtime += runtime
    return (n, alpha, sat_count, batch_size, total_runtime, total_none)

def generate_tasks():
    tasks = []
    for n in N_VALUES:
        for alpha in ALPHAS:
            # runs = RUNS_HIGH if LEFT_ALPHA <= alpha <= RIGHT_ALPHA else RUNS_LOW
            runs = RUNS_HIGH
            for i in range(0, runs, BATCH_SIZE):
                batch_size = min(BATCH_SIZE, runs - i)
                tasks.append((n, alpha, batch_size))
    random.shuffle(tasks)
    return tasks

if __name__ == "__main__":
    tasks = generate_tasks()

    print(f"Running experiment with {len(tasks)} batches")
    print(f"Using {cpu_count()} CPU cores")
    print(f"Batch size: {BATCH_SIZE}, Total runs: {sum(batch[2] for batch in tasks)}")

    results_dict = defaultdict(lambda: {"sat_count": 0, "total_runs": 0, "total_runtime": 0.0, "total_none": 0})
    completed = 0

    with Pool(processes=cpu_count()) as pool:
        for n, alpha, sat_count, runs, runtime, total_none in pool.imap_unordered(run_batch, tasks):
            completed += 1
            if completed % 50 == 0:
                print(f"Completed {completed}/{len(tasks)} batches", flush=True)

            key = (n, alpha)
            results_dict[key]["sat_count"] += sat_count
            results_dict[key]["total_runs"] += runs
            results_dict[key]["total_runtime"] += runtime
            results_dict[key]["total_none"] += total_none

    with open(OUTPUT_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["n", "alpha", "pr_satisfiable", "avg_runtime"])
        
        for (n, alpha), data in sorted(results_dict.items()):
            pr_sat = data["sat_count"] / data["total_runs"]
            avg_runtime = data["total_runtime"] / data["total_runs"]
            pr_none = data["total_none"] / data["total_runs"]
            writer.writerow([n, alpha, pr_sat, avg_runtime])
    print("Percentage None:", pr_none * 100, "%")
    print("Experiment completed, results saved to", OUTPUT_FILE)
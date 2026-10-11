import csv
import random
import time
import numpy as np
from pysat.solvers import Cadical153
from multiprocessing import Pool, cpu_count
from collections import defaultdict

K = 3
# For 2-SAT: [500, 1000, 4000, 16000]
# For 3-SAT: [90, 110, 130, 150, 170, 190, 210, 230, 250]
N_VALUES = [25,50,75,100,125,150,175,200]
# For 2-SAT: LEFT_ALPHA = 0.6, RIGHT_ALPHA = 1.6
# For 3-SAT: LEFT_ALPHA = 3.2, RIGHT_ALPHA = 5.2
LEFT_ALPHA = 3.2
RIGHT_ALPHA = 5.2
# For 2-SAT: from 0 to 2.5
# For 3-SAT: from 2 to 8
ALPHAS = np.concatenate([
    np.linspace(2,LEFT_ALPHA,10), # 10
    np.linspace(LEFT_ALPHA,RIGHT_ALPHA,20), # 15
    np.linspace(RIGHT_ALPHA,8,10) # 10
])
RUNS_LOW = 500
RUNS_HIGH = 3000
BATCH_SIZE = 20
CONF_BUDGET = 100000
OUTPUT_FILE = f"results/csv/{K}sat_parallelized_[{min(N_VALUES)},{max(N_VALUES)}]_{RUNS_LOW}_{RUNS_HIGH}.csv"

def generate(k, n, m):
    clauses = []
    variables = list(range(1, n + 1))
    for _ in range(m):
        vars_ = random.sample(variables, k)
        clause = [v if random.random() < 0.5 else -v for v in vars_]
        clauses.append(clause)
    return clauses

def solve_formula(clauses):
    with Cadical153(bootstrap_with=clauses) as solver:
        solver.conf_budget(CONF_BUDGET)
        start = time.perf_counter()
        result = solver.solve()
        runtime = time.perf_counter() - start
    return result, runtime

def run_batch(args):
    k, n, alpha, batch_size = args
    m = int(alpha * n)

    sat_count = 0
    total_runtime = 0.0
    total_none = 0

    for _ in range(batch_size):
        clauses = generate(k, n, m)
        result, runtime = solve_formula(clauses)
        if result:
            sat_count += 1
        elif result is None:
            total_none += 1
        total_runtime += runtime

    return (n, alpha, sat_count, batch_size, total_runtime, total_none)

def generate_tasks():
    tasks = []
    for n in N_VALUES:
        for alpha in ALPHAS:
            runs = RUNS_HIGH if LEFT_ALPHA <= alpha <= RIGHT_ALPHA else RUNS_LOW
            for i in range(0, runs, BATCH_SIZE):
                batch_size = min(BATCH_SIZE, runs - i)
                tasks.append((K, n, alpha, batch_size))
    random.shuffle(tasks)
    return tasks

if __name__ == "__main__":
    tasks = generate_tasks()

    print(f"Running experiment with {len(tasks)} batches")
    print(f"Using {cpu_count()} CPU cores")
    print(f"Batch size: {BATCH_SIZE}, Total runs: {sum(batch[3] for batch in tasks)}")

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

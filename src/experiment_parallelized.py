import csv
import random
import time
import numpy as np
from pysat.solvers import Minisat22
from multiprocessing import Pool, cpu_count
# from concurrent.futures import ProcessPoolExecutor

alphas = np.concatenate([
    np.linspace(2,4,10),
    np.linspace(4,4.5,25),
    np.linspace(4.5,6,10)
])
results = []
n_values = [100, 200, 300, 400]

def generate(k, n, m):
    clauses = []
    variables = list(range(1, n + 1))
    for _ in range(m):
        vars_ = random.sample(variables, k)
        clause = [v if random.random() < 0.5 else -v for v in vars_]
        clauses.append(clause)
    return clauses

def solve_formula(clauses):
    start = time.perf_counter()
    solver = Minisat22(bootstrap_with=clauses)
    result = solver.solve()
    runtime = time.perf_counter() - start
    solver.delete()
    return result, runtime

def run_single_experiment(args):
    k, n, alpha = args
    m = int(alpha * n)
    clauses = generate(k, n, m)
    result, runtime = solve_formula(clauses)
    return result, runtime

def run_experiment(k, n, alpha, runs=100):
    if 3.8 <= alpha <= 4.8:
        runs = 800
    else:
        runs = 200

    # args = [(k, n, alpha) for _ in range(runs)]
    args = [(k, n, alpha)] * runs

    with Pool(cpu_count()) as pool:
        results = pool.map(run_single_experiment, args)

    sats = [res[0] for res in results]
    runtimes = [res[1] for res in results]

    pr_sat = sum(sats) / runs
    avg_runtime = sum(runtimes) / runs

    return pr_sat, avg_runtime

if __name__ == "__main__":
    with open('results/experiment_parallelized_results.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["n", "alpha", "pr_satisfiable", "avg_runtime"])

        for n in n_values:
            for alpha in alphas:
                prob, runtime = run_experiment(3, n, alpha)
                writer.writerow([n, alpha, prob, runtime])

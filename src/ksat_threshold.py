"""
Satisfiability threshold of random k-SAT.

For every system size n and clause density alpha = m/n, sample random
k-SAT formulas, solve them with CaDiCaL and record the fraction of
satisfiable instances and the average solver runtime.

Example:
    python src/ksat_threshold.py --k 3 --n 50 60 70 80 90 100 --seed 1
    python src/ksat_threshold.py --k 2 --n 1000 2000 3000 --runs-high 2000
"""

import random
import time
from collections import defaultdict

import numpy as np
from pysat.solvers import Cadical153

from common import make_batches, make_parser, output_path, run_parallel, save_csv
from generators import random_ksat

# Default sweep per k: (alpha range, critical window, system sizes)
K_DEFAULTS = {
    2: dict(alpha_range=(0.0, 2.5), critical=(0.6, 1.6),
            n=[1000, 1500, 2000, 2500, 3000, 3500]),
    3: dict(alpha_range=(2.0, 8.0), critical=(3.2, 5.2),
            n=[50, 60, 70, 80, 90, 100]),
}


def alpha_grid(alpha_range, critical, points):
    """Clause densities, sampled more densely inside the critical window."""
    lo, hi = alpha_range
    c_lo, c_hi = critical
    n_left, n_crit, n_right = points
    grid = np.concatenate([
        np.linspace(lo, c_lo, n_left, endpoint=False),
        np.linspace(c_lo, c_hi, n_crit),
        np.linspace(c_hi, hi, n_right + 1)[1:],
    ])
    return [float(a) for a in grid]


def run_batch(task, seed):
    k, n, alpha, conf_budget, batch_size = task
    rng = random.Random(seed)
    m = int(alpha * n)
    sat = timeouts = 0
    runtime = 0.0
    for _ in range(batch_size):
        clauses = random_ksat(k, n, m, rng)
        with Cadical153(bootstrap_with=clauses) as solver:
            if conf_budget > 0:
                solver.conf_budget(conf_budget)
            start = time.perf_counter()
            result = solver.solve_limited() if conf_budget > 0 else solver.solve()
            runtime += time.perf_counter() - start
        if result is None:
            timeouts += 1
        elif result:
            sat += 1
    return n, alpha, sat, timeouts, runtime, batch_size


def main():
    parser = make_parser(__doc__, runs=None, batch_size=20)
    parser.add_argument("--k", type=int, default=3, help="clause length")
    parser.add_argument("--n", type=int, nargs="+",
                        help="system sizes (number of variables); default depends on k")
    parser.add_argument("--alpha-range", type=float, nargs=2, metavar=("MIN", "MAX"),
                        help="clause densities to sweep; default depends on k")
    parser.add_argument("--critical", type=float, nargs=2, metavar=("LOW", "HIGH"),
                        help="critical window, sampled densely; default depends on k")
    parser.add_argument("--points", type=int, nargs=3, default=[10, 20, 10],
                        metavar=("LEFT", "CRITICAL", "RIGHT"),
                        help="number of alpha values left of, inside and right of the window")
    parser.add_argument("--runs-low", type=int, default=1000,
                        help="instances per point outside the critical window")
    parser.add_argument("--runs-high", type=int, default=10000,
                        help="instances per point inside the critical window")
    parser.add_argument("--conf-budget", type=int, default=0,
                        help="CaDiCaL conflict budget per instance (0 = unlimited); "
                             "instances hitting it are reported in pr_timeout")
    args = parser.parse_args()
    if args.runs is not None:
        args.runs_low = args.runs_high = args.runs

    defaults = K_DEFAULTS.get(args.k)
    if defaults is None and None in (args.n, args.alpha_range, args.critical):
        parser.error(f"no defaults for k={args.k}: pass --n, --alpha-range and --critical")
    args.n = args.n or defaults["n"]
    args.alpha_range = args.alpha_range or defaults["alpha_range"]
    args.critical = args.critical or defaults["critical"]

    alphas = alpha_grid(args.alpha_range, args.critical, args.points)
    c_lo, c_hi = args.critical
    points = [(args.k, n, a, args.conf_budget) for n in args.n for a in alphas]
    tasks = make_batches(
        points,
        lambda p: args.runs_high if c_lo <= p[2] <= c_hi else args.runs_low,
        args.batch_size,
    )

    stats = defaultdict(lambda: np.zeros(4))  # sat, timeouts, runtime, runs
    for n, alpha, sat, timeouts, runtime, runs in run_parallel(
            run_batch, tasks, args.workers, args.seed):
        stats[(n, alpha)] += (sat, timeouts, runtime, runs)

    rows = [[n, alpha, sat / runs, runtime / runs, timeouts / runs]
            for (n, alpha), (sat, timeouts, runtime, runs) in sorted(stats.items())]
    out = output_path(args, "csv",
                      f"{args.k}sat_n{min(args.n)}-{max(args.n)}"
                      f"_runs{args.runs_low}-{args.runs_high}.csv")
    save_csv(out, ["n", "alpha", "pr_satisfiable", "avg_runtime", "pr_timeout"], rows, args)


if __name__ == "__main__":
    main()

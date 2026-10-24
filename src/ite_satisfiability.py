"""
Search for a satisfiability threshold in the random ITE tree ensemble.

For every tree height h and control parameter beta, sample random ITE trees
with a pool of m = int(beta * s(h)) variables, Tseitin-encode them into CNF
and solve them with CaDiCaL. Records Pr[SAT] and the average solver runtime.

The scaling s(h) is chosen with --scaling:
    leaves   s(h) = 3^h   (beta = m / 3^h, thesis Figure 5.1)
    height   s(h) = h     (beta = m / h,   thesis Figure 5.2)

Example:
    python src/ite_satisfiability.py --heights 1 2 3 4 --scaling height --runs 500 --seed 1
"""

import time
from collections import defaultdict

import numpy as np
from pysat.solvers import Cadical153

from common import make_batches, make_parser, output_path, run_parallel, save_csv
from generators import encode_ite, sample_ite_leaves

SCALINGS = {"leaves": lambda h: 3 ** h, "height": lambda h: h}


def run_batch(task, seed):
    h, beta, m, negations, batch_size = task
    rng = np.random.default_rng(seed)
    sat = 0
    runtime = 0.0
    for _ in range(batch_size):
        clauses = []
        root, _ = encode_ite(sample_ite_leaves(h, m, negations, rng), m, clauses.append)
        clauses.append([root])  # the tree must evaluate to 1
        with Cadical153(bootstrap_with=clauses) as solver:
            start = time.perf_counter()
            sat += bool(solver.solve())
            runtime += time.perf_counter() - start
    return h, beta, m, sat, runtime, batch_size


def main():
    parser = make_parser(__doc__, runs=5000, batch_size=10)
    parser.add_argument("--heights", type=int, nargs="+", default=[1, 2, 3, 4],
                        help="tree heights h")
    parser.add_argument("--scaling", choices=SCALINGS, default="height",
                        help="how the variable pool scales with h (see above)")
    parser.add_argument("--beta-range", type=float, nargs=2, default=[0.0, 8.0],
                        metavar=("MIN", "MAX"), help="range of the control parameter beta")
    parser.add_argument("--beta-points", type=int, default=800,
                        help="number of beta values in the range")
    parser.add_argument("--negations", action="store_true",
                        help="allow negated variables in the leaf alphabet")
    args = parser.parse_args()

    scale = SCALINGS[args.scaling]
    betas = np.linspace(*args.beta_range, args.beta_points)
    points = [(h, float(b), int(b * scale(h)), args.negations)
              for h in args.heights for b in betas]
    tasks = make_batches(points, args.runs, args.batch_size)

    stats = defaultdict(lambda: np.zeros(3))  # sat, runtime, runs
    for h, beta, m, sat, runtime, runs in run_parallel(run_batch, tasks, args.workers, args.seed):
        stats[(h, beta, m)] += (sat, runtime, runs)

    rows = [[h, beta, m, sat / runs, runtime / runs]
            for (h, beta, m), (sat, runtime, runs) in sorted(stats.items())]
    neg = "neg" if args.negations else "noneg"
    out = output_path(args, "csv",
                      f"ite_sat_h{min(args.heights)}-{max(args.heights)}"
                      f"_{args.scaling}_runs{args.runs}_{neg}.csv")
    save_csv(out, ["h", "beta", "m", "pr_satisfiable", "avg_runtime"], rows, args)


if __name__ == "__main__":
    main()

"""
Contingency of the random ITE tree ensemble.

For a fixed (small) variable pool m and increasing tree height h, classify
random ITE trees as a contradiction (UNSAT), a tautology, or contingent.
The tree is encoded once and solved twice under the assumptions root = 1 and
root = 0.

Example:
    python src/ite_contingency.py --m 1 --heights 0 1 2 3 4 5 6 --runs 1000 --seed 1
"""

from collections import defaultdict

import numpy as np
from pysat.solvers import Cadical153

from common import make_batches, make_parser, output_path, run_parallel, save_csv
from generators import encode_ite, sample_ite_leaves


def classify(h, m, negations, rng):
    """Return 'contingent', 'tautology' or 'unsat' for one random tree."""
    with Cadical153() as solver:
        root, _ = encode_ite(sample_ite_leaves(h, m, negations, rng), m, solver.add_clause)
        can_be_true = solver.solve(assumptions=[root])
        can_be_false = solver.solve(assumptions=[-root])
    if can_be_true and can_be_false:
        return "contingent"
    return "tautology" if can_be_true else "unsat"


def run_batch(task, seed):
    h, m, negations, batch_size = task
    rng = np.random.default_rng(seed)
    counts = defaultdict(int)
    for _ in range(batch_size):
        counts[classify(h, m, negations, rng)] += 1
    return h, counts["contingent"], counts["tautology"], counts["unsat"], batch_size


def main():
    parser = make_parser(__doc__, runs=5000, batch_size=100)
    parser.add_argument("--m", type=int, default=1, help="size of the variable pool")
    parser.add_argument("--heights", type=int, nargs="+", default=list(range(13)),
                        help="tree heights h")
    parser.add_argument("--negations", action="store_true",
                        help="allow negated variables in the leaf alphabet")
    args = parser.parse_args()

    points = [(h, args.m, args.negations) for h in args.heights]
    tasks = make_batches(points, args.runs, args.batch_size)

    stats = defaultdict(lambda: np.zeros(4))  # contingent, tautology, unsat, runs
    for h, con, tau, uns, runs in run_parallel(run_batch, tasks, args.workers, args.seed):
        stats[h] += (con, tau, uns, runs)

    rows = [[h, con / runs, tau / runs, uns / runs, (con + tau) / runs]
            for h, (con, tau, uns, runs) in sorted(stats.items())]
    neg = "neg" if args.negations else "noneg"
    out = output_path(args, "csv", f"ite_contingency_m{args.m}_runs{args.runs}_{neg}.csv")
    save_csv(out, ["h", "pr_contingent", "pr_tautology", "pr_unsat", "pr_sat_total"], rows, args)


if __name__ == "__main__":
    main()

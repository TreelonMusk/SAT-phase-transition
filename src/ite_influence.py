"""
Individual variable influence in the random ITE tree ensemble.

For every tree height h and variable pool size m, sample a random ITE tree
and a uniformly random assignment, then check whether flipping variable x_1
changes the value of the root. The fraction of such samples estimates the
expected influence Inf_1(f_T). No SAT solver is needed: trees are evaluated
directly (vectorized with numpy).

Example:
    python src/ite_influence.py --heights 5 7 9 --runs 1000 --seed 1
    python src/ite_influence.py --heights 8 --m $(seq 100 100 2000)
"""

from collections import defaultdict

import numpy as np

from common import make_batches, make_parser, output_path, run_parallel, save_csv
from generators import evaluate_ite, ite_leaf_values, sample_ite_leaves


def run_batch(task, seed):
    h, m, negations, batch_size = task
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(batch_size):
        leaves = sample_ite_leaves(h, m, negations, rng)
        assignment = rng.integers(0, 2, m).astype(bool)
        flipped = assignment.copy()
        flipped[0] = ~flipped[0]
        hits += (evaluate_ite(ite_leaf_values(leaves, m, assignment))
                 != evaluate_ite(ite_leaf_values(leaves, m, flipped)))
    return h, m, hits, batch_size


def main():
    parser = make_parser(__doc__, runs=5000, batch_size=100)
    parser.add_argument("--heights", type=int, nargs="+", default=[1, 3, 5, 7, 9],
                        help="tree heights h")
    parser.add_argument("--m", type=int, nargs="+", default=[2 ** i for i in range(15)],
                        help="variable pool sizes, powers of two by default")
    parser.add_argument("--negations", action="store_true",
                        help="allow negated variables in the leaf alphabet")
    args = parser.parse_args()
    if min(args.m) < 1:
        parser.error("--m values must be at least 1 (variable x_1 must exist)")

    points = [(h, m, args.negations) for h in args.heights for m in args.m]
    tasks = make_batches(points, args.runs, args.batch_size)

    stats = defaultdict(lambda: np.zeros(2))  # hits, runs
    for h, m, hits, runs in run_parallel(run_batch, tasks, args.workers, args.seed):
        stats[(h, m)] += (hits, runs)

    rows = [[h, m, hits / runs] for (h, m), (hits, runs) in sorted(stats.items())]
    neg = "neg" if args.negations else "noneg"
    out = output_path(args, "csv",
                      f"ite_influence_h{'-'.join(map(str, args.heights))}"
                      f"_runs{args.runs}_{neg}.csv")
    save_csv(out, ["h", "m", "influence"], rows, args)


if __name__ == "__main__":
    main()

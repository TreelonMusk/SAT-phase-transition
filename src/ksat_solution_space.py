"""
Solution-space sampling for random k-SAT.

Generates one random formula and samples its solutions with a two-tiered
stochastic local search: every inter-cluster job starts from a random
assignment and descends to a solution (global jump), then repeatedly kicks
that solution by a few bit flips and descends again (local jumps). The unique
solutions are saved as a 0/1 matrix in a .npy file.

Example:
    python src/ksat_solution_space.py --n 100 --alpha 3 --clusters 800 --local-steps 800 --seed 1
"""

import random

import numpy as np

from common import make_parser, output_path, run_parallel, write_metadata
from generators import random_ksat


def is_satisfied(clause, assignment):
    return any((lit > 0) == assignment[abs(lit)] for lit in clause)


def sls_search(clauses, n, rng, assignment=None, max_flips=2000):
    """Simplified WalkSAT: flip a random variable of a random violated clause."""
    if assignment is None:
        assignment = {i: rng.randint(0, 1) for i in range(1, n + 1)}
    else:
        assignment = dict(assignment)
    for _ in range(max_flips):
        violated = [c for c in clauses if not is_satisfied(c, assignment)]
        if not violated:
            return assignment
        var = abs(rng.choice(rng.choice(violated)))
        assignment[var] = 1 - assignment[var]
    return None


def sample_cluster(task, seed):
    """One inter-cluster job: a global jump followed by `local_steps` local jumps."""
    clauses, n, local_steps, kick_min, kick_max, max_flips = task
    rng = random.Random(seed)
    as_row = lambda a: [a[i] for i in range(1, n + 1)]

    base = sls_search(clauses, n, rng, max_flips=max_flips)
    if base is None:
        return []
    solutions = [as_row(base)]
    for _ in range(local_steps):
        kicked = dict(base)
        for v in rng.sample(range(1, n + 1), rng.randint(kick_min, kick_max)):
            kicked[v] = 1 - kicked[v]
        local = sls_search(clauses, n, rng, kicked, max_flips)
        if local is None:
            continue
        solutions.append(as_row(local))
        if rng.random() < 0.5:  # continue the chain from the new solution
            base = local
    return solutions


def main():
    parser = make_parser(__doc__)
    parser.add_argument("--n", type=int, default=100, help="number of variables")
    parser.add_argument("--alpha", type=float, default=3.0, help="clause density m/n")
    parser.add_argument("--k", type=int, default=3, help="clause length")
    parser.add_argument("--clusters", type=int, default=800,
                        help="number of inter-cluster jobs (C in Algorithm 1)")
    parser.add_argument("--local-steps", type=int, default=800,
                        help="local jumps per inter-cluster job (S in Algorithm 1)")
    parser.add_argument("--kick", type=int, nargs=2, default=[3, 6], metavar=("MIN", "MAX"),
                        help="range of the number of bits flipped by a local kick")
    parser.add_argument("--max-flips", type=int, default=2000,
                        help="flip limit of a single local search")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    clauses = random_ksat(args.k, args.n, int(args.alpha * args.n), rng)
    task = (clauses, args.n, args.local_steps, *args.kick, args.max_flips)
    tasks = [task] * args.clusters

    sampler_seed = rng.getrandbits(63) if args.seed is not None else None
    solutions = []
    for cluster in run_parallel(sample_cluster, tasks, args.workers, sampler_seed):
        solutions.extend(cluster)
    if not solutions:
        parser.exit(1, "No solutions found; is the formula satisfiable?\n")
    unique = np.unique(np.array(solutions, dtype=np.uint8), axis=0)

    out = output_path(args, "npy", f"solution_space_{args.k}sat_n{args.n}_a{args.alpha:g}.npy")
    np.save(out, unique)
    write_metadata(out, args, unique_solutions=len(unique))
    print(f"Saved {len(unique)} unique solutions to {out}")


if __name__ == "__main__":
    main()

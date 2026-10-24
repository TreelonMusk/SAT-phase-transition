"""
Shared experiment parts: command-line options, parallel batch
execution with reproducible seeding, and saving results (CSV + JSON metadata).
"""

import argparse
import csv
import json
import os
import random
import sys
import time
from datetime import datetime
from multiprocessing import Pool, cpu_count

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(REPO_ROOT, "results")


class _HelpFormatter(argparse.ArgumentDefaultsHelpFormatter,
                     argparse.RawDescriptionHelpFormatter):
    """Show defaults and keep the line breaks of the script docstring."""


def make_parser(description, runs=None, batch_size=None):
    """
    Argument parser with the execution options shared by every experiment.
    --runs and --batch-size are only added when a default batch size is given.
    """
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=_HelpFormatter)
    g = parser.add_argument_group("execution")
    if batch_size is not None:
        g.add_argument("--runs", type=int, default=runs,
                       help="number of random instances sampled per parameter point")
        g.add_argument("--batch-size", type=int, default=batch_size,
                       help="instances per task sent to a worker process")
    g.add_argument("--workers", type=int, default=cpu_count(),
                   help="number of worker processes")
    g.add_argument("--seed", type=int, default=None,
                   help="base random seed (omit for a non-reproducible run)")
    g.add_argument("--out", default=None,
                   help="output file (default: auto-named inside results/)")
    return parser


def make_batches(points, runs, batch_size):
    """
    Split the samples of every parameter point into batches.
    `points` is a list of tuples; `runs` is an int or a function point -> int.
    Each task is the point tuple with the batch size appended.
    """
    tasks = []
    for point in points:
        total = runs(point) if callable(runs) else runs
        for start in range(0, total, batch_size):
            tasks.append((*point, min(batch_size, total - start)))
    return tasks


def _call(job):
    worker, task, seed = job
    return worker(task, seed)


def run_parallel(worker, tasks, workers, seed=None):
    """
    Run `worker(task, seed)` for every task on a process pool and yield the
    results as they complete. Every task gets its own seed derived from the
    base seed, so a run with a fixed --seed is reproducible regardless of
    scheduling order.
    """
    rng = random.Random(seed)
    jobs = [(worker, task, rng.getrandbits(63) if seed is not None else None)
            for task in tasks]
    rng.shuffle(jobs)  # mix cheap and expensive tasks for load balancing

    total = len(jobs)
    step = max(1, total // 100)
    start = time.time()
    print(f"Running {total} tasks on {workers} workers...", file=sys.stderr)
    with Pool(processes=workers) as pool:
        for done, result in enumerate(pool.imap_unordered(_call, jobs), 1):
            if done % step == 0 or done == total:
                print(f"\r  {done}/{total} tasks ({time.time() - start:.0f}s)",
                      end="", file=sys.stderr, flush=True)
            yield result
    print(file=sys.stderr)


def output_path(args, subdir, default_name):
    """Return --out if given, otherwise results/<subdir>/<default_name>."""
    path = args.out or os.path.join(RESULTS_DIR, subdir, default_name)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    return path


def write_metadata(path, args, **extra):
    """Write a JSON file next to `path` recording how it was produced."""
    meta = {
        "command": " ".join([os.path.basename(sys.executable)] + sys.argv),
        "created": datetime.now().isoformat(timespec="seconds"),
        "args": vars(args),
        **extra,
    }
    with open(os.path.splitext(path)[0] + ".json", "w") as f:
        json.dump(meta, f, indent=2, default=str)


def save_csv(path, header, rows, args, **extra):
    """Write rows to a CSV file and its JSON metadata sidecar."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    write_metadata(path, args, **extra)
    print(f"Results saved to {path}")

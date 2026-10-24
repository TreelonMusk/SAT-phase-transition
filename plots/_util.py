"""Small helpers shared by the plot scripts."""

import argparse
import json
import os

import matplotlib.pyplot as plt

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLOTS_DIR = os.path.join(REPO_ROOT, "results", "plots")


def make_parser(description):
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", help="output image (default: results/plots/<input name>.png)")
    parser.add_argument("--dpi", type=int, default=300, help="resolution of the saved image")
    parser.add_argument("--show", action="store_true", help="also open the figure in a window")
    return parser


def read_metadata(data_path):
    """Return the JSON sidecar written by the experiment scripts, or {}."""
    path = os.path.splitext(data_path)[0] + ".json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def default_out(data_path, suffix=""):
    name = os.path.splitext(os.path.basename(data_path))[0]
    return os.path.join(PLOTS_DIR, f"{name}{suffix}.png")


def finish(fig, args, out):
    """Save the figure and optionally show it."""
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    fig.savefig(out, dpi=args.dpi, bbox_inches="tight")
    print(f"Plot saved to {out}")
    if args.show:
        plt.show()

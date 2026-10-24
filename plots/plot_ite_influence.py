"""
Plot the output of src/ite_influence.py (thesis Figures 5.5-5.9).

Expected influence of a single variable against the pool size m, one curve
per tree height h. With --scale-base B the x-axis becomes the finite-size
scaling parameter beta = m / B^h; B = 1.5 gives the data collapse of
Figure 5.9, B = 3 the non-collapsing Figure 5.8.

Also accepts the older per-height CSVs (columns m, individual_influence_probability);
the height is then read from the file name (..._h9...).

Example:
    python plots/plot_ite_influence.py results/csv/ite_influence_h1-3-5-7-9_runs5000_neg.csv
    python plots/plot_ite_influence.py <csv> --scale-base 1.5
"""

import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colormaps

from _util import default_out, finish, make_parser

MARKERS = ["o", "s", "^", "D", "v", "p", "*", "h", "X"]


def load(paths):
    frames = []
    for path in paths:
        df = pd.read_csv(path).rename(columns={"individual_influence_probability": "influence"})
        if "h" not in df:
            match = re.search(r"_h(\d+)", path)
            if not match:
                raise SystemExit(f"{path}: no 'h' column and no _h<height> in the file name")
            df["h"] = int(match.group(1))
        frames.append(df[["h", "m", "influence"]])
    return pd.concat(frames)


def main():
    parser = make_parser(__doc__)
    parser.add_argument("csv", nargs="+", help="CSV(s) produced by src/ite_influence.py")
    parser.add_argument("--scale-base", type=float,
                        help="plot against beta = m / B^h instead of m")
    parser.add_argument("--linear", action="store_true", help="linear instead of log2 x-axis")
    args = parser.parse_args()

    df = load(args.csv)
    heights = sorted(df["h"].unique())
    colors = colormaps["plasma"](np.linspace(0, 0.9, len(heights)))

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for i, h in enumerate(heights):
        sub = df[df["h"] == h].sort_values("m")
        x = sub["m"] / args.scale_base ** h if args.scale_base else sub["m"]
        ax.plot(x, sub["influence"], marker=MARKERS[i % len(MARKERS)], color=colors[i],
                linewidth=1.7, markersize=5, label=f"Height h = {h}")

    if args.scale_base:
        ax.set_xlabel(fr"Control Parameter Density $\beta = m / {args.scale_base:g}^h$")
    else:
        ax.set_xlabel("Variable Pool Size ($m$)")
    if not args.linear:
        ax.set_xscale("log", base=2)
    ax.set_ylabel("Expected Variable Influence")
    ax.grid(True, which="both", ls="--", alpha=0.4)
    if len(heights) > 1:
        ax.legend(loc="lower left", fontsize=10)
    fig.tight_layout()

    suffix = f"_collapse{args.scale_base:g}" if args.scale_base else ""
    finish(fig, args, args.out or default_out(args.csv[0], suffix))


if __name__ == "__main__":
    main()

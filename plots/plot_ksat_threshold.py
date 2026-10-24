"""
Plot the output of src/ksat_threshold.py (thesis Figures 4.1-4.3, A.1, A.2).

Default: Pr[SAT] (top) and average runtime (bottom) against alpha, one curve
per system size n, with the empirical threshold band between the
Pr[SAT] = 0.5 crossings of the smallest and largest n.

Example:
    python plots/plot_ksat_threshold.py results/csv/3sat_n50-100_runs1000-10000.csv
    python plots/plot_ksat_threshold.py <csv> --runtime-only --log
    python plots/plot_ksat_threshold.py <csv> --surface
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from _util import default_out, finish, make_parser

ALPHA_LABEL = r"Clause density $\alpha \,\,\, (m/n)$"
SAT_LABEL = r"Fraction of satisfiable instances $\Pr[\rm SAT]$"


def crossing(alpha, pr_sat, level=0.5):
    """Alpha at which a (decreasing) Pr[SAT] curve crosses `level`."""
    return float(np.interp(level, pr_sat[::-1], alpha[::-1]))


def plot_curves(df, args):
    sizes = sorted(df["n"].unique())
    rows = 1 if args.runtime_only else 2
    fig, axes = plt.subplots(rows, 1, sharex=True, figsize=(7, 4.5 * rows), squeeze=False)
    axes = axes[:, 0]
    ax_time = axes[-1]

    for n in sizes:
        sub = df[df["n"] == n].sort_values("alpha")
        if not args.runtime_only:
            axes[0].plot(sub["alpha"], sub["pr_satisfiable"], label=fr"$n={n}$")
        ax_time.plot(sub["alpha"], sub["avg_runtime"] * 1000, label=fr"$n={n}$")

    if not args.no_band and len(sizes) > 1:
        ends = [df[df["n"] == n].sort_values("alpha") for n in (sizes[0], sizes[-1])]
        lo, hi = sorted(crossing(s["alpha"].values, s["pr_satisfiable"].values) for s in ends)
        for ax in axes:
            ax.axvspan(lo, hi, color="gray", alpha=0.15)
            ax.axvline(lo, color="gray", linestyle=":", linewidth=1)
            ax.axvline(hi, color="gray", linestyle=":", linewidth=1)
        print(f"Threshold band (Pr[SAT] = 0.5 crossings of n={sizes[0]} and n={sizes[-1]}): "
              f"[{lo:.3f}, {hi:.3f}]")

    if not args.runtime_only:
        axes[0].axhline(0.5, color="gray", linestyle="--", linewidth=1, alpha=0.7)
        axes[0].set_ylabel(SAT_LABEL)
        axes[0].grid(True)
        axes[0].legend()
    if args.log:
        ax_time.set_yscale("log")
    ax_time.set_ylabel("Average Runtime (ms" + (", log scale)" if args.log else ")"))
    ax_time.set_xlabel(ALPHA_LABEL)
    ax_time.grid(True)
    if args.runtime_only:
        ax_time.legend()
    fig.tight_layout()
    return fig


def plot_surface(df, args):
    column = "pr_satisfiable" if not args.runtime_only else "avg_runtime"
    pivoted = df.pivot(index="alpha", columns="n", values=column)
    N, A = np.meshgrid(pivoted.columns, pivoted.index)
    Z = pivoted.values
    zlabel = r"Fraction $\Pr[\rm SAT]$"
    if args.runtime_only:
        Z = np.log10(Z * 1000)
        zlabel = r"Average Runtime ($\log_{10}$ ms)"

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(A, N, Z, cmap="viridis")
    ax.view_init(elev=10, azim=-60)
    ax.set_xlabel(r"$\alpha \,\,\, (m/n)$")
    ax.set_ylabel("Variables $n$")
    ax.set_zlabel(zlabel)
    fig.colorbar(surf, shrink=0.5, aspect=5)
    return fig


def main():
    parser = make_parser(__doc__)
    parser.add_argument("csv", help="CSV produced by src/ksat_threshold.py")
    parser.add_argument("--runtime-only", action="store_true", help="only plot the runtime")
    parser.add_argument("--log", action="store_true", help="logarithmic runtime axis")
    parser.add_argument("--no-band", action="store_true", help="hide the threshold band")
    parser.add_argument("--surface", action="store_true",
                        help="3D surface over (alpha, n) instead of curves")
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    fig = plot_surface(df, args) if args.surface else plot_curves(df, args)
    suffix = ("_surface" if args.surface else "") + ("_runtime" if args.runtime_only else "") \
        + ("_log" if args.log else "")
    finish(fig, args, args.out or default_out(args.csv, suffix))


if __name__ == "__main__":
    main()

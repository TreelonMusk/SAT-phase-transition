"""
Plot the output of src/ite_satisfiability.py (thesis Figures 5.1, 5.2).

Pr[SAT] (top) and average runtime (bottom) against beta, one series per
tree height h.

Example:
    python plots/plot_ite_satisfiability.py results/csv/ite_sat_h1-4_height_runs5000_noneg.csv
"""

import pandas as pd
import matplotlib.pyplot as plt

from _util import default_out, finish, make_parser, read_metadata

BETA_LABELS = {"leaves": r"$\beta = m/3^h$", "height": r"$\beta = m/h$"}


def main():
    parser = make_parser(__doc__)
    parser.add_argument("csv", help="CSV produced by src/ite_satisfiability.py")
    parser.add_argument("--xlabel", help="x-axis label (default: taken from the run metadata)")
    args = parser.parse_args()

    df = pd.read_csv(args.csv).rename(columns={"alpha": "beta"})  # older CSVs used 'alpha'
    scaling = read_metadata(args.csv).get("args", {}).get("scaling")
    xlabel = args.xlabel or BETA_LABELS.get(scaling, r"$\beta$")

    fig, (ax_sat, ax_time) = plt.subplots(2, 1, sharex=True, figsize=(7, 9))
    for h in sorted(df["h"].unique()):
        sub = df[df["h"] == h]
        ax_sat.scatter(sub["beta"], sub["pr_satisfiable"], s=3, label=f"$h={h}$")
        ax_time.scatter(sub["beta"], sub["avg_runtime"] * 1000, s=3, label=f"$h={h}$")

    ax_sat.set_ylabel(r"Fraction of satisfiable instances $\Pr[\rm SAT]$")
    ax_sat.legend(markerscale=3)
    ax_sat.grid(True)
    ax_time.set_ylabel("Average Runtime (ms)")
    ax_time.set_xlabel(xlabel)
    ax_time.grid(True)
    fig.tight_layout()
    finish(fig, args, args.out or default_out(args.csv))


if __name__ == "__main__":
    main()

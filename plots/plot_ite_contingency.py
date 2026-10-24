"""
Plot the output of src/ite_contingency.py (thesis Figures 5.3, 5.4).

Pr[Contingent], Pr[TAUT], Pr[UNSAT] and Pr[SAT] against the tree height h.
Pass two CSVs (e.g. without and with negations) to stack them vertically.

Example:
    python plots/plot_ite_contingency.py results/csv/ite_contingency_m1_runs5000_noneg.csv \\
                                         results/csv/ite_contingency_m1_runs5000_neg.csv
"""

import pandas as pd
import matplotlib.pyplot as plt

from _util import default_out, finish, make_parser


def main():
    parser = make_parser(__doc__)
    parser.add_argument("csv", nargs="+", help="CSV(s) produced by src/ite_contingency.py")
    args = parser.parse_args()

    fig, axes = plt.subplots(len(args.csv), 1, sharex=True,
                             figsize=(7, 4.5 * len(args.csv)), squeeze=False)
    for ax, path in zip(axes[:, 0], args.csv):
        df = pd.read_csv(path)
        ax.plot(df["h"], df["pr_contingent"], label="Pr[Contingent]", marker="o", color="blue")
        ax.plot(df["h"], df["pr_tautology"], label="Pr[TAUT]", marker="s", color="green")
        ax.plot(df["h"], df["pr_unsat"], label="Pr[UNSAT]", marker="^", color="red")
        ax.plot(df["h"], df["pr_sat_total"], label="Pr[SAT]", linestyle="--",
                color="black", alpha=0.6)
        ax.set_ylabel("Probability")
        ax.grid(True, alpha=0.3)
        ax.legend()
    axes[-1, 0].set_xlabel(r"Tree Height $h$")
    fig.tight_layout()
    finish(fig, args, args.out or default_out(args.csv[0]))


if __name__ == "__main__":
    main()

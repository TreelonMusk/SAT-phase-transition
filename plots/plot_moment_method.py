"""
Analytical figures of the moment method for random k-SAT (thesis Chapter 3).

    lambda-s   Lambda_S(r) for k = 5 and alpha in {14, 18, 22, 26, 30}   (Figure 3.2)
    lambda-n   f_S vs f_N, Lambda_N(r) for alpha in {8..12}, and Lambda_N
               at alpha = 9.973                                          (Figure 3.3)

No data needed; the curves are computed from Equations (3.20) and (3.36).

Example:
    python plots/plot_moment_method.py lambda-n
"""

import os

import numpy as np
import matplotlib.pyplot as plt

from _util import PLOTS_DIR, finish, make_parser

R = np.linspace(1e-10, 1 - 1e-10, 1000)  # avoid 0^0 at the endpoints


def f_S(r, k):
    return 1 - 2 ** (1 - k) + 2 ** (-k) * r ** k


def f_N(r, k):
    return 1 - 2 ** (2 - k) + 2 ** (1 - k) * (r ** k + (1 - r) ** k)


def overlap_entropy(r):
    return r ** r * (1 - r) ** (1 - r)


def Lambda(f, r, k, alpha):
    return 2 * f(r, k) ** alpha / overlap_entropy(r)


def plot_lambda_s(k):
    fig, ax = plt.subplots(figsize=(6, 6))
    for alpha in [14, 18, 22, 26, 30]:
        ax.plot(R, Lambda(f_S, R, k, alpha), "k-")
    ax.set_xlabel("$r$", fontsize=12)
    ax.set_ylabel(r"$\Lambda_S(r)$", fontsize=12)
    ax.set_xlim(0, 1)
    ax.grid(True, linestyle=":", alpha=0.6)
    fig.tight_layout()
    return fig


def plot_lambda_n(k):
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.5))
    axs[0].plot(R, f_S(R, k), "k-", label=r"$f_S(r)$")
    axs[0].plot(R, f_N(R, k), "k--", label=r"$f_N(r)$")
    axs[0].set_ylabel("Probability", fontsize=12)
    axs[0].legend()
    for alpha in [8, 9, 10, 11, 12]:
        axs[1].plot(R, Lambda(f_N, R, k, alpha), color="black")
    axs[2].plot(R, Lambda(f_N, R, k, 9.973), "k-")
    for ax in axs[1:]:
        ax.set_ylabel(r"$\Lambda_N(r)$", fontsize=12)
    for ax in axs:
        ax.set_xlabel("$r$", fontsize=12)
        ax.grid(True, linestyle=":", alpha=0.6)
    fig.tight_layout()
    return fig


def main():
    parser = make_parser(__doc__)
    parser.add_argument("figure", choices=["lambda-s", "lambda-n"], help="which figure to draw")
    parser.add_argument("--k", type=int, default=5, help="clause length")
    args = parser.parse_args()

    fig = plot_lambda_s(args.k) if args.figure == "lambda-s" else plot_lambda_n(args.k)
    name = args.figure.replace("-", "_") + f"_k{args.k}.png"
    finish(fig, args, args.out or os.path.join(PLOTS_DIR, name))


if __name__ == "__main__":
    main()

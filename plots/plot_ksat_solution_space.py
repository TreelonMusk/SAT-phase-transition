"""
Plot the output of src/ksat_solution_space.py (thesis Figures 4.7, 4.8, A.3).

Produces a 2D UMAP projection of the sampled solutions (Hamming metric) and
a histogram of the pairwise Hamming distances, as two separate images.

Example:
    python plots/plot_ksat_solution_space.py results/npy/solution_space_3sat_n100_a3.8.npy
    python plots/plot_ksat_solution_space.py <npy> --kind hamming --log
"""

import os

import numpy as np
import matplotlib.pyplot as plt

from _util import default_out, finish, make_parser, read_metadata


def plot_umap(data, title, args):
    import umap  # imported lazily: slow to load and only needed here

    embedding = umap.UMAP(n_neighbors=15, metric="hamming", min_dist=0.1,
                          random_state=args.seed).fit_transform(data)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(embedding[:, 0], embedding[:, 1], alpha=0.6, s=10, c="blue", edgecolors="none")
    ax.set_title(f"Solution Space Geometry ({title})")
    ax.set_xticks([])
    ax.set_yticks([])
    fig.tight_layout()
    return fig


def plot_hamming(data, title, args):
    from scipy.spatial.distance import pdist

    n = data.shape[1]
    if len(data) > args.max_samples:
        rng = np.random.default_rng(args.seed)
        data = data[rng.choice(len(data), args.max_samples, replace=False)]
    distances = pdist(data, metric="hamming") * n  # fraction -> number of bits

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(distances, bins=np.arange(-0.5, n + 1.5, 1), density=True,
            color="purple", alpha=0.7, edgecolor="black")
    if args.log:
        ax.set_yscale("log")
    ax.set_title(f"Pairwise Hamming Distance Distribution ({title})")
    ax.set_xlabel("Hamming Distance (Number of flipped variables)")
    ax.set_ylabel("Frequency" + (", log scale" if args.log else ""))
    ax.grid(axis="y", alpha=0.7)
    fig.tight_layout()
    return fig


def main():
    parser = make_parser(__doc__)
    parser.add_argument("npy", help=".npy file produced by src/ksat_solution_space.py")
    parser.add_argument("--kind", choices=["umap", "hamming", "both"], default="both",
                        help="which figure(s) to make")
    parser.add_argument("--log", action="store_true", help="logarithmic histogram axis")
    parser.add_argument("--max-samples", type=int, default=20000,
                        help="subsample this many solutions for the Hamming histogram")
    parser.add_argument("--seed", type=int, default=80, help="seed for UMAP and subsampling")
    args = parser.parse_args()

    data = np.load(args.npy)
    meta = read_metadata(args.npy).get("args", {})
    title = rf"N={data.shape[1]}" + (rf", $\alpha$={meta['alpha']:g}" if "alpha" in meta else "")
    print(f"Loaded {len(data)} solutions over {data.shape[1]} variables")

    if args.out and args.kind == "both":
        parser.error("--out needs a single --kind (umap or hamming)")
    if args.kind in ("umap", "both"):
        finish(plot_umap(data, title, args), args, args.out or default_out(args.npy, "_umap"))
    if args.kind in ("hamming", "both"):
        suffix = "_hamming" + ("_log" if args.log else "")
        finish(plot_hamming(data, title, args), args, args.out or default_out(args.npy, suffix))


if __name__ == "__main__":
    main()

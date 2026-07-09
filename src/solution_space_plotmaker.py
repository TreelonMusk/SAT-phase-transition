import numpy as np
import umap
import matplotlib.pyplot as plt
import os

N = 100
ALPHA = 2
filename = f"results/npy/solution_space_n{N}_a{ALPHA}.npy"
OUTPUT_PLOT = f"results/plots/solution_space_n{N}_a{ALPHA}.png"

print(f"Loading data from {filename}...")
data = np.load(filename)

print(f"Running UMAP on {len(data)} solutions...")
# Adjusted parameters for better cluster separation
reducer = umap.UMAP(n_neighbors=15, metric='hamming', min_dist=0.1, random_state=80)
embedding = reducer.fit_transform(data)

plt.figure(figsize=(8, 6))
plt.scatter(embedding[:, 0], embedding[:, 1], alpha=0.6, s=10, c='blue', edgecolors='none')
plt.title(f"Solution Space Geometry (N={N}, $\\alpha$={ALPHA})")
# plt.axis('off')
plt.xticks([])
plt.yticks([])
plt.tight_layout()

os.makedirs(os.path.dirname(OUTPUT_PLOT), exist_ok=True)
plt.savefig(OUTPUT_PLOT, dpi=300)
print(f"Plot saved to '{OUTPUT_PLOT}'")
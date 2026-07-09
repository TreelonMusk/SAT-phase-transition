import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist
import os

N = 100
ALPHA = 2
filename = f"results/npy/solution_space_n{N}_a{ALPHA}.npy"
OUTPUT_PLOT = f"results/plots/avg_ham_n{N}_a{ALPHA}.png"
MAX_SAMPLES = 20000

print(f"Loading data from {filename}...")
data = np.load(filename)

# 1. Calculate all pairwise Hamming distances
# pdist with metric='hamming' returns the *proportion* of differing bits.
# Multiply by N to get the absolute number of flipped variables.
print("Calculating pairwise Hamming distances...")

if len(data) > MAX_SAMPLES:
    np.random.shuffle(data)
    data = data[:MAX_SAMPLES]
distances = pdist(data, metric='hamming') * N

# 2. Plot the Histogram
plt.figure(figsize=(8, 5))
plt.hist(distances, bins=np.arange(-0.5, N+1.5, 1), density=True, color='purple', alpha=0.7, edgecolor='black')
# plt.yscale('log')
plt.title(f"Pairwise Hamming Distance Distribution (N={N}, $\\alpha$={ALPHA})")
plt.xlabel("Hamming Distance (Number of flipped variables)")
plt.ylabel("Frequency")
plt.grid(axis='y', alpha=0.7)
plt.tight_layout()
# plt.show()

os.makedirs(os.path.dirname(OUTPUT_PLOT), exist_ok=True)
plt.savefig(OUTPUT_PLOT, dpi=300)
print(f"Plot saved to '{OUTPUT_PLOT}'")
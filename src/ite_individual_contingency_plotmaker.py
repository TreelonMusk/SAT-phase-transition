# import pandas as pd
# import matplotlib.pyplot as plt
# import os

# H_VALUE = 12
# csv_path = f"results/csv/variable_influence_transition_h{H_VALUE}.csv"
# output_plot_path = "results/plots/variable_influence_phase_transition.png"

# if not os.path.exists(csv_path):
#     print(f"Error: Could not find '{csv_path}'.")
# else:
#     # Read the experimental data
#     df = pd.read_csv(csv_path)
    
#     # Create publication-quality figure
#     plt.figure(figsize=(8, 5))
    
#     # Plot experimental data points and a smooth line linking them
#     plt.plot(df['m'], df['individual_influence_probability'], 
#              marker='o', color='darkviolet', linewidth=2, markersize=5, 
#              label='Empirical Variable Influence')
    
#     # Add titles and axis labels using standard thesis formatting
#     plt.title(f"Complexity Phase Transition: Information Dilution (Fixed h={H_VALUE})", fontsize=12, fontweight='bold')
#     plt.xlabel("Variable Pool Size (m)", fontsize=11)
#     plt.ylabel("Pr(Individual Variable Alters Output)", fontsize=11)
    
#     # Set the X-axis to a logarithmic scale to cleanly show the exponential decay
#     plt.xscale('log', base=2)
#     plt.xticks(df['m'], labels=[str(m) for m in df['m']])
    
#     # Style tweaks for scannability
#     plt.grid(True, which="both", ls="--", alpha=0.5)
#     plt.legend(loc="upper right", fontsize=10)
#     plt.tight_layout()
    
#     # Save the figure to your results directory
#     plt.savefig(output_plot_path, dpi=300)
#     print(f"Plot saved to '{output_plot_path}'")


# import pandas as pd
# import matplotlib.pyplot as plt
# import matplotlib.cm as cm
# import os

# csv_path = "results/csv/pure_variable_scaling_data.csv"
# output_plot = "results/plots/pure_variable_scaling_collapse.png"

# if not os.path.exists(csv_path):
#     print("Error: Run the data generation script first.")
# else:
#     df = pd.read_csv(csv_path)
#     unique_heights = sorted(df['h'].unique())
#     num_heights = len(unique_heights)
    
#     colors = cm.plasma([i / max(1, num_heights - 1) for i in range(num_heights)]) if num_heights > 1 else ['darkviolet']
#     markers = ['o', 's', '^', 'D', 'v', 'p', '*', 'h', 'X']
    
#     plt.figure(figsize=(9, 5.5))
#     gamma = 1.305
    
#     for idx, h in enumerate(unique_heights):
#         sub_df = df[df['h'] == h].copy()
        
#         # This maps absolute m directly to the true structural control parameter
#         sub_df['beta'] = sub_df['m'] / (gamma ** h)
#         sub_df = sub_df.sort_values(by='beta')
        
#         plt.plot(sub_df['beta'], sub_df['influence_probability'],
#                  marker=markers[idx % len(markers)], color=colors[idx], linewidth=1.7, markersize=5,
#                  label=f"Height h = {h}")
                 
#     plt.title("True Finite-Size Scaling: Pure Geometric Pool Overlap", fontsize=12, fontweight='bold')
#     plt.xlabel(r"Corrected Control Parameter Density ($\beta = m / 1.305^h$)", fontsize=11)
#     plt.ylabel("Pr(Individual Variable Alters Output)", fontsize=11)
#     plt.xscale('log', base=2)
#     # plt.axhline(y=0.475, color='gray', linestyle=':', alpha=0.6, label='Saturated Phase Asymptote')
#     plt.grid(True, which="both", ls="--", alpha=0.4)
#     plt.legend(loc="lower left", fontsize=10)
#     plt.tight_layout()
    
#     os.makedirs(os.path.dirname(output_plot), exist_ok=True)
#     plt.savefig(output_plot, dpi=300)
#     print(f"Plot saved cleanly to '{output_plot}'")


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os

H_VALUES = [0, 1, 3, 5, 7, 10, 11, 12, 13]
OUTPUT_PLOT = "results/plots/pure_variable_scaling_collapse.png"

num_heights = len(H_VALUES)
colors = cm.plasma([i / max(1, num_heights - 1) for i in range(num_heights)]) if num_heights > 1 else ['darkviolet']
markers = ['o', 's', '^', 'D', 'v', 'p', '*', 'h', 'X']

plt.figure(figsize=(9, 5.5))
gamma = 1.5

for idx, height in enumerate(H_VALUES):
    csvPath = f"results/csv/variable_influence_transition_h{height}.csv"
    df = pd.read_csv(csvPath)
    df['beta'] = df['m'] / (gamma ** height)
    df = df.sort_values(by='beta')

    plt.plot(df['beta'], df['individual_influence_probability'], 
             marker=markers[idx % len(markers)], color=colors[idx], linewidth=1.7, markersize=5,
             label=f"Height h = {height}")

plt.title("Trying", fontsize=12, fontweight='bold')
plt.xlabel(fr"Control Parameter Density ($\beta = m / {gamma}^h$)", fontsize=11)
plt.ylabel("Pr(Individual Variable Alters Output)", fontsize=11)
plt.xscale('log', base=2)
plt.grid(True, which="both", ls="--", alpha=0.4)
plt.legend(loc="lower left", fontsize=10)
plt.tight_layout()

os.makedirs(os.path.dirname(OUTPUT_PLOT), exist_ok=True)
plt.savefig(OUTPUT_PLOT, dpi=300)
print(f"Plot saved to '{OUTPUT_PLOT}'")

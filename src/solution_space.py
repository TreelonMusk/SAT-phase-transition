# import numpy as np
# from pysat.solvers import Cadical153
# from sklearn.manifold import TSNE
# import pandas as pd
# import random

# # Reuse your generate function here
# def generate_formula(k, n, alpha):
#     m = int(alpha * n)
#     clauses = []
#     variables = list(range(1, n + 1))
#     for _ in range(m):
#         vars_ = random.sample(variables, k)
#         clause = [v if random.random() < 0.5 else -v for v in vars_]
#         clauses.append(clause)
#     return clauses

# def get_projections(n, alpha_list, k=3, n_sols=10000):
#     all_data = []
    
#     for alpha in alpha_list:
#         print(f"Processing alpha: {alpha}")
#         clauses = generate_formula(k, n, alpha)
        
#         with Cadical153(bootstrap_with=clauses) as solver:
#             solutions = []
#             for model in solver.enum_models():
#                 # Convert [-1, 2, -3] to [0, 1, 0]
#                 binary_sol = [1 if lit > 0 else 0 for lit in model]
#                 solutions.append(binary_sol)
#                 if len(solutions) >= n_sols: break
            
#             if not solutions:
#                 continue
                
#             # Perform t-SNE projection to 2D (or 3D)
#             # This "squashes" the N-dimensional Hamming space into visual coordinates
#             data_np = np.array(solutions)
#             # tsne = TSNE(n_components=2, perplexity=min(30, len(solutions)-1))
#             tsne = TSNE(
#                 n_components=2, 
#                 perplexity=min(30, len(solutions)-1),
#                 metric='hamming',  # Essential for binary SAT solutions
#                 init='pca',        # Helps with global structure
#                 learning_rate='auto',
#                 n_jobs=-1          # Uses all CPU cores for the t-SNE calculation
#             )
#             coords = tsne.fit_transform(data_np)
            
#             # Store results with the alpha label
#             df = pd.DataFrame(coords, columns=['x', 'y'])
#             df['alpha'] = alpha
#             all_data.append(df)
            
#     return pd.concat(all_data)

# # Usage
# # alphas_to_test = [3.0, 3.8, 4.1, 4.2, 4.25]
# alphas_to_test = [2.0, 3.8, 4.2]
# viz_df = get_projections(n=30, alpha_list=alphas_to_test)
# viz_df.to_csv("results/solution_space_coords1.csv")







# import numpy as np
# from pysat.solvers import Cadical153
# from sklearn.manifold import TSNE
# import pandas as pd
# from concurrent.futures import ProcessPoolExecutor
# import random

# def generate_formula(k, n, alpha):
#     m = int(alpha * n)
#     clauses = []
#     variables = list(range(1, n + 1))
#     for _ in range(m):
#         vars_ = random.sample(variables, k)
#         clause = [v if random.random() < 0.5 else -v for v in vars_]
#         clauses.append(clause)
#     return clauses

# def process_single_alpha(alpha, n, k, n_sols):
#     """Everything for ONE alpha happens here, on ONE core."""
#     print(f"Starting alpha: {alpha}")
#     clauses = generate_formula(k, n, alpha)
    
#     solutions = []
#     with Cadical153(bootstrap_with=clauses) as solver:
#         for model in solver.enum_models():
#             binary_sol = [1 if lit > 0 else 0 for lit in model]
#             solutions.append(binary_sol)
#             if len(solutions) >= n_sols:
#                 break
    
#     if not solutions:
#         return pd.DataFrame()

#     # Perform t-SNE locally on this process
#     data_np = np.array(solutions)
#     # n_jobs=1 here because the parallelization happens at the Alpha level
#     tsne = TSNE(n_components=2, metric='hamming', n_jobs=1, init='pca', learning_rate='auto', perplexity=min(30, len(solutions)-1))
#     coords = tsne.fit_transform(data_np)
    
#     df = pd.DataFrame(coords, columns=['x', 'y'])
#     df['alpha'] = alpha
#     print(f"Finished alpha: {alpha}")
#     return df

# # --- IN YOUR MAIN EXECUTION BLOCK ---
# if __name__ == '__main__':
#     alphas_to_test = [2.0, 3.8, 4.2]
#     n = 30
#     k = 3
#     n_sols = 100000 
    
#     # max_workers defaults to the number of processors on your machine
#     with ProcessPoolExecutor() as executor:
#         # This sends each alpha to a different core
#         results = list(executor.map(
#             process_single_alpha, 
#             alphas_to_test, 
#             [n]*len(alphas_to_test), 
#             [k]*len(alphas_to_test), 
#             [n_sols]*len(alphas_to_test)
#         ))

#     viz_df = pd.concat(results)
#     viz_df.to_csv("results/parallel_results.csv")





# import numpy as np
# from pysat.solvers import Cadical153
# from sklearn.manifold import TSNE
# import pandas as pd
# from concurrent.futures import ProcessPoolExecutor
# import random

# def get_solutions(n, k, alpha, n_sols):
#     m = int(alpha * n)
#     variables = list(range(1, n + 1))
#     clauses = []
#     for _ in range(m):
#         vars_ = random.sample(variables, k)
#         clauses.append([v if random.random() < 0.5 else -v for v in vars_])
    
#     solutions = []
#     with Cadical153(bootstrap_with=clauses) as solver:
#         # Optimization: limit enumeration strictly
#         for model in solver.enum_models():
#             solutions.append([1 if lit > 0 else 0 for lit in model])
#             if len(solutions) >= n_sols:
#                 break
#     return solutions

# def process_alpha(alpha):
#     # Setup constants inside for clean pickling
#     N, K, MAX_SOLS = 30, 3, 20000 # Reduced for visual clarity and speed
    
#     print(f"Solving for Alpha: {alpha}...")
#     sols = get_solutions(N, K, alpha, MAX_SOLS)
    
#     if len(sols) < 10: return None

#     # 3D Projection
#     tsne = TSNE(
#         n_components=3, # Change to 3 for 3D plots
#         metric='hamming',
#         init='random', 
#         perplexity=min(30, len(sols)-1),
#         n_jobs=1 # Keep this 1 to avoid nested parallelization
#     )
    
#     coords = tsne.fit_transform(np.array(sols))
#     df = pd.DataFrame(coords, columns=['x', 'y', 'z'])
#     df['alpha'] = alpha
#     return df

# if __name__ == '__main__':
#     # Using more samples per alpha to smooth out "weird" results
#     alphas = [2.0, 3.0, 3.5, 3.8, 4.0, 4.2]
    
#     # This will actually use your cores
#     with ProcessPoolExecutor(max_workers=6) as executor:
#         results = list(executor.map(process_alpha, alphas))
    
#     # Filter out Nones and combine
#     final_df = pd.concat([r for r in results if r is not None])
#     final_df.to_csv("results/solution_space_coords1.csv", index=False)
#     print("Done! Ready for Plotly.")





# import numpy as np
# from pysat.solvers import Cadical153
# from sklearn.manifold import TSNE
# from sklearn.decomposition import PCA
# import pandas as pd
# from multiprocessing import Pool, cpu_count
# import random

# def get_viz_data(args):
#     """Worker function for one alpha."""
#     n, alpha, k, n_sols, dims = args
#     m = int(alpha * n)
    
#     # Generate one formula for this worker
#     variables = list(range(1, n + 1))
#     clauses = []
#     for _ in range(m):
#         vars_ = random.sample(variables, k)
#         clauses.append([v if random.random() < 0.5 else -v for v in vars_])
    
#     solutions = []
#     with Cadical153(bootstrap_with=clauses) as solver:
#         for model in solver.enum_models():
#             solutions.append([1 if lit > 0 else 0 for lit in model])
#             if len(solutions) >= n_sols:
#                 break
    
#     if len(solutions) < 5: # TSNE needs a minimum number of points
#         return None

#     # pca = PCA(n_components=dims)

#     # TSNE settings optimized for SAT solutions
#     tsne = TSNE(
#         n_components=dims, 
#         metric='hamming', 
#         init='random', 
#         perplexity=min(30, len(solutions)-1),
#         n_jobs=1 # Critical: let the Pool handle the cores, not TSNE
#     )
    
#     # pca_coords = pca.fit_transform(np.array(solutions))
#     tsne_coords = tsne.fit_transform(np.array(solutions))
    
#     # Create DF with dynamic column names based on dims
#     cols = ['x', 'y', 'z'] if dims == 3 else ['x', 'y']
#     df = pd.DataFrame(tsne_coords, columns=cols)
#     # df = pd.DataFrame({
#     #     'pca_x': pca_coords[:, 0], 'pca_y': pca_coords[:, 1],
#     #     'tsne_x': tsne_coords[:, 0], 'tsne_y': tsne_coords[:, 1],
#     #     'alpha': alpha,
#     #     'avg_hamming': avg_hamming  # This value will be the same for all rows of this alpha
#     # })
#     df['alpha'] = alpha
#     return df

# if __name__ == "__main__":
#     # CONFIG
#     N = 30
#     K = 3
#     # ALPHAS = [2.0, 3.0, 3.8, 4.0, 4.2, 4.25] # For K = 3
#     ALPHAS = [0.5, 0.7, 0.9, 1.0, 1.1, 1.2] # For K = 2
#     MAX_SOLS = 200000 # Keep this reasonable so TSNE doesn't explode
#     DIMENSIONS = 2  # Set to 2 or 3
    
#     tasks = [(N, a, K, MAX_SOLS, DIMENSIONS) for a in ALPHAS]

#     print(f"Spawning {len(tasks)} visualization jobs across {cpu_count()} cores...")
    
#     with Pool(processes=cpu_count()) as pool:
#         # Using map ensures we get results back in order
#         results = pool.map(get_viz_data, tasks)

#     # Clean up and Save
#     final_df = pd.concat([r for r in results if r is not None])
#     final_df.to_csv("results/solution_space_coords2.csv", index=False)
#     print("Success! File saved.")


import numpy as np
from pysat.solvers import Cadical153
import umap
from sklearn.decomposition import PCA
import pandas as pd
from multiprocessing import Pool, cpu_count
import random
import os

os.environ["OMP_NUM_THREADS"] = "1"  # Disable OpenMP multithreading for UMAP

def get_viz_data(args):
    """Worker function for one alpha."""
    n, alpha, k, n_sols, dims = args
    m = int(alpha * n)
    
    # Generate one formula for this worker
    variables = list(range(1, n + 1))
    clauses = []
    for _ in range(m):
        vars_ = random.sample(variables, k)
        clauses.append([v if random.random() < 0.5 else -v for v in vars_])
    
    solutions = []
    with Cadical153(bootstrap_with=clauses) as solver:
        for model in solver.enum_models():
            solutions.append([1 if lit > 0 else 0 for lit in model])
            if len(solutions) >= n_sols:
                break
    
    if len(solutions) < 5: # UMAP needs a minimum number of points
        return None

    # pca = PCA(n_components=dims)

    # UMAP settings optimized for SAT solutions
    reducer = umap.UMAP(
        n_components=dims,
        metric='hamming',
        n_neighbors=15,
        min_dist=0.1,
        init='spectral',
        n_jobs=1
    )
    
    # pca_coords = pca.fit_transform(np.array(solutions))
    umap_coords = reducer.fit_transform(np.array(solutions))
    
    # Create DF with dynamic column names based on dims
    cols = ['x', 'y', 'z'] if dims == 3 else ['x', 'y']
    df = pd.DataFrame(umap_coords, columns=cols)
    df['alpha'] = alpha
    return df

if __name__ == "__main__":
    N = 50
    K = 2
    # ALPHAS = [2.0, 3.0, 3.8, 4.0] # For K = 3
    ALPHAS = [0.2, 0.5, 0.8, 1, 1.2, 1.4] # For K = 2
    MAX_SOLS = 200000
    DIMENSIONS = 2  # Set to 2 or 3
    
    tasks = [(N, a, K, MAX_SOLS, DIMENSIONS) for a in ALPHAS]

    print(f"Spawning {len(tasks)} visualization jobs across {cpu_count()} cores...")
    
    with Pool(processes=cpu_count()) as pool:
        # Using map ensures we get results back in order
        results = pool.map(get_viz_data, tasks)

    # Clean up and Save
    final_df = pd.concat([r for r in results if r is not None])
    final_df.to_csv(f"results/csv/solution_space_coords_N={N}.csv", index=False)
    print("File saved.")

import random
import numpy as np
import multiprocessing as mp

def generate_random_3sat(n, alpha):
    m = int(n * alpha)
    variables = list(range(1, n + 1))
    return [[v if random.random() < 0.5 else -v for v in random.sample(variables, 3)] for _ in range(m)]

def evaluate_clause(clause, assignment):
    return any((lit > 0 and assignment[lit] == 1) or (lit < 0 and assignment[-lit] == 0) for lit in clause)

def walksat_solve(clauses, n, initial_assignment=None, max_flips=2000):
    assignment = {i: random.choice([0, 1]) for i in range(1, n + 1)} if initial_assignment is None else initial_assignment.copy()
    for _ in range(max_flips):
        unsat_clauses = [c for c in clauses if not evaluate_clause(c, assignment)]
        if not unsat_clauses:
            return assignment
        clause = random.choice(unsat_clauses)
        var_to_flip = abs(random.choice(clause)) # Simplified WalkSAT heuristic
        assignment[var_to_flip] = 1 - assignment[var_to_flip]
    return None

def sample_single_cluster(args):
    clauses, n, solutions_per_cluster = args
    local_solutions = []
    
    # Global jumps
    base_solution = walksat_solve(clauses, n)
    if not base_solution:
        return [] # Failed to find a base solution
    
    local_solutions.append([base_solution[i] for i in range(1, n + 1)])
        
    # Local jumps
    for _ in range(solutions_per_cluster):
        perturbed = base_solution.copy()
        kick = random.randint(3,6) # maybe change to (4,8)
        for v in random.sample(list(range(1, n + 1)), kick):
            perturbed[v] = 1 - perturbed[v]
            
        local_solution = walksat_solve(clauses, n, initial_assignment=perturbed)
        if local_solution:
            local_solutions.append([local_solution[i] for i in range(1, n + 1)])

            if random.random() < 0.5:
                base_solution = local_solution
            
    return local_solutions

if __name__ == "__main__":
    N = 100
    ALPHA = 2
    NUM_CLUSTERS = 2000
    SOLS_PER_CLUSTER = 2000

    print(f"Generating formula n={N}, alpha={ALPHA}...")
    clauses = generate_random_3sat(N, ALPHA)

    tasks = [(clauses, N, SOLS_PER_CLUSTER) for _ in range(NUM_CLUSTERS)]
    all_solutions = []
    
    print(f"Sampling clusters using {mp.cpu_count()} cores...")
    with mp.Pool(mp.cpu_count()) as pool:
        results = pool.map(sample_single_cluster, tasks)
        
    for cluster_sols in results:
        all_solutions.extend(cluster_sols)
        
    # We remove duplicates
    unique_solutions = np.unique(np.array(all_solutions), axis=0)
    
    filename = f"results/npy/solution_space_n{N}_a{ALPHA}.npy"
    np.save(filename, unique_solutions)
    print(f"Saved {len(unique_solutions)} unique solutions to {filename}")
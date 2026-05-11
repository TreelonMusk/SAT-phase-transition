# # import random

# # def generate_inf_debug(n_vars, alpha):
# #     m_nodes = max(1, int(alpha * n_vars))
# #     aux_offset = n_vars
# #     pool = ['T', 'F']
    
# #     print(f"--- Generating INF for N={n_vars}, Alpha={alpha} ({m_nodes} nodes) ---")
# #     for i in range(1, m_nodes + 1):
# #         current_node = aux_offset + i
# #         control_var = random.randint(1, n_vars)
# #         left = random.choice(pool)
# #         right = random.choice(pool)
        
# #         # Log the high-level logic
# #         print(f"Node_{current_node} = IF Var_{control_var} THEN {left} ELSE {right}")
# #         pool.append(current_node)
    
# #     print(f"Root: Node_{aux_offset + m_nodes}")

# # if __name__ == "__main__":
# #     n_vars = 10
# #     alpha = 2.5
# #     generate_inf_debug(n_vars, alpha)


# import random

# def generate_inf(n, depth):
#     """
#     Generates a random Boolean formula in IF-Normal Form.
    
#     Args:
#         n (int): The number of variables (labeled 1 to n).
#         depth (int): The maximum depth of the ITE tree.
        
#     Returns:
#         tuple or int: A recursive structure (var, then_branch, else_branch) 
#                       or a leaf value (0 or 1).
#     """
#     # Base case: if depth is 0, return a random boolean constant
#     if depth == 0:
#         return random.choice([0, 1])
    
#     # Randomly decide to stop early to create varied tree shapes
#     if depth > 1 and random.random() < 0.2:
#         return random.choice([0, 1])

#     # Select a random variable for the decision node
#     var = random.randint(1, n)
    
#     # Recursively generate branches
#     then_branch = generate_inf(n, depth - 1)
#     else_branch = generate_inf(n, depth - 1)
    
#     return (var, then_branch, else_branch)

# # Example Usage:
# # n=3 variables, depth=2 tree
# # Returns: (2, (1, 0, 1), 0) -> "If x2 then (if x1 then 0 else 1) else 0"
# print(generate_inf(10, 5))



# import random
# import numpy as np

# def generate_ite_cnf(n_vars, n_nodes):
#     clauses = []
#     # 1...n_vars are user variables
#     # n_vars + 1 is reserved for CONST_0
#     # n_vars + 2 is reserved for CONST_1
#     # n_vars + 3... are auxiliary variables for gates
    
#     CONST_0 = n_vars + 1
#     CONST_1 = n_vars + 2
#     next_aux = n_vars + 3
    
#     # Base constraints for constants
#     clauses.append([-CONST_0])
#     clauses.append([CONST_1])
    
#     def get_leaf():
#         r = random.random()
#         if r < 0.1: return CONST_0
#         if r < 0.2: return CONST_1
#         return random.randint(1, n_vars)

#     def add_ite_gate(c, t, e):
#         nonlocal next_aux
#         out = next_aux
#         next_aux += 1
        
#         # Tseytin encoding for Out <=> ITE(C, T, E)
#         # (C and T) => Out  ->  (~C or ~T or Out)
#         # (C and ~T) => ~Out ->  (~C or T or ~Out)
#         # (~C and E) => Out  ->  (C or ~E or Out)
#         # (~C and ~E) => ~Out -> (C or E or ~Out)
#         clauses.append([-c, -t, out])
#         clauses.append([-c, t, -out])
#         clauses.append([c, -e, out])
#         clauses.append([c, e, -out])
#         return out

#     def build_tree(m):
#         if m <= 0:
#             return get_leaf()
        
#         # Ensure m-1 nodes are split, allowing any branch (including condition) 
#         # to be complex or a leaf.
#         m_left = m - 1
#         p1 = random.randint(0, m_left)
#         p2 = random.randint(0, m_left - p1)
#         p3 = m_left - p1 - p2
        
#         # Shuffle to ensure the 'Condition' slot isn't always the smallest/largest
#         parts = [p1, p2, p3]
#         random.shuffle(parts)
                
#         return add_ite_gate(build_tree(parts[0]), build_tree(parts[1]), build_tree(parts[2]))


#     root = build_tree(n_nodes)
#     # The whole formula is satisfied if the root evaluates to True
#     clauses.append([root])
    
#     return clauses

# # Test run
# test_clauses = generate_ite_cnf(10, 10)
# print(f"Nodes: 10, Variables: 10, Generated Clauses: {len(test_clauses)}")
# print(f"Sample clauses: {test_clauses[:10]}")


# class ITE_Node:
#     def __init__(self):
#         self.C = None  # Control variable
#         self.T = None  # Then branch
#         self.E = None  # Else branch

#     def insert(self):    

# def generate_ite(h, m):
#     """
#     Generates a random regular ITE tree of {h,m,0,1,f}.
#     """
#     if h == 0:
#         idx = random.randrange(m + 2)
#         if idx < m:
#             return f"x{idx}"
#         elif idx == m:
#             return "0"
#         else:
#             return "1"
    
#     # Recursive step
#     cond = generate_ite(h - 1, m)
#     then_node = generate_ite(h - 1, m)
#     else_node = generate_ite(h - 1, m)
    
#     return f"ITE({cond}, {then_node}, {else_node})"

# print(generate_ite(18, 10))


import random

def generate_leaves(h, m):
    """
    Generates a flat list of 3^h leaf assignments.
    0 to m-1: Variables x1 to xm
    m: Constant 0
    m+1: Constant 1
    """
    n = 3**h
    return [random.randrange(m + 2) for _ in range(n)]

def tree_to_cnf(leaves, m):
    """
    Converts a ternary ITE tree (as a flat leaf list) to CNF using 
    the Tseytin 4-clause gate encoding.
    """
    clauses = []
    
    # 1. Fixed Variables
    # x1 to xm: Indices 1 to m
    # Constant 0: Index m + 1
    # Constant 1: Index m + 2
    c0 = m + 1
    c1 = m + 2
    clauses.append([-c0]) # Force constant 0 to False
    clauses.append([c1])  # Force constant 1 to True
    
    # Initialize the bottom layer with variable indices
    current_layer_vars = []
    for leaf in leaves:
        if leaf < m:
            current_layer_vars.append(leaf + 1)
        elif leaf == m:
            current_layer_vars.append(c0)
        else:
            current_layer_vars.append(c1)
            
    # 2. Build internal gates bottom-up
    next_aux_var = m + 3
    while len(current_layer_vars) > 1:
        next_layer = []
        # Group siblings by threes: (Condition, Then, Else)
        for i in range(0, len(current_layer_vars), 3):
            c, t, e = current_layer_vars[i:i+3]
            v_i = next_aux_var
            next_aux_var += 1
            
            # Standard 4-clause ITE gate: v_i <-> (c ? t : e)
            clauses.append([-c, -t, v_i])  # (c ^ t) -> v_i
            clauses.append([-c,  t, -v_i]) # (c ^ !t) -> !v_i
            clauses.append([ c, -e,  v_i]) # (!c ^ e) -> v_i
            clauses.append([ c,  e, -v_i]) # (!c ^ !e) -> !v_i
            
            next_layer.append(v_i)
        current_layer_vars = next_layer
        
    # 3. Constraint: The root of the whole tree must be True
    root_var = current_layer_vars[0]
    clauses.append([root_var])
    
    return clauses, next_aux_var - 1

def export_dimacs(clauses, num_vars):
    """Converts the clause list into standard DIMACS format."""
    header = f"p cnf {num_vars} {len(clauses)}"
    body = "\n".join(" ".join(map(str, c)) + " 0" for c in clauses)
    return f"{header}\n{body}"

# Execution Example:
h = 8  # Depth 3 = 3^16 = 43046721 leaves
m = 4000 # 200 input variables
leaves = generate_leaves(h, m)
clauses, total_vars = tree_to_cnf(leaves, m)
dimacs_str = export_dimacs(clauses, total_vars)

# Save to file for your SAT solver
with open(f"ite_{h}_{m}.cnf", "w") as f:
    f.write(dimacs_str)

print(f"CNF generated with {total_vars} variables and {len(clauses)} clauses.")

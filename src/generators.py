"""
Random instance generators for the two studied ensembles.

Random k-SAT  F_k(n, m):  m clauses, each over k distinct variables chosen
uniformly from n, every literal negated with probability 1/2.

Random ITE    T(h, beta, Sigma):  a regular ternary tree of height h whose
3^h leaves are labelled uniformly at random from the alphabet Sigma, and whose
internal nodes are ITE(c, t, e) = (c AND t) OR (NOT c AND e) gates.

ITE leaves are encoded as DIMACS-style integers, for a pool of m variables:
    +i / -i   variable x_i / its negation (1 <= i <= m)
    m + 1     constant 0
    m + 2     constant 1
"""

import numpy as np


def random_ksat(k, n, m, rng):
    """Random k-SAT formula as a list of DIMACS clauses (rng: random.Random)."""
    variables = range(1, n + 1)
    return [[v if rng.random() < 0.5 else -v for v in rng.sample(variables, k)]
            for _ in range(m)]


def ite_constants(m):
    """DIMACS indices used for the constants 0 and 1."""
    return m + 1, m + 2


def sample_ite_leaves(h, m, negations, rng):
    """
    Sample the 3^h leaves of a random ITE tree uniformly from the alphabet
    Sigma = {x_1..x_m, 0, 1}, or {x_1..x_m, -x_1..-x_m, 0, 1} with negations.
    rng: numpy.random.Generator. Returns an int64 array.
    """
    n_leaves = 3 ** h
    c0, c1 = ite_constants(m)
    if negations:
        r = rng.integers(0, 2 * m + 2, n_leaves)
        lits = r // 2 + 1
        lits = np.where(r % 2 == 1, -lits, lits)
        return np.where(r < 2 * m, lits, np.where(r == 2 * m, c0, c1))
    r = rng.integers(0, m + 2, n_leaves)
    return np.where(r < m, r + 1, np.where(r == m, c0, c1))


def encode_ite(leaves, m, add_clause, fold_constants=True):
    """
    Tseitin-encode an ITE tree into CNF, bottom-up, layer by layer.

    Every internal gate v <-> ITE(c, t, e) gets one auxiliary variable and four
    clauses. With `fold_constants`, gates whose condition is a constant, or
    whose branches are identical, are collapsed instead of encoded.
    Clauses are passed to `add_clause` (e.g. list.append or solver.add_clause),
    including the two unit clauses that fix the constants.

    Returns (root literal, highest variable index used).
    """
    c0, c1 = ite_constants(m)
    add_clause([-c0])
    add_clause([c1])

    layer = [int(x) for x in leaves]
    next_aux = m + 3
    while len(layer) > 1:
        next_layer = []
        for i in range(0, len(layer), 3):
            c, t, e = layer[i:i + 3]
            if fold_constants:
                if c == c1:
                    next_layer.append(t)
                    continue
                if c == c0:
                    next_layer.append(e)
                    continue
                if t == e:
                    next_layer.append(t)
                    continue
            v = next_aux
            next_aux += 1
            add_clause([-c, -t, v])   # (c and t) -> v
            add_clause([-c, t, -v])   # (c and not t) -> not v
            add_clause([c, -e, v])    # (not c and e) -> v
            add_clause([c, e, -v])    # (not c and not e) -> not v
            next_layer.append(v)
        layer = next_layer
    return layer[0], next_aux - 1


def ite_leaf_values(leaves, m, assignment):
    """Boolean value of every leaf under `assignment` (0/1 array of length m)."""
    # Lookup table indexed by literal + m, covering literals -m .. m + 2.
    assignment = np.asarray(assignment, dtype=bool)
    table = np.zeros(2 * m + 3, dtype=bool)
    table[m + 1:2 * m + 1] = assignment          # +x_i  -> index m + i
    table[:m] = ~assignment[::-1]                # -x_i  -> index m - i
    table[2 * m + 1] = False                     # constant 0
    table[2 * m + 2] = True                      # constant 1
    return table[leaves + m]


def evaluate_ite(values):
    """Evaluate an ITE tree bottom-up from its leaf values; returns a bool."""
    while len(values) > 1:
        triples = values.reshape(-1, 3)
        values = np.where(triples[:, 0], triples[:, 1], triples[:, 2])
    return bool(values[0])


def to_dimacs(clauses, num_vars):
    """Render clauses in the DIMACS CNF text format."""
    lines = [f"p cnf {num_vars} {len(clauses)}"]
    lines += [" ".join(map(str, c)) + " 0" for c in clauses]
    return "\n".join(lines) + "\n"

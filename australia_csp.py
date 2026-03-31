"""
=============================================================================
 CSP Assignment — Problem 1: Australia Map Coloring
 Reference: Artificial Intelligence: A Modern Approach (4th Ed.)
            Stuart Russell & Peter Norvig, Pearson
            Chapter 6 — Constraint Satisfaction Problems
            Figure 6.1
=============================================================================
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx


# =============================================================================
#  GENERIC CSP FRAMEWORK
#  Backtracking Search (AIMA Fig 6.5) with MRV + Forward Checking
# =============================================================================

class CSP:
    """
    Generic binary-constraint CSP solver.

    Parameters
    ----------
    variables  : list of variable names
    domains    : dict  {var: [possible values]}
    neighbors  : dict  {var: [list of neighboring vars]}
    constraint : callable(var_A, val_A, var_B, val_B) -> bool
    """

    def __init__(self, variables, domains, neighbors, constraint):
        self.variables  = list(variables)
        self.domains    = {v: list(domains[v]) for v in variables}
        self.neighbors  = neighbors
        self.constraint = constraint

    def backtracking_search(self):
        """Entry point — returns assignment dict or None if unsolvable."""
        return self._backtrack({})

    def _backtrack(self, assignment):
        if len(assignment) == len(self.variables):
            return dict(assignment)

        var = self._mrv(assignment)

        for value in list(self.domains[var]):
            if self._consistent(var, value, assignment):
                assignment[var] = value
                snapshot = {v: list(self.domains[v]) for v in self.variables}

                if self._forward_check(var, value, assignment):
                    result = self._backtrack(assignment)
                    if result is not None:
                        return result

                for v in self.variables:
                    self.domains[v] = snapshot[v]
                del assignment[var]

        return None

    def _mrv(self, assignment):
        """Minimum Remaining Values heuristic (AIMA §6.3.1)"""
        unassigned = [v for v in self.variables if v not in assignment]
        return min(unassigned, key=lambda v: len(self.domains[v]))

    def _consistent(self, var, value, assignment):
        return all(
            self.constraint(var, value, nb, assignment[nb])
            for nb in self.neighbors.get(var, [])
            if nb in assignment
        )

    def _forward_check(self, var, value, assignment):
        """Forward Checking — prune neighbors' domains (AIMA §6.3.2)"""
        for nb in self.neighbors.get(var, []):
            if nb not in assignment:
                self.domains[nb] = [
                    v for v in self.domains[nb]
                    if self.constraint(nb, v, var, value)
                ]
                if not self.domains[nb]:
                    return False
        return True


def ne_constraint(A, a, B, b):
    """Neighbouring regions must have different colours."""
    return a != b


# =============================================================================
#  PROBLEM 1 — AUSTRALIA MAP COLORING
# =============================================================================

def solve_australia():
    print("=" * 60)
    print("PROBLEM 1 — AUSTRALIA MAP COLORING")
    print("Reference: AIMA 4th Ed., Figure 6.1")
    print("=" * 60)

    # Variables: 7 states / territories
    variables = ['WA', 'NT', 'Q', 'SA', 'NSW', 'V', 'T']

    # Domain: 3 colours are sufficient (four-colour theorem guarantees ≤4)
    colors  = ['Red', 'Green', 'Blue']
    domains = {v: colors[:] for v in variables}

    # Adjacency from AIMA Figure 6.1
    neighbors = {
        'WA':  ['NT', 'SA'],
        'NT':  ['WA', 'Q', 'SA'],
        'Q':   ['NT', 'SA', 'NSW'],
        'SA':  ['WA', 'NT', 'Q', 'NSW', 'V'],
        'NSW': ['Q', 'SA', 'V'],
        'V':   ['SA', 'NSW'],
        'T':   []           # Tasmania — island, no land neighbours
    }

    csp      = CSP(variables, domains, neighbors, ne_constraint)
    solution = csp.backtracking_search()

    print("\nSolution:")
    for v in variables:
        print(f"  {v:5s} → {solution[v]}")

    # ── Verify ────────────────────────────────────────────────────────────────
    print("\nVerification (no two adjacent regions share a colour):")
    ok = True
    for v, nbs in neighbors.items():
        for nb in nbs:
            if solution[v] == solution[nb]:
                print(f"  ✗ CONFLICT: {v} and {nb} both = {solution[v]}")
                ok = False
    if ok:
        print("  ✓ All constraints satisfied!")

    # ── Visualize ─────────────────────────────────────────────────────────────
    HEX = {'Red': '#e74c3c', 'Green': '#27ae60', 'Blue': '#2980b9'}

    # Approximate positions matching Figure 6.1(b)
    pos = {
        'WA':  (0.0, 2.0),
        'NT':  (2.0, 3.2),
        'Q':   (4.2, 3.2),
        'SA':  (2.6, 1.8),
        'NSW': (4.2, 1.8),
        'V':   (3.8, 0.6),
        'T':   (3.5, -0.6)
    }

    G = nx.Graph()
    G.add_nodes_from(variables)
    for v, nbs in neighbors.items():
        for nb in nbs:
            if v < nb:
                G.add_edge(v, nb)

    node_colors = [HEX[solution[v]] for v in G.nodes()]

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor('#f8f9fa')
    ax.set_facecolor('#f8f9fa')

    nx.draw_networkx(
        G, pos=pos, ax=ax,
        node_color=node_colors, node_size=2200,
        font_size=14, font_weight='bold', font_color='white',
        edge_color='#444', width=2.5
    )

    patches = [mpatches.Patch(color=HEX[c], label=c) for c in colors]
    ax.legend(handles=patches, loc='lower left', fontsize=11,
              framealpha=0.9, edgecolor='#aaa')
    ax.set_title(
        "Australia Map Coloring — CSP\n"
        "AIMA 4th Ed. (Russell & Norvig) — Figure 6.1",
        fontsize=14, fontweight='bold', pad=15
    )
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('australia_map_coloring.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("\nVisualization saved → australia_map_coloring.png")
    return solution


if __name__ == "__main__":
    solve_australia()

"""
=============================================================================
 CSP Assignment — Problem 3: Sudoku Puzzle
 Reference: Artificial Intelligence: A Modern Approach (4th Ed.)
            Stuart Russell & Peter Norvig, Pearson
            Chapter 6 §6.1.2 — Figure 6.4
=============================================================================
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# =============================================================================
#  GENERIC CSP FRAMEWORK
#  Backtracking Search (AIMA Fig 6.5) with MRV + Forward Checking
# =============================================================================

class CSP:
    def __init__(self, variables, domains, neighbors, constraint):
        self.variables  = list(variables)
        self.domains    = {v: list(domains[v]) for v in variables}
        self.neighbors  = neighbors
        self.constraint = constraint

    def backtracking_search(self):
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
    return a != b


# =============================================================================
#  PROBLEM 3 — SUDOKU (AIMA §6.1.2, Figure 6.4)
# =============================================================================

def solve_sudoku():
    print("=" * 60)
    print("PROBLEM 3 — SUDOKU PUZZLE (CSP)")
    print("Reference: AIMA 4th Ed., §6.1.2, Figure 6.4")
    print("=" * 60)

    ROWS = 'ABCDEFGHI'
    COLS = '123456789'

    # 81 variables: A1 … I9
    variables = [r + c for r in ROWS for c in COLS]

    # Puzzle — Figure 6.4(a).  '0' = empty cell.
    puzzle_flat = (
        "003020600"
        "900305001"
        "001806400"
        "008102900"
        "700000008"
        "006708200"
        "002609500"
        "800203009"
        "005010300"
    )

    domains = {}
    given   = {}
    for i, var in enumerate(variables):
        d = int(puzzle_flat[i])
        if d == 0:
            domains[var] = list(range(1, 10))
        else:
            domains[var] = [d]
            given[var]   = d

    # Neighbours: same row ∪ same column ∪ same 3×3 box (excluding self)
    def same_row(v, u): return v[0] == u[0]
    def same_col(v, u): return v[1] == u[1]
    def same_box(v, u):
        r = ROWS.index(v[0]) // 3 == ROWS.index(u[0]) // 3
        c = (int(v[1]) - 1) // 3 == (int(u[1]) - 1) // 3
        return r and c

    neighbors = {
        v: [u for u in variables
            if u != v and (same_row(v, u) or same_col(v, u) or same_box(v, u))]
        for v in variables
    }

    csp      = CSP(variables, domains, neighbors, ne_constraint)
    solution = csp.backtracking_search()

    print("\nSolved Sudoku grid:")
    header = "    " + "  ".join(COLS)
    print(header)
    print("   " + "-" * 27)
    for r in ROWS:
        row = [str(solution[r + c]) for c in COLS]
        row_str = (f"{row[0]} {row[1]} {row[2]} | "
                   f"{row[3]} {row[4]} {row[5]} | "
                   f"{row[6]} {row[7]} {row[8]}")
        print(f" {r} | {row_str}")
        if r in ('C', 'F'):
            print("   " + "-" * 27)

    # ── Verify ────────────────────────────────────────────────────────────────
    print("\nVerification:")
    ok = True
    for v, nbs in neighbors.items():
        for nb in nbs:
            if solution[v] == solution[nb]:
                print(f"  ✗ CONFLICT: {v}={solution[v]} and {nb}={solution[nb]}")
                ok = False
                break
        if not ok:
            break
    if ok:
        print("  ✓ All row, column, and box constraints satisfied!")

    # ── Visualize ─────────────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    fig.patch.set_facecolor('#f4f6f7')

    views = [
        ("(a) Puzzle — Figure 6.4(a)",    given,    ),
        ("(b) Solution — Figure 6.4(b)",  solution, ),
    ]

    for ax_idx, (title, data) in enumerate(views):
        ax = axes[ax_idx]
        ax.set_xlim(0, 9)
        ax.set_ylim(0, 9)
        ax.set_aspect('equal')
        ax.set_title(title, fontsize=13, fontweight='bold', pad=10)
        ax.axis('off')
        ax.set_facecolor('#fdfefe')

        # Alternating 3×3 box backgrounds
        for br in range(3):
            for bc in range(3):
                color = '#d5e8d4' if (br + bc) % 2 == 0 else '#dae8fc'
                ax.add_patch(plt.Rectangle(
                    (bc * 3, br * 3), 3, 3,
                    facecolor=color, edgecolor='none', zorder=0
                ))

        # Grid lines
        for i in range(10):
            lw  = 2.8 if i % 3 == 0 else 0.7
            col = '#1a1a2e' if i % 3 == 0 else '#888'
            ax.axhline(i, color=col, linewidth=lw, zorder=2)
            ax.axvline(i, color=col, linewidth=lw, zorder=2)

        # Fill numbers
        for i, r in enumerate(ROWS):
            for j, c in enumerate(COLS):
                var = r + c
                val = data.get(var)
                if val:
                    is_given = var in given
                    fc = '#1a1a2e' if is_given else '#1a5276'
                    fw = 'bold'   if is_given else 'normal'
                    fs = 13       if is_given else 11
                    ax.text(
                        j + 0.5, 8.5 - i, str(val),
                        ha='center', va='center',
                        fontsize=fs, fontweight=fw, color=fc, zorder=3
                    )

    plt.suptitle(
        "Sudoku — Constraint Satisfaction Problem\n"
        "AIMA 4th Ed. (Russell & Norvig) — §6.1.2, Figure 6.4",
        fontsize=14, fontweight='bold', y=1.02
    )
    plt.tight_layout()
    plt.savefig('sudoku.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("\nVisualization saved → sudoku.png")
    return solution


if __name__ == "__main__":
    solve_sudoku()

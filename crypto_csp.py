"""
=============================================================================
 CSP Assignment — Problem 4: Cryptarithmetic TWO + TWO = FOUR
 Reference: Artificial Intelligence: A Modern Approach (4th Ed.)
            Stuart Russell & Peter Norvig, Pearson
            Chapter 6 — Figure 6.2(a)
=============================================================================
 Each letter stands for a distinct digit (0–9).
 Find an assignment such that the arithmetic sum is correct,
 with the restriction that no leading zeros are allowed (T ≠ 0, F ≠ 0).

   Column decomposition (right to left):
     Col 1 (ones)     : O + O       = R + 10·C1
     Col 2 (tens)     : W + W + C1  = U + 10·C2
     Col 3 (hundreds) : T + T + C2  = O + 10·C3
     Col 4 (thousands): C3          = F

 Variables: T W O F U R  (digit variables, 0–9)
            C1 C2 C3     (carry bits, 0 or 1)
=============================================================================
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# =============================================================================
#  PROBLEM 4 — CRYPTARITHMETIC:  TWO + TWO = FOUR
# =============================================================================
# This uses a custom backtracking search that handles n-ary constraints
# (column equations involve 3–4 variables — beyond simple binary constraints).
# This mirrors the "higher-order / auxiliary variable" approach in AIMA §6.1.4.
# =============================================================================

def solve_crypto():
    print("=" * 60)
    print("PROBLEM 4 — CRYPTARITHMETIC: TWO + TWO = FOUR")
    print("Reference: AIMA 4th Ed., Figure 6.2(a)")
    print("=" * 60)

    letters = ['T', 'W', 'O', 'F', 'U', 'R']
    carries = ['C1', 'C2', 'C3']
    variables = letters + carries

    # Domains
    domains = {l: list(range(10)) for l in letters}   # digits 0–9
    domains['C1'] = [0, 1]                             # carry bits
    domains['C2'] = [0, 1]
    domains['C3'] = [0, 1]

    def backtrack(assignment):
        """
        Custom backtracker with early constraint checking on partial assignments.
        Checks column equations as soon as all participating variables are assigned.
        """
        if len(assignment) == len(variables):
            # Full assignment: verify all constraints
            d = assignment
            eq1  = (d['O'] + d['O']) == (d['R'] + 10 * d['C1'])
            eq2  = (d['W'] + d['W'] + d['C1']) == (d['U'] + 10 * d['C2'])
            eq3  = (d['T'] + d['T'] + d['C2']) == (d['O'] + 10 * d['C3'])
            eq4  = d['C3'] == d['F']
            nz   = d['T'] != 0 and d['F'] != 0
            vals = [d[l] for l in letters]
            dist = len(set(vals)) == len(vals)
            return dict(assignment) if (eq1 and eq2 and eq3 and eq4 and nz and dist) else None

        # Choose next unassigned variable (in order)
        var = next(v for v in variables if v not in assignment)

        for val in domains[var]:
            assignment[var] = val
            d = assignment
            ok = True

            # ── Constraint 1: No leading zeros ────────────────────────────
            if 'T' in d and d['T'] == 0:
                ok = False
            if ok and 'F' in d and d['F'] == 0:
                ok = False

            # ── Constraint 2: All letters take distinct digits ─────────────
            if ok:
                letter_vals = [d[l] for l in letters if l in d]
                if len(set(letter_vals)) != len(letter_vals):
                    ok = False

            # ── Constraint 3: Column equations (check when vars are known) ─
            # Col 1: O + O = R + 10·C1
            if ok and all(v in d for v in ['O', 'R', 'C1']):
                if (d['O'] + d['O']) != (d['R'] + 10 * d['C1']):
                    ok = False

            # Col 2: W + W + C1 = U + 10·C2
            if ok and all(v in d for v in ['W', 'U', 'C1', 'C2']):
                if (d['W'] + d['W'] + d['C1']) != (d['U'] + 10 * d['C2']):
                    ok = False

            # Col 3: T + T + C2 = O + 10·C3
            if ok and all(v in d for v in ['T', 'O', 'C2', 'C3']):
                if (d['T'] + d['T'] + d['C2']) != (d['O'] + 10 * d['C3']):
                    ok = False

            # Col 4: C3 = F
            if ok and all(v in d for v in ['C3', 'F']):
                if d['C3'] != d['F']:
                    ok = False

            if ok:
                result = backtrack(assignment)
                if result is not None:
                    return result

            del assignment[var]

        return None   # trigger backtrack

    solution = backtrack({})

    if solution:
        d    = solution
        TWO  = 100 * d['T'] + 10 * d['W'] + d['O']
        FOUR = 1000 * d['F'] + 100 * d['O'] + 10 * d['U'] + d['R']

        print(f"\n  Letter → Digit mapping:")
        for l in letters:
            print(f"    {l} = {d[l]}")
        print(f"\n  Carry bits:  C1={d['C1']}  C2={d['C2']}  C3={d['C3']}")
        print(f"\n  ┌─────────────────────────────┐")
        print(f"  │    T  W  O     {d['T']}  {d['W']}  {d['O']}      │")
        print(f"  │  + T  W  O   + {d['T']}  {d['W']}  {d['O']}      │")
        print(f"  │  ─────────   ─────────      │")
        print(f"  │  F  O  U  R  {d['F']}  {d['O']}  {d['U']}  {d['R']}     │")
        print(f"  └─────────────────────────────┘")
        print(f"\n  Verification:  {TWO} + {TWO} = {FOUR}  ✓")
    else:
        print("  No solution found.")

    # ── Visualize ─────────────────────────────────────────────────────────────
    d = solution

    fig, ax = plt.subplots(figsize=(7, 7))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')
    ax.axis('off')
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 7)

    def draw_cell(ax, x, y, letter, digit, color='white'):
        """Draw a letter label above its digit value."""
        ax.text(x, y + 0.55, letter, ha='center', va='center',
                fontsize=22, color='#aed6f1', fontfamily='monospace')
        ax.text(x, y,        str(digit), ha='center', va='center',
                fontsize=28, fontweight='bold', color=color,
                fontfamily='monospace')

    # Title
    ax.text(3, 6.5, "TWO + TWO = FOUR",
            ha='center', va='center', fontsize=18, fontweight='bold',
            color='#f1c40f')
    ax.text(3, 6.0, "Cryptarithmetic CSP  —  AIMA 4th Ed., Figure 6.2(a)",
            ha='center', va='center', fontsize=9.5, color='#aaa')

    # Row 1: TWO (green)
    xs3 = [1.5, 2.5, 3.5]
    for x, (l, dg) in zip(xs3, [('T', d['T']), ('W', d['W']), ('O', d['O'])]):
        draw_cell(ax, x, 4.5, l, dg, '#2ecc71')

    # '+' sign
    ax.text(0.65, 4.0, "+", ha='center', va='center',
            fontsize=32, fontweight='bold', color='white')

    # Row 2: TWO (green)
    for x, (l, dg) in zip(xs3, [('T', d['T']), ('W', d['W']), ('O', d['O'])]):
        draw_cell(ax, x, 3.1, l, dg, '#2ecc71')

    # Separator line
    ax.plot([0.2, 4.8], [2.5, 2.5], color='#f1c40f', linewidth=2.5)

    # Row 3: FOUR (red)
    xs4 = [1.0, 2.0, 3.0, 4.0]
    for x, (l, dg) in zip(xs4, [('F', d['F']), ('O', d['O']), ('U', d['U']), ('R', d['R'])]):
        draw_cell(ax, x, 1.5, l, dg, '#e74c3c')

    # Carry info
    ax.text(3, 0.85,
            f"Carries:  C₁ = {d['C1']}   C₂ = {d['C2']}   C₃ = {d['C3']}",
            ha='center', va='center', fontsize=12, color='#f1c40f')

    TWO  = 100 * d['T'] + 10 * d['W'] + d['O']
    FOUR = 1000 * d['F'] + 100 * d['O'] + 10 * d['U'] + d['R']
    ax.text(3, 0.2, f"{TWO}  +  {TWO}  =  {FOUR}",
            ha='center', va='center', fontsize=16,
            color='white', fontweight='bold')

    plt.tight_layout()
    plt.savefig('cryptarithmetic.png', dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close()
    print("\nVisualization saved → cryptarithmetic.png")
    return solution


if __name__ == "__main__":
    solve_crypto()

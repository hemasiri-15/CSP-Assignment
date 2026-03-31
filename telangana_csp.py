"""
=============================================================================
 CSP Assignment — Problem 2: Telangana Map Coloring (33 Districts)
 Reference: Artificial Intelligence: A Modern Approach (4th Ed.)
            Stuart Russell & Peter Norvig, Pearson
            Chapter 6 — Constraint Satisfaction Problems
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
#  PROBLEM 2 — TELANGANA MAP COLORING (33 Districts)
# =============================================================================

def solve_telangana():
    print("=" * 60)
    print("PROBLEM 2 — TELANGANA MAP COLORING (33 Districts)")
    print("Reference: AIMA 4th Ed., Chapter 6 — CSP")
    print("=" * 60)

    districts = [
        'Adilabad', 'KumurambheemAsifabad', 'Mancherial', 'Nirmal',
        'Nizamabad', 'Jagtial', 'Peddapalli', 'JayashankarBhupalpally',
        'RajannaSircilla', 'Karimnagar', 'Kamareddy', 'Medak',
        'Sangareddy', 'Siddipet', 'Jangaon', 'WarangalUrban',
        'WarangalRural', 'Mulugu', 'BhadradriKothagudem', 'Khammam',
        'Mahabubabad', 'Suryapet', 'Nalgonda', 'YadadriBhuvanagiri',
        'MedchalMalkajgiri', 'Hyderabad', 'Rangareddy', 'Vikarabad',
        'Mahabubnagar', 'Nagarkurnool', 'Wanaparthy',
        'JogulumbaGadwal', 'Narayanpet'
    ]

    colors  = ['Crimson', 'ForestGreen', 'RoyalBlue',
               'DarkOrange', 'MediumOrchid', 'DeepSkyBlue']
    domains = {d: colors[:] for d in districts}

    # Geographic adjacency for all 33 Telangana districts
    neighbors = {
        'Adilabad':               ['KumurambheemAsifabad', 'Nirmal', 'Mancherial'],
        'KumurambheemAsifabad':   ['Adilabad', 'Mancherial'],
        'Mancherial':             ['Adilabad', 'KumurambheemAsifabad', 'Nirmal',
                                   'Jagtial', 'Peddapalli'],
        'Nirmal':                 ['Adilabad', 'Mancherial', 'Nizamabad',
                                   'Kamareddy', 'Jagtial'],
        'Nizamabad':              ['Nirmal', 'Kamareddy', 'Jagtial', 'RajannaSircilla'],
        'Jagtial':                ['Nirmal', 'Mancherial', 'Nizamabad', 'Peddapalli',
                                   'Karimnagar', 'RajannaSircilla'],
        'Peddapalli':             ['Mancherial', 'Jagtial', 'Karimnagar',
                                   'JayashankarBhupalpally'],
        'JayashankarBhupalpally': ['Peddapalli', 'Karimnagar', 'Mulugu', 'WarangalRural'],
        'RajannaSircilla':        ['Nizamabad', 'Jagtial', 'Karimnagar',
                                   'Siddipet', 'Kamareddy'],
        'Karimnagar':             ['Jagtial', 'Peddapalli', 'JayashankarBhupalpally',
                                   'RajannaSircilla', 'Siddipet', 'WarangalRural'],
        'Kamareddy':              ['Nirmal', 'Nizamabad', 'RajannaSircilla',
                                   'Siddipet', 'Medak', 'Sangareddy'],
        'Medak':                  ['Kamareddy', 'Siddipet', 'Sangareddy'],
        'Sangareddy':             ['Kamareddy', 'Medak', 'Siddipet',
                                   'MedchalMalkajgiri', 'Hyderabad', 'Vikarabad'],
        'Siddipet':               ['Kamareddy', 'RajannaSircilla', 'Karimnagar',
                                   'Medak', 'Sangareddy', 'Jangaon',
                                   'YadadriBhuvanagiri', 'Nalgonda'],
        'Jangaon':                ['Siddipet', 'Karimnagar', 'WarangalUrban',
                                   'WarangalRural', 'YadadriBhuvanagiri'],
        'WarangalUrban':          ['Jangaon', 'WarangalRural', 'Mahabubabad'],
        'WarangalRural':          ['JayashankarBhupalpally', 'Karimnagar', 'Jangaon',
                                   'WarangalUrban', 'Mulugu', 'Mahabubabad'],
        'Mulugu':                 ['JayashankarBhupalpally', 'WarangalRural',
                                   'BhadradriKothagudem'],
        'BhadradriKothagudem':    ['Mulugu', 'WarangalRural', 'Khammam', 'Mahabubabad'],
        'Khammam':                ['BhadradriKothagudem', 'Mahabubabad',
                                   'Suryapet', 'Nalgonda'],
        'Mahabubabad':            ['WarangalUrban', 'WarangalRural',
                                   'BhadradriKothagudem', 'Khammam',
                                   'Suryapet', 'Jangaon'],
        'Suryapet':               ['Mahabubabad', 'Khammam', 'Nalgonda',
                                   'YadadriBhuvanagiri'],
        'Nalgonda':               ['Siddipet', 'Suryapet', 'YadadriBhuvanagiri',
                                   'MedchalMalkajgiri', 'Rangareddy',
                                   'Nagarkurnool', 'Khammam'],
        'YadadriBhuvanagiri':     ['Siddipet', 'Jangaon', 'Nalgonda',
                                   'Suryapet', 'MedchalMalkajgiri'],
        'MedchalMalkajgiri':      ['Sangareddy', 'YadadriBhuvanagiri', 'Nalgonda',
                                   'Hyderabad', 'Rangareddy'],
        'Hyderabad':              ['MedchalMalkajgiri', 'Rangareddy', 'Sangareddy'],
        'Rangareddy':             ['Hyderabad', 'MedchalMalkajgiri', 'Nalgonda',
                                   'Vikarabad', 'Mahabubnagar', 'Nagarkurnool'],
        'Vikarabad':              ['Sangareddy', 'Rangareddy', 'Mahabubnagar'],
        'Mahabubnagar':           ['Rangareddy', 'Vikarabad', 'Nalgonda',
                                   'Nagarkurnool', 'Wanaparthy', 'Narayanpet'],
        'Nagarkurnool':           ['Rangareddy', 'Nalgonda', 'Mahabubnagar', 'Wanaparthy'],
        'Wanaparthy':             ['Nagarkurnool', 'Mahabubnagar',
                                   'JogulumbaGadwal', 'Narayanpet'],
        'JogulumbaGadwal':        ['Wanaparthy', 'Narayanpet'],
        'Narayanpet':             ['Mahabubnagar', 'Wanaparthy', 'JogulumbaGadwal'],
    }

    csp      = CSP(districts, domains, neighbors, ne_constraint)
    solution = csp.backtracking_search()

    print("\nSolution:")
    for d in districts:
        print(f"  {d:<30s} → {solution[d]}")

    # ── Verify ────────────────────────────────────────────────────────────────
    print("\nVerification:")
    ok = True
    for v, nbs in neighbors.items():
        for nb in nbs:
            if solution[v] == solution[nb]:
                print(f"  ✗ CONFLICT: {v} and {nb} both = {solution[v]}")
                ok = False
    if ok:
        print("  ✓ All constraints satisfied!")

    # ── Visualize ─────────────────────────────────────────────────────────────
    HEX = {
        'Crimson':      '#c0392b',
        'ForestGreen':  '#27ae60',
        'RoyalBlue':    '#2471a3',
        'DarkOrange':   '#e67e22',
        'MediumOrchid': '#8e44ad',
        'DeepSkyBlue':  '#17a589',
    }

    # Approximate geographic positions (lon-ish, lat-ish) for Telangana
    pos = {
        'Adilabad':               (2.5,  9.5),
        'KumurambheemAsifabad':   (4.2,  9.9),
        'Mancherial':             (5.5,  9.2),
        'Nirmal':                 (2.6,  8.7),
        'Nizamabad':              (1.3,  7.9),
        'Jagtial':                (4.3,  8.4),
        'Peddapalli':             (5.8,  8.3),
        'JayashankarBhupalpally': (7.0,  8.0),
        'RajannaSircilla':        (3.0,  7.6),
        'Karimnagar':             (5.2,  7.6),
        'Kamareddy':              (1.9,  7.0),
        'Medak':                  (1.6,  6.1),
        'Sangareddy':             (1.0,  5.3),
        'Siddipet':               (3.5,  6.6),
        'Jangaon':                (5.4,  6.2),
        'WarangalUrban':          (6.3,  6.1),
        'WarangalRural':          (6.9,  6.9),
        'Mulugu':                 (7.9,  7.2),
        'BhadradriKothagudem':    (8.5,  6.4),
        'Khammam':                (7.8,  5.5),
        'Mahabubabad':            (6.8,  5.4),
        'Suryapet':               (6.4,  4.5),
        'Nalgonda':               (5.0,  4.2),
        'YadadriBhuvanagiri':     (5.8,  5.2),
        'MedchalMalkajgiri':      (3.0,  4.9),
        'Hyderabad':              (2.3,  4.5),
        'Rangareddy':             (2.6,  3.7),
        'Vikarabad':              (1.2,  4.0),
        'Mahabubnagar':           (3.1,  3.0),
        'Nagarkurnool':           (3.9,  2.5),
        'Wanaparthy':             (4.2,  1.8),
        'JogulumbaGadwal':        (3.6,  1.0),
        'Narayanpet':             (2.1,  1.5),
    }

    G = nx.Graph()
    G.add_nodes_from(districts)
    for v, nbs in neighbors.items():
        for nb in nbs:
            if v < nb:
                G.add_edge(v, nb)

    node_colors = [HEX[solution[v]] for v in G.nodes()]

    short = {
        'KumurambheemAsifabad':   'Kumuram\nAsifabad',
        'JayashankarBhupalpally': 'Jayashankar\nBhupalpally',
        'RajannaSircilla':        'Rajanna\nSircilla',
        'BhadradriKothagudem':    'Bhadradri\nKothagudem',
        'YadadriBhuvanagiri':     'Yadadri\nBhuvanagiri',
        'MedchalMalkajgiri':      'Medchal\nMalkajgiri',
        'JogulumbaGadwal':        'Jogulamba\nGadwal',
        'WarangalUrban':          'Warangal\nUrban',
        'WarangalRural':          'Warangal\nRural',
        'Mahabubnagar':           'Mahabub-\nnagar',
    }
    labels = {d: short.get(d, d) for d in districts}

    fig, ax = plt.subplots(figsize=(17, 15))
    fig.patch.set_facecolor('#ecf0f1')
    ax.set_facecolor('#ecf0f1')

    nx.draw_networkx(
        G, pos=pos, ax=ax,
        node_color=node_colors, node_size=900,
        labels=labels,
        font_size=5.5, font_weight='bold', font_color='white',
        edge_color='#555', width=1.4
    )

    patches = [mpatches.Patch(color=HEX[c], label=c) for c in colors]
    ax.legend(handles=patches, loc='lower right', fontsize=11,
              framealpha=0.95, edgecolor='#aaa',
              title='Colors', title_fontsize=12)
    ax.set_title(
        "Telangana District Map Coloring (33 Districts) — CSP\n"
        "AIMA 4th Ed. (Russell & Norvig), Chapter 6",
        fontsize=15, fontweight='bold', pad=20
    )
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('telangana_map_coloring.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("\nVisualization saved → telangana_map_coloring.png")
    return solution


if __name__ == "__main__":
    solve_telangana()

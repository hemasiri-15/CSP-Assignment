"""
=============================================================================
 CSP Assignment — Problem 2: Telangana Map Coloring (33 Districts)
 Adjacency computed directly from GeoJSON geometry — no manual errors.
 Reference: AIMA 4th Ed., Chapter 6
=============================================================================
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import geopandas as gpd
import warnings
warnings.filterwarnings('ignore')


# =============================================================================
#  GENERIC CSP FRAMEWORK  (Backtracking + MRV + Forward Checking)
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
        unassigned = [v for v in self.variables if v not in assignment]
        return min(unassigned, key=lambda v: len(self.domains[v]))

    def _consistent(self, var, value, assignment):
        return all(
            self.constraint(var, value, nb, assignment[nb])
            for nb in self.neighbors.get(var, [])
            if nb in assignment
        )

    def _forward_check(self, var, value, assignment):
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
#  STEP 1 — Compute real adjacencies from geometry
# =============================================================================

def compute_adjacency(gdf):
    districts = list(gdf['dtname'])
    adjacency = {d: [] for d in districts}
    gdf_idx   = gdf.set_index('dtname')

    for i, d1 in enumerate(districts):
        for j, d2 in enumerate(districts):
            if i >= j:
                continue
            geom1  = gdf_idx.loc[d1, 'geometry']
            geom2  = gdf_idx.loc[d2, 'geometry']
            shared = geom1.intersection(geom2)
            if not shared.is_empty and shared.geom_type not in ('Point', 'MultiPoint'):
                adjacency[d1].append(d2)
                adjacency[d2].append(d1)
    return adjacency


# =============================================================================
#  STEP 2 — Solve CSP
# =============================================================================

def solve(adjacency, districts):
    colors  = ['Crimson', 'ForestGreen', 'RoyalBlue', 'DarkOrange', 'MediumOrchid']
    domains = {d: colors[:] for d in districts}
    csp     = CSP(districts, domains, adjacency, ne_constraint)
    return csp.backtracking_search()


# =============================================================================
#  STEP 3 — Visualize
# =============================================================================

HEX = {
    'Crimson':      '#c0392b',
    'ForestGreen':  '#27ae60',
    'RoyalBlue':    '#2471a3',
    'DarkOrange':   '#e67e22',
    'MediumOrchid': '#8e44ad',
}

SHORT = {
    'Kumuram Bheem Asifabad': 'Kumuram\nBheem\nAsifabad',
    'Bhadradri Kothagudem':   'Bhadradri\nKothagudem',
    'Medchal Malkajgiri':     'Medchal\nMalkajgiri',
    'Yadadri Bhuvanagiri':    'Yadadri\nBhuvanagiri',
    'Rajanna Sircilla':       'Rajanna\nSircilla',
    'Jogulamba Gadwal':       'Jogulamba\nGadwal',
    'Warangal Rural':         'Warangal\nRural',
    'Warangal Urban':         'Warangal\nUrban',
    'Jayashankar':            'Jayashankar\nBhupalpally',
    'Ranga Reddy':            'Ranga\nReddy',
}


def draw_map(gdf, solution):
    gdf = gdf.copy()
    gdf['color'] = gdf['dtname'].map(
        lambda d: HEX.get(solution.get(d, 'MediumOrchid'), '#8e44ad')
    )

    fig, ax = plt.subplots(figsize=(14, 15))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')

    gdf.plot(color=gdf['color'], edgecolor='white', linewidth=0.8, ax=ax)

    for _, row in gdf.iterrows():
        centroid = row.geometry.centroid
        name     = row['dtname']
        label    = SHORT.get(name, name)
        nlines   = label.count('\n') + 1
        fs       = 6.2 if nlines >= 3 else (7.2 if nlines == 2 else 8.2)
        ax.text(
            centroid.x, centroid.y, label,
            ha='center', va='center',
            fontsize=fs, fontweight='bold', color='white',
            multialignment='center',
            path_effects=[pe.withStroke(linewidth=2.2, foreground='black')]
        )

    used    = sorted(set(solution.values()))
    patches = [mpatches.Patch(facecolor=HEX[c], edgecolor='white',
                              linewidth=1.0, label=c) for c in used]
    ax.legend(handles=patches, loc='lower right', fontsize=11,
              framealpha=0.95, edgecolor='#aaa', facecolor='#f0f0f0',
              title='CSP Colours', title_fontsize=11, labelcolor='#111')
    ax.set_title(
        "Telangana District Map Coloring (33 Districts) — CSP\n"
        "AIMA 4th Ed. (Russell & Norvig), Chapter 6",
        fontsize=15, fontweight='bold', color='white', pad=18
    )
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('02_telangana_map_coloring.png', dpi=180,
                bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print("Saved → 02_telangana_map_coloring.png")


# =============================================================================
#  MAIN
# =============================================================================

if __name__ == "__main__":
    print("Loading GeoJSON...")
    gdf       = gpd.read_file('TELANGANA_DISTRICTS.geojson')
    districts = list(gdf['dtname'])

    print("Computing real adjacencies from geometry...")
    adjacency = compute_adjacency(gdf)

    print("Running CSP (Backtracking + MRV + Forward Checking)...")
    solution  = solve(adjacency, districts)

    print("\nSolution:")
    for d, c in sorted(solution.items()):
        print(f"  {d:<30s} -> {c}")

    print("\nVerification:")
    ok = True
    for d, nbs in adjacency.items():
        for nb in nbs:
            if solution[d] == solution[nb]:
                print(f"  CONFLICT: {d} and {nb} both = {solution[d]}")
                ok = False
    if ok:
        print("  All constraints satisfied!")

    draw_map(gdf, solution)

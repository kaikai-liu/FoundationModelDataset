"""
IBERSEIS Wide-Angle geometry ASCII file inspection.

Downloads needed (place in iberseis_data/):
  IBERSEIS-WA-Geo.asc    geometry acquisition file

The geometry file covers:
  - Transect A (perfil A):   stations 1001 – 1686
  - Transect B (perfil B+C): stations 2001 – 3682

Shot points include Rio Tinto and Minas Cala — both Iberian Pyrite Belt mining sites.

Repository: https://doi.org/10.20350/digitalCSIC/9018
"""
from __future__ import annotations

import re
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'datasets' / 'seisdare' / 'iberseis' / 'raw' / 'iberseis_data'
OUT = ROOT / 'datasets' / 'seisdare' / 'iberseis' / 'wa_outputs'
OUT.mkdir(exist_ok=True)

GEO = DATA / 'IBERSEIS-WA-Geo.asc'

sns.set_theme(style='whitegrid', context='talk')
plt.rcParams['figure.dpi'] = 160
plt.rcParams['savefig.dpi'] = 200

# Shot points with mining / geological significance for annotation
MINING_SHOTS = {'Rio Tinto', 'Minas Cala'}


# ── File parsers ───────────────────────────────────────────────────────────
def parse_shot_points(raw_lines: list[str]) -> pd.DataFrame:
    """
    Extract named shot points from the file header section.
    Each shot line looks like:
      Name  (abbr)  zone S easting northing elevation  Shot time UTC ...
    All coordinates are UTM (zone 29S or 30S).
    Note: mixing UTM zones means absolute distances are approximate,
    but relative positions within each zone are correct.
    """
    shots = []
    current_profile = None
    for line in raw_lines:
        stripped = line.strip()
        if stripped.startswith('Perfil'):
            current_profile = stripped
            continue
        m = re.match(r'^([\w\s]+?)\s+\([\w\d]+\)\s+(\d+)\s+S\s+(\d+)\s+(\d+)\s+(\d+)', stripped)
        if m:
            name, zone, e, n, elev = m.groups()
            shots.append({
                'name': name.strip(),
                'profile': current_profile,
                'utm_zone': int(zone),
                'E': int(e),
                'N': int(n),
                'elev_m': int(elev),
                'is_mining': name.strip() in MINING_SHOTS,
            })
    return pd.DataFrame(shots)


def parse_stations(path: Path) -> tuple[list[str], pd.DataFrame]:
    """Read the receiver station table (numeric rows) after the header."""
    raw_lines = path.read_text(encoding='utf-8', errors='replace').splitlines()

    print('=== First 20 lines of geometry file ===')
    for i, line in enumerate(raw_lines[:20]):
        print(f'  {i+1:3d}: {line}')
    print()

    # Find where numeric data starts
    data_start = 0
    header_lines = []
    for i, line in enumerate(raw_lines):
        stripped = line.strip()
        if not stripped:
            continue
        first = stripped.split()[0]
        try:
            float(first)
            data_start = i
            break
        except ValueError:
            header_lines.append(line)

    shots_df = parse_shot_points(header_lines)

    try:
        df = pd.read_csv(
            path, skiprows=data_start, header=None, sep=r'\s+', engine='python',
        )
    except Exception:
        df = pd.DataFrame()

    return header_lines, shots_df, df


def assign_transect(station_id: pd.Series) -> pd.Series:
    labels = pd.Series('Unknown', index=station_id.index)
    labels[station_id.between(1001, 1686)] = 'Transect A'
    labels[station_id.between(2001, 3682)] = 'Transect B'
    return labels


# ── Plots ──────────────────────────────────────────────────────────────────
def plot_full_layout(stations: pd.DataFrame, shots: pd.DataFrame, out: Path):
    """
    Map view of all receiver stations (coloured by transect) and explosive
    shot points (including annotations for mining sites).
    Note: mixes UTM zone 29S and 30S — geometry is indicative, not metric-accurate.
    """
    fig, ax = plt.subplots(figsize=(13, 9))

    id_col, x_col, y_col = 0, 1, 2
    stations = stations.copy()
    stations['Transect'] = assign_transect(stations[id_col])

    palette = {'Transect A': '#1f77b4', 'Transect B': '#ff7f0e', 'Unknown': '#aaaaaa'}
    for label, grp in stations.groupby('Transect'):
        ax.scatter(grp[y_col], grp[x_col], s=8, alpha=0.55, c=palette[label], label=f'{label} receivers ({len(grp):,})')

    if not shots.empty:
        reg_shots = shots[~shots['is_mining']]
        mine_shots = shots[shots['is_mining']]
        if len(reg_shots):
            ax.scatter(reg_shots['E'], reg_shots['N'], s=80, marker='^',
                       c='#2ca02c', zorder=5, label='Explosion shot points')
        if len(mine_shots):
            ax.scatter(mine_shots['E'], mine_shots['N'], s=160, marker='*',
                       c='gold', edgecolors='black', linewidths=0.7, zorder=6,
                       label='Mining sites (Rio Tinto, Minas Cala)')
            for _, row in mine_shots.iterrows():
                ax.annotate(row['name'], (row['E'], row['N']),
                            textcoords='offset points', xytext=(6, 4),
                            fontsize=11, fontweight='bold', color='black',
                            bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.7))

    ax.set_xlabel('UTM Easting (m) — zone mixing: 29S / 30S')
    ax.set_ylabel('UTM Northing (m)')
    ax.set_title('IBERSEIS WA — receiver layout and shot points\n'
                 'Transects cross Iberian Pyrite Belt (Rio Tinto, Minas Cala)')
    ax.legend(loc='best', fontsize=10)
    plt.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)


def plot_station_spacing(df: pd.DataFrame, out: Path):
    """Inter-station spacing along each transect."""
    id_col, x_col, y_col = 0, 1, 2
    fig, axes = plt.subplots(2, 1, figsize=(13, 8), sharex=False)
    transect_defs = [
        ('Transect A (1001–1686)', (1001, 1686)),
        ('Transect B (2001–3682)', (2001, 3682)),
    ]
    for ax, (label, (lo, hi)) in zip(axes, transect_defs):
        sub = df[df[id_col].between(lo, hi)].sort_values(id_col)
        if len(sub) < 2:
            ax.set_title(f'{label} — no data')
            continue
        dx = np.diff(sub[x_col].values)
        dy = np.diff(sub[y_col].values)
        spacing = np.sqrt(dx**2 + dy**2)
        median_sp = np.median(spacing)
        ax.plot(sub[id_col].values[1:], spacing, linewidth=0.8, color='steelblue', alpha=0.8)
        ax.axhline(median_sp, color='firebrick', linestyle='--', linewidth=1.2,
                   label=f'Median: {median_sp:.0f} m')
        ax.set_title(f'{label} — inter-station spacing')
        ax.set_xlabel('Station ID')
        ax.set_ylabel('Spacing (m)')
        ax.legend(fontsize=10)
    plt.suptitle('IBERSEIS WA — station spacing along transects\n'
                 '(Transect B spans UTM zones 29S+30S — large outlier gaps are zone-crossing artifacts)', y=1.02)
    plt.tight_layout()
    fig.savefig(out, dpi=180)
    plt.close(fig)


# ── Summary report ─────────────────────────────────────────────────────────
def write_summary(header_lines, shots: pd.DataFrame, df: pd.DataFrame, out: Path):
    id_col = 0
    n_a = int(df[id_col].between(1001, 1686).sum())
    n_b = int(df[id_col].between(2001, 3682).sum())

    lines = [
        '# IBERSEIS WA geometry file inspection',
        '',
        '## Station table',
        f'- Total receiver stations: {len(df):,}',
        f'- Transect A (1001–1686): {n_a} stations',
        f'- Transect B (2001–3682): {n_b} stations',
        '',
        '## Shot points (explosive sources)',
    ]
    if not shots.empty:
        for _, row in shots.iterrows():
            flag = ' *** MINING SITE ***' if row['is_mining'] else ''
            lines.append(f'- {row["profile"]} | {row["name"]} | UTM {row["utm_zone"]}S | E={row["E"]} N={row["N"]} elev={row["elev_m"]}m{flag}')
    lines += [
        '',
        '## Key mining relevance',
        '- **Rio Tinto** is a shot point: one of the most historically significant',
        '  copper/iron-sulfide mines in the world, located in the Iberian Pyrite Belt.',
        '- **Minas Cala** is a shot point: another IPB mining location.',
        '- Both shots appear in Perfiles B and C, meaning the seismic lines were',
        '  specifically designed to image the crust beneath active mining districts.',
        '- This makes IBERSEIS WA a direct structural companion to SOTIEL — both',
        '  datasets image the same geological zone from different depths and angles.',
        '',
        '## Geological context',
        '- Two NE-SW transects across the SW Iberian Massif.',
        '- Zones crossed: South Portuguese Zone → Ossa-Morena Zone → Central Iberian Zone.',
        '- The Iberian Pyrite Belt sits within the South Portuguese Zone.',
        '',
        '## Columns in station table',
        '- col 0: station ID (1001–3682)',
        '- col 1: UTM northing (m, zone 29S)',
        '- col 2: UTM easting (m, zone 29S)',
        '- col 3: elevation (m)',
        '',
        '## Figures',
        '- `wa_geometry_layout.png`   — receiver + shot point map (mining sites annotated)',
        '- `wa_station_spacing.png`   — inter-station spacing per transect',
    ]
    (out / 'README_geometry.md').write_text('\n'.join(lines), encoding='utf-8')


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    if not GEO.exists():
        print(f'File not found: {GEO}')
        print('Download from: https://doi.org/10.20350/digitalCSIC/9018')
        print('Place IBERSEIS-WA-Geo.asc in:', DATA)
        return

    print(f'Reading geometry file: {GEO.name}')
    header_lines, shots, df = parse_stations(GEO)

    if df.empty:
        print('Could not parse station table — check file format.')
        return

    print(f'Parsed {len(df):,} receiver stations')
    print(f'Found {len(shots)} shot points')
    if not shots.empty:
        mining = shots[shots['is_mining']]['name'].tolist()
        if mining:
            print(f'Mining-site shot points: {mining}')
    print()

    plot_full_layout(df, shots, OUT / 'wa_geometry_layout.png')
    plot_station_spacing(df, OUT / 'wa_station_spacing.png')
    write_summary(header_lines, shots, df, OUT)

    print('Saved outputs to', OUT)
    for p in sorted(OUT.iterdir()):
        print('-', p.name)


if __name__ == '__main__':
    main()

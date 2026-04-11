"""
IBERSEIS Wide-Angle SEG-Y inspection script.

Downloads needed (place in iberseis_data/):
  IBERSEIS-WA.sgy     (~1.23 GB)   raw wide-angle seismic data
  IBERSEIS-WA-Geo.asc              geometry ASCII file

Repository: https://doi.org/10.20350/digitalCSIC/9018
"""
from __future__ import annotations

from pathlib import Path
import struct
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'datasets' / 'seisdare' / 'iberseis' / 'raw' / 'iberseis_data'
OUT = ROOT / 'datasets' / 'seisdare' / 'iberseis' / 'wa_outputs'
OUT.mkdir(exist_ok=True)

SEGY = DATA / 'IBERSEIS-WA.sgy'


# ── IBM float decoder ──────────────────────────────────────────────────────
def ibm_to_ieee(arr_u4: np.ndarray) -> np.ndarray:
    arr = arr_u4.astype(np.uint32)
    sign = np.where((arr >> 31) & 0x1, -1.0, 1.0)
    exponent = ((arr >> 24) & 0x7F).astype(np.int32) - 64
    fraction = (arr & 0x00FFFFFF).astype(np.float64) / float(0x01000000)
    out = sign * fraction * np.power(16.0, exponent)
    out[arr == 0] = 0.0
    return out.astype(np.float32)


# ── SEG-Y header parsers ───────────────────────────────────────────────────
def parse_binary_header(binary: bytes) -> dict:
    def u16(off): return struct.unpack('>H', binary[off:off+2])[0]
    def i32(off): return struct.unpack('>i', binary[off:off+4])[0]
    fmt = u16(24)
    return {
        'sample_interval_us': u16(16),
        'samples_per_trace': u16(20),
        'sample_format_code': fmt,
        'bps': {1:4, 2:4, 3:2, 4:4, 5:4, 6:8, 7:3, 8:1}[fmt],
    }


def parse_trace_header(th: bytes) -> dict:
    def i32(off): return struct.unpack('>i', th[off:off+4])[0]
    def u16(off): return struct.unpack('>H', th[off:off+2])[0]
    def i16(off): return struct.unpack('>h', th[off:off+2])[0]
    scalar = i16(70)
    scale = (1.0 / abs(scalar)) if scalar < 0 else (float(scalar) if scalar > 0 else 1.0)
    return {
        'field_record':  i32(8),
        'trace_num':     i32(12),
        'source_point':  i32(16),
        'cdp':           i32(20),
        'offset':        i32(36),
        'elev_receiver': i32(40),
        'elev_source':   i32(44),
        'coord_scalar':  scalar,
        'src_x':  i32(72) * scale,
        'src_y':  i32(76) * scale,
        'grp_x':  i32(80) * scale,
        'grp_y':  i32(84) * scale,
        'ns':     u16(114),
        'dt_us':  u16(116),
    }


# ── Core readers ───────────────────────────────────────────────────────────
def read_full_headers(path: Path) -> tuple[dict, list[dict]]:
    """Read binary header + ALL trace headers (skip sample data)."""
    with path.open('rb') as f:
        f.seek(3200)
        binhdr = parse_binary_header(f.read(400))
        bps = binhdr['bps']
        ns = binhdr['samples_per_trace']
        payload = ns * bps
        headers = []
        while True:
            th = f.read(240)
            if len(th) < 240:
                break
            headers.append(parse_trace_header(th))
            f.seek(payload, 1)
    return binhdr, headers


def decode_samples(raw: np.ndarray, fmt: int) -> np.ndarray:
    if fmt == 1:
        return ibm_to_ieee(raw)
    elif fmt == 5:
        return raw.view('>f4').astype(np.float32)
    else:
        return raw.view('>f4').astype(np.float32)


def read_preview_traces(path: Path, binhdr: dict, n: int = 120) -> tuple[list[dict], np.ndarray]:
    """Read first n traces into an array."""
    bps = binhdr['bps']
    ns = binhdr['samples_per_trace']
    fmt = binhdr['sample_format_code']
    headers, traces = [], []
    with path.open('rb') as f:
        f.seek(3600)
        for _ in range(n):
            th = f.read(240)
            if len(th) < 240:
                break
            headers.append(parse_trace_header(th))
            raw = np.frombuffer(f.read(ns * bps), dtype='>u4')
            traces.append(decode_samples(raw, fmt))
    return headers, np.stack(traces, axis=1)  # samples × traces


# ── Plots ──────────────────────────────────────────────────────────────────
def plot_trace_section(data: np.ndarray, dt_us: int, title: str, out: Path):
    time_ms = np.arange(data.shape[0]) * dt_us / 1000.0
    clip = np.percentile(np.abs(data), 99)
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.imshow(data, cmap='gray', aspect='auto',
              vmin=-clip, vmax=clip,
              extent=[1, data.shape[1], time_ms[-1], time_ms[0]])
    ax.set_xlabel('Trace index')
    ax.set_ylabel('Time (ms)')
    ax.set_title(title)
    plt.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)


def plot_offset_histogram(offsets: np.ndarray, out: Path):
    """WA datasets have characteristically large offsets — this plot shows coverage."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(offsets / 1000.0, bins=80, color='steelblue', edgecolor='none', alpha=0.85)
    ax.set_xlabel('Source–receiver offset (km)')
    ax.set_ylabel('Number of traces')
    ax.set_title('IBERSEIS WA — offset distribution\n(wide-angle profile: large offsets expected)')
    ax.axvline(0, color='red', linewidth=1, linestyle='--', label='Zero offset')
    ax.legend()
    plt.tight_layout()
    fig.savefig(out, dpi=180)
    plt.close(fig)


def plot_shot_coverage(hdrs: list[dict], out: Path):
    """Map all unique shot positions and receiver positions from trace headers."""
    src_x = np.array([h['src_x'] for h in hdrs])
    src_y = np.array([h['src_y'] for h in hdrs])
    grp_x = np.array([h['grp_x'] for h in hdrs])
    grp_y = np.array([h['grp_y'] for h in hdrs])

    # deduplicate
    src_pts = np.unique(np.column_stack([src_x, src_y]), axis=0)
    grp_pts = np.unique(np.column_stack([grp_x, grp_y]), axis=0)

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.scatter(grp_pts[:, 0], grp_pts[:, 1], s=10, alpha=0.5, c='steelblue', label=f'Receivers ({len(grp_pts):,})')
    ax.scatter(src_pts[:, 0], src_pts[:, 1], s=22, alpha=0.8, c='firebrick', marker='^', label=f'Sources ({len(src_pts):,})')
    ax.set_xlabel('X (coord units from header)')
    ax.set_ylabel('Y (coord units from header)')
    ax.set_title('IBERSEIS WA — source and receiver layout from SEG-Y trace headers')
    ax.legend()
    plt.tight_layout()
    fig.savefig(out, dpi=180)
    plt.close(fig)


def plot_offset_vs_record(hdrs: list[dict], out: Path):
    """Plot offset vs trace index — shows the wide-angle gather structure."""
    offsets = np.array([h['offset'] for h in hdrs])
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(offsets / 1000.0, linewidth=0.5, alpha=0.7, color='steelblue')
    ax.set_xlabel('Trace index')
    ax.set_ylabel('Offset (km)')
    ax.set_title('IBERSEIS WA — offset vs trace index\n(structure reveals how shot gathers are sorted)')
    ax.axhline(0, color='red', linewidth=0.8, linestyle='--')
    plt.tight_layout()
    fig.savefig(out, dpi=180)
    plt.close(fig)


# ── Summary report ─────────────────────────────────────────────────────────
def write_summary(binhdr: dict, all_hdrs: list[dict], file_size: int, out: Path):
    offsets = np.array([h['offset'] for h in all_hdrs])
    frs = np.array([h['field_record'] for h in all_hdrs])
    src_x = np.array([h['src_x'] for h in all_hdrs])
    src_y = np.array([h['src_y'] for h in all_hdrs])
    grp_x = np.array([h['grp_x'] for h in all_hdrs])
    grp_y = np.array([h['grp_y'] for h in all_hdrs])
    n_src = len(np.unique(np.column_stack([src_x, src_y]), axis=0))
    n_rec = len(np.unique(np.column_stack([grp_x, grp_y]), axis=0))

    lines = [
        '# IBERSEIS Wide-Angle SEG-Y local inspection',
        '',
        '## File info',
        f'- File: `IBERSEIS-WA.sgy`',
        f'- Size: {file_size:,} bytes ({file_size / 1e9:.2f} GB)',
        f'- Total traces: {len(all_hdrs):,}',
        f'- Samples per trace: {binhdr["samples_per_trace"]}',
        f'- Sample interval: {binhdr["sample_interval_us"]} µs ({binhdr["sample_interval_us"]/1000:.0f} ms)',
        f'- Sample format code: {binhdr["sample_format_code"]} ({"IBM float" if binhdr["sample_format_code"] == 1 else "IEEE float"})',
        f'- Record length: {binhdr["samples_per_trace"] * binhdr["sample_interval_us"] / 1e6:.1f} s',
        '',
        '## Acquisition summary',
        f'- Unique field records (shots): {len(np.unique(frs)):,}',
        f'- Unique source positions: {n_src:,}',
        f'- Unique receiver positions: {n_rec:,}',
        f'- Offset range: {offsets.min()/1000:.1f} – {offsets.max()/1000:.1f} km',
        f'- Median offset: {np.median(offsets)/1000:.1f} km',
        '',
        '## Wide-angle interpretation',
        '- Wide-angle (WA) seismic uses large source–receiver offsets (typically > 10 km) to',
        '  record head waves and wide-angle reflections for crustal velocity modeling.',
        '- Unlike normal incidence (NI) data, WA traces show first arrivals (Pg, Pn), crustal',
        '  reflections (PcP), and Moho reflections (PmP) at large offsets.',
        '- The two IBERSEIS transects cross the South Portuguese Zone, Ossa-Morena Zone,',
        '  and Central Iberian Zone — including the Iberian Pyrite Belt.',
        '- This dataset is most useful for: velocity modeling, crustal structure, and',
        '  providing spatial context for the SOTIEL mining seismic dataset.',
        '',
        '## Figures',
        '- `wa_first120_traces.png`   — first 120 traces (wiggle/color section)',
        '- `wa_offset_histogram.png`  — offset distribution (confirms WA character)',
        '- `wa_offset_vs_trace.png`   — offset vs trace index (shows gather structure)',
        '- `wa_shot_coverage.png`     — source/receiver map from trace headers',
    ]
    (out / 'README.md').write_text('\n'.join(lines), encoding='utf-8')


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    if not SEGY.exists():
        print(f'File not found: {SEGY}')
        print('Download from: https://doi.org/10.20350/digitalCSIC/9018')
        print('Place IBERSEIS-WA.sgy in:', DATA)
        return

    file_size = SEGY.stat().st_size
    print(f'Reading headers from {SEGY.name} ({file_size/1e9:.2f} GB) ...')
    binhdr, all_hdrs = read_full_headers(SEGY)
    print(f'  {len(all_hdrs):,} traces found')

    # WA traces are large (30000 samples × 4 bytes = ~120 KB each), so keep preview small
    n_preview = min(50, len(all_hdrs))
    print(f'Reading {n_preview} preview traces ...')
    preview_hdrs, preview_data = read_preview_traces(SEGY, binhdr, n=n_preview)

    print('Generating plots ...')
    plot_trace_section(
        preview_data, binhdr['sample_interval_us'],
        'IBERSEIS WA — first 120 traces',
        OUT / 'wa_first120_traces.png',
    )
    offsets = np.array([h['offset'] for h in all_hdrs])
    plot_offset_histogram(offsets, OUT / 'wa_offset_histogram.png')
    plot_offset_vs_record(all_hdrs, OUT / 'wa_offset_vs_trace.png')
    plot_shot_coverage(all_hdrs, OUT / 'wa_shot_coverage.png')

    write_summary(binhdr, all_hdrs, file_size, OUT)

    print('Saved outputs to', OUT)
    for p in sorted(OUT.iterdir()):
        print('-', p.name)


if __name__ == '__main__':
    main()

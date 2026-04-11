from __future__ import annotations

from pathlib import Path
import struct
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'datasets' / 'seisdare' / 'iberseis' / 'raw' / 'iberseis_data'
OUT = ROOT / 'datasets' / 'seisdare' / 'iberseis' / 'ni_outputs'
OUT.mkdir(exist_ok=True)
FILES = ['IBER6-5-mig.sgy', 'IBER6-5-stk.sgy']


def ibm_to_ieee(arr_u4: np.ndarray) -> np.ndarray:
    arr = arr_u4.astype(np.uint32)
    sign = np.where((arr >> 31) & 0x1, -1.0, 1.0)
    exponent = ((arr >> 24) & 0x7F).astype(np.int32) - 64
    fraction = (arr & 0x00FFFFFF).astype(np.float64) / float(0x01000000)
    out = sign * fraction * np.power(16.0, exponent)
    out[arr == 0] = 0.0
    return out.astype(np.float32)


def parse_header(path: Path):
    with path.open('rb') as f:
        text = f.read(3200)
        binary = f.read(400)
    def u16(start): return struct.unpack('>H', binary[start-3201:start-3201+2])[0]
    hdr = {
        'sample_interval_us': u16(3217),
        'samples_per_trace': u16(3221),
        'sample_format_code': u16(3225),
        'text_preview': '\n'.join(text[i:i+80].decode('cp500', errors='replace') for i in range(0, 5*80, 80)),
    }
    bps = {1:4,2:4,3:2,4:4,5:4,6:8,7:3,8:1}[hdr['sample_format_code']]
    hdr['trace_bytes'] = 240 + hdr['samples_per_trace'] * bps
    hdr['estimated_trace_count'] = (path.stat().st_size - 3600) // hdr['trace_bytes']
    return hdr


def read_preview(path: Path, n_traces: int = 120):
    hdr = parse_header(path)
    samples = hdr['samples_per_trace']
    bps = 4
    traces = []
    headers = []
    with path.open('rb') as f:
        f.seek(3600)
        for _ in range(n_traces):
            th = f.read(240)
            if len(th) < 240:
                break
            headers.append({
                'seq_line': struct.unpack('>i', th[0:4])[0],
                'seq_file': struct.unpack('>i', th[4:8])[0],
                'cdp': struct.unpack('>i', th[20:24])[0],
                'offset': struct.unpack('>i', th[36:40])[0],
                'ns': struct.unpack('>H', th[114:116])[0],
                'dt_us': struct.unpack('>H', th[116:118])[0],
            })
            raw = f.read(samples * bps)
            arr = np.frombuffer(raw, dtype='>u4')
            if hdr['sample_format_code'] == 1:
                tr = ibm_to_ieee(arr)
            else:
                tr = arr.view('>f4').astype(np.float32)
            traces.append(tr)
    return hdr, headers, np.stack(traces, axis=1)


def save_section(data: np.ndarray, dt_us: int, title: str, out: Path):
    time_ms = np.arange(data.shape[0]) * dt_us / 1000.0
    clip = np.percentile(np.abs(data), 99)
    plt.figure(figsize=(12, 7))
    plt.imshow(data, cmap='gray', aspect='auto', vmin=-clip, vmax=clip,
               extent=[1, data.shape[1], time_ms[-1], time_ms[0]])
    plt.xlabel('Trace index (preview)')
    plt.ylabel('Time (ms)')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out, dpi=220)
    plt.close()


def save_first_trace(data: np.ndarray, dt_us: int, title: str, out: Path):
    time_ms = np.arange(data.shape[0]) * dt_us / 1000.0
    plt.figure(figsize=(10, 4))
    plt.plot(time_ms, data[:, 0], linewidth=1)
    plt.xlabel('Time (ms)')
    plt.ylabel('Amplitude')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out, dpi=220)
    plt.close()


def main():
    summary = ['# IBERSEIS NI migrated + stack local inspection', '']
    for fname in FILES:
        path = DATA / fname
        hdr, headers, data = read_preview(path)
        stem = fname.replace('.sgy', '')
        save_section(data, hdr['sample_interval_us'], f'{fname} — first 120 traces', OUT / f'{stem}_first120_traces.png')
        save_first_trace(data, hdr['sample_interval_us'], f'{fname} — first trace', OUT / f'{stem}_first_trace.png')
        summary += [
            f'## {fname}',
            f'- Size: {path.stat().st_size:,} bytes',
            f'- Estimated traces: {hdr["estimated_trace_count"]:,}',
            f'- Samples/trace: {hdr["samples_per_trace"]}',
            f'- Sample interval: {hdr["sample_interval_us"]} microseconds',
            f'- Sample format code: {hdr["sample_format_code"]} (IBM float)',
            f'- First trace header: seq_line={headers[0]["seq_line"]}, cdp={headers[0]["cdp"]}, offset={headers[0]["offset"]}, ns={headers[0]["ns"]}, dt={headers[0]["dt_us"]}',
            '',
        ]
    summary += [
        '## Interpretation',
        '- Both files are locally usable and structurally simple to inspect.',
        '- The migrated and stack products are a much easier entry point than the raw IBERSEIS NI data.',
        '- Because they are post-processed 2D products, they are good for visualization and structural interpretation, but less suitable than raw gathers for acquisition-level ML tasks.',
        '',
        '## Figures',
        '- `IBER6-5-mig_first120_traces.png`',
        '- `IBER6-5-mig_first_trace.png`',
        '- `IBER6-5-stk_first120_traces.png`',
        '- `IBER6-5-stk_first_trace.png`',
    ]
    (OUT / 'README.md').write_text('\n'.join(summary), encoding='utf-8')
    print('Saved outputs to', OUT)
    for p in sorted(OUT.iterdir()):
        print('-', p.name)


if __name__ == '__main__':
    main()

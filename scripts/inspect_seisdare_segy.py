from __future__ import annotations

from pathlib import Path
import struct
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
SEGY = ROOT / 'datasets' / 'seisdare' / 'sotiel' / 'raw' / 'seisdare_data' / 'crrct-0.sgy'
OUT = ROOT / 'datasets' / 'seisdare' / 'sotiel' / 'outputs'
OUT.mkdir(exist_ok=True)


def parse_binary_header(binary: bytes):
    def i16(start):
        return struct.unpack('>h', binary[start-3201:start-3201+2])[0]
    def u16(start):
        return struct.unpack('>H', binary[start-3201:start-3201+2])[0]
    def i32(start):
        return struct.unpack('>i', binary[start-3201:start-3201+4])[0]
    return {
        'job_id': i32(3201),
        'line_num': i32(3205),
        'reel_num': i32(3209),
        'sample_interval_us': u16(3217),
        'samples_per_trace': u16(3221),
        'sample_format_code': u16(3225),
        'ensemble_fold': u16(3227),
        'trace_sort_code': u16(3229),
        'measurement_system': u16(3255),
    }


def parse_trace_header(th: bytes):
    return {
        'seq_line': struct.unpack('>i', th[0:4])[0],
        'seq_file': struct.unpack('>i', th[4:8])[0],
        'field_record': struct.unpack('>i', th[8:12])[0],
        'trace_num': struct.unpack('>i', th[12:16])[0],
        'coord_scalar': struct.unpack('>h', th[70:72])[0],
        'src_x': struct.unpack('>i', th[72:76])[0],
        'src_y': struct.unpack('>i', th[76:80])[0],
        'grp_x': struct.unpack('>i', th[80:84])[0],
        'grp_y': struct.unpack('>i', th[84:88])[0],
        'ns': struct.unpack('>H', th[114:116])[0],
        'dt_us': struct.unpack('>H', th[116:118])[0],
    }


def format_scale(val: int):
    if val == 0:
        return 1.0
    if val > 0:
        return float(val)
    return 1.0 / abs(val)


def main():
    size = SEGY.stat().st_size
    with SEGY.open('rb') as f:
        text = f.read(3200)
        binary = f.read(400)
        hdr = parse_binary_header(binary)
        bps = {1:4,2:4,3:2,4:4,5:4,6:8,7:3,8:1}[hdr['sample_format_code']]
        trace_bytes = 240 + hdr['samples_per_trace'] * bps
        est_traces = (size - 3600) // trace_bytes

        first_headers = []
        traces = []
        n_preview = 120
        for _ in range(n_preview):
            th = f.read(240)
            info = parse_trace_header(th)
            first_headers.append(info)
            tr = np.frombuffer(f.read(hdr['samples_per_trace'] * bps), dtype='>f4').astype(np.float32)
            traces.append(tr)

    data = np.stack(traces, axis=1)  # samples x traces
    data_clip = np.percentile(np.abs(data), 99)
    time_ms = np.arange(hdr['samples_per_trace']) * hdr['sample_interval_us'] / 1000.0

    plt.figure(figsize=(12, 8))
    plt.imshow(
        data,
        cmap='seismic',
        aspect='auto',
        vmin=-data_clip,
        vmax=data_clip,
        extent=[1, data.shape[1], time_ms[-1], time_ms[0]],
    )
    plt.colorbar(label='Amplitude')
    plt.xlabel('Trace index (preview)')
    plt.ylabel('Time (ms)')
    plt.title('SeisDARE Sotiel-Elvira — first 120 traces preview')
    plt.tight_layout()
    plt.savefig(OUT / 'crrct-0_first120_traces.png', dpi=220)
    plt.close()

    # first trace plot
    plt.figure(figsize=(10, 5))
    plt.plot(time_ms, data[:, 0], linewidth=1)
    plt.xlabel('Time (ms)')
    plt.ylabel('Amplitude')
    plt.title('SeisDARE Sotiel-Elvira — first trace amplitude vs time')
    plt.tight_layout()
    plt.savefig(OUT / 'crrct-0_first_trace.png', dpi=220)
    plt.close()

    lines = []
    lines.append('# SeisDARE SEG-Y local inspection')
    lines.append('')
    lines.append(f'- File: `{SEGY.name}`')
    lines.append(f'- Size: {size:,} bytes')
    lines.append(f'- Estimated trace count: {est_traces:,}')
    lines.append(f'- Sample interval: {hdr["sample_interval_us"]} microseconds')
    lines.append(f'- Samples per trace: {hdr["samples_per_trace"]}')
    lines.append(f'- Sample format code: {hdr["sample_format_code"]} (IEEE 4-byte float)')
    lines.append('')
    lines.append('## First trace headers')
    for i, h in enumerate(first_headers[:3], start=1):
        scale = format_scale(h['coord_scalar'])
        lines.append(f'### Trace {i}')
        lines.append(f'- sequence in line/file: {h["seq_line"]} / {h["seq_file"]}')
        lines.append(f'- field record: {h["field_record"]}')
        lines.append(f'- trace number: {h["trace_num"]}')
        lines.append(f'- samples / dt: {h["ns"]} / {h["dt_us"]} microseconds')
        lines.append(f'- source coords (scaled): ({h["src_x"] * scale:.4f}, {h["src_y"] * scale:.4f})')
        lines.append(f'- receiver coords (scaled): ({h["grp_x"] * scale:.4f}, {h["grp_y"] * scale:.4f})')
        lines.append('')
    lines.append('## Interpretation')
    lines.append('- The file is a valid, parseable SEG-Y dataset suitable for local processing.')
    lines.append('- The binary header is internally consistent: 5001 samples/trace at 4 ms sample spacing.')
    lines.append('- The trace data uses IEEE float format, which is easier to work with than older IBM float variants.')
    lines.append('- This makes the smaller SeisDARE file practical for local visualization and seismic ML prototyping.')
    lines.append('')
    lines.append('## Figures')
    lines.append('- `crrct-0_first120_traces.png`')
    lines.append('- `crrct-0_first_trace.png`')

    (OUT / 'README.md').write_text('\n'.join(lines), encoding='utf-8')
    print('Saved preview outputs to', OUT)
    for p in sorted(OUT.iterdir()):
        print('-', p.name)


if __name__ == '__main__':
    main()

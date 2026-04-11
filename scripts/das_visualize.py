from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'datasets' / 'das' / 'raw' / 'DAS_safe'
OUT = ROOT / 'datasets' / 'das' / 'outputs'
OUT.mkdir(exist_ok=True)

sns.set_theme(style='whitegrid', context='talk')
plt.rcParams['figure.dpi'] = 160
plt.rcParams['savefig.dpi'] = 200

LABEL_MAP = {
    0: 'Background / noise-like',
    1: 'Hammering',
    2: 'Vehicle vibration',
}
RAW_FILES = {
    'Background raw': 'noise1.csv',
    'Hammering raw': 'hammer1.csv',
    'Vehicle raw': 'vehicle1.csv',
    'Rain raw (archived)': 'rain.csv',
    'Fan raw (archived)': 'fan.csv',
}


def load_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == '.xlsx':
        return pd.read_excel(path, header=None)
    return pd.read_csv(path, header=None)


def split_xy(df: pd.DataFrame):
    x = df.iloc[:, :-1].to_numpy(dtype=np.float32)
    y = df.iloc[:, -1].to_numpy(dtype=np.int32)
    return x, y


def zscore_rows(x: np.ndarray) -> np.ndarray:
    mu = x.mean(axis=1, keepdims=True)
    sigma = x.std(axis=1, keepdims=True)
    sigma[sigma == 0] = 1.0
    return (x - mu) / sigma


def save_class_distribution(train_y: np.ndarray, test_y: np.ndarray):
    labels = sorted(set(train_y) | set(test_y))
    rows = []
    for split_name, y in [('Train', train_y), ('Test', test_y)]:
        vals, counts = np.unique(y, return_counts=True)
        counts_map = dict(zip(vals, counts))
        for lab in labels:
            rows.append({
                'Split': split_name,
                'Label': LABEL_MAP.get(lab, str(lab)),
                'Count': counts_map.get(lab, 0),
            })
    plot_df = pd.DataFrame(rows)
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=plot_df, x='Label', y='Count', hue='Split', palette='Set2')
    ax.set_title('Labeled DAS dataset class balance')
    ax.set_xlabel('Class')
    ax.set_ylabel('Sample count')
    ax.tick_params(axis='x', rotation=15)
    plt.tight_layout()
    plt.savefig(OUT / 'class_distribution.png')
    plt.close()


def save_waveform_examples(x: np.ndarray, y: np.ndarray):
    labels = sorted(np.unique(y))
    fig, axes = plt.subplots(len(labels), 1, figsize=(14, 9), sharex=True)
    if len(labels) == 1:
        axes = [axes]
    for ax, lab in zip(axes, labels):
        idxs = np.where(y == lab)[0][:3]
        for i, idx in enumerate(idxs):
            sig = x[idx]
            sig = (sig - sig.mean()) / (sig.std() + 1e-6)
            ax.plot(sig, linewidth=1.2, alpha=0.9, label=f'Sample {i+1}')
        ax.set_title(LABEL_MAP.get(lab, str(lab)))
        ax.set_ylabel('z-score')
        ax.legend(loc='upper right', ncol=3, fontsize=9)
    axes[-1].set_xlabel('Time index (2500 points)')
    fig.suptitle('Example normalized DAS waveforms by class', y=1.02)
    plt.tight_layout()
    plt.savefig(OUT / 'waveform_examples.png', bbox_inches='tight')
    plt.close()


def save_class_means(x: np.ndarray, y: np.ndarray):
    labels = sorted(np.unique(y))
    fig, axes = plt.subplots(len(labels), 1, figsize=(14, 10), sharex=True)
    if len(labels) == 1:
        axes = [axes]
    for ax, lab in zip(axes, labels):
        xx = zscore_rows(x[y == lab])
        mean = xx.mean(axis=0)
        std = xx.std(axis=0)
        ax.plot(mean, color='#1f77b4', linewidth=2, label='Mean waveform')
        ax.fill_between(np.arange(len(mean)), mean - std, mean + std, color='#1f77b4', alpha=0.2, label='±1 std')
        ax.set_title(LABEL_MAP.get(lab, str(lab)))
        ax.set_ylabel('z-score')
        ax.legend(loc='upper right', fontsize=10)
    axes[-1].set_xlabel('Time index')
    fig.suptitle('Class-average normalized waveform profiles', y=1.02)
    plt.tight_layout()
    plt.savefig(OUT / 'class_mean_std.png', bbox_inches='tight')
    plt.close()


def save_pca_scatter(train_x: np.ndarray, train_y: np.ndarray):
    z = zscore_rows(train_x)
    pca = PCA(n_components=2, random_state=42)
    emb = pca.fit_transform(z)
    df = pd.DataFrame({
        'PC1': emb[:, 0],
        'PC2': emb[:, 1],
        'Label': [LABEL_MAP.get(v, str(v)) for v in train_y],
    })
    plt.figure(figsize=(10, 8))
    ax = sns.scatterplot(data=df, x='PC1', y='PC2', hue='Label', palette='Set1', s=55, alpha=0.8)
    ax.set_title(
        f'PCA view of normalized labeled DAS signals\n'
        f'Explained variance: PC1={pca.explained_variance_ratio_[0]:.1%}, PC2={pca.explained_variance_ratio_[1]:.1%}'
    )
    plt.tight_layout()
    plt.savefig(OUT / 'pca_scatter.png')
    plt.close()


def save_fft_profiles(x: np.ndarray, y: np.ndarray):
    labels = sorted(np.unique(y))
    plt.figure(figsize=(12, 7))
    for lab in labels:
        xx = zscore_rows(x[y == lab])
        psd = np.abs(np.fft.rfft(xx, axis=1)) ** 2
        mean_psd = psd.mean(axis=0)
        freq = np.arange(len(mean_psd))
        plt.plot(freq[1:400], mean_psd[1:400], linewidth=2, label=LABEL_MAP.get(lab, str(lab)))
    plt.yscale('log')
    plt.title('Average frequency-domain signature by class')
    plt.xlabel('Frequency bin')
    plt.ylabel('Mean power (log scale)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / 'fft_profiles.png')
    plt.close()


def save_raw_gallery():
    fig, axes = plt.subplots(len(RAW_FILES), 1, figsize=(14, 12), sharex=True)
    if len(RAW_FILES) == 1:
        axes = [axes]
    for ax, (title, fname) in zip(axes, RAW_FILES.items()):
        df = load_table(DATA / fname)
        sig = df.iloc[0, :-1].to_numpy(dtype=np.float32)
        sig = (sig - sig.mean()) / (sig.std() + 1e-6)
        ax.plot(sig[:600], linewidth=1.25)
        ax.set_title(f'{title} — first window preview')
        ax.set_ylabel('z-score')
    axes[-1].set_xlabel('Time index (first 600 points shown)')
    fig.suptitle('Representative raw waveform previews from archived files', y=1.02)
    plt.tight_layout()
    plt.savefig(OUT / 'raw_trace_gallery.png', bbox_inches='tight')
    plt.close()


def save_summary(train_x, train_y, test_x, test_y):
    lines = []
    lines.append('# DAS dataset visualization summary')
    lines.append('')
    lines.append('## Files used')
    lines.append('- `DAS_safe/train.xlsx`')
    lines.append('- `DAS_safe/test.xlsx`')
    lines.append('- representative raw CSVs extracted from the archive')
    lines.append('')
    lines.append('## Basic dataset shape')
    lines.append(f'- Training set: {train_x.shape[0]} samples × {train_x.shape[1]} signal points')
    lines.append(f'- Test set: {test_x.shape[0]} samples × {test_x.shape[1]} signal points')
    lines.append(f'- Each row contains 2500 signal values plus 1 label column')
    lines.append('')
    lines.append('## Label distribution')
    for split_name, y in [('Train', train_y), ('Test', test_y)]:
        vals, counts = np.unique(y, return_counts=True)
        lines.append(f'### {split_name}')
        for v, c in zip(vals, counts):
            lines.append(f'- {LABEL_MAP.get(int(v), str(v))}: {int(c)} samples')
        lines.append('')
    lines.append('## Important observation')
    lines.append('- The labeled train/test workbooks contain **3 classes** only: labels 0, 1, and 2.')
    lines.append('- Based on the raw filenames in the archive, these appear to correspond approximately to:')
    lines.append('  - `0` = background / noise-like signals (and likely includes some non-hammer non-vehicle disturbances),')
    lines.append('  - `1` = hammering,')
    lines.append('  - `2` = vehicle vibration.')
    lines.append('- The zip archive also contains raw rain and fan files, but those do **not** appear as separate labels in the exported train/test workbooks.')
    lines.append('')
    lines.append('## Figures generated')
    for name in [
        'class_distribution.png',
        'waveform_examples.png',
        'class_mean_std.png',
        'pca_scatter.png',
        'fft_profiles.png',
        'raw_trace_gallery.png',
    ]:
        lines.append(f'- `{name}`')
    lines.append('')
    lines.append('## Quick interpretation')
    lines.append('- The dataset is balanced across the 3 labeled classes, which is helpful for a clean first-pass classifier.')
    lines.append('- Hammering and vehicle signals show visibly different waveform texture and spectral structure after normalization.')
    lines.append('- A simple PCA projection already shows whether classes are partially separable before any deep model is applied.')
    lines.append('- For a presentation, this dataset is best positioned as a **proof-of-concept DAS event classification dataset**, not yet a mining-grade orebody detection dataset.')
    lines.append('')
    (OUT / 'README.md').write_text('\n'.join(lines), encoding='utf-8')


def main():
    train = load_table(DATA / 'train.xlsx')
    test = load_table(DATA / 'test.xlsx')
    train_x, train_y = split_xy(train)
    test_x, test_y = split_xy(test)

    save_class_distribution(train_y, test_y)
    save_waveform_examples(train_x, train_y)
    save_class_means(train_x, train_y)
    save_pca_scatter(train_x, train_y)
    save_fft_profiles(train_x, train_y)
    save_raw_gallery()
    save_summary(train_x, train_y, test_x, test_y)

    print('Saved outputs to:', OUT)
    for p in sorted(OUT.iterdir()):
        print('-', p.name)


if __name__ == '__main__':
    main()

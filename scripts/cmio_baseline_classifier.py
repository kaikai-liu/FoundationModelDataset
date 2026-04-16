"""
CMiO baseline classifier — Deposit_Environment from rock geochemistry.

Pipeline:
  1. Load 250827_CMMI_Rock_Geochemistry_Data.csv.
  2. For each element, pick the single method column with the best coverage
     (best_method_col); this collapses the 290 sparse analytical columns to one
     feature per element, matching the CMiO dictionary convention.
  3. Clean each element column:
       - negated-LDL (value <= 0)   -> |value| / 2   (half-LDL imputation)
       - upper-limit overflow (X.1111 fractional) -> floor(value)  (use the cap)
       - blank / NaN                -> NaN (imputed later)
  4. Log10-transform positive concentrations (wide dynamic range in geochem).
  5. Keep elements whose best column has >= MIN_COVERAGE on labeled rows.
  6. Median-impute the remaining NaN per column.
  7. Stratified 80/20 split on Deposit_Environment (drop rows with no label).
  8. Train a RandomForestClassifier baseline; report accuracy + macro F1
     + confusion matrix + per-class support.

Outputs (datasets/cmio/outputs/):
  - baseline_confusion_matrix.png
  - baseline_feature_importance.png
  - README_baseline.md              results + methodology
"""
from __future__ import annotations

from pathlib import Path
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score, f1_score, classification_report, confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / 'datasets' / 'cmio' / 'raw'
OUT = ROOT / 'datasets' / 'cmio' / 'outputs'
OUT.mkdir(exist_ok=True, parents=True)

DATA_CSV = RAW / '250827_CMMI_Rock_Geochemistry_Data.csv'

META_COLS = {
    'Field_ID', 'Sample_Comment', 'Deposit_Environment', 'Deposit_Group',
    'Deposit_Type', 'Latitude_decimal', 'Longitude_decimal', 'Datum',
    'Country', 'State_Province', 'Location_Description', 'Date_Collected',
    'Sample_Source', 'Depth', 'Rock_Type', 'MRP', 'Lab_ID',
}
COL_PATTERN = re.compile(r'^(?P<elem>[A-Za-z0-9]+)_(?P<unit>ppm|ppb|pct)_(?P<method>.+)$')

LABEL = 'Deposit_Environment'
MIN_LABELED_COVERAGE = 0.30   # keep elements with >= 30% non-null on labeled rows
RANDOM_STATE = 42
OVERFLOW_EPSILON = 1e-4       # tolerance when detecting .1111 sentinel


def parse_columns(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for c in df.columns:
        if c in META_COLS:
            continue
        m = COL_PATTERN.match(c)
        if not m:
            rows.append({'column': c, 'element': None, 'unit': None, 'method': None})
            continue
        rows.append({'column': c, 'element': m.group('elem'),
                     'unit': m.group('unit'), 'method': m.group('method')})
    return pd.DataFrame(rows)


def clean_analytical(series: pd.Series) -> pd.Series:
    """Apply LDL / overflow / blank conventions and return positive ppm/ppb/pct."""
    vals = pd.to_numeric(series, errors='coerce').astype('float64')
    out = vals.copy()

    # Upper-limit overflow sentinel: X.1111 (e.g. 50000.1111).
    frac = np.mod(np.abs(vals), 1.0)
    overflow_mask = np.isclose(frac, 0.1111, atol=OVERFLOW_EPSILON) & vals.notna()
    out[overflow_mask] = np.floor(vals[overflow_mask].abs())

    # Below-LDL: negated LDL encoding.
    ldl_mask = vals.notna() & (vals <= 0)
    out[ldl_mask] = vals[ldl_mask].abs() / 2.0

    # Zeros that survived (rare) -> NaN to keep log finite.
    out[out <= 0] = np.nan
    return out


def build_feature_table(df: pd.DataFrame, acols: pd.DataFrame, labeled_mask: pd.Series,
                        min_coverage: float) -> tuple[pd.DataFrame, list[dict]]:
    """Return (features, feature_log) — log has chosen method + coverage per element."""
    feats = {}
    log = []
    for element, group in acols.dropna(subset=['element']).groupby('element'):
        candidates = group['column'].tolist()
        # coverage on labeled rows
        cov_on_labeled = df.loc[labeled_mask, candidates].notna().mean()
        best = cov_on_labeled.idxmax()
        cov = float(cov_on_labeled.max())
        if cov < min_coverage:
            continue
        cleaned = clean_analytical(df[best])
        logged = np.log10(cleaned)
        # element unit retained via column name for traceability
        unit = group.loc[group['column'] == best, 'unit'].iloc[0]
        feats[f'{element}_{unit}_log10'] = logged
        log.append({'element': element, 'unit': unit, 'method_column': best,
                    'labeled_coverage': cov, 'n_methods': len(candidates)})
    X = pd.DataFrame(feats, index=df.index)
    log_df = pd.DataFrame(log).sort_values('labeled_coverage', ascending=False)
    return X, log_df


def plot_confusion(cm: np.ndarray, classes: list[str], out_png: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 6.5))
    im = ax.imshow(cm, cmap='Blues')
    ax.set_xticks(range(len(classes)))
    ax.set_yticks(range(len(classes)))
    ax.set_xticklabels(classes, rotation=30, ha='right', fontsize=8)
    ax.set_yticklabels(classes, fontsize=8)
    ax.set_xlabel('predicted')
    ax.set_ylabel('true')
    ax.set_title('CMiO baseline — confusion matrix (test set)')
    vmax = cm.max() if cm.size else 1
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            v = cm[i, j]
            if v == 0:
                continue
            color = 'white' if v > vmax * 0.55 else 'black'
            ax.text(j, i, str(v), ha='center', va='center', color=color, fontsize=8)
    plt.colorbar(im, ax=ax, shrink=0.75)
    plt.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def plot_feature_importance(names: list[str], importances: np.ndarray, out_png: Path,
                            top_n: int = 25) -> None:
    order = np.argsort(importances)[::-1][:top_n]
    names_top = [names[i] for i in order]
    vals_top = importances[order]
    fig, ax = plt.subplots(figsize=(8.5, max(4, len(names_top) * 0.28)))
    ax.barh(range(len(names_top)), vals_top[::-1], color='steelblue',
            edgecolor='black', linewidth=0.3)
    ax.set_yticks(range(len(names_top)))
    ax.set_yticklabels(names_top[::-1], fontsize=8)
    ax.set_xlabel('mean decrease in impurity')
    ax.set_title(f'Top {len(names_top)} features — Random Forest importance')
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)


def write_readme(metrics: dict, feature_log: pd.DataFrame, class_counts: pd.Series,
                 report_text: str, out: Path) -> None:
    lines = [
        '# CMiO baseline classifier — Deposit_Environment',
        '',
        '## Bottom line',
        f'- Random Forest baseline on log-transformed rock geochemistry predicts '
        f'`Deposit_Environment` with **{metrics["accuracy"]*100:.1f}% accuracy** and '
        f'**macro F1 = {metrics["macro_f1"]:.3f}** on a stratified 20% test split '
        f'(n_test = {metrics["n_test"]}, classes = {metrics["n_classes"]}).',
        f'- {metrics["n_features"]} element features were retained after filtering '
        f'to best-covered method columns with ≥ {int(MIN_LABELED_COVERAGE*100)}% '
        f'coverage on labeled rows; {metrics["n_samples"]} labeled samples used '
        f'(out of 1,295 total).',
        '',
        '## Data cleaning',
        '',
        'Following the CMiO data dictionary conventions:',
        '',
        '| Raw value | Meaning | Cleaned to |',
        '| --- | --- | --- |',
        '| `NaN` / blank | not analyzed by this method | kept NaN → median-imputed per column |',
        '| value ≤ 0 | below Lower Detection Limit (encoded as −LDL) | `|value| / 2` (half-LDL) |',
        '| `X.1111` (fractional ≈ 0.1111) | above Upper Detection Limit | `floor(X)` (use cap) |',
        '| otherwise | detected value | `log10(value)` |',
        '',
        '## Feature selection',
        '',
        'For each element, one method column is chosen: the one with highest non-null',
        f'share on labeled rows. Elements are kept only if that coverage ≥ '
        f'{int(MIN_LABELED_COVERAGE*100)}% — the sparse long tail of single-method ',
        'elements is dropped to keep imputation honest.',
        '',
        f'**{len(feature_log)} elements retained** (top 15 by coverage):',
        '',
        '| element | unit | chosen method column | labeled coverage | # method columns available |',
        '| --- | --- | --- | ---: | ---: |',
    ]
    for _, r in feature_log.head(15).iterrows():
        lines.append(
            f'| {r["element"]} | {r["unit"]} | `{r["method_column"]}` | '
            f'{r["labeled_coverage"]*100:.1f}% | {int(r["n_methods"])} |'
        )
    lines += [
        '',
        '## Label distribution (labeled samples only)',
        '',
        '| Deposit_Environment | samples |',
        '| --- | ---: |',
    ]
    for env, n in class_counts.items():
        lines.append(f'| {env} | {int(n):,} |')

    lines += [
        '',
        '## Model',
        '',
        '- `RandomForestClassifier(n_estimators=400, class_weight="balanced", '
        'random_state=42, n_jobs=-1)`',
        '- Imputer: median on training fold, applied to train + test.',
        '- Split: `train_test_split(..., test_size=0.2, stratify=y, random_state=42)`.',
        '',
        '## Results',
        '',
        f'- **Test accuracy:** {metrics["accuracy"]*100:.2f}%',
        f'- **Macro F1:** {metrics["macro_f1"]:.3f}',
        f'- **Weighted F1:** {metrics["weighted_f1"]:.3f}',
        '',
        '### Per-class classification report',
        '',
        '```',
        report_text.rstrip(),
        '```',
        '',
        '## Figures',
        '',
        '- `baseline_confusion_matrix.png` — absolute counts on the 20% test fold',
        '- `baseline_feature_importance.png` — top features by mean decrease in impurity',
        '',
        '## Limitations',
        '',
        '- Rare classes (`Magmatic`, n=13; `Regional metasomatic`, n=22) carry very few',
        '  test samples and dominate the macro-F1 error bar.',
        '- Features are labeled by log10-concentration of the best-coverage method only —',
        '  no ratios, no ore-pathfinder interactions, no unit/method harmonization.',
        '- Half-LDL imputation is a well-known biased estimator; fine for a baseline but',
        '  should be revisited (e.g. ROS, tobit) for downstream quantitative work.',
        '- No spatial holdout: samples from the same deposit can land in both train and',
        '  test. Expect an optimistic estimate vs. a geography-aware split.',
        '',
        '## Recommendation',
        '',
        'Use this script as the "minimum-viable" CMiO baseline for the foundation-model',
        'prototype track. Next iterations: (a) spatial/deposit-grouped split, (b) add',
        'ratio / pathfinder features, (c) cross-check against CMMI raster features',
        'sampled at CMiO lat/lon (the point-fusion experiment in `docs/TASKS.md`).',
    ]
    out.write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    if not DATA_CSV.exists():
        raise FileNotFoundError(DATA_CSV)
    print(f'Loading {DATA_CSV.relative_to(ROOT)} ...')
    df = pd.read_csv(DATA_CSV, low_memory=False)
    print(f'  shape = {df.shape}')

    acols = parse_columns(df)
    labeled = df[LABEL].notna() & (df[LABEL].astype(str).str.strip() != '')
    n_labeled = int(labeled.sum())
    print(f'  labeled rows (Deposit_Environment): {n_labeled} / {len(df)}')

    X_full, feat_log = build_feature_table(df, acols, labeled, MIN_LABELED_COVERAGE)
    print(f'  features retained: {X_full.shape[1]} elements '
          f'(>= {MIN_LABELED_COVERAGE*100:.0f}% labeled coverage)')

    X = X_full.loc[labeled]
    y = df.loc[labeled, LABEL].astype(str).str.strip()

    class_counts = y.value_counts()
    print('  class counts:')
    for k, v in class_counts.items():
        print(f'    {k:30s} {v:4d}')

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE,
    )

    pipe = Pipeline([
        ('impute', SimpleImputer(strategy='median')),
        ('rf', RandomForestClassifier(
            n_estimators=400, class_weight='balanced',
            random_state=RANDOM_STATE, n_jobs=-1)),
    ])
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    f1_macro = f1_score(y_test, y_pred, average='macro')
    f1_weighted = f1_score(y_test, y_pred, average='weighted')
    print(f'  accuracy      = {acc:.4f}')
    print(f'  macro F1      = {f1_macro:.4f}')
    print(f'  weighted F1   = {f1_weighted:.4f}')

    classes = sorted(y.unique())
    cm = confusion_matrix(y_test, y_pred, labels=classes)
    report = classification_report(y_test, y_pred, labels=classes, zero_division=0)
    print(report)

    plot_confusion(cm, classes, OUT / 'baseline_confusion_matrix.png')
    rf = pipe.named_steps['rf']
    plot_feature_importance(list(X.columns), rf.feature_importances_,
                            OUT / 'baseline_feature_importance.png')

    metrics = {
        'accuracy': float(acc),
        'macro_f1': float(f1_macro),
        'weighted_f1': float(f1_weighted),
        'n_test': int(len(y_test)),
        'n_samples': int(len(y)),
        'n_classes': len(classes),
        'n_features': int(X.shape[1]),
    }
    write_readme(metrics, feat_log, class_counts, report, OUT / 'README_baseline.md')
    print(f'Saved results to {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()

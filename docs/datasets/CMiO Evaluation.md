# CMiO Evaluation

## Bottom line
CMiO is the **ore-system supervision branch** of the three-layer dataset stack. It is a small but label-rich tabular dataset — **1,295 rock samples × 290 analytical columns**, each sample tagged with a deposit environment/group/type from the Hofstra et al. (2021) CMMI classification scheme.

The scale matches neither CMMI (continental raster) nor SeisDARE (seismic traces), but that is the point: CMiO lives at the **sample / composition** level and connects geochemical fingerprints to deposit types.

---

## Why it matters
- The only one of the three layers with **direct deposit-type labels** on individual samples — the supervised signal the CMMI rasters largely lack in our downloaded subset.
- Public domain (USGS data release, DOI `10.5066/P14WGQ8V`), so fully reusable.
- Samples span **7 deposit environments**, **17 deposit groups**, and **100+ deposit types** including Low-sulfidation epithermal Au-Ag, MVT Zn-Pb, Porphyry Cu-Mo, VMS, Replacement, and Sediment-hosted Cu ± Co.
- All samples are georeferenced (lat/lon in WGS84), so CMiO can be spatially joined to CMMI geophysical layers at the point level.

---

## What I inspected
Repository: [10.5066/P14WGQ8V](https://doi.org/10.5066/P14WGQ8V) (ScienceBase item `686ecb93d4be020e5c0a6c07`, published 2025-09-16).

Downloaded payload: **~1.7 MB, 4 files.**

| File | Size | Purpose |
| --- | --- | --- |
| `250827_CMMI_Rock_Geochemistry_Data.csv` | 915 KB | sample × column geochemistry table |
| `250827_CMMI_Rock_Geochemistry_DataDictionary.csv` | 136 KB | column definitions, LDL ranges, lab method IDs |
| `250827_CMMI_Rock_Geochemistry_Metadata.xml` | 252 KB | FGDC CSDGM metadata |
| `250827_CMMI_Rock_Geochemistry_Locations.png` | 396 KB | publisher-supplied sample map |

### Table shape
| Dimension | Value |
| --- | --- |
| Samples | 1,295 |
| Columns | 307 (17 metadata + 290 analytical) |
| Unique elements/species | 84 |
| Analytical methods | 19 |
| Samples with lat/lon | 1,295 / 1,295 |

### Key categorical distributions

**Deposit_Environment** (coarse class — most useful supervision target)

| Environment | Samples |
| --- | ---: |
| Basin chemical | 571 |
| Magmatic hydrothermal | 389 |
| Basin hydrothermal | 224 |
| Volcanic basin hydrothermal | 45 |
| Metamorphic hydrothermal | 30 |
| Regional metasomatic | 22 |
| Magmatic | 13 |

**Rock_Type**: 571 sedimentary, 458 ore, 255 blank, small igneous tail.

**Country**: 1,006 US · 66 Mexico · 63 Sweden · 47 Japan · 31 Canada · 19 Australia · + 10 others.

### Analytical methods observed
19 distinct method suffixes — each corresponds to a USGS lab analytical package:
`ICP30`, `ICP49`, `ICP61` and `oICP61` (4-acid and aqua-regia 61-element packages), `ICP55` (sodium-peroxide 59-element), `ICP16` (major-oxide), `ICPREE` (REE package), `WDXRF` and `WDXRFbm` (wavelength-dispersive XRF), `pXRF` (portable XRF), `FA` and `oFA` (fire assay), `CV` (cold-vapour AAS for Hg), `CARB` / `TITR` / `ISE` / `MICROW` / `TOTAL`.

---

## Detection-limit convention

From the data dictionary: **values below the Lower Detection Limit are encoded as negative numbers** equal to −LDL (e.g. −0.01 for an Ag column whose LDL is 0.01 ppm). Upper-detection overflow is encoded with the `.1111` suffix (e.g. `50000.1111` for Zn). A blank/null means the sample was not analyzed by that method.

This is a non-standard encoding and will trip any naive "negative = error" filter. For Au, Cu, Pb, Zn, Mo, Ag the inspection figure `detection_limit_shares.png` reports the detected vs below-LDL counts per method.

---

## Strengths
### 1. Clean label structure
Every sample is tagged with `Deposit_Environment`, and 668 / 1,295 also carry a `Deposit_Group` label. Multi-level supervision (environment → group → type) is directly usable for classification tasks of varying granularity.

### 2. Georeferenced
100% of samples have decimal-degree lat/lon, so CMiO points can be joined to CMMI rasters at the pixel level for "geochemistry-at-location" features.

### 3. Multi-method cross-validation
For many elements (Ag, Cu, Pb, Zn, etc.) there are **multiple method columns** measuring the same element. This allows method-quality auditing and gives natural self-supervised reconstruction targets.

### 4. Explicit data dictionary with LDLs and units
LDLs, method IDs, and units are in a machine-readable companion CSV. This is uncommon in geochem releases and makes automated feature extraction straightforward.

### 5. Tiny footprint
The whole release is under 2 MB. Fits entirely in memory; no engineering overhead.

---

## Limitations
### 1. Small sample count
**1,295 samples** is small by ML standards. Deposit-type distribution is long-tailed — only 4 types have ≥ 50 samples, and 627 samples have a blank `Deposit_Type` (group/environment labels still filled in). Fine-grained classification will need either label folding or external augmentation.

### 2. US-dominant geography
77.7% of samples are in the United States. International coverage is sparse, so models trained on CMiO will overweight US host-rock chemistry and may not generalize to, e.g., African copperbelt or Tethyan Pb-Zn systems without additional data.

### 3. High column sparsity
No analytical column has ≥ 90% coverage; 225 of 290 columns are below 50% non-null. Multiple ICP packages cover overlapping element sets, so the "best" column per element must be picked rather than treating all 290 raw columns as features.

### 4. Detection-limit encoding
Negative-LDL convention means naive log-scaling or `np.log` will fail. Any preprocessing must distinguish `null` (not analyzed), `negative` (below LDL), and positive (detected) — three-valued element coverage, not boolean.

### 5. Not a sensing dataset
No signal, no image, no time series — CMiO is static tabular composition. On its own it cannot train an encoder for subsurface sensing; it must be fused with CMMI rasters or SeisDARE seismic traces.

### 6. Mineral-system coverage is uneven
Low-sulfidation epithermal Au-Ag (n=207) and MVT Zn-Pb (n=130) dominate. Other critical-mineral systems (REE, lithium brines, Ni-Co laterite, PGM) are under-sampled.

---

## Best role for this dataset

> CMiO is the **compositional-label branch** of the three-layer stack. Use it as a supervised-signal source that ties geochemical composition to deposit type, and use lat/lon to fuse it point-wise with CMMI geophysical rasters.

Not:

> A standalone training corpus for a foundation model. The sample count is too small and the modality is too narrow.

---

## Good first ML tasks

### Best first tasks
- **Deposit-environment classification** — 7-class target, ~1,294 samples, balanced enough at the environment level. Drop columns with < 50% coverage and use one "best" column per element (~84 features). Standard baseline: gradient boosting or small MLP.
- **Deposit-group classification** on the 693 samples with a labeled group (17 groups) — a natural second-level task once environment baselines work.
- **CMMI × CMiO point fusion** — extract CMMI raster values (magnetic, gravity, Moho, LAB, HGM) at each CMiO sample's lat/lon, test whether geophysics + geochemistry classifies deposit environment better than either alone.
- **Detection-pattern encoding** — treat the null/negative/positive triple as the feature and learn compositional fingerprints without worrying about absolute concentrations.

### Less suitable first tasks
- Fine-grained `Deposit_Type` classification (long tail, 627 nulls).
- Unsupervised representation learning on the raw 290-column table (sparsity kills contrast).
- Regression on individual element concentrations (too many LDL-censored values).

---

## Recommendation
Keep CMiO as a **high-priority but companion dataset**. It is the lightest of the three and the only one with deposit-type labels, but it cannot stand alone. Its best use is to **supervise** and **condition** the richer CMMI raster + SeisDARE seismic data.

If the goal is mineral prospectivity, a natural first experiment is to join CMiO points to the US-Canada CMMI rasters already inspected and train a joint classifier — this is the smallest useful demonstration that the three-layer strategy works.

---

## What to do next

### Option 1 — point fusion with CMMI
Sample every CMMI raster at each CMiO lat/lon. Produce a joined table: 1,295 rows × (84 elements + 7 geophysics channels + deposit label). Train a small classifier baseline.

### Option 2 — clean the analytical table
Build a "one best method per element" matrix (84 element columns, 1,295 rows, 3-state cells) and establish a deposit-environment classification baseline on it alone.

### Option 3 — stack with missing CMMI items
Once the 6 deferred CMMI items are retrieved — particularly the Zn-Pb deposit shapefile and black-shale geochemistry database — CMiO + CMMI deposits + black-shale geochemistry become a coherent supervised mineral-system dataset.

### My recommendation
1. Build the "best method per element" cleaned table (one day of work).
2. Train a 7-class `Deposit_Environment` baseline on it.
3. In parallel, retry the 6 deferred CMMI items to unlock point fusion.

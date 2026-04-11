# SeisDARE Evaluation — SIT4ME / Sotiel-Elvira

## Bottom line
SeisDARE is a strong public lead for **subsurface mining detection**, mainly because the **SIT4ME / Sotiel-Elvira** dataset is explicitly built for mining exploration.

It is much more relevant than the DAS event dataset we reviewed earlier.

---

## Why it matters
This dataset is useful because it is:
- mining-focused,
- seismic-based,
- openly accessible,
- large enough to be technically meaningful,
- close to real subsurface imaging workflows.

This makes it a good candidate for:
- seismic/geophysical encoder training,
- subsurface structure learning,
- mining-area seismic experiments,
- testing seismic preprocessing and ML pipelines.

---

## What I found
From the repository page and attached metadata:

### Repository / license
- Collection: **SeisDARE**
- Dataset: **SIT4ME: Innovative seismic imaging techniques for mining exploration – Sotiel-Elvira (Spain)**
- License: **CC BY 4.0**
- Main link: https://doi.org/10.20350/digitalCSIC/8633

### Acquisition details
The repository describes:
- **2D / 3D seismic data**
- **3-component data**
- **active-source reflection seismic acquisition**
- **32-ton vibroseis truck**
- about **900 source points**
- frequency sweeps of **10–100 Hz**

### Files visible from the repository
The page exposes a small but useful file list:
- `XYZ_SRC_REC_02_GEOMETRY.xls` — acquisition geometry
- `Descripcion_ficheros_SOTIEL_dataset.xlsx` — file description
- `crrct-0.sgy` — seismic line
- `sdx-00_modf.sgy` — seismic line

### Approximate file sizes
From the repository headers:
- `XYZ_SRC_REC_02_GEOMETRY.xls` — ~286 KB
- `Descripcion_ficheros_SOTIEL_dataset.xlsx` — ~9 KB
- `crrct-0.sgy` — ~608 MB
- `sdx-00_modf.sgy` — ~8.8 GB

This means the dataset is realistic to inspect, but not trivial.

---

## What the metadata suggests
The geometry spreadsheet contains **1,563 spatial records**.

A rough interpretation is:
- about **910 coded positions**, likely source points
- about **653 uncoded positions**, likely receiver positions

This is broadly consistent with the repository description of roughly **900 source points** and **~647 receivers**.

So the dataset appears to be a real field acquisition rather than a toy benchmark.

---

## Strengths
### 1. Strong mining relevance
Unlike geothermal or generic DAS datasets, this one is explicitly tied to **mining exploration**.

### 2. Real geophysical workflow fit
SEG-Y seismic lines plus acquisition geometry are directly useful for real seismic processing and ML experimentation.

### 3. Good role in a multimodal stack
It fits naturally as the **subsurface sensing branch** of a broader mineral exploration system.

### 4. Open and citable
The data is openly hosted and licensed, which is useful for research and internal prototyping.

---

## Limitations
### 1. Likely weak on direct labels
This looks more like a **raw seismic acquisition dataset** than a ready-made supervised ML benchmark.

So it is likely weak for:
- orebody labels,
- direct mineralization classes,
- drill-target labels.

### 2. Seismic-only is not enough
For a full mineral exploration model, this would still need to be paired with:
- geology,
- geophysics,
- drilling,
- ore or prospectivity context.

### 3. Some overhead to use
SEG-Y files at this size are usable, but they require a proper seismic parsing workflow.

---

## Best role for this dataset
The best role for SeisDARE / Sotiel-Elvira is:

> **subsurface encoder and seismic experimentation dataset**

Not:

> full end-to-end mineral targeting dataset by itself

That is the key distinction.

---

## Good first ML tasks
If we use this dataset, the first tasks should be modest and realistic.

### Best first tasks
- seismic data loading and geometry validation
- basic visualization of shot / receiver layout
- trace and section visualization
- unsupervised or self-supervised seismic representation learning
- anomaly or structure-aware feature extraction

### Less suitable as a first task
- direct ore prediction
- full prospectivity mapping from seismic alone
- deposit-type classification without paired labels

---

## Recommendation
SeisDARE should be kept as a **high-priority subsurface dataset**.

Recommended role in the bigger stack:
- **SeisDARE** = subsurface seismic branch
- **CMMI** = mineral prospectivity branch
- **CMiO** = ore-system / geochemistry branch

---

## What to do next
### Option 1
Download the smaller SEG-Y file first (`crrct-0.sgy`) and inspect it locally.

### Option 2
Move to **CMMI** next and compare how it complements SeisDARE.

### My recommendation
Do both in this order:
1. inspect the smaller SeisDARE SEG-Y file,
2. then review CMMI,
3. then fit all three datasets into one stack.

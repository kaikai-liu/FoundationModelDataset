# Subsurface Dataset Research Brief

## Project scope

**Goal:** Identify, download, inspect, and characterize public datasets relevant to subsurface mining detection and mineral prospectivity. Validate each dataset's ML utility through lightweight prototype experiments.

**In scope:**
- Dataset discovery, downloading, and format inspection
- Visualization and geometry validation
- Prototype ML experiments per dataset (self-supervised, classification, or anomaly detection — enough to confirm the data teaches a model something useful)
- Per-dataset evaluation READMEs
- Cross-dataset comparison and final evaluation report

**Out of scope:** Production model training, fine-tuning at scale, deployment, model infrastructure.

**Why this boundary:** Pure inspection validates format and structure. Prototype experiments validate whether the data actually produces useful signal. Both are needed to close this phase and hand off confident dataset recommendations to the model-building phase.

---

## Deliverables

### Per dataset
- Inspection README (file stats, acquisition summary, key findings)
- Visualization outputs (trace sections, geometry maps, signal plots)
- Prototype experiment result (at least one simple ML task validating the data produces useful learned signal)
- Dataset verdict: **strong anchor** / **supporting** / **weak** for the foundation model

### Project-level
- Cross-dataset comparison table (dataset × modality × scale × mining relevance × experiment verdict)
- Final evaluation report with dataset recommendations for the model build phase

---

## Executive summary
There is no single open benchmark that fully covers **subsurface mining detection**. The best near-term strategy is to combine:
- **subsurface sensing datasets** for seismic/DAS representation learning,
- **mineral-system datasets** for prospectivity and ore context,
- **private mine data** for final fine-tuning.

The main takeaway is simple:
- **SeisDARE** is the strongest public lead for mining-related subsurface sensing,
- **CMMI** is the strongest public lead for regional mineral prospectivity,
- **CMiO** is the best public geochemical companion dataset.

---

## 1. Core conclusion
Open mining-specific subsurface datasets are scarce. Most public datasets fall into one of three buckets:

1. **Subsurface sensing**  
   Seismic, DAS, geothermal, crustal imaging.

2. **Mineral prospectivity**  
   Geological and geophysical layers linked to mineral occurrence.

3. **Ore-system supervision**  
   Geochemistry and deposit-type data.

Because of this, the best path is not to find one perfect dataset, but to use a **layered dataset strategy**.

---

## 2. Most relevant datasets

### A. SeisDARE
**Role:** subsurface sensing branch  
**Why it matters:** includes mining-related seismic datasets, especially **SIT4ME / Sotiel-Elvira**.  
**Best use:** seismic/geophysical encoder training, subsurface structure learning, mining seismic experiments.  
**Limitation:** not enough alone for full mineral targeting.

Key link: https://essd.copernicus.org/articles/13/1053/2021/  
Mining dataset: https://doi.org/10.20350/digitalCSIC/8633

### B. CMMI
**Role:** mineral prospectivity branch  
**Why it matters:** combines geology, geophysics, faults, and prospectivity layers for critical mineral discovery.  
**Best use:** regional prospectivity modeling, evidential-layer fusion, weak supervision.  
**Limitation:** regional scale, not mine-scale sensing.

Key links:  
https://www.usgs.gov/centers/gggsc/science/critical-minerals-mapping-initiative-cmmi  
https://www.usgs.gov/data/national-scale-geophysical-geologic-and-mineral-resource-data-and-grids-united-states-canada

### C. CMiO
**Role:** ore-system / geochemistry branch  
**Why it matters:** links deposit types to multi-element ore chemistry.  
**Best use:** geochemical supervision, deposit-type reasoning, multimodal fusion with prospectivity layers.  
**Limitation:** not a sensing dataset by itself.

Key link: https://www.usgs.gov/publications/critical-minerals-ores-cmio-database

### D. DAS datasets (supporting only)
Examples: PoroTomo, Utah FORGE, Mendeley DAS intrusion dataset.  
**Role:** useful for signal and time-series prototyping.  
**Limitation:** weaker mining relevance than SeisDARE.

---

## 3. Prioritization

### Highest priority
1. **SeisDARE / SIT4ME** — best public dataset for mining-related subsurface sensing
2. **CMMI** — best public dataset for mineral prospectivity context
3. **CMiO** — best public dataset for ore-system supervision

### Lower priority
- geothermal seismic / DAS datasets
- generic seismic repositories
- toy event-classification datasets

---

## 4. Recommended data strategy

### Layer 1 — Subsurface sensing
Use **SeisDARE** to build or test seismic/geophysical encoders.

### Layer 2 — Mineral context
Use **CMMI** to connect geophysical evidence to mineral prospectivity.

### Layer 3 — Ore-system context
Use **CMiO** to add geochemical and deposit-type information.

### Layer 4 — Deployment data
Use proprietary mine geophysics, drillholes, assays, and interpretations for final fine-tuning.

---

## 5. Recommended message to the team
A good summary is:

> We should not rely on one dataset. SeisDARE is the strongest public starting point for subsurface mining detection, while CMMI and CMiO provide the mineral prospectivity and ore-system context needed to turn subsurface sensing into a useful exploration model.

---

## 6. Dataset rankings by use case

#### Closest to business / mineral exploration relevance
1. **CMMI** — geology + geophysics + prospectivity layers, directly answers “where are mineral systems?”
2. **CMiO** — deposit-type geochemistry, moves from “anomaly” to “mineral system hypothesis”
3. Prospectivity layers tied to CMMI
4. Partner/private mine data

#### Closest to subsurface detection technique
1. **SeisDARE** — real geophysical imaging, mining-relevant (Sotiel-Elvira), scientifically credible
2. **Utah FORGE / PoroTomo** — real field deployments but geothermal-first, not mining-first
3. SEG Open Data
4. Mendeley DAS (toy benchmark only)

#### Best next thing to evaluate
1. **CMMI**
2. **CMiO**
3. One more subsurface companion dataset (ALCUDIA or HONTOMÍN)

### Note on scale mismatch
These datasets live at very different scales:
- DAS / seismic = local, high-frequency, sensor-rich
- CMMI = regional, coarse, evidential-layer scale
- CMiO = deposit / sample scale, compositional

A foundation model connects these scales — but the first experiments should not try to do everything at once. Start at **regional prospectivity** (CMMI + CMiO), add sensor-level subsurface learning (SeisDARE) as a second branch.

## 7. Final recommendation
If we are being disciplined, the best next move is:
- **CMMI as the main dataset**
- **CMiO as the companion dataset**
- **SeisDARE** as the strongest subsurface branch

What I would **not** prioritize next is another small event-classification DAS dataset.

That said, if the goal is specifically **subsurface mining detection first**, the evaluation order should be:
1. **SeisDARE**
2. **CMMI**
3. **CMiO**

That keeps the work aligned with the mining problem while still building toward a broader multimodal foundation model.

# Dataset Research Tasks

## Status legend
- [x] Done
- [-] In progress / partial
- [ ] Not started

---

## Phase 1 — SeisDARE datasets

### SOTIEL (Iberian Pyrite Belt, mining anchor)
- [x] Inspect `crrct-0.sgy` headers + geometry
- [x] Visualize traces + geometry layout
- [x] Write README (`seisdare_preview/`, `seisdare_geometry_preview/`)
- [ ] Prototype experiment (e.g. self-supervised trace reconstruction or unsupervised structure detection)

### IBERSEIS NI (normal incidence, migrated + stack)
- [x] Inspect headers (`IBER6-5-mig.sgy`, `IBER6-5-stk.sgy`)
- [x] Visualize seismic sections
- [x] Write README (`iberseis_preview/`)
- [ ] Prototype experiment

### IBERSEIS WA (wide-angle, crustal imaging)
- [x] Inspect SEG-Y headers + geometry ASCII
- [x] Visualize offset histogram, shot coverage map, trace section
- [x] Write README + README_geometry (`iberseis_wa_preview/`)
- [-] Full download (currently 1.08 GB / ~1.14 GB — CSIC server cap; 9,010 of ~14,500 expected traces)
- [ ] Prototype experiment

### ALCUDIA
- [ ] Download SEG-Y file(s) from DIGITAL.CSIC
- [ ] Inspect headers + geometry
- [ ] Visualize + write README
- [ ] Prototype experiment

### HONTOMÍN
- [ ] Download SEG-Y file(s)
- [ ] Inspect headers + geometry
- [ ] Visualize + write README
- [ ] Prototype experiment

### CIMDEF
- [ ] Confirm download availability
- [ ] Inspect headers + geometry
- [ ] Visualize + write README
- [ ] Prototype experiment

---

## Phase 2 — CMMI (critical mineral prospectivity)
- [-] Download CMMI data package (USGS) — US-Canada geophysics + faults done (8 of 14 ScienceBase items; 6 deposit/prospectivity/geochemistry items deferred, hit HTTP 522)
- [x] Inspect raster layers (modalities, resolution, spatial coverage)
- [x] Visualize key layers
- [x] Write README (`datasets/cmmi/outputs/` + `docs/datasets/CMMI Evaluation - US-Canada Subset.md`)
- [ ] Retry missing ScienceBase items (Zn-Pb deposits, prospectivity models, black-shale geochemistry, Australia magnetic, geology shapefiles)
- [ ] Prototype experiment (e.g. prospectivity regression or anomaly ranking)

---

## Phase 3 — CMiO (ore-system geochemistry)
- [x] Download CMiO database (USGS) — rock geochemistry release, DOI 10.5066/P14WGQ8V (~1.7 MB, 1,295 samples × 307 columns)
- [x] Inspect structure (deposit types, elements, sample counts)
- [x] Visualize deposit-type distributions
- [x] Write README (`datasets/cmio/outputs/` + `docs/datasets/CMiO Evaluation.md`)
- [ ] Prototype experiment (e.g. deposit-environment classification or CMiO × CMMI point fusion)

---

## Phase 4 — Cross-dataset summary
- [ ] Write comparison table: dataset × modality × scale × mining relevance × experiment verdict
- [ ] Produce dataset coverage map figure
- [ ] Final evaluation report with recommendations for the model build phase

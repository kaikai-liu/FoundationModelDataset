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
- [ ] Download CMMI data package (USGS)
- [ ] Inspect raster layers (modalities, resolution, spatial coverage)
- [ ] Visualize key layers
- [ ] Write README
- [ ] Prototype experiment (e.g. prospectivity regression or anomaly ranking)

---

## Phase 3 — CMiO (ore-system geochemistry)
- [ ] Download CMiO database (USGS)
- [ ] Inspect structure (deposit types, elements, sample counts)
- [ ] Visualize deposit-type distributions
- [ ] Write README
- [ ] Prototype experiment (e.g. deposit-type classification from geochemistry)

---

## Phase 4 — Cross-dataset summary
- [ ] Write comparison table: dataset × modality × scale × mining relevance × experiment verdict
- [ ] Produce dataset coverage map figure
- [ ] Final evaluation report with recommendations for the model build phase

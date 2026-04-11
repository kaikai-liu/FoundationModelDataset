# Foundation Model Dataset Research

Dataset evaluation and characterization for a multimodal foundation model for mineral exploration ([EyeClimate](https://eyeclimate.com)).

**Scope:** This project identifies, downloads, inspects, and validates public datasets. It does not train models. The deliverable is a dataset evaluation report with recommendations for the model-build phase.

See [`docs/Subsurface Dataset Research Brief.md`](docs/Subsurface%20Dataset%20Research%20Brief.md) for strategy and [`docs/TASKS.md`](docs/TASKS.md) for current status.

---

## Setup

```bash
# Install dependencies (requires Python >= 3.10 and uv)
uv sync

# Activate virtual environment (Windows Git Bash)
source .venv/Scripts/activate
```

---

## Scripts

```bash
python scripts/das_visualize.py                 # DAS event classification dataset
python scripts/inspect_seisdare_segy.py         # SOTIEL SEG-Y inspection
python scripts/inspect_seisdare_geometry.py     # SOTIEL geometry validation
python scripts/inspect_iberseis_ni.py           # IBERSEIS normal-incidence (mig/stk)
python scripts/inspect_iberseis_wa_segy.py      # IBERSEIS wide-angle SEG-Y
python scripts/inspect_iberseis_wa_geometry.py  # IBERSEIS wide-angle geometry
python scripts/make_seisdare_summary_slide.py   # SOTIEL composite slide
```

Each script writes PNG visualizations and a README to the dataset's `outputs/` folder.

---

## Directory structure

```
datasets/
├── das/                  DAS event classification
│   ├── raw/
│   └── outputs/
└── seisdare/             SeisDARE collection
    ├── sotiel/           Mining seismic — Iberian Pyrite Belt
    │   ├── raw/
    │   └── outputs/
    └── iberseis/         Crustal seismic — Iberian Massif
        ├── raw/
        ├── ni_outputs/
        └── wa_outputs/
docs/
├── Subsurface Dataset Research Brief.md   dataset strategy + project scope
├── TASKS.md                               task checklist (current status)
├── datasets/                              per-dataset evaluation docs
└── others/                               background context
scripts/                                   inspection and visualization scripts
```

---

## Dataset strategy

Three-layer approach:

| Layer | Dataset | Role |
|-------|---------|------|
| Subsurface sensing | SeisDARE (SOTIEL, IBERSEIS) | Seismic encoder training |
| Mineral prospectivity | CMMI | Regional mineral targeting |
| Ore-system context | CMiO | Geochemical supervision |

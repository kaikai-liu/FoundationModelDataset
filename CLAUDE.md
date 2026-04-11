# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Dataset research and inspection pipeline for a **multimodal foundation model for mineral exploration** (EyeClimate project). The goal is to assess, validate, and visualize public subsurface datasets for pretraining a model that combines seismic, geochemical, and remote sensing data.

Recommended three-layer dataset strategy (from `docs/`):
1. **CMMI** — mineral prospectivity at regional scale (highest exploration relevance)
2. **CMiO** — ore-system geochemistry
3. **SeisDARE** — subsurface seismic sensing (SOTIEL as primary, IBERSEIS as supporting)

## Environment Setup

Uses **uv** as the package manager with a locked dependency file.

```bash
# Activate virtual environment (Windows Git Bash)
source .venv/Scripts/activate

# Install dependencies with uv
uv sync

# Or install with pip
pip install -e .
```

**Python >= 3.10 required.** Key dependencies: numpy, pandas, matplotlib, seaborn, scikit-learn, scipy, openpyxl, xlrd.

## Running Scripts

All scripts are standalone and run from the repo root. Each script defines `ROOT = Path(__file__).resolve().parent.parent` for path resolution.

```bash
python scripts/das_visualize.py                  # DAS event classification dataset
python scripts/inspect_seisdare_segy.py          # SeisDARE/SOTIEL SEG-Y inspection
python scripts/inspect_seisdare_geometry.py      # SeisDARE geometry validation
python scripts/inspect_iberseis_ni.py            # IBERSEIS normal-incidence (mig/stk)
python scripts/inspect_iberseis_wa_geometry.py   # IBERSEIS wide-angle geometry ASCII
python scripts/inspect_iberseis_wa_segy.py       # IBERSEIS wide-angle SEG-Y
python scripts/make_seisdare_summary_slide.py    # Composite presentation slide
```

There are no tests, linters, or build steps configured.

## Architecture

### Script Pattern
Each `inspect_*.py` script follows the same structure:
1. Parse binary/ASCII data (SEG-Y headers using `struct`, Excel via pandas, ASCII manually)
2. Validate geometry or signal statistics
3. Write PNG visualizations + a `README.md` summary to the dataset's `outputs/` directory

Scripts are batch/one-time inspection tools, not a reusable library. Avoid introducing shared modules unless multiple scripts genuinely need them.

### SEG-Y Parsing
All seismic scripts parse SEG-Y manually using `struct.unpack` — there is no segyio dependency. Key details:
- Binary header at byte 3200–3600 (format code, sample interval, samples per trace)
- Trace headers are 240 bytes each; key fields hard-coded by byte offset
- IBERSEIS files use **IBM float format** (format code 1) requiring a custom `ibm_to_ieee()` conversion; SeisDARE uses IEEE float (format code 5)

### Directory Structure

```
datasets/
├── das/
│   ├── raw/          DAS_safe/ (labeled XLSX + CSVs), DAS_extracted/, DAS.zip
│   └── outputs/      PNG visualizations + README.md
└── seisdare/
    ├── sotiel/
    │   ├── raw/      seisdare_data/ (SEG-Y), geometry XLS files
    │   └── outputs/  PNG visualizations + README.md + README_geometry.md
    └── iberseis/
        ├── raw/      iberseis_data/ (SEG-Y), iberseis_meta/
        ├── ni_outputs/   NI migrated/stack inspection outputs
        └── wa_outputs/   WA inspection outputs
docs/
├── Subsurface Dataset Research Brief.md   project scope + dataset strategy
├── TASKS.md                               active task checklist
├── datasets/                              per-dataset evaluation docs
└── others/                               background context docs
scripts/                                   inspection + visualization scripts
```

### Key Dataset Facts (from prior inspection)
- **DAS:** 901 train / 180 test samples, 3 classes (background / hammering / vehicle), balanced
- **SeisDARE SOTIEL:** 30,038 traces, 5001 samples/trace, 4 ms sample interval, IEEE float, CC BY 4.0
- **IBERSEIS NI:** Migrated + stacked products, IBM float format, Iberian Pyrite Belt
- **IBERSEIS WA:** 1.08 GB, 9 shots, 9,010 traces, offsets up to 268.8 km, shot points at mining sites (Rio Tinto, Minas Cala)

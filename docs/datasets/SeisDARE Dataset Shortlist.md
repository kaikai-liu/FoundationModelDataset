# SeisDARE Dataset Shortlist

## Goal
Rank the SeisDARE datasets by relevance to **subsurface mining detection** and near-term value for EyeClimate.

---

## Ranking

### 1. SOTIEL
- **Why it ranks first:** explicitly focused on **mining exploration**
- **Type:** HR normal incidence
- **Setting:** onshore, Iberian Pyrite Belt
- **Best role:** mining-specific anchor dataset

### 2. IBERSEIS
- **Why it ranks high:** strong hard-rock crustal imaging in the Iberian Massif
- **Type:** DSS normal incidence + wide angle
- **Setting:** onshore
- **Best role:** structural and regional subsurface context

### 3. ALCUDIA
- **Why it ranks high:** onshore crustal dataset in geologically relevant Iberian zones
- **Type:** DSS normal incidence + wide angle
- **Setting:** onshore
- **Best role:** supporting structural dataset for transfer learning

### 4. CIMDEF
- **Why it is useful:** onshore wide-angle dataset with regional structural relevance
- **Type:** DSS wide angle
- **Setting:** onshore
- **Best role:** complementary subsurface dataset

### 5. HONTOMÍN
- **Why it is still useful:** high-resolution onshore seismic dataset
- **Type:** HR normal incidence
- **Setting:** CO2 storage site characterization
- **Best role:** method testing and seismic ML prototyping

---

## Lower priority datasets for this use case
- **VICANAS** — nuclear waste disposal site characterization
- **INTERGEO** — fault / seismicity study
- **MARCONI / IAM / ESCI** — important geophysics, but less directly relevant to mining detection
- **SIMA / RIFSIS** — valuable crustal studies, but less directly tied to mining exploration

---

## Recommended use
- **SOTIEL** = mining-specific subsurface anchor
- **IBERSEIS + ALCUDIA + CIMDEF** = regional / structural support datasets
- **HONTOMÍN** = high-resolution seismic method transfer dataset

---

## Recommendation
If we stay inside SeisDARE, the best next dataset to inspect is:

## **IBERSEIS**

Why:
- onshore
- structurally rich
- closer to hard-rock geology than offshore margin datasets
- strong complement to SOTIEL

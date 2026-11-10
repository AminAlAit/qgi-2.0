# QGI 2.0 — Soft Power & Institutional Index Engine (2023)

**Generation 2.0 of 7.0** · Originally developed under **`AminAlAit/trojan-2.0`** · **Current Production Platform:** [**`AminAlAit/qgi` (QGI 7.0)**](https://github.com/AminAlAit/qgi) ([qgintelligence.com](https://qgintelligence.com))

---

## Overview

Built in late 2023 as **`trojan-2.0`**, **QGI 2.0** was the first complete rewrite of the original `qgi-1.0` (`trojan`) script collection. After hitting maintenance limits with flat scripts and pickled dictionaries in 1.0, this generation introduced:
1. A formal object-oriented `Index` domain model (`src/classes/index.py`) capable of representing multi-dimensional institutional, economic, and Soft Power indices across countries.
2. A modular **ETLP (Extract-Transform-Load-Patternize)** pipeline (`src/etlp/` and `src/stages/patternize/`).
3. Matrix Profile motif discovery experiments (`nbs/stumpy_explorer.ipynb`) using the `STUMPY` time-series library to detect recurring sub-sequence regimes without pre-specifying fixed window lengths.
4. Reproducible dependency management via **Poetry** (`pyproject.toml`, `poetry.lock`).

---

## Architecture & Key Modules

- **`src/classes/index.py` (`Index` Domain Class):**
  - Encapsulated indicator coverage checks (`is_comprehensive()`), temporal completeness filtering, and `get_patternizable_indexes()` to automatically filter raw datasets down to panels dense enough for bilateral comparison.
- **`src/etlp/etlp.py` (ETLP Pipeline):**
  - Standardized ingestion and panel harmonization before passing normalized country-year matrices to the patternizer stage.
- **`src/stages/patternize/patternize.py` (`patternize_handler`):**
  - Decoupled pattern extraction from UI rendering so pattern runs could be executed in batch mode via `config/` YAML/JSON parameters.
- **`nbs/stumpy_explorer.ipynb` (Matrix Profile Research):**
  - Evaluated fast Z-normalized Euclidean distance matrix profiles (`stumpy.stump`) against rank-correlation approaches for multi-decade country series.
- **`streamlit/`:**
  - Lightweight Streamlit interface wired to the `src/` package layout.

---

## Repository Structure

```text
qgi-2.0/
├── config/                        # Pipeline & index configuration definitions
├── data/                          # Raw & harmonized Soft Power / institutional panels
├── nbs/                           # Research notebooks (stumpy_explorer.ipynb)
├── src/
│   ├── classes/                   # Index OOP domain model (index.py)
│   ├── etlp/                      # Extract-Transform-Load-Patternize runner (etlp.py)
│   └── stages/patternize/         # Modular patternization engine (patternize.py)
├── streamlit/                     # Prototype Streamlit views
├── main.ipynb                     # End-to-end interactive pipeline runner
├── pyproject.toml                 # Poetry package & dependency specification
└── poetry.lock                    # Locked reproducible environment
```

---

## Why We Outgrew QGI 2.0

- **Single-Index Scope vs. Global Macro Catalog:** `trojan-2.0` proved the ETLP architecture on curated institutional indices, but scaling to 1,400+ World Bank World Development Indicators (WDI) required a relational query layer and a multi-page analytical web app — leading directly to **QGI 3.0** (`qgi-streamlit`) in early 2024.

---

## QGI Generational Roadmap (`v1.0` → `v7.0`)

| Generation | Year | Repository | Original Name(s) | Architectural Milestone |
| :--- | :--- | :--- | :--- | :--- |
| **QGI 1.0** | 2023 | [`AminAlAit/qgi-1.0`](https://github.com/AminAlAit/qgi-1.0) | `trojan`, `trojan-streamlit` | Initial pairwise country correlation engine & first Streamlit UI |
| **QGI 2.0** *(Here)* | 2023 | **`AminAlAit/qgi-2.0`** | `trojan-2.0` | Poetry-packaged ETLP pipeline, `Index` OOP hierarchy & STUMPY matrix profiles |
| **QGI 3.0** | 2024 | [`AminAlAit/qgi-3.0`](https://github.com/AminAlAit/qgi-3.0) | `qgi` (2024), `qgi-streamlit`, `qgi-local` | Multi-page Streamlit analytical terminal backed by relational SQLite/MySQL queries |
| **QGI 4.0** | 2025 | [`AminAlAit/qgi-4.0`](https://github.com/AminAlAit/qgi-4.0) | `qgi-4.0` | Formalization of the SCDI metric (Spearman + Cross-Correlation + DTW), Pipelines A–E & X Bot v1 |
| **QGI 5.0** | 2025–2026 | [`AminAlAit/qgi-5.0`](https://github.com/AminAlAit/qgi-5.0) | `qgi-pipeline-a/b/c` | First AWS cloud migration: Serverless Lambda ETL, Dockerized AWS Batch FFT worker & Athena CTAS |
| **QGI 6.0** | 2026 | `AminAlAit/qgi-6.0` | `qgi-aws-tf`, `qgi-infra`, `qgi-pipeline`, `qgi-data`, `qgi-ml`, `qgi-frontend`, `qgi-docs` | 4-account AWS Organization (14.3B FFT correlations), 42-model Trajectory Engine & Next.js 16 terminal |
| **QGI 7.0** *(Active)* | 2026–Present | [**`AminAlAit/qgi`**](https://github.com/AminAlAit/qgi) | `qgi`, `qgi-docs` | Unified production monorepo & live analytical terminal at [qgintelligence.com](https://qgintelligence.com) |
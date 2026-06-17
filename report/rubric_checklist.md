# Rubric Checklist

Scoring rubric for the final project with evidence mapping.

---

## Problem Understanding and Source Selection — 10

- **Status:** PASS
- **Where it appears:** `SOURCE_SELECTION.md`; Notebook Section 1; Report Section 1
- **Evidence:** Clear IDS problem definition, NSL-KDD dataset, article link, inline-code source note, reproducibility risks documented
- **What is still weak:** Original author did not publish a dedicated GitHub repository
- **Estimated points:** 9/10

---

## Summary Quality — 15

- **Status:** PASS
- **Where it appears:** Notebook Section 1; Report Sections 1 and 7; `report/executive_summary.md`; `README.md`
- **Evidence:** Source, dataset, methodology, and claims summarized in own words with links; secondary GitHub clearly labeled
- **What is still weak:** None major
- **Estimated points:** 14/15

---

## Critical Evaluation of the Author's Claims — 20

- **Status:** PASS
- **Where it appears:** Notebook Section 8; Report Section 2; PDF Table 1; `results/tables/claim_evaluation.csv`
- **Evidence:** Five claims compared against author-split and official-test reproduction results; supported/partial/not supported judgments with explanations
- **What is still weak:** FastAPI severity-scoring claims were not fully re-implemented
- **Estimated points:** 18/20

---

## Feature Engineering Analysis — 10

- **Status:** PASS
- **Where it appears:** Notebook Section 4; Report Section 3; `src/preprocessing.py`; `results/tables/redundant_feature_report.json`
- **Evidence:** Encoding, scaling, SMOTE, redundancy detection, leakage-safe fit on training data, cybersecurity interpretation in report
- **What is still weak:** No ablation study removing SMOTE or correlated features
- **Estimated points:** 9/10

---

## Exploratory Data Analysis — 15

- **Status:** PASS
- **Where it appears:** Notebook Section 3; Report Section 5.2; `src/eda.py`; `results/figures/` and `results/tables/`
- **Evidence:** Distributions, missing values, outliers, class imbalance, crosstab, Spearman correlation with method justification; temporal limitation documented
- **What is still weak:** No temporal analysis possible because NSL-KDD has no time column (explicitly documented)
- **Estimated points:** 14/15

---

## Model Training and Comparison — 15

- **Status:** PASS
- **Where it appears:** Notebook Section 5; Report Section 5.3; `src/models.py`; `results/tables/model_comparison.csv`
- **Evidence:** Logistic Regression baseline, Random Forest, Isolation Forest; fixed random seed; official and author splits
- **What is still weak:** No hyperparameter search beyond tutorial defaults
- **Estimated points:** 14/15

---

## Evaluation and Error Analysis — 10

- **Status:** PASS
- **Where it appears:** Notebook Sections 6–7; Report Sections 5.4–5.8; PDF Tables 3–4; `src/evaluation.py`; `src/error_analysis.py`
- **Evidence:** Full metric formulas, cybersecurity interpretation, confusion matrices, FP/FN examples, error-pattern summary
- **What is still weak:** Threshold tuning for operational recall targets not explored
- **Estimated points:** 9/10

---

## Code Quality and Software Engineering — 5

- **Status:** PASS
- **Where it appears:** `src/` modules, `run_pipeline.py`, `scripts/`, notebook imports
- **Evidence:** Modular code, fixed seeds, relative output paths in notebook/report, outputs saved under `results/`
- **What is still weak:** Course PDFs excluded via `.gitignore`; dataset must be downloaded before run
- **Estimated points:** 5/5

---

## Total Estimated Score

**93 / 100**

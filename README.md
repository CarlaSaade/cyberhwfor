# Network Intrusion Detection — Reproduction & Critical Evaluation

University final project for **Data Science in Cyber**. This repository reproduces and critically evaluates a published intrusion detection tutorial using the NSL-KDD dataset.

## Selected source

- **Primary article:** [AI-Powered Cyber Security Part 2: Building an Intrusion Detection System with Python and Scikit-learn](https://chandanbhagat.com.np/ai-powered-cyber-security-part-2-building-an-intru/)
- **Original GitHub repository:** *Not provided by the article author.* The tutorial publishes complete Python code inline in the blog post.
- **Secondary reference only (similar NSL-KDD IDS project):** https://github.com/akinyeraakintunde/network-intrusion-detection-ml
- **Dataset:** [NSL-KDD](https://www.unb.ca/cic/datasets/nsl.html)

See `SOURCE_SELECTION.md` for full source justification and reproducibility notes.

## Dataset files (not committed to Git)

The NSL-KDD files are large and listed in `.gitignore`. Download them before running anything:

```bash
python scripts/download_data.py
```

This creates:

- `data/KDDTrain+.txt`
- `data/KDDTest+.txt`

Mirror used by the download script: https://github.com/jmnwong/NSL-KDD-Dataset

## Main findings (official NSL-KDD test set)

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|-------|----------|-----------|--------|-----|---------|
| Logistic Regression | 0.7539 | 0.9167 | 0.6243 | 0.7428 | 0.7940 |
| Random Forest (author-style) | 0.7757 | 0.9689 | 0.6260 | 0.7606 | 0.9660 |
| Isolation Forest | 0.7884 | 0.9365 | 0.6740 | 0.7839 | N/A |

On the **author's random split of the training file**, Random Forest reached accuracy **0.9990** and ROC-AUC **0.9999**, closely matching the blog's reported values. The large gap to the official test set supports the author's own caveat that real-world performance is lower.

## Repository structure

```
project_root/
├── README.md
├── SOURCE_SELECTION.md
├── requirements.txt
├── run_pipeline.py
├── notebooks/final_project.ipynb
├── scripts/
│   ├── download_data.py
│   ├── build_notebook.py
│   └── generate_report_pdf.py
├── src/
├── data/                  # dataset downloaded locally (gitignored)
├── results/figures/
├── results/tables/
├── results/metrics/
└── report/
    ├── report_content.md
    ├── executive_summary.md
    ├── rubric_checklist.md
    └── final_report.pdf
```

## Installation

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
python scripts/download_data.py
```

## How to run the notebook

```bash
jupyter notebook notebooks/final_project.ipynb
```

Run all cells from top to bottom. The notebook imports reusable functions from `src/` and writes outputs to `results/`.

## Exact reproduction commands

```bash
pip install -r requirements.txt
python scripts/download_data.py
python -m py_compile run_pipeline.py scripts/download_data.py scripts/build_notebook.py scripts/generate_report_pdf.py src/*.py
python run_pipeline.py
python scripts/build_notebook.py
jupyter nbconvert --to notebook --execute notebooks/final_project.ipynb --output final_project.ipynb
python scripts/generate_report_pdf.py
```

Generated artifacts:

- Metrics and tables under `results/`
- Written report under `report/report_content.md`
- PDF report under `report/final_report.pdf`

## Recommendation

The tutorial is a useful educational baseline, but high accuracy on a random training-file split is **not** sufficient evidence for production IDS deployment. Evaluate on the official NSL-KDD test split and prioritize attack recall, F2, and MCC over accuracy alone.

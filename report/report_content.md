# Final Report — Network Intrusion Detection Reproduction

## 1. Summary of the Source

This project critically evaluates a published cybersecurity data-science tutorial on **network intrusion detection (NIDS)**:

**AI-Powered Cyber Security Part 2: Building an Intrusion Detection System with Python and Scikit-learn**  
Author: Chandan Bhagat  
Link: https://chandanbhagat.com.np/ai-powered-cyber-security-part-2-building-an-intru/

The article defines a clear cybersecurity problem: detect malicious network connections using machine-learning models trained on connection-level features from the **NSL-KDD** benchmark. The proposed solution includes:

- preprocessing with `StandardScaler` and one-hot encoding,
- **SMOTE** for class imbalance,
- a **Random Forest** classifier for labeled attack detection,
- an **Isolation Forest** trained on normal traffic for anomaly scoring,
- a FastAPI deployment example with severity scoring.

The author reports near-perfect performance on a random 80/20 split of the training file (accuracy ≈ 0.99, ROC-AUC ≈ 0.9987) and explicitly warns that real-world performance will be lower.

**Repository note:** the original article provides complete inline Python code but **does not link a dedicated GitHub repository**. A separate reference repository with a similar NSL-KDD pipeline (https://github.com/akinyeraakintunde/network-intrusion-detection-ml) is used only as a **secondary engineering reference**, not as the primary evaluated source.

## 2. Critical Evaluation

| Claim | Author's Evidence | Our Reproduction Evidence | Supported? | Explanation |
|-------|-------------------|---------------------------|------------|-------------|
| RF reaches ~99% precision/recall | classification_report in blog (~0.99 for both classes) | Author split: acc=0.9990, recall=0.9983; Official test: acc=0.7757, recall=0.6260 | Partially | High metrics reproduce on the tutorial split but not on the official NSL-KDD test set |
| ROC-AUC ≈ 0.9987 | Printed tutorial output | Author split AUC=0.9999; Official test AUC=0.9660 | Partially | Very high AUC is split-dependent |
| Training under 5 minutes | Stated in article | Pipeline completed in a few minutes on CPU | Supported | Runtime claim is realistic for NSL-KDD |
| Isolation Forest helps unknown threats | Trains IF on normal traffic and combines with RF in API | Official test IF recall=0.6740 vs RF recall=0.6260 | Partially | IF improves recall slightly but still misses many attacks |
| Real-world performance is lower | Explicit caveat in blog | Official test accuracy 0.7757 vs author split 0.9990 | Supported | Our official-test gap confirms the author's warning |

**Methodology assessment:** preprocessing and SMOTE are appropriate teaching steps, but evaluating only a random split of the training file overstates generalization. The conclusion that ML IDS can work is directionally reasonable, but the numeric claims are not sufficient for production decisions without official benchmarking.

See also: `results/tables/claim_evaluation.csv`

## 3. Feature Engineering Analysis

We applied the same core transformations described by the author, fitting all preprocessing on training data only to avoid leakage:

1. **One-hot encoding** for `protocol_type`, `service`, and `flag` — converts categorical connection metadata into model-ready numeric inputs.
2. **StandardScaler** for numeric connection statistics — prevents high-magnitude byte-count columns from dominating tree splits.
3. **SMOTE** on encoded training features only — synthesizes minority-class examples to improve attack representation during training.
4. **Redundancy checks** identified constant column `num_outbound_cmds` and highly correlated error-rate pairs (`serror_rate` / `srv_serror_rate`, `rerror_rate` / `srv_rerror_rate`).

**Why these steps matter in cybersecurity:** IDS features mix categorical protocol metadata with highly skewed numeric traffic statistics. Without scaling and encoding, models may overweight arbitrary numeric magnitude rather than attack-relevant behavior. SMOTE mitigates under-representation of attack patterns during training, although it cannot fix dataset shift between train and official test splits.

**Outcome:** these transformations improved trainability and interpretability, but did not eliminate poor attack recall on the official test set. That suggests the main limitation is dataset shift and class overlap in NSL-KDD's official split, not only preprocessing choices.

Reference: `results/tables/redundant_feature_report.json`

## 4. Reproducibility Analysis

| Question | Answer |
|----------|--------|
| Did the original code run? | Yes — core training logic is reproducible from inline blog code |
| Were dependencies clear? | Mostly (`scikit-learn`, `imbalanced-learn`, `pandas`) |
| Were all files available? | No — NSL-KDD must be downloaded separately via `scripts/download_data.py` |
| Was dataset version clear? | Yes (`KDDTrain+.txt`, `KDDTest+.txt`) |
| Hidden preprocessing steps? | No major hidden steps found |
| Did we need to change anything? | Added official test evaluation for realistic benchmarking |
| Could a grader reproduce? | Yes via `requirements.txt`, download script, notebook, and pipeline |

**Overall reproducibility judgment:** **Moderately high** for the tutorial workflow itself; **moderate** for the article's headline performance claims because split choice dominates the results.

## 5. Experimental Results

### 5.1 Data summary

- Training rows: **125,973**
- Official test rows: **22,544**
- Training class distribution: **67,343 normal / 58,630 attack** (53.5% normal)

### 5.2 Exploratory Data Analysis findings

These findings come from the notebook and `src/eda.py` outputs saved under `results/figures/` and `results/tables/`.

**Class imbalance:** the training set is moderately imbalanced (53.5% normal, 46.5% attack). This is not extreme, but accuracy can still hide poor attack detection if not examined carefully.

**Missing values:** zero missing values were found across all columns in both train and test files (`results/tables/train_column_overview.csv`).

**Duplicate rows:** none detected in the training file.

**Constant / irrelevant columns:** `num_outbound_cmds` is constant and non-informative; `label`, `difficulty`, and derived `attack_category` are excluded from modeling.

**Outlier analysis:** `duration`, `src_bytes`, `dst_bytes`, and `count` show long-tailed distributions with extreme values (Figure 1: `results/figures/train_outlier_boxplots.png`). This supports using Spearman rather than Pearson correlation.

**Crosstab analysis:** attacks are concentrated in specific services such as telnet, ftp, http, and private network flows (Figure/table: `results/figures/train_service_attack_crosstab.png`, `results/tables/train_service_attack_crosstab.csv`).

**Spearman correlation:** strong monotonic links among error-rate features indicate redundant signals from scanning and flooding behavior (Figure 2: `results/figures/train_spearman_correlation.png`). This is useful for redundancy detection, not causal inference.

**Why no temporal analysis:** NSL-KDD contains no timestamp or session-order field. Each row is an independent connection record, so time-series or drift-over-time analysis is not applicable.

**Sampling realism:** NSL-KDD is a classic benchmark but dated; attack types and traffic mixes may not reflect modern enterprise networks.

### 5.3 Models trained

1. Logistic Regression (baseline)
2. Random Forest (author-style supervised model)
3. Isolation Forest (author-style anomaly model)

### 5.4 Official NSL-KDD test metrics

| Model | Accuracy | Precision | Recall | F1 | F2 | MCC | ROC-AUC |
|-------|----------|-----------|--------|-----|-----|-----|---------|
| Logistic Regression | 0.7539 | 0.9167 | 0.6243 | 0.7428 | 0.6669 | 0.5583 | 0.7940 |
| Random Forest | 0.7757 | 0.9689 | 0.6260 | 0.7606 | 0.6737 | 0.6156 | 0.9660 |
| Isolation Forest | 0.7884 | 0.9365 | 0.6740 | 0.7839 | 0.7141 | 0.6178 | N/A |

Reference: `results/tables/model_comparison.csv`

### 5.5 Metric definitions and cybersecurity interpretation

| Metric | Formula (binary) | What it measures | Cybersecurity meaning in IDS |
|--------|------------------|------------------|------------------------------|
| Accuracy | (TP + TN) / N | Overall correctness | Can look acceptable while many attacks are missed |
| Precision | TP / (TP + FP) | Alert quality among predicted attacks | False positives create alert fatigue |
| Recall | TP / (TP + FN) | Attack capture rate | False negatives allow intrusions to continue |
| F1 | 2PR / (P + R) | Balance of precision and recall | Useful when both alert load and misses matter |
| F2 | 5PR / (4P + R) | Recall-weighted F-score | Prioritizes catching attacks over alert purity |
| MCC | (TP·TN − FP·FN) / sqrt(...) | Balanced correlation score | More reliable than accuracy under imbalance |
| ROC-AUC | Area under TPR vs FPR | Threshold-free ranking quality | Strong ranking does not guarantee operational recall at default threshold |
| Confusion Matrix | [[TN, FP], [FN, TP]] | Counts of each error type | Essential for IDS operational review |

**False positives in IDS:** normal traffic flagged as attack. Example from our Random Forest errors: UDP `private` service flows with unusual host-rate statistics but true label `normal` (`results/tables/false_positive_examples.csv`).

**False negatives in IDS:** attacks flagged as normal. Example: TCP `telnet` / `guess_passwd` and `mscan` flows with subtle feature values predicted as normal (`results/tables/false_negative_examples.csv`).

**Which error is more dangerous here?** False negatives are generally more dangerous because they allow compromise to proceed. False positives still matter because they consume analyst capacity and can hide true incidents in noisy alert streams.

**Random Forest official confusion matrix:** TN=9453, FP=258, FN=4799, TP=8034 (`results/tables/confusion_matrix_official_random_forest.csv`). High precision (0.9689) coexists with 4,799 missed attacks.

### 5.6 Author-style random split (Random Forest)

- Accuracy: **0.9990**
- Recall: **0.9983**
- ROC-AUC: **0.9999**

Reference: `results/tables/author_split_model_comparison.csv`

This closely matches the blog's reported values and demonstrates how split choice inflates headline metrics.

### 5.7 Figures and tables

- Figure 1: `results/figures/train_outlier_boxplots.png`
- Figure 2: `results/figures/train_spearman_correlation.png`
- Figure 3: `results/figures/confusion_matrix_official_random_forest.png`
- Figure 4: `results/figures/roc_curve_official_random_forest.png`
- Table: `results/tables/model_comparison.csv`
- Table: `results/tables/claim_evaluation.csv`
- Table: `results/tables/error_examples.csv`
- Table: `results/tables/error_pattern_summary.csv`

### 5.8 Error analysis summary

Misclassifications are concentrated on **TCP** flows and on services **telnet**, **pop_3**, **private**, **ftp**, and **http**. Common flags in errors include **SF**, **RSTO**, **REJ**, and **S0**. This suggests the model learns broad traffic-family patterns but struggles with low-volume or rare attack classes that resemble legitimate administrative traffic.

## 6. Conclusions

- The tutorial is **educationally strong** and technically reproducible on the author's chosen split.
- The headline **99% metrics are supported only on the tutorial's random split**, not on the official NSL-KDD test set.
- The author's caution about real-world degradation is **validated**.
- For cybersecurity deployment, prioritize **attack recall, F2, and MCC** over accuracy.
- Recommended use: **prototype / teaching baseline**, not production IDS by itself.

## 7. Executive Summary

We reproduced a published NSL-KDD intrusion detection tutorial combining Random Forest, SMOTE, and Isolation Forest. On the author's random training-file split, Random Forest achieved accuracy **0.9990** and ROC-AUC **0.9999**, matching the blog's near-perfect report. On the official NSL-KDD test set, the same model dropped to accuracy **0.7757** and attack recall **0.6260**, while Isolation Forest achieved the highest F1 (**0.7839**) and recall (**0.6740**). The author's warning that benchmark numbers overstate real-world performance is supported. The most important insight is that high accuracy alone is insufficient in cybersecurity classification; split design and attack recall must be scrutinized before trusting claims.

## 8. Summing It Up

This project demonstrates that published cybersecurity ML tutorials can look excellent under one evaluation protocol and much weaker under a harder, standard benchmark. The original solution's strengths are clarity, practical preprocessing, and an honest caveat about deployment. Its weaknesses are split choice, lack of official test reporting, and insufficient emphasis on attack recall. Future improvements should include per-attack-type evaluation, threshold tuning for operational recall targets, and testing on newer intrusion datasets.

**Final recommendation:** adopt the pipeline as a learning exercise, but require official benchmark evaluation and security-oriented metrics before treating results as deployment evidence.

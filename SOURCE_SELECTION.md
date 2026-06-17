# Selected Source for Final Project

## Selected article / blog / tutorial

**Title:** AI-Powered Cyber Security Part 2: Building an Intrusion Detection System with Python and Scikit-learn

**Author:** Chandan Bhagat

**Article link:** https://chandanbhagat.com.np/ai-powered-cyber-security-part-2-building-an-intru/

## Original GitHub repository link

**Not provided by the original author.** The tutorial publishes complete Python code inline in the blog post (data loader, feature engineering, training script, and FastAPI service).

**Reference implementation (similar NSL-KDD IDS project):** https://github.com/akinyeraakintunde/network-intrusion-detection-ml

We use this repository only as a secondary reference for engineering patterns; the primary claims evaluated here come from the blog post.

## Dataset source link

- Official NSL-KDD page: https://www.unb.ca/cic/datasets/nsl.html
- Files used in this reproduction: `KDDTrain+.txt`, `KDDTest+.txt`
- Download mirror used locally: https://github.com/jmnwong/NSL-KDD-Dataset

## Cybersecurity problem

**Network Intrusion Detection (NIDS):** classify network connections as normal or malicious based on connection-level features extracted from traffic logs.

## Why the problem matters

Organizations need automated detection beyond static signatures because modern attacks change quickly and may not match known patterns. Missing attacks can lead to data breaches; excessive false alerts reduce analyst effectiveness.

## Proposed solution

The author proposes a hybrid IDS pipeline:

1. Preprocess NSL-KDD features (scale numeric fields, encode categorical protocol/service/flag fields)
2. Apply SMOTE to address class imbalance in the training split
3. Train a Random Forest classifier for labeled attack detection
4. Train an Isolation Forest on normal traffic for anomaly scoring
5. Expose both models through a FastAPI endpoint with severity scoring

## Dataset used

**NSL-KDD**

- Training file: 125,973 connection records
- Official test file: 22,544 connection records
- 41 input features + attack label + difficulty score
- Binary task in our reproduction: normal (0) vs attack (1)

## Model / methodology used

- Preprocessing: `StandardScaler` + `OneHotEncoder` via `ColumnTransformer`
- Imbalance handling: SMOTE (`imblearn`)
- Baseline reproduced in our project: Logistic Regression
- Author's supervised model: Random Forest (`n_estimators=200`, `max_depth=20`, `class_weight='balanced'`)
- Author's unsupervised model: Isolation Forest trained on normal connections only
- Evaluation in article: random 80/20 split on `KDDTrain+.txt`
- Additional evaluation in our project: official `KDDTest+.txt`

## Main claims made by the original author

1. Random Forest achieves about 99% precision and recall on held-out data from the training file
2. ROC-AUC is approximately 0.9987
3. Training completes in under 5 minutes on a laptop CPU
4. Isolation Forest complements Random Forest for detecting unknown threats
5. Real-world performance will be lower than the benchmark numbers shown in the tutorial

## Why this source satisfies the assignment requirements

| Requirement | How this source satisfies it |
|-------------|-------------------------------|
| Clearly defines a cybersecurity problem | Yes — network intrusion detection |
| Proposes a solution | Yes — SMOTE + Random Forest + Isolation Forest + API |
| Includes implementation or GitHub repository | Yes — full inline implementation in the article |
| Provides dataset or enough information to reproduce | Yes — NSL-KDD with explicit column list and training code |
| Practical to run locally | Yes — runs on CPU with open-source Python libraries |

## Reproducibility risks

1. **No standalone repository** — code must be copied from the blog post
2. **Dataset not bundled** — NSL-KDD must be downloaded separately
3. **Split choice affects metrics heavily** — the article evaluates a random split of the training file, not the official NSL-KDD test set
4. **Some tutorial snippets are illustrative** — FastAPI/Docker sections are not fully packaged as a repo
5. **Environment versions** — exact metric values may vary slightly across library versions, though we reproduced the article's near-99% results on the same split setup

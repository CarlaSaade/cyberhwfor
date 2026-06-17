# Executive Summary

This project reproduced a published NSL-KDD intrusion detection tutorial that combines Random Forest,
SMOTE, and Isolation Forest. Using the author's random train/test split, we matched the blog's near-99%
metrics (accuracy 0.9990, ROC-AUC 0.9999). On the official NSL-KDD test set, performance dropped to
accuracy 0.7757 and attack recall 0.6260 for Random Forest, confirming that benchmark claims are highly
split-dependent. The author's warning about real-world degradation is supported. For cybersecurity use,
attack recall and MCC are more informative than accuracy. The approach is useful for learning and prototyping,
but not sufficient alone for production IDS deployment without rigorous official benchmarking and error analysis.

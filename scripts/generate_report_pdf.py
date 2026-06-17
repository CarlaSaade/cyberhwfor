"""Generate a professional PDF report for the final project."""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PDF = PROJECT_ROOT / "report" / "final_report.pdf"
METRICS_PATH = PROJECT_ROOT / "results" / "metrics" / "run_summary.json"
FIGURES_DIR = PROJECT_ROOT / "results" / "figures"


def load_metrics() -> dict:
    with METRICS_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def fmt(value: float | None, digits: int = 4) -> str:
    if value is None:
        return "N/A"
    return f"{value:.{digits}f}"


def escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "DocTitle",
            parent=styles["Title"],
            fontSize=20,
            leading=24,
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "subtitle": ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#444444"),
            spaceAfter=20,
        ),
        "h1": ParagraphStyle(
            "SectionH1",
            parent=styles["Heading1"],
            fontSize=14,
            leading=18,
            spaceBefore=14,
            spaceAfter=8,
            textColor=colors.HexColor("#1F3A5F"),
        ),
        "h2": ParagraphStyle(
            "SectionH2",
            parent=styles["Heading2"],
            fontSize=11,
            leading=14,
            spaceBefore=10,
            spaceAfter=6,
            textColor=colors.HexColor("#2E5984"),
        ),
        "body": ParagraphStyle(
            "BodyJustified",
            parent=styles["BodyText"],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=styles["BodyText"],
            fontSize=10,
            leading=14,
            leftIndent=14,
            bulletIndent=0,
            spaceAfter=4,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
        ),
        "table_cell": ParagraphStyle(
            "TableCell",
            parent=styles["BodyText"],
            fontSize=8,
            leading=10,
        ),
        "caption": ParagraphStyle(
            "Caption",
            parent=styles["BodyText"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#555555"),
            spaceAfter=10,
        ),
    }


def make_table(headers: list[str], rows: list[list[str]], col_widths: list[float]) -> Table:
    styles = build_styles()
    wrapped_headers = [Paragraph(escape(header), styles["table_header"]) for header in headers]
    wrapped_rows = [
        [Paragraph(escape(str(cell)), styles["table_cell"]) for cell in row]
        for row in rows
    ]
    data = [wrapped_headers] + wrapped_rows
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF7")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1F3A5F")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def add_section(story: list, styles: dict, title: str, paragraphs: list[str]) -> None:
    story.append(Paragraph(escape(title), styles["h1"]))
    for paragraph in paragraphs:
        story.append(Paragraph(escape(paragraph), styles["body"]))


def add_bullets(story: list, styles: dict, items: list[str]) -> None:
    for item in items:
        story.append(Paragraph(f"• {escape(item)}", styles["bullet"]))


def add_figure(story: list, styles: dict, path: Path, caption: str, width: float = 15 * cm) -> None:
    if path.exists():
        img = Image(str(path), width=width, height=width * 0.55)
        story.append(img)
        story.append(Paragraph(escape(caption), styles["caption"]))


def build_pdf() -> None:
    metrics = load_metrics()
    official = metrics["official_test_metrics"]
    author_rf = metrics["author_split_random_forest_metrics"]
    styles = build_styles()
    story: list = []

    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="Network Intrusion Detection Reproduction Report",
        author="Data Science in Cyber Final Project",
    )

    story.append(Paragraph("Network Intrusion Detection", styles["title"]))
    story.append(Paragraph("Reproduction and Critical Evaluation Report", styles["title"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(
        Paragraph(
            "Source: AI-Powered Cyber Security Part 2 — Building an Intrusion Detection System with Python and Scikit-learn",
            styles["subtitle"],
        )
    )
    story.append(
        Paragraph(
            "Dataset: NSL-KDD (KDDTrain+.txt, KDDTest+.txt) | All metrics loaded from results/metrics/run_summary.json",
            styles["subtitle"],
        )
    )
    story.append(PageBreak())

    add_section(
        story,
        styles,
        "1. Summary of the Source",
        [
            "This project critically evaluates a published cybersecurity data-science tutorial on network intrusion detection (NIDS). "
            "The selected article explains how to build an IDS using the NSL-KDD benchmark with scikit-learn.",
            "The author proposes preprocessing (scaling and one-hot encoding), SMOTE for class imbalance, a Random Forest classifier "
            "for labeled attack detection, an Isolation Forest trained on normal traffic for anomaly scoring, and a FastAPI deployment example.",
            "The article reports near-perfect performance on a random 80/20 split of the training file (accuracy about 0.99, ROC-AUC about 0.9987) "
            "and explicitly warns that real-world performance will be lower.",
            "Important limitation for reproducibility: the original article provides inline Python code but does not link a dedicated GitHub repository. "
            "A separate reference repository with a similar NSL-KDD pipeline is used only as a secondary engineering reference, not as the primary evaluated source.",
        ],
    )

    add_section(
        story,
        styles,
        "2. Critical Evaluation",
        [
            "We reproduced the author's core methodology and compared five published claims against our own experiments. "
            "Table 1 summarizes the claim-evaluation results using metrics from both the author-style split and the official NSL-KDD test set.",
        ],
    )
    story.append(
        make_table(
            ["Claim", "Author Evidence", "Our Evidence", "Supported?", "Explanation"],
            [
                [
                    "RF reaches ~99% precision/recall",
                    "classification_report in blog",
                    f"Author split acc={fmt(author_rf['accuracy'])}, recall={fmt(author_rf['recall'])}; "
                    f"Official test acc={fmt(official['random_forest']['accuracy'])}, recall={fmt(official['random_forest']['recall'])}",
                    "Partially",
                    "High metrics reproduce on the tutorial split but not on the official test set.",
                ],
                [
                    "ROC-AUC ≈ 0.9987",
                    "Printed tutorial output",
                    f"Author split AUC={fmt(author_rf['roc_auc'])}; Official test AUC={fmt(official['random_forest']['roc_auc'])}",
                    "Partially",
                    "Very high AUC is split-dependent.",
                ],
                [
                    "Training under 5 minutes",
                    "Stated in article",
                    "Pipeline completed in a few minutes on CPU",
                    "Supported",
                    "Runtime claim is realistic for NSL-KDD.",
                ],
                [
                    "Isolation Forest helps unknown threats",
                    "IF trained on normal traffic",
                    f"Official IF recall={fmt(official['isolation_forest']['recall'])} vs RF recall={fmt(official['random_forest']['recall'])}",
                    "Partially",
                    "IF improves recall slightly but still misses many attacks.",
                ],
                [
                    "Real-world performance is lower",
                    "Explicit caveat in blog",
                    f"Official acc={fmt(official['random_forest']['accuracy'])} vs author split acc={fmt(author_rf['accuracy'])}",
                    "Supported",
                    "Our official-test gap confirms the author's warning.",
                ],
            ],
            [2.6 * cm, 2.5 * cm, 4.0 * cm, 1.5 * cm, 4.8 * cm],
        )
    )
    story.append(Paragraph("Table 1. Critical evaluation of the author's claims.", styles["caption"]))
    add_section(
        story,
        styles,
        "",
        [
            "Methodology assessment: preprocessing and SMOTE are reasonable teaching steps, but evaluating only a random split of the training file overstates generalization. "
            "The article's conclusion that ML IDS can work is directionally reasonable, yet the headline numbers are not sufficient for production decisions without official benchmarking.",
        ],
    )

    add_section(
        story,
        styles,
        "3. Feature Engineering Analysis",
        [
            "We applied the same core transformations described by the author, fitting all preprocessing on training data only to avoid leakage.",
        ],
    )
    add_bullets(
        story,
        styles,
        [
            "One-hot encoding for protocol_type, service, and flag converts categorical connection metadata into model-ready numeric inputs.",
            "StandardScaler on numeric features prevents high-magnitude byte-count columns from dominating tree splits.",
            "SMOTE on encoded training features increases attack representation during training without touching the test set.",
            "Redundancy checks identified constant column num_outbound_cmds and highly correlated error-rate pairs "
            "(serror_rate/srv_serror_rate and rerror_rate/srv_rerror_rate).",
        ],
    )
    add_section(
        story,
        styles,
        "",
        [
            "These transformations improve trainability and interpretability, but they did not eliminate poor attack recall on the official test set. "
            "That suggests the main limitation is dataset shift and class overlap in the official NSL-KDD split, not only preprocessing choices.",
        ],
    )

    add_section(
        story,
        styles,
        "4. Reproducibility Analysis",
        [
            "Table 2 summarizes reproducibility findings for graders and future researchers.",
        ],
    )
    story.append(
        make_table(
            ["Question", "Finding"],
            [
                ["Did the original code run?", "Yes — core training logic is reproducible from inline blog code."],
                ["Were dependencies clear?", "Mostly — scikit-learn, imbalanced-learn, pandas are listed."],
                ["Were all files available?", "No — NSL-KDD must be downloaded separately via scripts/download_data.py."],
                ["Was dataset version clear?", "Yes — KDDTrain+.txt and KDDTest+.txt are standard NSL-KDD files."],
                ["Hidden preprocessing steps?", "No major hidden steps found."],
                ["Changes needed?", "We added official test evaluation for realistic benchmarking."],
                ["Could a grader reproduce?", "Yes — requirements.txt, download script, notebook, and pipeline."],
            ],
            [5.5 * cm, 11.0 * cm],
        )
    )
    story.append(Paragraph("Table 2. Reproducibility checklist.", styles["caption"]))
    add_section(
        story,
        styles,
        "",
        [
            "Overall reproducibility judgment: moderately high for the tutorial workflow itself; moderate for the article's headline performance claims because split choice dominates the results.",
        ],
    )

    add_section(
        story,
        styles,
        "5. Experimental Results",
        [
            f"Data: training rows = {metrics['train_rows']:,}; official test rows = {metrics['test_rows']:,}. "
            "Training class distribution: 67,343 normal and 58,630 attack (53.5% normal). "
            "Models trained: Logistic Regression (baseline), Random Forest (author-style supervised model), and Isolation Forest (author-style anomaly model).",
            "Exploratory Data Analysis findings are summarized below before the metric tables.",
        ],
    )

    add_section(story, styles, "5.1 Exploratory Data Analysis Findings", [])
    add_bullets(
        story,
        styles,
        [
            "Class imbalance: the training set is moderately imbalanced (53.5% normal, 46.5% attack), not extreme but still requiring careful metric choice.",
            "Missing values: zero missing values were found across all 43 columns in both train and test files.",
            "Duplicate rows: none detected in the training file.",
            "Constant columns: num_outbound_cmds contains a single value and carries no discriminative information.",
            "Outliers: duration, src_bytes, dst_bytes, and count show long tails; boxplots are saved in Figure 1.",
            "Crosstab analysis: attacks are concentrated in specific services such as telnet, ftp, and private network flows (Table 3 reference in results/tables/train_service_attack_crosstab.csv).",
            "Spearman correlation: strong monotonic links among error-rate features indicate redundant signals from scanning and flooding behavior (Figure 2).",
            "Temporal analysis: not performed because NSL-KDD contains no timestamp or session-order field; each row is an independent connection record.",
        ],
    )
    add_figure(
        story,
        styles,
        FIGURES_DIR / "train_outlier_boxplots.png",
        "Figure 1. Outlier analysis for selected numeric features (results/figures/train_outlier_boxplots.png).",
        width=14 * cm,
    )
    add_figure(
        story,
        styles,
        FIGURES_DIR / "train_spearman_correlation.png",
        "Figure 2. Spearman correlation heatmap for numeric NSL-KDD features (results/figures/train_spearman_correlation.png).",
        width=14 * cm,
    )

    add_section(
        story,
        styles,
        "5.2 Evaluation Metrics and Cybersecurity Interpretation",
        [
            "Table 3 lists official NSL-KDD test metrics. Table 4 defines the metrics used in this project.",
        ],
    )
    story.append(
        make_table(
            ["Model", "Accuracy", "Precision", "Recall", "F1", "F2", "MCC", "ROC-AUC"],
            [
                [
                    "Logistic Regression",
                    fmt(official["logistic_regression"]["accuracy"]),
                    fmt(official["logistic_regression"]["precision"]),
                    fmt(official["logistic_regression"]["recall"]),
                    fmt(official["logistic_regression"]["f1"]),
                    fmt(official["logistic_regression"]["f2"]),
                    fmt(official["logistic_regression"]["mcc"]),
                    fmt(official["logistic_regression"]["roc_auc"]),
                ],
                [
                    "Random Forest",
                    fmt(official["random_forest"]["accuracy"]),
                    fmt(official["random_forest"]["precision"]),
                    fmt(official["random_forest"]["recall"]),
                    fmt(official["random_forest"]["f1"]),
                    fmt(official["random_forest"]["f2"]),
                    fmt(official["random_forest"]["mcc"]),
                    fmt(official["random_forest"]["roc_auc"]),
                ],
                [
                    "Isolation Forest",
                    fmt(official["isolation_forest"]["accuracy"]),
                    fmt(official["isolation_forest"]["precision"]),
                    fmt(official["isolation_forest"]["recall"]),
                    fmt(official["isolation_forest"]["f1"]),
                    fmt(official["isolation_forest"]["f2"]),
                    fmt(official["isolation_forest"]["mcc"]),
                    "N/A",
                ],
            ],
            [3.0 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 1.2 * cm, 1.2 * cm, 1.2 * cm, 1.5 * cm],
        )
    )
    story.append(Paragraph("Table 3. Official NSL-KDD test metrics (results/tables/model_comparison.csv).", styles["caption"]))

    story.append(
        make_table(
            ["Metric", "Formula (binary)", "Cybersecurity meaning in IDS"],
            [
                ["Accuracy", "(TP + TN) / N", "Overall correctness; misleading when attack cost or imbalance is ignored."],
                ["Precision", "TP / (TP + FP)", "Alert quality. False positives waste analyst time and create alert fatigue."],
                ["Recall", "TP / (TP + FN)", "Attack capture rate. False negatives allow intrusions to continue unnoticed."],
                ["F1", "2PR / (P + R)", "Balanced trade-off between alert quality and attack capture."],
                ["F2", "5PR / (4P + R)", "Weights recall higher; useful when missing attacks is costlier than extra alerts."],
                ["MCC", "(TP·TN − FP·FN) / sqrt(...)", "Balanced correlation score that remains informative under class imbalance."],
                ["ROC-AUC", "Area under TPR vs FPR curve", "Threshold-free ranking quality; does not by itself measure operational alert load."],
                ["Confusion Matrix", "[[TN, FP], [FN, TP]]", "Shows exact error types; essential for IDS operational review."],
            ],
            [2.0 * cm, 3.5 * cm, 10.0 * cm],
        )
    )
    story.append(Paragraph("Table 4. Metric definitions and cybersecurity interpretation.", styles["caption"]))

    add_section(
        story,
        styles,
        "",
        [
            f"Author-style random split (Random Forest): accuracy = {fmt(author_rf['accuracy'])}, recall = {fmt(author_rf['recall'])}, "
            f"ROC-AUC = {fmt(author_rf['roc_auc'])}. This closely matches the blog's reported values and shows how split choice inflates headline metrics.",
            "Random Forest official-test confusion matrix: TN=9453, FP=258, FN=4799, TP=8034 (results/tables/confusion_matrix_official_random_forest.csv). "
            "Although precision is high (0.9689), 4,799 attacks are missed — a serious false-negative burden for security operations.",
        ],
    )
    add_figure(
        story,
        styles,
        FIGURES_DIR / "confusion_matrix_official_random_forest.png",
        "Figure 3. Random Forest confusion matrix on the official test set.",
        width=10 * cm,
    )
    add_figure(
        story,
        styles,
        FIGURES_DIR / "roc_curve_official_random_forest.png",
        "Figure 4. Random Forest ROC curve on the official test set (AUC = 0.9660).",
        width=11 * cm,
    )

    add_section(
        story,
        styles,
        "5.3 Error Analysis",
        [
            "False positives (normal traffic classified as attack) often involve private, other, or telnet-related flows with unusual byte-count or flag patterns that resemble attack traffic. "
            "Example false positive pattern: UDP private service, flag SF, low byte counts, high dst_host_same_src_port_rate — predicted attack but label normal.",
            "False negatives (attacks classified as normal) include low-volume R2L and probe attacks such as guess_passwd, mscan, and telnet/ftp flows with subtle feature values. "
            "Example false negative: TCP telnet flow labeled guess_passwd with failed-login indicators, predicted normal.",
            "Error-pattern summary shows most misclassifications occur on TCP flows and on services telnet, pop_3, private, ftp, and http (results/tables/error_pattern_summary.csv).",
            "Cybersecurity implication: false negatives are more dangerous than false positives for this problem because missed attacks can lead to compromise, while false positives mainly increase analyst workload. "
            "Even so, high false-positive volume at scale can hide true incidents, so both error types matter.",
        ],
    )

    add_section(
        story,
        styles,
        "6. Conclusions",
        [
            "The tutorial is educationally strong and technically reproducible on the author's chosen split.",
            "The headline 99% metrics are supported only on the tutorial's random split, not on the official NSL-KDD test set.",
            "The author's caution about real-world degradation is validated by our experiments.",
            "For cybersecurity deployment, attack recall, F2, and MCC are more informative than accuracy alone.",
            "Recommended use: prototype and teaching baseline, not production IDS without official benchmarking and threshold tuning.",
        ],
    )

    add_section(
        story,
        styles,
        "7. Executive Summary",
        [
            f"We reproduced a published NSL-KDD intrusion detection tutorial combining Random Forest, SMOTE, and Isolation Forest. "
            f"On the author's random training-file split, Random Forest achieved accuracy {fmt(author_rf['accuracy'])} and ROC-AUC {fmt(author_rf['roc_auc'])}, matching the blog's near-perfect report. "
            f"On the official NSL-KDD test set, the same model dropped to accuracy {fmt(official['random_forest']['accuracy'])} and attack recall {fmt(official['random_forest']['recall'])}, "
            f"while Isolation Forest achieved the highest F1 ({fmt(official['isolation_forest']['f1'])}) and recall ({fmt(official['isolation_forest']['recall'])}). "
            "The most important insight is that high accuracy alone is insufficient in cybersecurity classification; split design and attack recall must be scrutinized before trusting claims.",
        ],
    )

    add_section(
        story,
        styles,
        "8. Summing It Up",
        [
            "Published cybersecurity ML tutorials can look excellent under one evaluation protocol and much weaker under a harder standard benchmark. "
            "The original solution's strengths are clarity, practical preprocessing, and an honest caveat about deployment. "
            "Its weaknesses are split choice, lack of official test reporting, and insufficient emphasis on attack recall.",
            "Future improvements should include per-attack-type evaluation, threshold tuning for operational recall targets, and testing on newer intrusion datasets.",
            "Final recommendation: adopt the pipeline as a learning exercise, but require official benchmark evaluation and security-oriented metrics before treating results as deployment evidence.",
        ],
    )

    doc.build(story)
    print("Wrote report/final_report.pdf")


if __name__ == "__main__":
    build_pdf()

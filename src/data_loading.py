"""Load and inspect the NSL-KDD intrusion detection dataset."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.utils import resolve_data_path

NSL_KDD_COLUMNS = [
    "duration",
    "protocol_type",
    "service",
    "flag",
    "src_bytes",
    "dst_bytes",
    "land",
    "wrong_fragment",
    "urgent",
    "hot",
    "num_failed_logins",
    "logged_in",
    "num_compromised",
    "root_shell",
    "su_attempted",
    "num_root",
    "num_file_creations",
    "num_shells",
    "num_access_files",
    "num_outbound_cmds",
    "is_host_login",
    "is_guest_login",
    "count",
    "srv_count",
    "serror_rate",
    "srv_serror_rate",
    "rerror_rate",
    "srv_rerror_rate",
    "same_srv_rate",
    "diff_srv_rate",
    "srv_diff_host_rate",
    "dst_host_count",
    "dst_host_srv_count",
    "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate",
    "dst_host_serror_rate",
    "dst_host_srv_serror_rate",
    "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate",
    "label",
    "difficulty",
]

ATTACK_MAP = {
    "normal": 0,
    "back": 1,
    "land": 1,
    "neptune": 1,
    "pod": 1,
    "smurf": 1,
    "teardrop": 1,
    "mailbomb": 1,
    "processtable": 1,
    "udpstorm": 1,
    "apache2": 1,
    "worm": 1,
    "ipsweep": 2,
    "nmap": 2,
    "portsweep": 2,
    "satan": 2,
    "mscan": 2,
    "saint": 2,
    "ftp_write": 3,
    "guess_passwd": 3,
    "imap": 3,
    "multihop": 3,
    "phf": 3,
    "spy": 3,
    "warezclient": 3,
    "warezmaster": 3,
    "sendmail": 3,
    "named": 3,
    "snmpget": 3,
    "snmpguess": 3,
    "xlock": 3,
    "xsnoop": 3,
    "httptunnel": 3,
    "buffer_overflow": 4,
    "loadmodule": 4,
    "perl": 4,
    "rootkit": 4,
    "ps": 4,
    "sqlattack": 4,
    "xterm": 4,
}


def load_nsl_kdd(path: str | Path) -> pd.DataFrame:
    """Load an NSL-KDD TXT/CSV file with standard column names."""
    df = pd.read_csv(path, names=NSL_KDD_COLUMNS)
    df["label"] = df["label"].astype(str).str.strip()
    df["attack_category"] = df["label"].map(
        lambda value: ATTACK_MAP.get(value, -1)
    )
    df["binary_label"] = (df["attack_category"] != 0).astype(int)
    return df


def load_train_test(
    train_filename: str = "KDDTrain+.txt",
    test_filename: str = "KDDTest+.txt",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load official NSL-KDD train and test splits."""
    train_path = resolve_data_path(train_filename)
    test_path = resolve_data_path(test_filename)
    return load_nsl_kdd(train_path), load_nsl_kdd(test_path)


def get_feature_columns() -> list[str]:
    """Return model input columns used by the original tutorial."""
    categorical = {"protocol_type", "service", "flag"}
    return [column for column in NSL_KDD_COLUMNS if column not in {"label", "difficulty"} and column not in categorical] + sorted(categorical)


def get_numeric_columns() -> list[str]:
    """Return numeric feature columns."""
    categorical = {"protocol_type", "service", "flag"}
    return [
        column
        for column in NSL_KDD_COLUMNS
        if column not in {"label", "difficulty"} and column not in categorical
    ]


def get_categorical_columns() -> list[str]:
    """Return categorical feature columns."""
    return ["protocol_type", "service", "flag"]

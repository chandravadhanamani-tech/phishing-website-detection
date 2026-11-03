"""
preprocessing.py - Dataset Preprocessing for Phishing Detection
"""

import sys
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

TARGET_COLUMN = "Result"
LABEL_MAP = {-1: 0, 0: 1, 1: 1}


class DataPreprocessor:
    def __init__(self, target_col: str = TARGET_COLUMN):
        self.target_col    = target_col
        self.feature_names = []

    def load_uci_dataset(self, filepath: str) -> pd.DataFrame:
        print(f"[+] Loading dataset from: {filepath}")
        try:
            df = pd.read_csv(filepath)
        except Exception:
            df = pd.read_csv(filepath, sep="\t")

        print(f"   Shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        return df

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        print("\n[+] Cleaning dataset...")
        original_shape = df.shape

        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        df = df.drop_duplicates()
        print(f"   Dropped {original_shape[0] - len(df)} duplicate rows")

        threshold = len(df.columns) * 0.5
        df = df.dropna(thresh=threshold)
        df = df.fillna(df.median(numeric_only=True))

        if self.target_col not in df.columns:
            for alt in ["class", "label", "phishing", "CLASS", "LABEL"]:
                if alt in df.columns:
                    df = df.rename(columns={alt: self.target_col})
                    break

        if self.target_col in df.columns:
            df[self.target_col] = df[self.target_col].map(LABEL_MAP)
            df = df.dropna(subset=[self.target_col])
            df[self.target_col] = df[self.target_col].astype(int)

        print(f"   Final shape: {df.shape}")
        self.print_dataset_stats(df)
        return df

    def get_feature_target_split(self, df: pd.DataFrame):
        if self.target_col not in df.columns:
            raise ValueError(
                f"Target column '{self.target_col}' not found. "
                f"Available: {list(df.columns)}"
            )

        X = df.drop(columns=[self.target_col])
        y = df[self.target_col]

        self.feature_names = list(X.columns)
        print(f"\n[+] Features: {len(self.feature_names)}, Samples: {len(y)}")
        return X, y

    def get_train_test_split(self, X, y, test_size: float = 0.2, random_state: int = 42):
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size     = test_size,
            random_state  = random_state,
            stratify      = y,
        )
        print(f"\n[+] Train/Test split:")
        print(f"   Train: {len(X_train)} samples")
        print(f"   Test:  {len(X_test)} samples")
        return X_train, X_test, y_train, y_test

    def get_feature_names(self) -> list:
        return self.feature_names

    def print_dataset_stats(self, df: pd.DataFrame) -> None:
        if self.target_col in df.columns:
            counts = df[self.target_col].value_counts()
            total  = len(df)
            print(f"\n[+] Class Distribution:")
            for label, count in counts.items():
                name = "Phishing (1)" if label == 1 else "Legitimate (0)"
                pct  = count / total * 100
                print(f"   {name}: {count:,} ({pct:.1f}%)")

        missing = df.isnull().sum().sum()
        if missing > 0:
            print(f"   [-] Missing values remaining: {missing}")

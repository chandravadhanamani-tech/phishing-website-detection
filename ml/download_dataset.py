"""
download_dataset.py - Automatically downloads and prepares the UCI Phishing Websites dataset.
"""

import os
import urllib.request
import pandas as pd

def download_and_convert():
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00327/Training%20Dataset.arff"
    target_dir = os.path.join(os.path.dirname(__file__), "data", "raw")
    os.makedirs(target_dir, exist_ok=True)

    arff_path = os.path.join(target_dir, "Training Dataset.arff")
    csv_path  = os.path.join(target_dir, "phishing_dataset.csv")

    print(f"[+] Downloading UCI dataset from: {url}")
    urllib.request.urlretrieve(url, arff_path)
    print("[+] Download completed.")

    print("[+] Converting ARFF format to CSV...")
    attributes = []
    data_lines = []
    reading_data = False

    with open(arff_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if not line_str or line_str.startswith("%"):
                continue
            if line_str.lower().startswith("@attribute"):
                parts = line_str.split()
                attr_name = parts[1].strip("'\"")
                attributes.append(attr_name)
            elif line_str.lower().startswith("@data"):
                reading_data = True
                continue
            elif reading_data:
                parts = [x.strip() for x in line_str.split(",")]
                if len(parts) == len(attributes):
                    data_lines.append(parts)

    df = pd.DataFrame(data_lines, columns=attributes)
    
    # Ensure target column is numeric
    if "Result" in df.columns:
        df["Result"] = pd.to_numeric(df["Result"], errors="coerce")

    df.to_csv(csv_path, index=False)
    print(f"[+] Dataset saved successfully to: {csv_path}")
    print(f"[+] Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"[+] Features: {list(df.columns[:5])} ... Total: {len(df.columns)}")

if __name__ == "__main__":
    download_and_convert()

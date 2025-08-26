#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
from pathlib import Path
import pandas as pd


def find_col(df: pd.DataFrame, score_col) -> str:
    """Case-insensitive exact match in column names; raises error with suggestions if not found."""
    # 1) Automatically find columns containing "score" (case-insensitive)

    score_cols = [c for c in df.columns if score_col in str(c).lower()]
    if not score_cols:
        raise SystemExit(f"No column containing {score_col} found.")
    score_col = score_cols[0]  # Take the first match
    return score_col

def main():
    ap = argparse.ArgumentParser(description="Calculate average {model}-score and group averages by complexity.")
    ap.add_argument("-i", "--input", required=True, help="Input xlsx path")
    ap.add_argument("-c", "--score_col", default="score")
    ap.add_argument("-o", "--output", default=None, help="Write results to this xlsx (optional)")
    args = ap.parse_args()

    path = args.input

    # 检查文件是否存在
    if not Path(path).exists():
        raise SystemExit(f"File not found: {path}")

    if 'xlsx' in path:
        df = pd.read_excel(path, sheet_name=args.sheet)
    elif 'csv' in path:
        df = pd.read_csv(path)
    else:
        raise SystemExit(f"Unsupported file format: {path}")


    score_col = find_col(df, args.score_col)
    comp_col = 'complexity'

    # Convert to numeric
    df[score_col] = pd.to_numeric(df[score_col], errors="coerce")

    overall_mean = df[score_col].mean()
    by_complexity = (
        df.groupby(comp_col, dropna=False)[score_col]
        .mean()
        .reset_index()
        .rename(columns={score_col: "avg_score"})
        .sort_values("avg_score", ascending=False)
    )

    # Print results
    print(f"File: {path}")
    print(f"Score column: {score_col}")
    print(by_complexity.to_string(index=False))
    # Calculate the mean of all scores in by_complexity
    overall_mean = by_complexity['avg_score'].mean()
    print(f"Overall mean: {overall_mean:.4f}")


    # Optional export
    if args.output:
        out = Path(args.output)
        with pd.ExcelWriter(out, engine="xlsxwriter") as w:
            pd.DataFrame({"metric": ["overall_mean"], "value": [overall_mean]}).to_excel(
                w, index=False, sheet_name="overall"
            )
            by_complexity.to_excel(w, index=False, sheet_name="by_complexity")
        print(f"\nWritten to: {out.resolve()}")


if __name__ == "__main__":
    main()

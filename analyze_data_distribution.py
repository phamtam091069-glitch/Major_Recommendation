#!/usr/bin/env python3
"""
Analyze data distribution across majors to identify imbalance issues.
Generates a detailed report showing which majors are underrepresented.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter
import json

def analyze_distribution():
    """Analyze major distribution in the dataset."""
    
    data_path = Path("data/raw/students.csv")
    
    if not data_path.exists():
        print(f"❌ File not found: {data_path}")
        return
    
    # Read dataset
    df = pd.read_csv(data_path)
    print(f"✅ Loaded {len(df)} records from {data_path}\n")
    
    # Get the target column (try multiple names)
    target_col = None
    for col_name in ['nganh_phu_hop', 'nganh', 'major']:
        if col_name in df.columns:
            target_col = col_name
            break
    
    if target_col is None:
        print(f"❌ Target column not found. Available columns: {df.columns.tolist()}")
        return
    
    print(f"📍 Using target column: '{target_col}'\n")
    
    # Get distribution
    distribution = df[target_col].value_counts().sort_values(ascending=False)
    
    # Calculate statistics
    total_records = len(df)
    total_majors = len(distribution)
    min_samples = distribution.min()
    max_samples = distribution.max()
    mean_samples = distribution.mean()
    median_samples = distribution.median()
    std_samples = distribution.std()
    imbalance_ratio = max_samples / min_samples if min_samples > 0 else float('inf')
    
    # Categorize majors
    underrepresented_50 = distribution[distribution < 50]
    underrepresented_100 = distribution[distribution < 100]
    underrepresented_150 = distribution[distribution < 150]
    well_represented = distribution[distribution >= 150]
    
    # Print header
    print("=" * 80)
    print("📊 DATA DISTRIBUTION ANALYSIS REPORT")
    print("=" * 80)
    print(f"Dataset: {data_path}")
    print(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Overall statistics
    print("📈 OVERALL STATISTICS")
    print("-" * 80)
    print(f"Total Records:       {total_records:,}")
    print(f"Total Majors:        {total_majors}")
    print(f"Mean/Major:          {mean_samples:.1f}")
    print(f"Median/Major:        {median_samples:.1f}")
    print(f"Std Dev:             {std_samples:.1f}")
    print(f"Min Samples:         {min_samples}")
    print(f"Max Samples:         {max_samples}")
    print(f"Imbalance Ratio:     {imbalance_ratio:.2f}:1", end="")
    if imbalance_ratio > 3:
        print(" ❌ (HIGH - DATA IS IMBALANCED)")
    elif imbalance_ratio > 1.5:
        print(" ⚠️ (MODERATE)")
    else:
        print(" ✅ (LOW - DATA IS BALANCED)")
    print()
    
    # Detailed distribution
    print("\n📊 DETAILED DISTRIBUTION (TOP 20)")
    print("-" * 80)
    print(f"{'Rank':<5} {'Major':<50} {'Samples':<10} {'%':<8}")
    print("-" * 80)
    for i, (major, count) in enumerate(distribution.head(20).items(), 1):
        percentage = (count / total_records) * 100
        print(f"{i:<5} {major:<50} {count:<10} {percentage:.2f}%")
    
    if len(distribution) > 20:
        print(f"... and {len(distribution) - 20} more majors")
    print()
    
    # Underrepresented majors
    print("\n⚠️ UNDERREPRESENTED MAJORS ANALYSIS")
    print("-" * 80)
    
    print(f"\n🔴 CRITICAL (<50 samples): {len(underrepresented_50)} majors")
    if len(underrepresented_50) > 0:
        print(f"{'Major':<50} {'Current':<10} {'Need':<10} {'Gap':<10}")
        print("-" * 80)
        for major, count in underrepresented_50.items():
            needed = 150 - count
            print(f"{major:<50} {count:<10} {150:<10} {needed:<10}")
    else:
        print("✅ No majors with less than 50 samples")
    
    print(f"\n🟡 MODERATE (50-100 samples): {len(underrepresented_100)} majors")
    if len(underrepresented_100) > 0:
        print(f"{'Major':<50} {'Current':<10} {'Need':<10} {'Gap':<10}")
        print("-" * 80)
        for major, count in underrepresented_100.items():
            needed = 150 - count
            print(f"{major:<50} {count:<10} {150:<10} {needed:<10}")
    else:
        print("✅ No majors with 50-100 samples")
    
    print(f"\n🟠 LOW (100-150 samples): {len(underrepresented_150)} majors")
    if len(underrepresented_150) > 0:
        print(f"{'Major':<50} {'Current':<10} {'Need':<10} {'Gap':<10}")
        print("-" * 80)
        for major, count in underrepresented_150.items():
            needed = 150 - count
            print(f"{major:<50} {count:<10} {150:<10} {needed:<10}")
    else:
        print("✅ No majors with 100-150 samples")
    
    print(f"\n🟢 WELL-REPRESENTED (≥150 samples): {len(well_represented)} majors")
    if len(well_represented) > 0:
        print(f"{'Major':<50} {'Samples':<10}")
        print("-" * 80)
        for major, count in well_represented.items():
            print(f"{major:<50} {count:<10}")
    else:
        print("⚠️ No majors with 150+ samples - strong imbalance!")
    
    # Augmentation recommendation
    print("\n\n💡 DATA AUGMENTATION RECOMMENDATION")
    print("=" * 80)
    
    target_samples_per_major = 150  # Target for balanced dataset
    total_gap = sum(max(0, target_samples_per_major - count) for count in distribution)
    projected_total = total_records + total_gap
    
    print(f"\nTarget Strategy: Balance all majors to {target_samples_per_major} samples/major")
    print(f"\nCurrent State:")
    print(f"  - Total records: {total_records:,}")
    print(f"  - Imbalance ratio: {imbalance_ratio:.2f}:1")
    print(f"\nAfter Augmentation:")
    print(f"  - Projected total: ~{projected_total:,} records")
    print(f"  - Records to add: ~{total_gap:,}")
    print(f"  - Imbalance ratio: 1.00:1 (PERFECT)")
    print(f"  - All majors: {target_samples_per_major} samples each")
    
    # Save detailed report
    report_data = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "total_records": int(total_records),
        "total_majors": int(total_majors),
        "statistics": {
            "mean": float(mean_samples),
            "median": float(median_samples),
            "std": float(std_samples),
            "min": int(min_samples),
            "max": int(max_samples),
            "imbalance_ratio": float(imbalance_ratio)
        },
        "distribution": distribution.to_dict(),
        "underrepresented": {
            "critical": underrepresented_50.to_dict(),
            "moderate": underrepresented_100[~underrepresented_100.index.isin(underrepresented_50.index)].to_dict(),
            "low": underrepresented_150[~underrepresented_150.index.isin(underrepresented_100.index)].to_dict(),
        },
        "augmentation_recommendation": {
            "target_samples_per_major": target_samples_per_major,
            "projected_total": int(projected_total),
            "records_to_add": int(total_gap)
        }
    }
    
    # Save report
    report_path = Path("reports/data_distribution_analysis.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n✅ Detailed report saved to: {report_path}")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    analyze_distribution()

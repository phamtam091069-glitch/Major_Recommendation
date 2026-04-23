"""
Test Script - Data Cleaning Module
Demo và test các hàm làm sạch dữ liệu
"""

import logging
import pandas as pd
from pathlib import Path
from clean_data import DataCleaner, main

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_basic_cleaning():
    """Test làm sạch dữ liệu cơ bản."""
    print("\n" + "="*70)
    print("TEST 1: BASIC DATA CLEANING")
    print("="*70 + "\n")
    
    # Load dữ liệu gốc
    input_file = Path(__file__).parent / "raw" / "students.csv"
    if not input_file.exists():
        logger.error(f"❌ Không tìm thấy file: {input_file}")
        return False
    
    logger.info(f"📂 Load dữ liệu từ: {input_file}")
    df = pd.read_csv(input_file, encoding="utf-8")
    logger.info(f"✅ Shape gốc: {df.shape}\n")
    
    # Tạo cleaner
    cleaner = DataCleaner(df, verbose=True)
    
    # Chạy làm sạch
    df_cleaned, report = cleaner.clean_all(
        handle_missing=True,
        handle_outliers=True,
        handle_duplicates=True,
    )
    
    # In báo cáo
    print("\n" + "="*70)
    print("BÁOCÁO LÀMSẠCH")
    print("="*70)
    print(f"Shape gốc: {report['original_shape']}")
    print(f"Shape cuối: {report['final_shape']}")
    print(f"Rows xóa: {report['original_shape'][0] - report['final_shape'][0]}")
    print(f"Cols xóa: {report['original_shape'][1] - report['final_shape'][1]}")
    
    if report['missing_stats']:
        print(f"\n📊 Missing Values:")
        for col, stats in report['missing_stats'].items():
            print(f"   - {col}: {stats['count']} ({stats['percentage']}%)")
    
    if report['duplicate_stats']:
        print(f"\n📋 Duplicates:")
        print(f"   - Exact: {report['duplicate_stats'].get('exact_duplicates_removed', 0)}")
        print(f"   - Near: {len(report['duplicate_stats'].get('near_duplicates', []))}")
    
    print("\n" + "="*70 + "\n")
    return True


def test_missing_detection():
    """Test phát hiện missing values."""
    print("\n" + "="*70)
    print("TEST 2: MISSING VALUES DETECTION")
    print("="*70 + "\n")
    
    # Tạo dữ liệu test
    test_data = {
        "col1": [1, 2, None, 4, 5],
        "col2": ["a", "b", "c", None, "e"],
        "col3": [10, None, 30, 40, None],
    }
    df_test = pd.DataFrame(test_data)
    
    logger.info(f"📊 Dữ liệu test:\n{df_test}\n")
    
    # Phát hiện
    cleaner = DataCleaner(df_test, verbose=True)
    missing_stats = cleaner.detect_missing_values()
    
    print("\n" + "="*70)
    print("THỐNG KÊ MISSING")
    print("="*70)
    for col, stats in missing_stats.items():
        print(f"{col}: {stats['count']} missing ({stats['percentage']}%)")
    print("="*70 + "\n")
    
    return True


def test_outlier_detection():
    """Test phát hiện outliers."""
    print("\n" + "="*70)
    print("TEST 3: OUTLIER DETECTION")
    print("="*70 + "\n")
    
    # Tạo dữ liệu test
    test_data = {
        "age": [20, 22, 25, 23, 24, 150],  # 150 là outlier
        "score": [70, 75, 72, 78, 75, 800],  # 800 là outlier
    }
    df_test = pd.DataFrame(test_data)
    
    logger.info(f"📊 Dữ liệu test:\n{df_test}\n")
    
    # Phát hiện
    cleaner = DataCleaner(df_test, verbose=True)
    outliers_iqr = cleaner.detect_outliers_iqr()
    
    print("\n" + "="*70)
    print("OUTLIERS DETECTED (IQR METHOD)")
    print("="*70)
    for col, indices in outliers_iqr.items():
        print(f"{col}: rows {indices}")
    print("="*70 + "\n")
    
    # Handle outliers
    cleaner.handle_outliers(method="iqr")
    print(f"Dữ liệu sau cap:\n{cleaner.df}\n")
    
    return True


def test_duplicate_detection():
    """Test phát hiện duplicates."""
    print("\n" + "="*70)
    print("TEST 4: DUPLICATE DETECTION")
    print("="*70 + "\n")
    
    # Tạo dữ liệu test
    test_data = {
        "name": ["Alice", "Bob", "Alice", "Charlie", "Bob"],
        "age": [25, 30, 25, 35, 30],
        "city": ["HN", "SG", "HN", "HN", "SG"],
    }
    df_test = pd.DataFrame(test_data)
    
    logger.info(f"📊 Dữ liệu test:\n{df_test}\n")
    
    # Phát hiện exact
    cleaner = DataCleaner(df_test, verbose=True)
    exact_count = cleaner.detect_duplicates_exact()
    
    # Phát hiện near
    near_info = cleaner.detect_duplicates_near()
    
    print("\n" + "="*70)
    print("DUPLICATES DETECTED")
    print("="*70)
    print(f"Exact duplicates: {exact_count}")
    print(f"Near duplicates: {len(near_info['near_duplicates'])}")
    if near_info['near_duplicates']:
        for dup in near_info['near_duplicates']:
            print(f"  - Row {dup['row_i']} vs {dup['row_j']}: {dup['similarity']*100:.1f}% similar")
    print("="*70 + "\n")
    
    # Handle
    cleaner.handle_duplicates(keep_first=True)
    print(f"Dữ liệu sau xóa duplicates:\n{cleaner.df}\n")
    
    return True


def test_end_to_end():
    """Test end-to-end cleaning."""
    print("\n" + "="*70)
    print("TEST 5: END-TO-END CLEANING")
    print("="*70 + "\n")
    
    # Paths
    input_file = Path(__file__).parent / "raw" / "students.csv"
    output_file = Path(__file__).parent / "raw" / "students_cleaned_test.csv"
    
    if not input_file.exists():
        logger.error(f"❌ Không tìm thấy file: {input_file}")
        return False
    
    # Run main
    logger.info(f"📂 Input: {input_file}")
    logger.info(f"📂 Output: {output_file}\n")
    
    df_cleaned, report = main(
        str(input_file),
        str(output_file),
        verbose=True
    )
    
    # Verify
    logger.info(f"\n✅ Cleaned data shape: {df_cleaned.shape}")
    logger.info(f"✅ Output file saved: {output_file.exists()}")
    
    return True


def print_summary():
    """In tóm tắt chức năng."""
    print("\n" + "="*70)
    print("DATA CLEANING MODULE - TÓMSẮT CHỨC NĂNG")
    print("="*70)
    
    summary = """
    📋 MODULE GỒM CÁC HÀM:
    
    1. detect_missing_values()
       → Phát hiện giá trị bị thiếu (NaN, None)
       → Output: Dict với % missing cho mỗi cột
    
    2. handle_missing_values()
       → Xử lý missing: xóa cột/hàng hoặc điền value
       → Xóa cột nếu >50% missing
       → Điền mode (categorical) hoặc mean (numeric)
    
    3. detect_outliers_iqr() & detect_outliers_zscore()
       → Phát hiện outlier bằng 2 phương pháp
       → IQR: Q1 - 1.5×IQR to Q3 + 1.5×IQR
       → Z-score: |Z| > 3
    
    4. handle_outliers()
       → Xử lý outlier bằng cap (Winsorization)
       → Giữ lại dữ liệu nhưng giới hạn trong range
    
    5. detect_duplicates_exact() & detect_duplicates_near()
       → Phát hiện exact và near-duplicates
       → Near-duplicate: >85% similarity
    
    6. handle_duplicates()
       → Xóa duplicate rows
    
    7. clean_all()
       → Hàm tổng hợp: xử lý missing + outlier + duplicate
    
    8. save_cleaned_data()
       → Lưu dữ liệu sạch và báo cáo chi tiết
    
    📊 OUTPUT:
       - CSV file sạch: data/raw/students_cleaned.csv
       - Báo cáo JSON: data/raw/cleaning_report.json
       - Log chi tiết với emoji ✅ ⚠️ ❌
    
    🚀 CÁCH DÙNG:
       python clean_data.py [input_file] [output_file]
    """
    print(summary)
    print("="*70 + "\n")


if __name__ == "__main__":
    print_summary()
    
    # Run tests
    tests = [
        ("Basic Cleaning", test_basic_cleaning),
        ("Missing Detection", test_missing_detection),
        ("Outlier Detection", test_outlier_detection),
        ("Duplicate Detection", test_duplicate_detection),
        ("End-to-End", test_end_to_end),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} PASSED\n")
            else:
                failed += 1
                logger.error(f"❌ {test_name} FAILED\n")
        except Exception as e:
            failed += 1
            logger.error(f"❌ {test_name} FAILED: {e}\n")
    
    # Summary
    print("="*70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("="*70 + "\n")

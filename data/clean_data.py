"""
Data Cleaning Module - Làm Sạch Dữ Liệu
Xử lý: Missing Values, Outliers, Duplicates
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from difflib import SequenceMatcher
from sklearn.ensemble import IsolationForest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
MISSING_THRESHOLD_HIGH = 0.5  # Xóa cột nếu > 50% missing
MISSING_THRESHOLD_LOW = 0.05  # Xóa hàng nếu < 5% missing
OUTLIER_IQR_MULTIPLIER = 1.5  # IQR method multiplier
OUTLIER_ZSCORE_THRESHOLD = 3.0  # Z-score threshold
DUPLICATE_SIMILARITY_THRESHOLD = 0.85  # 85% similarity = near-duplicate

CATEGORICAL_COLS = [
    "so_thich_chinh",
    "mon_hoc_yeu_thich",
    "ky_nang_noi_bat",
    "tinh_cach",
    "moi_truong_lam_viec_mong_muon",
    "muc_tieu_nghe_nghiep",
]

TEXT_COLS = ["mo_ta_ban_than", "dinh_huong_tuong_lai"]


class DataCleaner:
    """Class xử lý làm sạch dữ liệu."""

    def __init__(self, df: pd.DataFrame, verbose: bool = True):
        """
        Khởi tạo DataCleaner.
        
        Args:
            df: DataFrame cần làm sạch
            verbose: In log chi tiết
        """
        self.df_original = df.copy()
        self.df = df.copy()
        self.verbose = verbose
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "original_shape": df.shape,
            "missing_stats": {},
            "outlier_stats": {},
            "duplicate_stats": {},
            "final_shape": None,
            "rows_removed": [],
            "columns_removed": [],
        }

    def _log(self, message: str, level: str = "info"):
        """Log message với emoji."""
        if not self.verbose:
            return
        if level == "info":
            logger.info(f"ℹ️  {message}")
        elif level == "warning":
            logger.warning(f"⚠️  {message}")
        elif level == "error":
            logger.error(f"❌ {message}")
        elif level == "success":
            logger.info(f"✅ {message}")

    def detect_missing_values(self) -> Dict[str, Any]:
        """Phát hiện giá trị bị thiếu."""
        self._log("=== PHÁT HIỆN MISSING VALUES ===")
        
        missing_stats = {}
        for col in self.df.columns:
            missing_count = self.df[col].isnull().sum()
            missing_pct = (missing_count / len(self.df)) * 100
            missing_stats[col] = {
                "count": int(missing_count),
                "percentage": round(missing_pct, 2),
            }
            
            if missing_pct > 0:
                self._log(
                    f"Cột '{col}': {missing_count} missing ({missing_pct:.2f}%)",
                    "warning"
                )
        
        self.report["missing_stats"] = missing_stats
        total_missing = self.df.isnull().sum().sum()
        self._log(f"Tổng missing: {total_missing} cells", "info")
        return missing_stats

    def handle_missing_values(self) -> int:
        """Xử lý giá trị bị thiếu."""
        self._log("=== XỬ LÝ MISSING VALUES ===")
        rows_before = len(self.df)
        
        # Bước 1: Xóa cột có > 50% missing
        cols_to_drop = []
        for col, stats in self.report["missing_stats"].items():
            if stats["percentage"] > MISSING_THRESHOLD_HIGH * 100:
                cols_to_drop.append(col)
                self._log(f"Xóa cột '{col}' (>{MISSING_THRESHOLD_HIGH*100}% missing)", "warning")
        
        if cols_to_drop:
            self.df = self.df.drop(columns=cols_to_drop)
            self.report["columns_removed"].extend(cols_to_drop)
        
        # Bước 2: Xóa hàng có > 50% missing
        rows_with_many_missing = self.df[self.df.isnull().sum(axis=1) > len(self.df.columns) * 0.5].index
        if len(rows_with_many_missing) > 0:
            self.df = self.df.drop(rows_with_many_missing)
            self._log(f"Xóa {len(rows_with_many_missing)} hàng có >50% missing", "warning")
        
        # Bước 3: Điền giá trị cho cột còn lại
        for col in self.df.columns:
            if self.df[col].isnull().sum() > 0:
                if col in CATEGORICAL_COLS:
                    # Điền mode cho categorical
                    fill_value = self.df[col].mode()[0] if not self.df[col].mode().empty else "khong_xac_dinh"
                    self.df[col].fillna(fill_value, inplace=True)
                    self._log(f"Điền '{fill_value}' cho cột '{col}' (mode)", "success")
                else:
                    # Điền mean cho numeric
                    if self.df[col].dtype in [np.float64, np.int64]:
                        fill_value = self.df[col].mean()
                        self.df[col].fillna(fill_value, inplace=True)
                        self._log(f"Điền {fill_value:.2f} cho cột '{col}' (mean)", "success")
                    else:
                        # Điền mode cho string/object
                        fill_value = self.df[col].mode()[0] if not self.df[col].mode().empty else "N/A"
                        self.df[col].fillna(fill_value, inplace=True)
                        self._log(f"Điền '{fill_value}' cho cột '{col}' (mode)", "success")
        
        rows_removed = rows_before - len(self.df)
        self._log(f"Xóa {rows_removed} hàng; Final: {len(self.df)} rows", "success")
        return rows_removed

    def detect_outliers_iqr(self) -> Dict[str, List[int]]:
        """Phát hiện outlier bằng IQR method."""
        self._log("=== PHÁT HIỆN OUTLIERS (IQR METHOD) ===")
        outliers_dict = {}
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - OUTLIER_IQR_MULTIPLIER * IQR
            upper_bound = Q3 + OUTLIER_IQR_MULTIPLIER * IQR
            
            outlier_mask = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
            outlier_indices = self.df[outlier_mask].index.tolist()
            
            if len(outlier_indices) > 0:
                outliers_dict[col] = outlier_indices
                self._log(
                    f"Cột '{col}': {len(outlier_indices)} outliers "
                    f"(bounds: [{lower_bound:.2f}, {upper_bound:.2f}])",
                    "warning"
                )
        
        return outliers_dict

    def detect_outliers_zscore(self) -> Dict[str, List[int]]:
        """Phát hiện outlier bằng Z-score method."""
        self._log("=== PHÁT HIỆN OUTLIERS (Z-SCORE METHOD) ===")
        outliers_dict = {}
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            mean = self.df[col].mean()
            std = self.df[col].std()
            
            if std == 0:
                continue
            
            z_scores = np.abs((self.df[col] - mean) / std)
            outlier_mask = z_scores > OUTLIER_ZSCORE_THRESHOLD
            outlier_indices = self.df[outlier_mask].index.tolist()
            
            if len(outlier_indices) > 0:
                outliers_dict[col] = outlier_indices
                self._log(
                    f"Cột '{col}': {len(outlier_indices)} outliers "
                    f"(Z-score > {OUTLIER_ZSCORE_THRESHOLD})",
                    "warning"
                )
        
        return outliers_dict

    def handle_outliers(self, method: str = "iqr") -> int:
        """Xử lý outlier bằng cách cap (Winsorization)."""
        self._log(f"=== XỬ LÝ OUTLIERS ({method.upper()}) ===")
        rows_before = len(self.df)
        
        if method == "iqr":
            outliers_dict = self.detect_outliers_iqr()
        elif method == "zscore":
            outliers_dict = self.detect_outliers_zscore()
        else:
            self._log("Phương pháp không hợp lệ. Dùng IQR.", "warning")
            outliers_dict = self.detect_outliers_iqr()
        
        # Cap outliers thay vì xóa
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - OUTLIER_IQR_MULTIPLIER * IQR
            upper_bound = Q3 + OUTLIER_IQR_MULTIPLIER * IQR
            
            # Cap values
            self.df[col] = self.df[col].clip(lower=lower_bound, upper=upper_bound)
        
        self._log("Outliers được cap (Winsorization), không xóa", "success")
        
        # Lưu vào report
        self.report["outlier_stats"] = {
            "method": method,
            "outliers_detected": outliers_dict,
            "action": "cap",
        }
        
        return rows_before - len(self.df)

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Tính độ tương đồng giữa 2 chuỗi (0-1)."""
        return SequenceMatcher(None, str1, str2).ratio()

    def detect_duplicates_exact(self) -> int:
        """Phát hiện duplicate chính xác."""
        self._log("=== PHÁT HIỆN EXACT DUPLICATES ===")
        dup_count = self.df.duplicated().sum()
        self._log(f"Tìm thấy {dup_count} exact duplicates", "warning" if dup_count > 0 else "success")
        return dup_count

    def detect_duplicates_near(self, subset: Optional[List[str]] = None) -> Dict[str, Any]:
        """Phát hiện near-duplicates theo fuzzy matching."""
        self._log("=== PHÁT HIỆN NEAR-DUPLICATES (Fuzzy) ===")
        
        if subset is None:
            subset = CATEGORICAL_COLS
        
        near_dups = []
        checked_pairs = set()
        
        for i in range(len(self.df)):
            for j in range(i + 1, len(self.df)):
                pair_key = (i, j)
                if pair_key in checked_pairs:
                    continue
                
                checked_pairs.add(pair_key)
                
                # So sánh subset columns
                similarity_scores = []
                for col in subset:
                    if col in self.df.columns:
                        str1 = str(self.df.iloc[i][col]).lower()
                        str2 = str(self.df.iloc[j][col]).lower()
                        similarity = self._calculate_similarity(str1, str2)
                        similarity_scores.append(similarity)
                
                if similarity_scores:
                    avg_similarity = np.mean(similarity_scores)
                    if avg_similarity >= DUPLICATE_SIMILARITY_THRESHOLD:
                        near_dups.append({
                            "row_i": i,
                            "row_j": j,
                            "similarity": round(avg_similarity, 3),
                        })
        
        if near_dups:
            self._log(f"Tìm thấy {len(near_dups)} near-duplicates (similarity >= {DUPLICATE_SIMILARITY_THRESHOLD})", "warning")
        else:
            self._log("Không tìm thấy near-duplicates", "success")
        
        return {"near_duplicates": near_dups}

    def handle_duplicates(self, keep_first: bool = True) -> int:
        """Xử lý duplicate."""
        self._log("=== XỬ LÝ DUPLICATES ===")
        rows_before = len(self.df)
        
        # Xóa exact duplicates
        exact_dup_count = self.detect_duplicates_exact()
        self.df = self.df.drop_duplicates(keep="first" if keep_first else "last")
        self._log(f"Xóa {exact_dup_count} exact duplicates", "success" if exact_dup_count > 0 else "info")
        
        # Phát hiện near-duplicates
        near_dup_info = self.detect_duplicates_near()
        self.report["duplicate_stats"] = {
            "exact_duplicates_removed": exact_dup_count,
            "near_duplicates": near_dup_info["near_duplicates"],
        }
        
        rows_removed = rows_before - len(self.df)
        self._log(f"Final: {len(self.df)} rows", "success")
        return rows_removed

    def clean_all(self, handle_missing: bool = True, handle_outliers: bool = True, 
                  handle_duplicates: bool = True) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Làm sạch toàn diện."""
        self._log("\n" + "="*60)
        self._log("BẮTĐẦU LÀMSẠCH DỮ LIỆU")
        self._log("="*60 + "\n")
        
        if handle_missing:
            self.detect_missing_values()
            self.handle_missing_values()
        
        if handle_outliers:
            self.handle_outliers(method="iqr")
        
        if handle_duplicates:
            self.handle_duplicates(keep_first=True)
        
        self.report["final_shape"] = self.df.shape
        
        # Summary
        self._log("\n" + "="*60)
        self._log("TÓM TẮT LÀMSẠCH")
        self._log("="*60)
        self._log(f"Shape gốc: {self.report['original_shape']}")
        self._log(f"Shape cuối: {self.report['final_shape']}")
        self._log(f"Rows xóa: {self.report['original_shape'][0] - self.report['final_shape'][0]}")
        self._log(f"Cols xóa: {self.report['original_shape'][1] - self.report['final_shape'][1]}")
        self._log("="*60 + "\n")
        
        return self.df, self.report

    def save_cleaned_data(self, output_path: str, save_report: bool = True) -> None:
        """Lưu dữ liệu đã làm sạch."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.df.to_csv(output_path, index=False, encoding="utf-8")
        self._log(f"✅ Lưu dữ liệu sạch: {output_path}", "success")
        
        if save_report:
            report_path = output_path.parent / "cleaning_report.json"
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(self.report, f, ensure_ascii=False, indent=2)
            self._log(f"✅ Lưu báo cáo: {report_path}", "success")

    def get_report(self) -> Dict[str, Any]:
        """Trả về báo cáo làm sạch."""
        return self.report


def main(input_path: str, output_path: str, verbose: bool = True):
    """Main function để chạy data cleaning."""
    logger.info("\n" + "="*60)
    logger.info("DATA CLEANING MODULE")
    logger.info("="*60 + "\n")
    
    # Load data
    logger.info(f"📂 Đang load dữ liệu từ: {input_path}")
    df = pd.read_csv(input_path, encoding="utf-8")
    logger.info(f"✅ Load thành công: {df.shape} (rows, cols)\n")
    
    # Clean
    cleaner = DataCleaner(df, verbose=verbose)
    df_cleaned, report = cleaner.clean_all(
        handle_missing=True,
        handle_outliers=True,
        handle_duplicates=True,
    )
    
    # Save
    cleaner.save_cleaned_data(output_path, save_report=True)
    
    return df_cleaned, report


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 2:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
    else:
        input_path = "data/raw/students.csv"
        output_path = "data/raw/students_cleaned.csv"
    
    main(input_path, output_path, verbose=True)



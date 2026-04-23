#!/usr/bin/env python3
"""
Script debug: Kiểm tra giá trị score từ predictor + format kết quả
So sánh: score model vs score final + hiển thị tên ngành
"""
import json
from utils.predictor import load_predictor
from utils.constants import MAJOR_DISPLAY, SUGGESTION_VI

def test_score_calculation():
    """Test tính toán score với dữ liệu mẫu."""
    print("=" * 70)
    print("DEBUG: KIỂM TRA TÍNH TOÁN SCORE")
    print("=" * 70)
    
    # Load predictor
    try:
        predictor = load_predictor()
        print("✓ Predictor loaded successfully")
    except Exception as e:
        print(f"✗ Error loading predictor: {e}")
        return
    
    # Dữ liệu mẫu (Tech)
    test_data = {
        "so_thich_chinh": "Cong nghe",
        "mon_hoc_yeu_thich": "Tin hoc",
        "ky_nang_noi_bat": "Phan tich",
        "tinh_cach": "Ti mi",
        "moi_truong_lam_viec_mong_muon": "Ky thuat",
        "muc_tieu_nghe_nghiep": "Thu nhap cao",
        "mo_ta_ban_than": "Em thich may tinh, logic va phan tich du lieu.",
        "dinh_huong_tuong_lai": "Em muon hoc AI, data hoac phat trien phan mem.",
    }
    
    print("\n📋 Test Data:")
    print(json.dumps(test_data, ensure_ascii=False, indent=2))
    
    # Predict
    print("\n🔄 Predicting...")
    try:
        result = predictor.predict(test_data)
    except Exception as e:
        print(f"✗ Prediction error: {e}")
        return
    
    # Hiển thị Top 3
    print("\n✅ RESULT - TOP 3:")
    print("-" * 70)
    
    for idx, item in enumerate(result.get("top_3", []), 1):
        major = item.get("major", "N/A")
        score = item.get("score", 0)
        score_model = item.get("score_model", 0)
        score_criteria = item.get("score_criteria", 0)
        score_relative = item.get("score_relative", 0)
        raw_score = item.get("raw_score", 0)
        
        print(f"\n#{idx} {major}")
        print(f"  score (final)         = {score}%")
        print(f"  score_model (70%)     = {score_model}%")
        print(f"  score_criteria (30%)  = {score_criteria}%")
        print(f"  score_relative        = {score_relative}%")
        print(f"  raw_score             = {raw_score}")
        
        # Kiểm tra công thức
        calculated = 0.7 * score_model + 0.3 * score_criteria
        print(f"  ✓ Check: 0.7×{score_model} + 0.3×{score_criteria} = {calculated:.2f}")
    
    print("\n" + "=" * 70)
    print("DEBUG: Các Top 5 (thô):")
    print("-" * 70)
    
    for idx, item in enumerate(result.get("top_5_diem_tho", []), 1):
        major = item.get("nganh", "N/A")
        diem_tho = item.get("diem_tho", 0)
        diem_model = item.get("diem_model", 0)
        diem_tieu_chi = item.get("diem_tieu_chi", 0)
        
        print(f"#{idx} {major}: thô={diem_tho:.4f}, model={diem_model:.2f}%, criteria={diem_tieu_chi:.2f}%")
    
    print("\n" + "=" * 70)
    print("✅ DEBUG HOÀN THÀNH!")
    print("=" * 70)

if __name__ == "__main__":
    test_score_calculation()

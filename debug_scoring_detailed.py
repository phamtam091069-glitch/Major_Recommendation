"""
Debug script để trace chi tiết scoring cho hồ sơ người dùng.
Từ hình ảnh người dùng gửi:
- Sở thích chính: Nghề thuật
- Môn học yêu thích: Toán
- Kỹ năng nổi bật: Tổ chức & lập kế hoạch
- Tính cách: Thi mị
- Môi trường làm việc: Linh hoạt
- Mục tiêu nghề nghiệp: Theo đam mê
- Mô tả bản thân: Em thích về trí sáng tạo cao, thích tìm hiểu điều mới mẻ
- Định hướng tương lai: Em muốn làm trong ngành thiết kế
"""

import json
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger(__name__)

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.predictor import Predictor, load_predictor
from utils.features import row_dict_from_payload
import pandas as pd

def debug_score():
    """Debug hồ sơ cụ thể."""
    
    print("=" * 80)
    print("DEBUG SCORING - CHẨN ĐOÁN VẤN ĐỀ")
    print("=" * 80)
    
    # Hồ sơ từ hình ảnh
    payload = {
        "so_thich_chinh": "Nghe thuat",  # Sơ thích chính = Nghề thuật
        "mon_hoc_yeu_thich": "Toan",  # Toán
        "ky_nang_noi_bat": "To chuc va lap ke hoach",  # Tổ chức & lập kế hoạch
        "tinh_cach": "Thi mi",  # Thi mị
        "moi_truong_lam_viec": "Linh hoat",  # Linh hoạt
        "muc_tieu_nghe_nghiep": "Theo dam me",  # Theo đam mê
        "mo_ta_ban_than": "Em thich ve tri sang tao cao, thich tim hieu dieu moi me",  # Mô tả
        "dinh_huong_tuong_lai": "Em muon lam trong nganh thiet ke",  # Định hướng = Thiết kế
    }
    
    print("\n📋 INPUT PAYLOAD:")
    for key, val in payload.items():
        print(f"  {key}: {val}")
    
    # Load predictor
    print("\n⏳ Loading predictor...")
    try:
        predictor = load_predictor()
        print(f"✅ Predictor loaded successfully")
    except Exception as e:
        print(f"❌ Error loading predictor: {e}")
        return
    
    # Predict
    print("\n🔍 Running prediction...")
    try:
        result = predictor.predict(payload)
    except Exception as e:
        print(f"❌ Error in prediction: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Display results
    print("\n" + "=" * 80)
    print("📊 KẾT QUẢ (Top 3 Ngành):")
    print("=" * 80)
    
    for i, item in enumerate(result.get("top_3", []), 1):
        major_key = item.get("major_key", "???")
        major_display = item.get("major", "???")
        score = item.get("score", 0)
        score_model = item.get("score_model", 0)
        score_criteria = item.get("score_criteria", 0)
        confidence = item.get("confidence_score", 0)
        
        print(f"\n#{i} 🎯 {major_display}")
        print(f"   Major key: {major_key}")
        print(f"   ├─ Final Score:     {score:.2f}%")
        print(f"   ├─ Model Score:     {score_model:.2f}% (30% weight)")
        print(f"   ├─ Criteria Score:  {score_criteria:.2f}% (70% weight)")
        print(f"   ├─ Confidence:      {confidence:.2f}%")
        print(f"   └─ Feedback: {item.get('feedback', 'N/A')}")
    
    # Detailed scoring breakdown
    print("\n" + "=" * 80)
    print("🔬 DETAILED SCORING BREAKDOWN (All Majors):")
    print("=" * 80)
    
    all_scores = result.get("all_scores", {})
    
    # Sort by final score descending
    sorted_majors = sorted(
        all_scores.items(),
        key=lambda x: x[1].get("score", 0),
        reverse=True
    )
    
    print(f"\n{'Rank':<5} {'Ngành':<40} {'Model':<8} {'Criteria':<8} {'Final':<8} {'Conf':<8}")
    print("-" * 80)
    
    for rank, (major_key, scores) in enumerate(sorted_majors, 1):
        major_display = scores.get("major_display", major_key)
        model_score = scores.get("score_model", 0)
        criteria_score = scores.get("score_criteria", 0)
        final_score = scores.get("score", 0)
        confidence = scores.get("confidence", 0)
        
        # Truncate major name if too long
        if len(major_display) > 40:
            major_display = major_display[:37] + "..."
        
        print(f"{rank:<5} {major_display:<40} {model_score:>6.2f}% {criteria_score:>6.2f}% {final_score:>6.2f}% {confidence:>6.2f}%")
    
    # Analyze why "Thiết kế" is not top 1
    print("\n" + "=" * 80)
    print("🔍 ANALYSIS - TẠI SAO 'THIẾT KẾ' KHÔNG PHẢI TOP 1?")
    print("=" * 80)
    
    # Find design-related majors
    design_keywords = ["thiet ke", "design", "sang tao", "creative", "my thuat"]
    design_majors = {}
    
    for major_key, scores in all_scores.items():
        major_display = scores.get("major_display", major_key)
        if any(kw in major_key.lower() or kw in major_display.lower() for kw in design_keywords):
            design_majors[major_key] = scores
    
    if design_majors:
        print(f"\n🎨 Design-related majors found ({len(design_majors)}):")
        for major_key, scores in sorted(design_majors.items(), key=lambda x: x[1].get("score", 0), reverse=True):
            print(f"  • {scores.get('major_display', major_key)}: {scores.get('score', 0):.2f}%")
    else:
        print("\n⚠️  NO design-related majors found in database!")
        print("   This might be the root cause!")
    
    # Check criteria scoring
    print("\n" + "=" * 80)
    print("📐 CRITERIA SCORE DETAILS (for top 3 majors):")
    print("=" * 80)
    
    for i, (major_key, scores) in enumerate(sorted_majors[:3], 1):
        print(f"\n#{i} {scores.get('major_display', major_key)}")
        criteria_detail = scores.get("criteria_detail", {})
        for field, weight in criteria_detail.items():
            print(f"  {field}: {weight:.2f}")
    
    # Input features analysis
    print("\n" + "=" * 80)
    print("🧬 INPUT FEATURE ANALYSIS:")
    print("=" * 80)
    
    # Get profile text
    from utils.features import build_profile_text
    profile_text = build_profile_text(payload)
    print(f"\nProfile text for TF-IDF: {profile_text}")
    
    print("\n" + "=" * 80)
    print("✅ Debug complete!")
    print("=" * 80)

if __name__ == "__main__":
    debug_score()

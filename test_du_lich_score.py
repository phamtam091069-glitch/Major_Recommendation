"""Test score calculation for Du lịch profile after retraining"""
from utils.predictor import load_predictor

# Test data: Du lịch profile
test_data = {
    "so_thich_chinh": "Du lich",
    "mon_hoc_yeu_thich": "Anh",
    "ky_nang_noi_bat": "Giao tiep",
    "tinh_cach": "Huong ngoai",
    "moi_truong_lam_viec_mong_muon": "Linh hoat",
    "muc_tieu_nghe_nghiep": "Theo dam me",
    "mo_ta_ban_than": "Em thich khám phá văn hóa và giới thiệu địa điểm mới cho mọi người.",
    "dinh_huong_tuong_lai": "Em muốn làm hướng dẫn viên hoặc điều hành tour.",
}

predictor = load_predictor()
result = predictor.predict(test_data)

print("=" * 70)
print("Test: Du lịch profile score after retrain")
print("=" * 70)

for idx, item in enumerate(result.get("top_3", [])):
    major = item.get("nganh", "N/A")
    score_final = item.get("score_final", 0)
    score_model = item.get("score_model", 0)
    score_criteria = item.get("score_criteria", 0)
    
    print(f"\n#{idx + 1}. {major}")
    print(f"   Điểm cuối: {score_final}")
    print(f"   Điểm model (60%): {score_model}")
    print(f"   Điểm tiêu chí (40%): {score_criteria}")
    print(f"   Kiểm tra: 0.6 × {score_model} + 0.4 × {score_criteria} = {0.6 * score_model + 0.4 * score_criteria:.2f}")

print("\n" + "=" * 70)
print("Summary: Check if Du lịch is now ranked higher")
print("=" * 70)

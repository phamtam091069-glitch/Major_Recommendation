"""
Debug predictor kết quả thô để xem cấu trúc dữ liệu.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.predictor import load_predictor

def debug():
    payload = {
        "so_thich_chinh": "Nghe thuat",
        "mon_hoc_yeu_thich": "Toan",
        "ky_nang_noi_bat": "To chuc va lap ke hoach",
        "tinh_cach": "Thi mi",
        "moi_truong_lam_viec": "Linh hoat",
        "muc_tieu_nghe_nghiep": "Theo dam me",
        "mo_ta_ban_than": "Em thich ve tri sang tao cao, thich tim hieu dieu moi me",
        "dinh_huong_tuong_lai": "Em muon lam trong nganh thiet ke",
    }
    
    print("=" * 80)
    print("RAW PREDICTOR OUTPUT")
    print("=" * 80)
    
    predictor = load_predictor()
    result = predictor.predict(payload)
    
    print("\n📦 FULL RESULT STRUCTURE:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("KEYS IN RESULT:")
    print(f"  {list(result.keys())}")
    
    print("\n" + "=" * 80)
    print("TOP_3 ITEMS:")
    for i, item in enumerate(result.get("top_3", []), 1):
        print(f"\n  Item #{i}:")
        print(f"    Keys: {list(item.keys())}")
        for key, val in item.items():
            if isinstance(val, dict):
                print(f"    {key}: {list(val.keys())}")
            else:
                print(f"    {key}: {val}")

if __name__ == "__main__":
    debug()

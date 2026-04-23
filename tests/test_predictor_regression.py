from utils.predictor import CRITERIA_WEIGHTS, load_predictor


def test_criteria_weights_match_current_priority_config():
    assert CRITERIA_WEIGHTS == {
        "so_thich_chinh": 0.23,
        "mon_hoc_yeu_thich": 0.08,
        "ky_nang_noi_bat": 0.16,
        "tinh_cach": 0.14,
        "moi_truong_lam_viec_mong_muon": 0.12,
        "muc_tieu_nghe_nghiep": 0.03,
        "mo_ta_ban_than": 0.04,
        "dinh_huong_tuong_lai": 0.20,
    }
    assert round(sum(CRITERIA_WEIGHTS.values()), 2) == 1.00


def test_predictor_prioritizes_data_profile_over_unrelated_health_major():
    predictor = load_predictor()

    payload = {
        "so_thich_chinh": "Cong nghe",
        "mon_hoc_yeu_thich": "Toan",
        "ky_nang_noi_bat": "Phan tich du lieu",
        "tinh_cach": "Ti mi",
        "moi_truong_lam_viec_mong_muon": "Van phong",
        "muc_tieu_nghe_nghiep": "Phat trien chuyen mon",
        "mo_ta_ban_than": "Em thich lam viec voi so lieu va tim ra quy luat trong du lieu.",
        "dinh_huong_tuong_lai": "Em muon tro thanh Data Scientist hoac Business Analyst.",
    }

    result = predictor.predict(payload)
    top_majors = [item["nganh"] for item in result["top_3"]]

    assert top_majors[0] == "Khoa hoc du lieu"
    assert "Cong nghe thong tin" in top_majors
    assert "He thong thong tin" in top_majors
    assert "Vat ly tri lieu va phuc hoi chuc nang" not in top_majors

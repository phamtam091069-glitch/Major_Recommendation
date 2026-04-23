"""
Debug script to identify scoring discrepancy issues.
Tests each component of the prediction pipeline.
"""

import json
import sys
import io
from pathlib import Path
import pandas as pd

# Fix UTF-8 encoding for Vietnamese text
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from utils.predictor import load_predictor
from utils.features import row_dict_from_payload
from utils.constants import MAJOR_DISPLAY, SUGGESTION_VI, CATEGORICAL_COLS, TEXT_COLS

# Test data - user input with high preference for interior design
TEST_PAYLOAD = {
    "so_thich_chinh": "Nghệ thuật",
    "mon_hoc_yeu_thich": "Văn",
    "ky_nang_noi_bat": "Sáng tạo",
    "tinh_cach": "Tỉ mỉ",
    "moi_truong_lam_viec_mong_muon": "Linh hoạt",
    "muc_tieu_nghe_nghiep": "Theo đam mê",
    "mo_ta_ban_than": "Em thích thiết kế nội thất, lên kế hoạch bố cục không gian một cách chi tiết.",
    "dinh_huong_tuong_lai": "Em muốn trở thành designer nội thất chuyên nghiệp."
}

def normalize_payload(payload):
    """Normalize payload using same logic as app.py"""
    return row_dict_from_payload(payload)

def test_input_normalization():
    """Test 1: Input Normalization"""
    print("\n" + "="*80)
    print("TEST 1: INPUT NORMALIZATION")
    print("="*80)
    
    normalized = normalize_payload(TEST_PAYLOAD)
    print(f"\n✓ Normalized payload:")
    for key, value in normalized.items():
        print(f"  {key}: {value}")
    
    return normalized

def test_feature_extraction(predictor, normalized_data):
    """Test 2: Feature Extraction"""
    print("\n" + "="*80)
    print("TEST 2: FEATURE EXTRACTION")
    print("="*80)
    
    # Convert dict to DataFrame for OHE transformer
    df = pd.DataFrame([normalized_data])
    
    # Test OneHot encoding
    print("\n✓ Testing OneHot Encoding (6 categorical fields):")
    try:
        ohe_features = predictor.ohe.transform(
            df[["so_thich_chinh", "mon_hoc_yeu_thich", "ky_nang_noi_bat", 
                           "tinh_cach", "moi_truong_lam_viec_mong_muon", "muc_tieu_nghe_nghiep"]]
        )
        print(f"  Shape: {ohe_features.shape}")
        print(f"  Sparse matrix density: {ohe_features.nnz / (ohe_features.shape[0] * ohe_features.shape[1]):.2%}")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return None
    
    # Test TF-IDF encoding  
    print("\n✓ Testing TF-IDF Vectorization (2 text fields):")
    text_data = normalized_data["mo_ta_ban_than"] + " " + normalized_data["dinh_huong_tuong_lai"]
    try:
        tfidf_features = predictor.tfidf.transform([text_data])
        print(f"  Text: '{text_data[:80]}...'")
        print(f"  Shape: {tfidf_features.shape}")
        print(f"  Sparse matrix density: {tfidf_features.nnz / (tfidf_features.shape[0] * tfidf_features.shape[1]):.2%}")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return None
    
    return ohe_features, tfidf_features, text_data

def test_model_prediction(predictor, normalized_data, ohe_features, tfidf_features):
    """Test 3: Model Prediction"""
    print("\n" + "="*80)
    print("TEST 3: MODEL PREDICTIONS")
    print("="*80)
    
    # Get raw model probability
    import numpy as np
    from scipy.sparse import hstack
    
    combined_features = hstack([ohe_features, tfidf_features])
    
    print(f"\n✓ Combined feature shape: {combined_features.shape}")
    print(f"  Total features: {combined_features.shape[1]}")
    
    try:
        # Get probability predictions
        proba = predictor.model.predict_proba(combined_features)[0]
        
        print(f"\n✓ Model probability output (top 10 majors):")
        top_indices = np.argsort(proba)[::-1][:10]
        for idx in top_indices:
            major_key = predictor.major_names[idx]
            major_display = MAJOR_DISPLAY.get(major_key, major_key)
            prob = proba[idx]
            print(f"  {idx:2d}. {major_display:40s} = {prob:.4f}")
            
        # Find interior design rank
        interior_design_idx = predictor.major_names.index("Thiet ke noi that")
        interior_prob = proba[interior_design_idx]
        print(f"\n  💡 Interior Design (Thiet ke noi that):")
        print(f"     Rank: {np.argsort(proba)[::-1].tolist().index(interior_design_idx) + 1} / {len(proba)}")
        print(f"     Probability: {interior_prob:.4f}")
        
        return proba
        
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_criteria_scoring(normalized_data):
    """Test 4: Criteria Scoring"""
    print("\n" + "="*80)
    print("TEST 4: CRITERIA SCORING (8 weights)")
    print("="*80)
    
    # Criteria weights from README
    weights = {
        "so_thich_chinh": 0.23,
        "dinh_huong_tuong_lai": 0.20,
        "ky_nang_noi_bat": 0.16,
        "tinh_cach": 0.14,
        "moi_truong_lam_viec_mong_muon": 0.12,
        "mon_hoc_yeu_thich": 0.08,
        "mo_ta_ban_than": 0.04,
        "muc_tieu_nghe_nghiep": 0.03
    }
    
    print(f"\n✓ Criteria Weights:")
    total_weight = 0
    for field, weight in weights.items():
        print(f"  {field:35s} = {weight:5.2%}")
        total_weight += weight
    print(f"  {'TOTAL':35s} = {total_weight:5.2%}")
    
    print(f"\n✓ Your Input Values:")
    for field in weights.keys():
        value = normalized_data.get(field, "")
        preview = str(value)[:60]
        print(f"  {field:35s} = {preview}")
    
    return weights

def test_full_prediction(predictor, normalized_data):
    """Test 5: Full Prediction Pipeline"""
    print("\n" + "="*80)
    print("TEST 5: FULL PREDICTION (End-to-End)")
    print("="*80)
    
    try:
        result = predictor.predict(normalized_data)
        
        print(f"\n✓ Prediction Result:")
        print(f"  Total majors ranked: {len(result.get('top_3', []))}")
        
        top_3 = result.get("top_3", [])
        for i, item in enumerate(top_3, 1):
            major_key = item.get("nganh", "")
            major_display = MAJOR_DISPLAY.get(major_key, major_key)
            score = item.get("score", 0)
            score_model = item.get("score_model", 0)
            score_criteria = item.get("score_criteria", 0)
            
            print(f"\n  {i}. {major_display}")
            print(f"     Score: {score:.2f}")
            print(f"     Model Score: {score_model:.4f}")
            print(f"     Criteria Score: {score_criteria:.4f}")
            print(f"     Formula: 0.6 × {score_model:.4f} + 0.4 × {score_criteria:.4f} = {score:.2f}")
        
        # Check formula correctness
        print(f"\n✓ Verifying Formula: 0.6 × model_score + 0.4 × criteria_score")
        for i, item in enumerate(top_3, 1):
            score_model = float(item.get("score_model", 0))
            score_criteria = float(item.get("score_criteria", 0))
            score_actual = float(item.get("score", 0))
            score_calculated = 0.6 * score_model + 0.4 * score_criteria
            
            match = "✓" if abs(score_actual - score_calculated) < 0.01 else "✗"
            print(f"  {match} Item {i}: {score_actual:.2f} vs calculated {score_calculated:.2f}")
        
        return result
        
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_interior_design_specifically(predictor, normalized_data):
    """Test 6: Specific test for Interior Design"""
    print("\n" + "="*80)
    print("TEST 6: INTERIOR DESIGN SCORING ANALYSIS")
    print("="*80)
    
    print("\n✓ Input Analysis:")
    print(f"  So thich chinh: {normalized_data.get('so_thich_chinh')} (should match 'Nghệ thuật')")
    print(f"  Ky nang noi bat: {normalized_data.get('ky_nang_noi_bat')} (should match 'Sáng tạo')")
    print(f"  Tinh cach: {normalized_data.get('tinh_cach')} (should match 'Tỉ mỉ')")
    print(f"  Mo ta ban than: contains 'thiết kế nội thất'?", 
          "thiết kế nội thất" in normalized_data.get('mo_ta_ban_than', '').lower())
    print(f"  Dinh huong tuong lai: contains 'designer nội thất'?",
          "designer nội thất" in normalized_data.get('dinh_huong_tuong_lai', '').lower())
    
    print("\n✓ Expected Scoring:")
    print("  - So thich chinh (Nghe thuat): 23% weight → Should match interior design")
    print("  - Ky nang noi bat (Sang tao): 16% weight → Should match interior design")
    print("  - Tinh cach (Tinh mi): 14% weight → Should match interior design")
    print("  - Text similarity: TF-IDF should find 'thiet ke noi that' keywords")
    
    print("\n✓ Expected Result:")
    print("  Interior Design should rank TOP 1-2 with HIGH score (>70%)")

def main():
    print("\n" + "="*80)
    print("SCORING DISCREPANCY DEBUG - COMPLETE PIPELINE")
    print("="*80)
    print(f"Test Profile: {json.dumps(TEST_PAYLOAD, ensure_ascii=False, indent=2)}")
    
    # Load predictor
    try:
        predictor = load_predictor()
        print("✓ Model loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load model: {e}")
        return
    
    # Run tests
    normalized_data = test_input_normalization()
    if normalized_data is None:
        return
    
    features = test_feature_extraction(predictor, normalized_data)
    if features is None:
        return
    
    ohe_features, tfidf_features, text_data = features
    
    proba = test_model_prediction(predictor, normalized_data, ohe_features, tfidf_features)
    if proba is None:
        return
    
    criteria_weights = test_criteria_scoring(normalized_data)
    
    result = test_full_prediction(predictor, normalized_data)
    if result is None:
        return
    
    test_interior_design_specifically(predictor, normalized_data)
    
    # Summary
    print("\n" + "="*80)
    print("DEBUG SUMMARY")
    print("="*80)
    print("""
✓ All components tested:
  1. Input Normalization - Check if fields mapped correctly
  2. Feature Extraction - Check OneHot & TF-IDF shapes
  3. Model Predictions - Check probabilities
  4. Criteria Scoring - Check weights sum to 100%
  5. Full Pipeline - Check formula correctness
  6. Interior Design - Check why score is low
  
Check if:
  - Model probability for Interior Design is low (model issue)
  - Criteria score calculation is wrong (weighting issue)
  - Formula application is incorrect (0.6/0.4 split issue)
  - Text matching not working (TF-IDF issue)
    """)

if __name__ == "__main__":
    main()

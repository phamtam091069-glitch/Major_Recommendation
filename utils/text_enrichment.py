"""
Text Enrichment Module - Using Deepseek Fallback API
Enriches empty or insufficient text fields (mo_ta_ban_than, dinh_huong_tuong_lai)
by calling Deepseek API based on categorical features.
"""

import logging
from typing import Any, Dict, Optional, Mapping

from .constants import CATEGORICAL_COLS, TEXT_COLS
from .deepseek_fallback_api import get_deepseek_fallback_api

logger = logging.getLogger(__name__)


def check_text_fields_empty(row: Mapping[str, Any]) -> bool:
    """
    Check if text fields are empty or below minimum threshold.
    
    Args:
        row: Student data row with text fields
        
    Returns:
        True if text fields need enrichment, False otherwise
    """
    for col in TEXT_COLS:
        text = str(row.get(col, "")).strip()
        # If ANY text field has meaningful content (>10 chars), don't enrich
        if len(text) > 10:
            return False
    
    return True


def build_enrichment_prompt(row: Mapping[str, Any]) -> str:
    """
    Build a prompt for Deepseek API to generate enriched text fields.
    
    Args:
        row: Student data row with categorical features
        
    Returns:
        Prompt string for Deepseek API
    """
    # Extract categorical features
    features = {}
    for col in CATEGORICAL_COLS:
        val = str(row.get(col, "")).strip()
        if val and val.lower() != "khong xac dinh":
            features[col] = val
    
    prompt = """Bạn là một cố vấn tư vấn ngành học chuyên nghiệp. 
Dựa trên thông tin sau của học sinh, hãy tạo ra 2 đoạn text ngắn (mỗi đoạn 2-3 câu):

1. **Mô tả bản thân**: Mô tả tính cách, sở thích và điểm mạnh của học sinh dựa trên các thông tin đã cho
2. **Định hướng tương lai**: Mô tả mục tiêu sự nghiệp và con đường phát triển mà học sinh hướng tới

Thông tin học sinh:
"""
    
    if "so_thich_chinh" in features:
        prompt += f"- Sở thích chính: {features['so_thich_chinh']}\n"
    if "mon_hoc_yeu_thich" in features:
        prompt += f"- Môn học yêu thích: {features['mon_hoc_yeu_thich']}\n"
    if "ky_nang_noi_bat" in features:
        prompt += f"- Kỹ năng nổi bật: {features['ky_nang_noi_bat']}\n"
    if "tinh_cach" in features:
        prompt += f"- Tính cách: {features['tinh_cach']}\n"
    if "moi_truong_lam_viec_mong_muon" in features:
        prompt += f"- Môi trường làm việc mong muốn: {features['moi_truong_lam_viec_mong_muon']}\n"
    if "muc_tieu_nghe_nghiep" in features:
        prompt += f"- Mục tiêu nghề nghiệp: {features['muc_tieu_nghe_nghiep']}\n"
    
    prompt += """
Trả lời theo định dạng sau (KHÔNG thêm bất kỳ text nào khác):

[MÔ TẢ BẢN THÂN]
<2-3 câu mô tả bản thân>

[ĐỊNH HƯỚNG TƯƠNG LAI]
<2-3 câu về mục tiêu sự nghiệp>"""
    
    return prompt


def parse_enrichment_response(response_text: str) -> Dict[str, str]:
    """
    Parse Deepseek API response to extract enriched text fields.
    
    Args:
        response_text: Response from Deepseek API
        
    Returns:
        Dict with keys: 'mo_ta_ban_than', 'dinh_huong_tuong_lai'
    """
    result = {
        "mo_ta_ban_than": "",
        "dinh_huong_tuong_lai": ""
    }
    
    try:
        # Split by section headers
        lines = response_text.strip().split("\n")
        current_section = None
        section_content = []
        
        for line in lines:
            line = line.strip()
            
            if "[MÔ TẢ BẢN THÂN]" in line or "MO TA BAN THAN" in line:
                # Save previous section
                if current_section and section_content:
                    content = " ".join(section_content).strip()
                    if current_section == "self":
                        result["mo_ta_ban_than"] = content
                    elif current_section == "future":
                        result["dinh_huong_tuong_lai"] = content
                
                current_section = "self"
                section_content = []
            
            elif "[ĐỊNH HƯỚNG TƯƠNG LAI]" in line or "DINH HUONG TUONG LAI" in line:
                # Save previous section
                if current_section and section_content:
                    content = " ".join(section_content).strip()
                    if current_section == "self":
                        result["mo_ta_ban_than"] = content
                    elif current_section == "future":
                        result["dinh_huong_tuong_lai"] = content
                
                current_section = "future"
                section_content = []
            
            elif current_section and line and not line.startswith("["):
                section_content.append(line)
        
        # Save last section
        if current_section and section_content:
            content = " ".join(section_content).strip()
            if current_section == "self":
                result["mo_ta_ban_than"] = content
            elif current_section == "future":
                result["dinh_huong_tuong_lai"] = content
        
        logger.info(f"✓ Parsed enriched text: mo_ta_ban_than={len(result['mo_ta_ban_than'])}ch, dinh_huong_tuong_lai={len(result['dinh_huong_tuong_lai'])}ch")
        
        return result
    
    except Exception as e:
        logger.error(f"✗ Failed to parse enrichment response: {e}")
        return result


def enrich_text_fields(row: Mapping[str, Any]) -> Dict[str, str]:
    """
    Enrich empty text fields using Deepseek API.
    
    Args:
        row: Student data row
        
    Returns:
        Dict with enriched text fields, or empty dict if enrichment failed
    """
    # Check if enrichment is needed
    if not check_text_fields_empty(row):
        logger.debug("Text fields have sufficient content, skipping enrichment")
        return {}
    
    logger.info("Enriching empty text fields via Deepseek API...")
    
    try:
        # Build prompt
        prompt = build_enrichment_prompt(row)
        
        # Call Deepseek API
        api = get_deepseek_fallback_api()
        response = api.analyze_free_text(
            user_text=prompt,
            context="text_enrichment"
        )
        
        if not response.get("success"):
            logger.warning(f"✗ Deepseek API call failed: {response.get('error', 'Unknown error')}")
            return {}
        
        # Parse response
        enriched = parse_enrichment_response(response.get("response", ""))
        
        if enriched.get("mo_ta_ban_than") or enriched.get("dinh_huong_tuong_lai"):
            logger.info(f"✓ Text enrichment successful")
            return enriched
        else:
            logger.warning("✗ Enrichment response was empty or unparseable")
            return {}
    
    except Exception as e:
        logger.error(f"✗ Text enrichment error: {e}", exc_info=True)
        return {}


def get_enriched_row(row: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Get row with enriched text fields if needed.
    
    Args:
        row: Original student data row
        
    Returns:
        Row dict with enriched text fields (if enrichment was applied)
    """
    # Convert to dict if needed
    row_dict = dict(row) if not isinstance(row, dict) else row.copy()
    
    # Try to enrich if needed
    if check_text_fields_empty(row):
        enriched = enrich_text_fields(row)
        if enriched:
            # Update with enriched values
            row_dict.update(enriched)
            row_dict["_enriched"] = True
    
    return row_dict

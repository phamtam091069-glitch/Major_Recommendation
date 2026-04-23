#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate a detailed block diagram of the prediction module as PNG using PIL
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_prediction_diagram():
    """Create a detailed diagram showing the prediction module flow"""
    
    # Image dimensions
    width = 1600
    height = 2400
    bg_color = (255, 255, 255)
    
    # Create image
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to load fonts, fallback to default
    try:
        title_font = ImageFont.truetype("arial.ttf", 24)
        heading_font = ImageFont.truetype("arial.ttf", 18)
        text_font = ImageFont.truetype("arial.ttf", 14)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        title_font = ImageFont.load_default()
        heading_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Colors
    color_input = (255, 228, 181)      # Peach
    color_process = (180, 215, 255)    # Light blue
    color_calc = (215, 255, 180)       # Light green
    color_criteria = (255, 215, 180)   # Light orange
    color_boost = (215, 180, 255)      # Light purple
    color_blend = (255, 180, 215)      # Light pink
    color_output = (180, 255, 215)     # Light cyan
    color_final = (144, 238, 144)      # Light green (final)
    
    text_color = (0, 0, 0)
    border_color = (50, 50, 50)
    arrow_color = (100, 100, 100)
    
    def draw_box(x, y, width, height, text, color, is_important=False):
        """Draw a rounded rectangle box with text"""
        border_width = 3 if is_important else 2
        draw.rectangle([x, y, x + width, y + height], fill=color, outline=border_color, width=border_width)
        
        # Draw text with word wrapping
        lines = text.split('\n')
        line_height = 18
        total_height = len(lines) * line_height
        start_y = y + (height - total_height) // 2
        
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=text_font)
            text_width = bbox[2] - bbox[0]
            text_x = x + (width - text_width) // 2
            text_y = start_y + i * line_height
            draw.text((text_x, text_y), line, fill=text_color, font=text_font)
        
        return y + height
    
    def draw_arrow(x1, y1, x2, y2, label=""):
        """Draw an arrow between two points"""
        draw.line([(x1, y1), (x2, y2)], fill=arrow_color, width=2)
        
        # Arrow head
        arrow_size = 10
        if y2 > y1:  # Downward arrow
            draw.polygon([(x2, y2), (x2 - arrow_size, y2 - arrow_size), (x2 + arrow_size, y2 - arrow_size)], fill=arrow_color)
        
        # Label
        if label:
            bbox = draw.textbbox((0, 0), label, font=small_font)
            text_width = bbox[2] - bbox[0]
            draw.text((x1 + (x2 - x1 - text_width) // 2, (y1 + y2) // 2 - 10), label, fill=arrow_color, font=small_font)
    
    y_pos = 20
    
    # Title
    draw.text((width // 2 - 250, y_pos), "SƠ ĐỒ CHI TIẾT MODULE PREDICTION", fill=text_color, font=title_font)
    y_pos += 50
    
    # Input section
    draw.text((50, y_pos), "📥 BƯỚC 1: DỮ LIỆU ĐẦU VÀO", fill=text_color, font=heading_font)
    y_pos += 40
    
    draw_box(50, y_pos, 700, 80, "TRƯỜNG CATEGORICAL\n(6 fields)\n• Sở thích • Môn học • Tính cách\n• Kỹ năng • Môi trường • Mục tiêu", color_input)
    y_pos += 100
    
    draw_arrow(400, y_pos - 80, 400, y_pos)
    
    draw_box(50, y_pos, 700, 60, "TRƯỜNG TEXT (2 fields)\n• Mô tả bản thân • Định hướng tương lai", color_input)
    y_pos += 80
    
    # Feature Engineering section
    draw.text((50, y_pos), "⚙️ BƯỚC 2: FEATURE ENGINEERING", fill=text_color, font=heading_font)
    y_pos += 40
    
    draw_arrow(200, y_pos - 60, 200, y_pos)
    draw_arrow(600, y_pos - 60, 600, y_pos)
    
    draw_box(50, y_pos, 300, 80, "ONE-HOT\nENCODING\n(Categorical → Vector)", color_process)
    draw_box(450, y_pos, 300, 80, "TF-IDF\nVECTORIZATION\n(Text → Vector)", color_process)
    y_pos += 100
    
    draw_arrow(200, y_pos - 80, 400, y_pos)
    draw_arrow(600, y_pos - 80, 400, y_pos)
    
    draw_box(250, y_pos, 300, 60, "🎯 FEATURE VECTOR\n(One-hot + TF-IDF)", color_process)
    y_pos += 80
    
    # Three scoring branches
    draw.text((50, y_pos), "📊 BƯỚC 3: TÍNH ĐIỂM (3 thành phần)", fill=text_color, font=heading_font)
    y_pos += 40
    
    draw_arrow(400, y_pos - 40, 200, y_pos)
    draw_arrow(400, y_pos - 40, 400, y_pos)
    draw_arrow(400, y_pos - 40, 600, y_pos)
    
    # Model Score (30%)
    draw_box(50, y_pos, 300, 100, "⚙️ MODEL SCORE\n(30% weight)\nRandomForest + TF-IDF\nCosine Similarity", color_calc)
    
    # Criteria Score (40%)
    draw_box(375, y_pos, 300, 100, "📐 CRITERIA SCORE\n(40% weight)\n8 Tiêu chí minh bạch\nWeighted sum", color_criteria)
    
    # Rule Boost (30%)
    draw_box(700, y_pos, 300, 100, "🔧 RULE BOOST\n(30% weight)\nTech/Language/Education\nSignal detection", color_boost)
    
    y_pos += 120
    
    # Detailed criteria breakdown
    draw.text((50, y_pos), "📋 Chi tiết 8 Tiêu chí:", fill=text_color, font=text_font)
    y_pos += 30
    
    criteria_text = """
    1. Sở thích chính: 23%          5. Môi trường làm việc: 12%
    2. Định hướng tương lai: 20%   6. Môn học yêu thích: 8%
    3. Kỹ năng nổi bật: 16%         7. Mô tả bản thân: 4%
    4. Tính cách: 14%                 8. Mục tiêu nghề nghiệp: 3%
    """
    
    for line in criteria_text.strip().split('\n'):
        draw.text((70, y_pos), line, fill=text_color, font=small_font)
        y_pos += 20
    
    y_pos += 20
    
    # Blending formula
    draw.text((50, y_pos), "⚡ BƯỚC 4: BLENDING SCORES", fill=text_color, font=heading_font)
    y_pos += 40
    
    formula = "CÔNG THỨC:\nFinal_Score = 0.30 × Model_Score + 0.70 × Criteria_Score + Rule_Boost\n\nKết quả: 0-100 (Điểm cuối cho mỗi ngành)"
    
    for line in formula.split('\n'):
        draw.text((70, y_pos), line, fill=text_color, font=text_font)
        y_pos += 25
    
    y_pos += 20
    
    draw_arrow(400, y_pos - 100, 400, y_pos)
    
    draw_box(200, y_pos, 400, 80, "🎲 BLENDED SCORE\n(Kết hợp 3 thành phần)", color_blend, is_important=True)
    y_pos += 100
    
    # All majors scoring
    draw_arrow(400, y_pos - 80, 400, y_pos)
    
    draw.text((50, y_pos), "📊 BƯỚC 5: TÍNH ĐIỂM TẤT CẢ NGÀNH", fill=text_color, font=heading_font)
    y_pos += 40
    
    majors_text = "Lặp lại quy trình trên cho TẤT CẢ 15 NGÀNH\n\nCông nghệ thông tin, Khoa học dữ liệu, Quản trị kinh doanh, Marketing,\nThiết kế đồ họa, Điều dưỡng, Ngôn ngữ Anh, Luật, Sư phạm, HSTQLM,\nKế toán tài chính, Du lịch và lữ hành, Báo chí & truyền thông, Kiến trúc, Kỹ thuật cơ khí"
    
    for line in majors_text.split('\n'):
        draw.text((70, y_pos), line, fill=text_color, font=small_font)
        y_pos += 20
    
    y_pos += 20
    
    # Ranking
    draw_arrow(400, y_pos - 40, 400, y_pos)
    
    draw.text((50, y_pos), "🔢 BƯỚC 6: RANKING & TOP 3", fill=text_color, font=heading_font)
    y_pos += 40
    
    draw_box(100, y_pos, 600, 100, "1️⃣ Sắp xếp tất cả 15 ngành theo điểm (giảm dần)\n2️⃣ Chọn TOP 3 ngành có điểm cao nhất\n3️⃣ Tính Confidence Score cho mỗi ngành", color_calc)
    y_pos += 120
    
    # Confidence & Response
    draw_arrow(400, y_pos - 80, 400, y_pos)
    
    draw.text((50, y_pos), "📈 BƯỚC 7: CONFIDENCE & RESPONSE", fill=text_color, font=heading_font)
    y_pos += 40
    
    response_text = """Confidence_Score dựa trên:
    • Fit score của ngành được chọn
    • Độ tách biệt với ngành kế tiếp (ngành thứ 4)
    • Nhãn: Cao (70+) / Trung bình (50-70) / Tham khảo (<50)

Phản hồi JSON chứa:
    • major: Tên ngành hiển thị
    • score: Điểm cuối (0-100)
    • score_model: Điểm từ ML
    • score_criteria: Điểm từ tiêu chí
    • confidence_score: Độ tin cậy (0-100)
    • confidence: Nhãn mức độ
    • suggestion: Lời khuyên cho học sinh"""
    
    for line in response_text.split('\n'):
        if line.strip():
            draw.text((70, y_pos), line, fill=text_color, font=small_font)
        y_pos += 18
    
    y_pos += 30
    
    # Output
    draw_arrow(400, y_pos - 40, 400, y_pos)
    
    draw_box(150, y_pos, 500, 80, "✅ OUTPUT JSON\n(Top 3 + Điểm + Giải thích)", color_final, is_important=True)
    y_pos += 100
    
    draw_arrow(400, y_pos - 80, 400, y_pos)
    
    draw_box(150, y_pos, 500, 60, "📤 TRUYỀN VỀ FRONTEND\n(Hiển thị UI cho người dùng)", color_final, is_important=True)
    
    # Save image
    output_path = Path(__file__).parent / "prediction_module_diagram.png"
    img.save(str(output_path), 'PNG')
    print(f"✅ Diagram created successfully: {output_path}")
    return str(output_path)

if __name__ == '__main__':
    create_prediction_diagram()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tạo biểu đồ cấu trúc dự án dạng PNG"""

import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

# Tạo image với kích thước lớn
WIDTH = 1400
HEIGHT = 2000
BG_COLOR = (240, 245, 250)  # Light blue background
TEXT_COLOR = (30, 40, 60)  # Dark blue text
TITLE_COLOR = (0, 102, 204)  # Bright blue
SECTION_COLOR = (100, 149, 237)  # Cornflower blue
ITEM_COLOR = (70, 130, 180)  # Steel blue
FILE_COLOR = (50, 100, 150)  # Dark steel blue

img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
draw = ImageDraw.Draw(img)

# Cố gắng tải font, nếu không có thì dùng default
try:
    title_font = ImageFont.truetype("arial.ttf", 32)
    section_font = ImageFont.truetype("arial.ttf", 20)
    item_font = ImageFont.truetype("arial.ttf", 16)
    text_font = ImageFont.truetype("arial.ttf", 13)
except:
    title_font = ImageFont.load_default()
    section_font = ImageFont.load_default()
    item_font = ImageFont.load_default()
    text_font = ImageFont.load_default()

y_pos = 30

def draw_title(text, y):
    """Vẽ tiêu đề"""
    draw.text((30, y), text, fill=TITLE_COLOR, font=title_font)
    return y + 50

def draw_section(text, y):
    """Vẽ header section"""
    draw.rectangle([(20, y-5), (WIDTH-20, y+35)], fill=(200, 220, 240), outline=SECTION_COLOR, width=2)
    draw.text((40, y+5), text, fill=SECTION_COLOR, font=section_font)
    return y + 50

def draw_item(text, y, indent=0):
    """Vẽ item"""
    x_start = 50 + indent * 25
    draw.text((x_start, y), text, fill=ITEM_COLOR, font=item_font)
    return y + 30

def draw_text(text, y, indent=0):
    """Vẽ text thường"""
    x_start = 50 + indent * 25
    draw.text((x_start, y), text, fill=TEXT_COLOR, font=text_font)
    return y + 24

# Main content
y_pos = draw_title("📁 CẤU TRÚC DỰ ÁN MAJOR-RECOMMENDATION", y_pos)

# Section 1: Root Files
y_pos = draw_section("📄 ROOT FILES (Thư mục gốc)", y_pos)
y_pos = draw_item("app.py - Flask main app (1131 lines)", y_pos, 0)
y_pos = draw_item("train_model.py - Huấn luyện ML model", y_pos, 0)
y_pos = draw_item("requirements.txt - Dependencies", y_pos, 0)
y_pos = draw_item("README.md - Hướng dẫn chi tiết", y_pos, 0)
y_pos += 20

# Section 2: Data
y_pos = draw_section("📁 data/ - Dữ liệu Huấn Luyện", y_pos)
y_pos = draw_item("generate_balanced_students.py", y_pos, 1)
y_pos = draw_text("→ Tạo dữ liệu synthetic cân bằng (400-1200 mẫu/ngành)", y_pos, 2)
y_pos = draw_item("audit_dataset.py", y_pos, 1)
y_pos = draw_text("→ Kiểm tra chất lượng dữ liệu", y_pos, 2)
y_pos = draw_item("clean_data.py - Làm sạch dữ liệu", y_pos, 1)
y_pos = draw_item("majors_profiles.json - Mô tả chi tiết ngành", y_pos, 1)
y_pos = draw_item("salary_benchmarks.json - Bảng lương", y_pos, 1)
y_pos = draw_item("raw/", y_pos, 1)
y_pos = draw_text("├─ students.csv (dữ liệu chính)", y_pos, 2)
y_pos = draw_text("├─ students_balanced_400.csv", y_pos, 2)
y_pos = draw_text("└─ students_holdout.csv (test set)", y_pos, 2)
y_pos += 20

# Section 3: Models
y_pos = draw_section("📁 models/ - Trained Models & Artifacts", y_pos)
y_pos = draw_item("rf_model.pkl", y_pos, 1)
y_pos = draw_text("→ Random Forest hoặc Logistic Regression model", y_pos, 2)
y_pos = draw_item("ohe.pkl - OneHot Encoder (6 categorical cols)", y_pos, 1)
y_pos = draw_item("tfidf.pkl - TF-IDF Vectorizer (2 text cols)", y_pos, 1)
y_pos = draw_item("classes.pkl - Danh sách 15 ngành", y_pos, 1)
y_pos = draw_item("majors.json - Thông tin chi tiết ngành", y_pos, 1)
y_pos = draw_item("hybrid_config.json - Weight: 60% Model + 40% Criteria", y_pos, 1)
y_pos += 20

# Section 4: Utils
y_pos = draw_section("📁 utils/ - Modules Hỗ Trợ", y_pos)
y_pos = draw_item("predictor.py - Hybrid scoring (Model + Criteria)", y_pos, 1)
y_pos = draw_item("chatbot.py - MajorChatbot với AI fallback", y_pos, 1)
y_pos = draw_item("features.py - Feature engineering", y_pos, 1)
y_pos = draw_item("constants.py - Paths, weights, display names", y_pos, 1)
y_pos = draw_item("Fallback APIs:", y_pos, 1)
y_pos = draw_text("├─ claude_fallback_api.py", y_pos, 2)
y_pos = draw_text("├─ openai_fallback_api.py", y_pos, 2)
y_pos = draw_text("├─ deepseek_fallback_api.py", y_pos, 2)
y_pos = draw_text("└─ chiasegpu_fallback_api.py", y_pos, 2)
y_pos = draw_item("response_validator.py - Validate API responses", y_pos, 1)
y_pos = draw_item("text_enrichment.py - Enrichment text fields", y_pos, 1)
y_pos += 20

# Section 5: Frontend
y_pos = draw_section("🎨 Frontend (templates/ + static/)", y_pos)
y_pos = draw_item("templates/", y_pos, 1)
y_pos = draw_text("├─ index.html - Form tư vấn ngành", y_pos, 2)
y_pos = draw_text("└─ chatbot.html - Giao diện chat", y_pos, 2)
y_pos = draw_item("static/", y_pos, 1)
y_pos = draw_text("├─ script.js - Form handling + chuẩn hóa input", y_pos, 2)
y_pos = draw_text("├─ style.css - CSS chính", y_pos, 2)
y_pos = draw_text("├─ chatbot-page.js - Chat logic", y_pos, 2)
y_pos = draw_text("└─ chatbot-page.css - Chat styling", y_pos, 2)
y_pos += 20

# Section 6: Tests & Reports
y_pos = draw_section("🧪 Tests & Reports", y_pos)
y_pos = draw_item("tests/ - 5+ unit tests", y_pos, 1)
y_pos = draw_text("├─ test_predictor_regression.py", y_pos, 2)
y_pos = draw_text("├─ test_api_smoke.py", y_pos, 2)
y_pos = draw_text("├─ test_chatbot_context.py", y_pos, 2)
y_pos = draw_text("└─ test_chatbot_ambiguity_unittest.py", y_pos, 2)
y_pos = draw_item("reports/", y_pos, 1)
y_pos = draw_text("├─ evaluation.txt - Model metrics", y_pos, 2)
y_pos = draw_text("├─ confusion_matrix.csv", y_pos, 2)
y_pos = draw_text("└─ per_class_metrics.csv", y_pos, 2)

# Save image
output_path = "PROJECT_STRUCTURE_DIAGRAM_VI.png"
img.save(output_path)
import sys
sys.stdout.reconfigure(encoding='utf-8')
print(f"✅ Biểu đồ đã được tạo: {output_path}")
print(f"📐 Kích thước: {WIDTH}x{HEIGHT} pixels")

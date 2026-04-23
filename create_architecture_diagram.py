#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tạo biểu đồ kiến trúc hệ thống dạng PNG"""

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1600
HEIGHT = 2200
BG_COLOR = (245, 250, 255)
TEXT_COLOR = (20, 30, 50)
TITLE_COLOR = (0, 102, 204)
BOX_COLOR = (100, 180, 220)
BOX_BORDER = (0, 102, 204)
ARROW_COLOR = (150, 100, 200)
LABEL_COLOR = (50, 50, 150)

img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
draw = ImageDraw.Draw(img)

try:
    title_font = ImageFont.truetype("arial.ttf", 28)
    section_font = ImageFont.truetype("arial.ttf", 18)
    text_font = ImageFont.truetype("arial.ttf", 14)
    small_font = ImageFont.truetype("arial.ttf", 12)
except:
    title_font = ImageFont.load_default()
    section_font = ImageFont.load_default()
    text_font = ImageFont.load_default()
    small_font = ImageFont.load_default()

def draw_box(x, y, w, h, text, font=text_font, color=BOX_COLOR):
    """Vẽ hộp với text"""
    draw.rectangle([(x, y), (x+w, y+h)], fill=color, outline=BOX_BORDER, width=2)
    text_x = x + 10
    text_y = y + h//2 - 10
    draw.text((text_x, text_y), text, fill=TEXT_COLOR, font=font)

def draw_arrow(x1, y1, x2, y2, label=""):
    """Vẽ mũi tên"""
    draw.line([(x1, y1), (x2, y2)], fill=ARROW_COLOR, width=2)
    if label:
        mid_x = (x1 + x2) // 2
        mid_y = (y1 + y2) // 2
        draw.text((mid_x + 10, mid_y - 10), label, fill=LABEL_COLOR, font=small_font)

y = 30
draw.text((50, y), "HỆ THỐNG TƯ VẤN NGÀNH HỌC - KIẾN TRÚC", fill=TITLE_COLOR, font=title_font)

# Layer 1: Frontend
y = 100
draw.text((50, y), "┌─ LAYER 1: FRONTEND (Giao diện người dùng)", fill=LABEL_COLOR, font=section_font)
y += 50

draw_box(100, y, 300, 70, "Form HTML\nindex.html", text_font)
draw_box(500, y, 300, 70, "Chat Interface\nchatbot.html", text_font)
draw_box(900, y, 300, 70, "JavaScript\n(script.js, chatbot.js)", text_font)
draw_box(1300, y, 250, 70, "CSS Styling\n(style.css)", text_font)

draw_arrow(250, y+70, 250, y+110)
draw_arrow(650, y+70, 650, y+110)
draw_arrow(1050, y+70, 1050, y+110)

# Layer 2: API Endpoints
y += 150
draw.text((50, y), "┌─ LAYER 2: FLASK API (app.py)", fill=LABEL_COLOR, font=section_font)
y += 50

draw_box(150, y, 250, 70, "GET /\n(Form page)", text_font)
draw_box(500, y, 250, 70, "POST /predict\n(Prediction API)", text_font)
draw_box(850, y, 250, 70, "POST /chat\n(Chatbot API)", text_font)
draw_box(1200, y, 320, 70, "GET /health\n(Status check)", text_font)

draw_arrow(400, y+120, 250, y+150)
draw_arrow(625, y+120, 625, y+150)
draw_arrow(975, y+120, 975, y+150)

# Layer 3: Business Logic
y += 180
draw.text((50, y), "┌─ LAYER 3: BUSINESS LOGIC", fill=LABEL_COLOR, font=section_font)
y += 50

draw_box(100, y, 280, 80, "Predictor\n(Hybrid Score)\nModel + Criteria", text_font)
draw_box(500, y, 280, 80, "MajorChatbot\n(AI Response)\nFallback APIs", text_font)
draw_box(900, y, 280, 80, "Feature Eng\n(OHE, TF-IDF)\nNormalization", text_font)

draw_arrow(240, y+100, 240, y+140)
draw_arrow(640, y+100, 640, y+140)
draw_arrow(1040, y+100, 1040, y+140)

# Layer 4: Data & Model
y += 160
draw.text((50, y), "┌─ LAYER 4: ML MODELS & DATA", fill=LABEL_COLOR, font=section_font)
y += 50

draw_box(80, y, 200, 70, "RF Model\n(rf_model.pkl)", text_font)
draw_box(350, y, 200, 70, "TF-IDF\n(tfidf.pkl)", text_font)
draw_box(620, y, 200, 70, "OneHot\n(ohe.pkl)", text_font)
draw_box(890, y, 200, 70, "Classes\n(classes.pkl)", text_font)
draw_box(1160, y, 200, 70, "Config\n(hybrid_config)", text_font)

draw_arrow(180, y+80, 180, y+120)
draw_arrow(450, y+80, 450, y+120)
draw_arrow(720, y+80, 720, y+120)

# Layer 5: Data Sources
y += 150
draw.text((50, y), "┌─ LAYER 5: DATA & AI PROVIDERS", fill=LABEL_COLOR, font=section_font)
y += 50

draw_box(100, y, 220, 70, "Training Data\n(students.csv)", text_font)
draw_box(420, y, 220, 70, "Majors Info\n(majors.json)", text_font)
draw_box(740, y, 220, 70, "Salary Data\n(salary_bench)", text_font)
draw_box(1060, y, 220, 70, "Claude API\n(Fallback)", text_font)

draw_arrow(210, y+80, 210, y+120)
draw_arrow(530, y+80, 530, y+120)
draw_arrow(850, y+80, 850, y+120)

# Flow Description
y += 150
draw.text((50, y), "QUY TRÌNH HOẠT ĐỘNG:", fill=TITLE_COLOR, font=section_font)
y += 40

flows = [
    "1. Người dùng nhập form → Frontend chuẩn hóa dữ liệu",
    "2. POST /predict → app.py xử lý request",
    "3. Predictor tính hybrid score (60% ML + 40% criteria)",
    "4. Trả Top 3 ngành + điểm + confidence",
    "5. POST /chat → MajorChatbot xử lý chat",
    "6. Dùng TF-IDF + Fallback API (Claude/OpenAI/Deepseek)",
    "7. Trả response AI với context aware"
]

for flow in flows:
    draw.text((70, y), flow, fill=TEXT_COLOR, font=small_font)
    y += 35

# Scoring Details
y += 30
draw.text((50, y), "CÔNG THỨC SCORING:", fill=TITLE_COLOR, font=section_font)
y += 40

scoring_info = [
    "Final Score = 0.60 × Model Score + 0.40 × Criteria Score",
    "",
    "Model Score = 0.5 × ML Probability + 0.3 × Cosine Similarity + 0.2 × Rule Hints",
    "",
    "Criteria Score = Σ (Field Score × Weight)",
    "  • Sở thích chính: 23%",
    "  • Định hướng tương lai: 20%",
    "  • Kỹ năng nổi bật: 16%",
    "  • Tính cách: 14%",
    "  • Môi trường làm việc: 12%",
    "  • Môn học yêu thích: 8%",
    "  • Mô tả bản thân: 4%",
    "  • Mục tiêu nghề nghiệp: 3%"
]

for info in scoring_info:
    draw.text((70, y), info, fill=TEXT_COLOR, font=small_font)
    y += 28

img.save("PROJECT_ARCHITECTURE_DIAGRAM_VI.png")
import sys
sys.stdout.reconfigure(encoding='utf-8')
print("✅ Biểu đồ kiến trúc đã được tạo: PROJECT_ARCHITECTURE_DIAGRAM_VI.png")
print(f"📐 Kích thước: {WIDTH}x{HEIGHT} pixels")

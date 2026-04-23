#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_features_diagram():
    width, height = 1600, 1200
    img = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 28)
        heading_font = ImageFont.truetype("arial.ttf", 18)
        text_font = ImageFont.truetype("arial.ttf", 14)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        title_font = heading_font = text_font = small_font = ImageFont.load_default()
    
    color_prediction = (255, 200, 124)
    color_chatbot = (173, 216, 230)
    color_data = (144, 238, 144)
    color_feature = (200, 162, 200)
    color_border = (0, 0, 0)
    color_text = (0, 0, 0)
    color_arrow = (255, 0, 0)
    
    draw.text((width//2 - 350, 20), "SYSTEM FEATURES DIAGRAM", fill=color_text, font=title_font)
    draw.text((width//2 - 200, 60), "(5.1.2 - So do chuc nang)", fill=color_text, font=heading_font)
    
    y = 120
    
    # CENTER: USER INPUT
    user_x, user_y = width//2 - 150, y
    draw.rectangle([user_x, user_y, user_x + 300, user_y + 80], fill=(255, 255, 200), outline=color_border, width=2)
    draw.text((user_x + 80, user_y + 20), "USER INPUT", fill=color_text, font=heading_font)
    draw.text((user_x + 10, user_y + 50), "8 Profile Fields", fill=color_text, font=text_font)
    
    y += 150
    
    # LEFT: PREDICTION MODULE
    pred_x, pred_y = 100, y
    draw.rectangle([pred_x, pred_y, pred_x + 450, pred_y + 280], fill=color_prediction, outline=color_border, width=3)
    draw.text((pred_x + 100, pred_y + 20), "PREDICTION MODULE", fill=color_text, font=heading_font)
    draw.text((pred_x + 20, pred_y + 60), "Input: User profile (8 fields)", fill=color_text, font=text_font)
    draw.text((pred_x + 20, pred_y + 90), "Process:", fill=color_text, font=text_font)
    draw.text((pred_x + 30, pred_y + 115), "• OneHot Encoding", fill=color_text, font=small_font)
    draw.text((pred_x + 30, pred_y + 135), "• TF-IDF Vectorization", fill=color_text, font=small_font)
    draw.text((pred_x + 30, pred_y + 155), "• RandomForest ML", fill=color_text, font=small_font)
    draw.text((pred_x + 30, pred_y + 175), "• Content-based Scoring", fill=color_text, font=small_font)
    draw.text((pred_x + 30, pred_y + 195), "• Rule-based Boosting", fill=color_text, font=small_font)
    draw.text((pred_x + 20, pred_y + 225), "Output: Top 3 majors", fill=color_text, font=text_font)
    draw.text((pred_x + 20, pred_y + 250), "with scores & confidence", fill=color_text, font=text_font)
    
    # CENTER-RIGHT: CHATBOT MODULE
    chat_x, chat_y = 600, y
    draw.rectangle([chat_x, chat_y, chat_x + 450, chat_y + 280], fill=color_chatbot, outline=color_border, width=3)
    draw.text((chat_x + 120, chat_y + 20), "CHATBOT MODULE", fill=color_text, font=heading_font)
    draw.text((chat_x + 20, chat_y + 60), "Input: User questions", fill=color_text, font=text_font)
    draw.text((chat_x + 20, chat_y + 90), "Process:", fill=color_text, font=text_font)
    draw.text((chat_x + 30, chat_y + 115), "• Pattern Matching", fill=color_text, font=small_font)
    draw.text((chat_x + 30, chat_y + 135), "• Context Detection", fill=color_text, font=small_font)
    draw.text((chat_x + 30, chat_y + 155), "• NLP Processing", fill=color_text, font=small_font)
    draw.text((chat_x + 30, chat_y + 175), "• Fallback API (OpenAI)", fill=color_text, font=small_font)
    draw.text((chat_x + 30, chat_y + 195), "• Response Generation", fill=color_text, font=small_font)
    draw.text((chat_x + 20, chat_y + 225), "Output: Contextual", fill=color_text, font=text_font)
    draw.text((chat_x + 20, chat_y + 250), "responses & suggestions", fill=color_text, font=text_font)
    
    # RIGHT: DATA MANAGEMENT
    data_x, data_y = 1100, y
    draw.rectangle([data_x, data_y, data_x + 400, data_y + 280], fill=color_data, outline=color_border, width=3)
    draw.text((data_x + 80, data_y + 20), "DATA MANAGEMENT", fill=color_text, font=heading_font)
    draw.text((data_x + 20, data_y + 60), "Load Models:", fill=color_text, font=text_font)
    draw.text((data_x + 30, data_y + 85), "• rf_model.pkl", fill=color_text, font=small_font)
    draw.text((data_x + 30, data_y + 105), "• ohe.pkl", fill=color_text, font=small_font)
    draw.text((data_x + 30, data_y + 125), "• tfidf.pkl", fill=color_text, font=small_font)
    draw.text((data_x + 20, data_y + 155), "Load Data:", fill=color_text, font=text_font)
    draw.text((data_x + 30, data_y + 180), "• majors.json", fill=color_text, font=small_font)
    draw.text((data_x + 30, data_y + 200), "• salary_benchmarks", fill=color_text, font=small_font)
    draw.text((data_x + 30, data_y + 220), "• feedback_data.json", fill=color_text, font=small_font)
    draw.text((data_x + 20, data_y + 250), "Cache & Access", fill=color_text, font=text_font)
    
    # FEATURE COMPONENTS SECTION
    y = pred_y + 300
    draw.text((50, y), "FEATURE COMPONENTS:", fill=color_text, font=heading_font)
    y += 50
    
    components = [
        ("OneHot Encoder", "Categorical → Binary Vectors", color_feature),
        ("TF-IDF Vectorizer", "Text → Weighted Term Vectors", color_feature),
        ("RandomForest", "Multi-class Classification", color_feature),
        ("Predictor", "Combine All Components", color_feature)
    ]
    
    for i, (title, desc, color) in enumerate(components):
        x = 100 + (i % 2) * 750
        box_y = y + (i // 2) * 100
        draw.rectangle([x, box_y, x + 650, box_y + 80], fill=color, outline=color_border, width=2)
        draw.text((x + 20, box_y + 15), title, fill=color_text, font=text_font)
        draw.text((x + 20, box_y + 45), desc, fill=color_text, font=small_font)
    
    output_path = Path(__file__).parent / "SYSTEM_FEATURES_DIAGRAM.png"
    img.save(str(output_path), 'PNG')
    print(f"✅ System Features diagram created: {output_path}")

if __name__ == '__main__':
    create_features_diagram()

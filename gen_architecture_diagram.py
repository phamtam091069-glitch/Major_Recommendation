#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate 3-Tier Architecture Diagram as PNG
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_architecture_diagram():
    """Create a detailed 3-tier architecture diagram"""
    
    # Image dimensions
    width = 1400
    height = 1000
    bg_color = (255, 255, 255)
    
    # Create image
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to load fonts
    try:
        title_font = ImageFont.truetype("arial.ttf", 28)
        heading_font = ImageFont.truetype("arial.ttf", 20)
        text_font = ImageFont.truetype("arial.ttf", 14)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        title_font = ImageFont.load_default()
        heading_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Colors
    color_tier1 = (173, 216, 230)  # Light blue
    color_tier2 = (144, 238, 144)  # Light green
    color_tier3 = (255, 218, 185)  # Peach
    color_border = (0, 0, 0)
    color_text = (0, 0, 0)
    color_arrow = (255, 0, 0)
    
    # Title
    draw.text((width // 2 - 300, 20), "3-TIER ARCHITECTURE DIAGRAM", fill=color_text, font=title_font)
    draw.text((width // 2 - 250, 60), "(Client - Server - Storage)", fill=color_text, font=heading_font)
    
    y_pos = 120
    
    # TIER 1: CLIENT
    tier1_x, tier1_y = 100, y_pos
    tier1_w, tier1_h = 1200, 200
    
    draw.rectangle([tier1_x, tier1_y, tier1_x + tier1_w, tier1_y + tier1_h], 
                   fill=color_tier1, outline=color_border, width=3)
    draw.text((tier1_x + 50, tier1_y + 20), "TIER 1: CLIENT (Frontend - Presentation Layer)", 
              fill=color_text, font=heading_font)
    draw.text((tier1_x + 50, tier1_y + 60), "• HTML/CSS/JavaScript", fill=color_text, font=text_font)
    draw.text((tier1_x + 50, tier1_y + 90), "• Form Input + Results Display", fill=color_text, font=text_font)
    draw.text((tier1_x + 50, tier1_y + 120), "• User Validation & Normalization", fill=color_text, font=text_font)
    draw.text((tier1_x + 600, tier1_y + 60), "Files:", fill=color_text, font=text_font)
    draw.text((tier1_x + 600, tier1_y + 90), "• templates/index.html", fill=color_text, font=small_font)
    draw.text((tier1_x + 600, tier1_y + 110), "• static/script.js", fill=color_text, font=small_font)
    draw.text((tier1_x + 600, tier1_y + 130), "• static/style.css", fill=color_text, font=small_font)
    
    # Arrow down from Tier 1
    arrow_x = tier1_x + tier1_w // 2
    arrow_y1 = tier1_y + tier1_h
    arrow_y2 = arrow_y1 + 40
    draw.line([(arrow_x, arrow_y1), (arrow_x, arrow_y2)], fill=color_arrow, width=3)
    draw.polygon([(arrow_x, arrow_y2), (arrow_x - 15, arrow_y2 - 20), (arrow_x + 15, arrow_y2 - 20)], fill=color_arrow)
    draw.text((arrow_x - 150, arrow_y1 + 10), "HTTP/REST API (JSON)", fill=color_arrow, font=small_font)
    
    y_pos = arrow_y2 + 20
    
    # TIER 2: SERVER
    tier2_x, tier2_y = 100, y_pos
    tier2_w, tier2_h = 1200, 220
    
    draw.rectangle([tier2_x, tier2_y, tier2_x + tier2_w, tier2_y + tier2_h], 
                   fill=color_tier2, outline=color_border, width=3)
    draw.text((tier2_x + 50, tier2_y + 20), "TIER 2: SERVER (Backend - Application Layer)", 
              fill=color_text, font=heading_font)
    draw.text((tier2_x + 50, tier2_y + 60), "• Flask Web Server", fill=color_text, font=text_font)
    draw.text((tier2_x + 50, tier2_y + 90), "• Prediction Logic (ML + Content-based)", fill=color_text, font=text_font)
    draw.text((tier2_x + 50, tier2_y + 120), "• Chatbot Processing (NLP)", fill=color_text, font=text_font)
    draw.text((tier2_x + 50, tier2_y + 150), "• Data Encoding (OneHot + TF-IDF)", fill=color_text, font=text_font)
    draw.text((tier2_x + 600, tier2_y + 60), "Endpoints:", fill=color_text, font=text_font)
    draw.text((tier2_x + 600, tier2_y + 90), "• GET / (Form)", fill=color_text, font=small_font)
    draw.text((tier2_x + 600, tier2_y + 110), "• POST /predict (Prediction)", fill=color_text, font=small_font)
    draw.text((tier2_x + 600, tier2_y + 130), "• GET /health (Status)", fill=color_text, font=small_font)
    draw.text((tier2_x + 600, tier2_y + 150), "• POST /chat (Chatbot)", fill=color_text, font=small_font)
    
    # Arrow down from Tier 2
    arrow_x = tier2_x + tier2_w // 2
    arrow_y1 = tier2_y + tier2_h
    arrow_y2 = arrow_y1 + 40
    draw.line([(arrow_x, arrow_y1), (arrow_x, arrow_y2)], fill=color_arrow, width=3)
    draw.polygon([(arrow_x, arrow_y2), (arrow_x - 15, arrow_y2 - 20), (arrow_x + 15, arrow_y2 - 20)], fill=color_arrow)
    draw.text((arrow_x - 100, arrow_y1 + 10), "File I/O + JSON", fill=color_arrow, font=small_font)
    
    y_pos = arrow_y2 + 20
    
    # TIER 3: STORAGE
    tier3_x, tier3_y = 100, y_pos
    tier3_w, tier3_h = 1200, 160
    
    draw.rectangle([tier3_x, tier3_y, tier3_x + tier3_w, tier3_y + tier3_h], 
                   fill=color_tier3, outline=color_border, width=3)
    draw.text((tier3_x + 50, tier3_y + 20), "TIER 3: STORAGE (Data Layer - Local File System)", 
              fill=color_text, font=heading_font)
    draw.text((tier3_x + 50, tier3_y + 60), "Models:", fill=color_text, font=text_font)
    draw.text((tier3_x + 50, tier3_y + 85), 
              "• rf_model.pkl  • ohe.pkl  • tfidf.pkl  • classes.pkl  • majors.json", 
              fill=color_text, font=small_font)
    draw.text((tier3_x + 600, tier3_y + 60), "Data:", fill=color_text, font=text_font)
    draw.text((tier3_x + 600, tier3_y + 85), 
              "• raw/students.csv  • majors_profiles.json  • salary_benchmarks.json", 
              fill=color_text, font=small_font)
    
    # Save image
    output_path = Path(__file__).parent / "SYSTEM_ARCHITECTURE_DIAGRAM.png"
    img.save(str(output_path), 'PNG')
    print(f"✅ 3-Tier Architecture diagram created: {output_path}")
    return str(output_path)

if __name__ == '__main__':
    create_architecture_diagram()

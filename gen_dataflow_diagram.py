#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_dataflow_diagram():
    width, height = 1800, 1400
    img = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 28)
        heading_font = ImageFont.truetype("arial.ttf", 18)
        text_font = ImageFont.truetype("arial.ttf", 14)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        title_font = heading_font = text_font = small_font = ImageFont.load_default()
    
    color_client = (173, 216, 230)
    color_api = (255, 200, 124)
    color_server = (144, 238, 144)
    color_storage = (255, 218, 185)
    color_border = (0, 0, 0)
    color_text = (0, 0, 0)
    color_arrow = (255, 0, 0)
    
    draw.text((width//2 - 400, 20), "DATA FLOW DIAGRAM", fill=color_text, font=title_font)
    draw.text((width//2 - 300, 60), "(5.1.3 - API Communication & File Access)", fill=color_text, font=heading_font)
    
    y = 120
    
    # CLIENT SIDE
    client_x, client_y = 50, y
    draw.rectangle([client_x, client_y, client_x + 400, client_y + 200], 
                   fill=color_client, outline=color_border, width=3)
    draw.text((client_x + 80, client_y + 20), "CLIENT SIDE", fill=color_text, font=heading_font)
    draw.text((client_x + 20, client_y + 60), "Frontend Browser", fill=color_text, font=text_font)
    draw.text((client_x + 20, client_y + 90), "User Input Form", fill=color_text, font=text_font)
    draw.text((client_x + 20, client_y + 120), "Data Validation", fill=color_text, font=text_font)
    draw.text((client_x + 20, client_y + 150), "Remove Diacritics", fill=color_text, font=text_font)
    
    # API LAYER - LEFT SIDE
    api_x, api_y = 500, y
    draw.rectangle([api_x, api_y, api_x + 400, api_y + 450], 
                   fill=color_api, outline=color_border, width=3)
    draw.text((api_x + 120, api_y + 20), "API ENDPOINTS", fill=color_text, font=heading_font)
    
    endpoints = [
        ("GET /", "Return HTML Form"),
        ("POST /predict", "Prediction Request"),
        ("GET /health", "Check Status"),
        ("POST /chat", "Chatbot Request")
    ]
    
    api_y_offset = api_y + 70
    for endpoint, desc in endpoints:
        draw.text((api_x + 20, api_y_offset), endpoint, fill=color_text, font=text_font)
        draw.text((api_x + 150, api_y_offset), desc, fill=color_text, font=small_font)
        api_y_offset += 60
    
    draw.text((api_x + 20, api_y + 380), "JSON Request/Response", fill=color_text, font=text_font)
    
    # SERVER SIDE
    server_x, server_y = 950, y
    draw.rectangle([server_x, server_y, server_x + 400, server_y + 200], 
                   fill=color_server, outline=color_border, width=3)
    draw.text((server_x + 100, server_y + 20), "SERVER SIDE", fill=color_text, font=heading_font)
    draw.text((server_x + 20, server_y + 60), "Flask Application", fill=color_text, font=text_font)
    draw.text((server_x + 20, server_y + 90), "Process Request", fill=color_text, font=text_font)
    draw.text((server_x + 20, server_y + 120), "Execute Prediction", fill=color_text, font=text_font)
    draw.text((server_x + 20, server_y + 150), "Generate Response", fill=color_text, font=text_font)
    
    # Arrows: CLIENT -> API
    arrow_y = client_y + 100
    draw.line([(client_x + 400, arrow_y), (api_x, arrow_y)], fill=color_arrow, width=3)
    draw.polygon([(api_x, arrow_y), (api_x - 15, arrow_y - 10), (api_x - 15, arrow_y + 10)], fill=color_arrow)
    draw.text((client_x + 250, arrow_y - 20), "HTTP POST (JSON)", fill=color_arrow, font=small_font)
    
    # Arrows: API -> SERVER
    arrow_y = server_y + 100
    draw.line([(api_x + 400, arrow_y), (server_x, arrow_y)], fill=color_arrow, width=3)
    draw.polygon([(server_x, arrow_y), (server_x - 15, arrow_y - 10), (server_x - 15, arrow_y + 10)], fill=color_arrow)
    draw.text((api_x + 200, arrow_y - 20), "Process", fill=color_arrow, font=small_font)
    
    # Arrows: SERVER -> API (response)
    arrow_y = server_y + 150
    draw.line([(server_x, arrow_y), (api_x + 400, arrow_y)], fill=color_arrow, width=3)
    draw.polygon([(api_x + 400, arrow_y), (api_x + 400 + 15, arrow_y - 10), (api_x + 400 + 15, arrow_y + 10)], fill=color_arrow)
    draw.text((api_x + 150, arrow_y + 10), "JSON Response", fill=color_arrow, font=small_font)
    
    # Arrows: API -> CLIENT (response)
    arrow_y = client_y + 150
    draw.line([(api_x, arrow_y), (client_x + 400, arrow_y)], fill=color_arrow, width=3)
    draw.polygon([(client_x + 400, arrow_y), (client_x + 400 + 15, arrow_y - 10), (client_x + 400 + 15, arrow_y + 10)], fill=color_arrow)
    draw.text((client_x + 200, arrow_y + 10), "Display Results", fill=color_arrow, font=small_font)
    
    # FILE ACCESS SECTION
    y = client_y + 250
    draw.text((50, y), "FILE ACCESS & STORAGE:", fill=color_text, font=heading_font)
    y += 50
    
    # STORAGE BOXES
    storage_items = [
        ("Model Files", "rf_model.pkl\nohe.pkl\ntfidf.pkl\nclasses.pkl", (100, y)),
        ("Config Files", "hybrid_config.json\nmajors.json\nconstants.py", (450, y)),
        ("Data Files", "students.csv\nmajors_profiles.json\nsalary_benchmarks.json", (800, y)),
        ("Feedback", "feedback_data.json\nuser_feedback.json", (1150, y))
    ]
    
    for title, content, (x, box_y) in storage_items:
        draw.rectangle([x, box_y, x + 280, box_y + 200], 
                       fill=color_storage, outline=color_border, width=2)
        draw.text((x + 70, box_y + 15), title, fill=color_text, font=text_font)
        draw.text((x + 20, box_y + 50), content, fill=color_text, font=small_font)
    
    # REQUEST/RESPONSE EXAMPLE
    y += 250
    draw.text((50, y), "REQUEST/RESPONSE EXAMPLES:", fill=color_text, font=heading_font)
    y += 50
    
    # REQUEST EXAMPLE
    draw.rectangle([50, y, 850, y + 200], fill=(240, 248, 255), outline=color_border, width=2)
    draw.text((60, y + 15), "POST /predict Request (JSON):", fill=color_text, font=text_font)
    request_text = """{
  "so_thich_chinh": "cong nghe",
  "mon_hoc_yeu_thich": "tin hoc",
  "ky_nang_noi_bat": "lap trinh",
  "tinh_cach": "tho thao",
  ...
}"""
    for i, line in enumerate(request_text.split('\n')):
        draw.text((70, y + 45 + i*25), line, fill=color_text, font=small_font)
    
    # RESPONSE EXAMPLE
    draw.rectangle([900, y, 1750, y + 200], fill=(240, 248, 255), outline=color_border, width=2)
    draw.text((910, y + 15), "POST /predict Response (JSON):", fill=color_text, font=text_font)
    response_text = """{
  "top_3": [
    {"major": "Cong nghe thong tin", "score": 85},
    {"major": "Khoa hoc du lieu", "score": 78},
    {"major": "He thong thong tin", "score": 72}
  ]
}"""
    for i, line in enumerate(response_text.split('\n')):
        draw.text((920, y + 45 + i*25), line, fill=color_text, font=small_font)
    
    output_path = Path(__file__).parent / "SYSTEM_DATAFLOW_DIAGRAM.png"
    img.save(str(output_path), 'PNG')
    print(f"✅ System Data Flow diagram created: {output_path}")

if __name__ == '__main__':
    create_dataflow_diagram()

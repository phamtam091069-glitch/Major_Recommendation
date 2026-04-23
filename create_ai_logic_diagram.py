#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tạo sơ đồ khối logic AI hoạt động"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Cài đặt font cho tiếng Việt
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# Tạo figure
fig, ax = plt.subplots(1, 1, figsize=(14, 20))
ax.set_xlim(0, 10)
ax.set_ylim(0, 28)
ax.axis('off')

# Màu sắc
color_input = '#E8F4F8'
color_process = '#B3E5FC'
color_model = '#81D4FA'
color_criteria = '#4FC3F7'
color_output = '#01579B'
color_decision = '#FFF9C4'
color_arrow = '#424242'

def draw_box(ax, x, y, width, height, text, color, fontsize=10, style='round', weight='bold'):
    """Vẽ hộp văn bản"""
    if style == 'round':
        box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                            boxstyle="round,pad=0.1", 
                            edgecolor='#424242', facecolor=color,
                            linewidth=2)
    else:
        box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                            boxstyle="square,pad=0.05",
                            edgecolor='#424242', facecolor=color,
                            linewidth=2)
    ax.add_patch(box)
    
    # Thêm text
    if isinstance(text, list):
        full_text = '\n'.join(text)
    else:
        full_text = text
    ax.text(x, y, full_text, ha='center', va='center', 
           fontsize=fontsize, weight=weight, wrap=True)

def draw_arrow(ax, x1, y1, x2, y2, label='', curve=0):
    """Vẽ mũi tên"""
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle='->', mutation_scale=25,
                           color=color_arrow, linewidth=2.5,
                           connectionstyle=f"arc3,rad={curve}")
    ax.add_patch(arrow)
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x + 0.3, mid_y, label, fontsize=9, 
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

# Tiêu đề
ax.text(5, 27, 'SƠ ĐỒ KHỐI LOGIC AI TƯ VẤN NGÀNH HỌC', 
       ha='center', va='center', fontsize=16, weight='bold',
       bbox=dict(boxstyle='round,pad=0.7', facecolor='#FFC107', alpha=0.9))

# 1. INPUT
y_pos = 25
draw_box(ax, 5, y_pos, 3, 0.8, 'INPUT: Hồ sơ Học Sinh', color_input, fontsize=11)

draw_arrow(ax, 5, y_pos - 0.4, 5, y_pos - 1.1)

# 2. CỘI HÓA DỮ LIỆU
y_pos = 23.5
draw_box(ax, 5, y_pos, 4, 1.2, 
        ['Chuẩn Hóa Dữ Liệu',
         '• Tiếng Việt: Có dấu → Không dấu',
         '• Lowercase + strip whitespace'],
        color_process, fontsize=9)

draw_arrow(ax, 5, y_pos - 0.6, 5, y_pos - 1.3)

# 3. FEATURE ENGINEERING
y_pos = 21.5
draw_box(ax, 5, y_pos, 4.5, 1.5,
        ['Feature Engineering',
         '① OneHot Encode (6 fields)',
         '   - so_thich_chinh, mon_hoc, ky_nang',
         '   - tinh_cach, moi_truong, muc_tieu',
         '② TF-IDF (2 fields):',
         '   - mo_ta_ban_than, dinh_huong_tuong_lai'],
        color_process, fontsize=8.5)

draw_arrow(ax, 5, y_pos - 0.75, 5, y_pos - 1.5)

# 4. SPLIT LUỒNG
y_pos = 19
ax.text(5, y_pos + 0.3, 'TÍNH ĐIỂM (HYBRID APPROACH)', 
       ha='center', va='center', fontsize=11, weight='bold',
       bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFF59D'))

# Mũi tên phân nhánh
draw_arrow(ax, 5, y_pos - 0.5, 2.5, y_pos - 1.2)
draw_arrow(ax, 5, y_pos - 0.5, 7.5, y_pos - 1.2)

# 5a. MODEL SCORE (60%)
y_pos = 17
draw_box(ax, 2.5, y_pos + 0.5, 3.5, 0.7, 'MODEL SCORE (60%)', 
        color_model, fontsize=11, weight='bold')

draw_box(ax, 2.5, y_pos - 0.8, 3.8, 1.8,
        ['① Random Forest Probability',
         '   Xác suất từ model đã train',
         '',
         '② Cosine Similarity',
         '   So sánh profile ↔ Major mô tả',
         '',
         '③ Rule Boosting:',
         '   • Tech focus: +18% (ML)',
         '   • Language focus: +20% (Anh)'],
        '#BBDEFB', fontsize=8)

# 5b. CRITERIA SCORE (40%)
y_pos = 17
draw_box(ax, 7.5, y_pos + 0.5, 3.5, 0.7, 'CRITERIA SCORE (40%)', 
        color_criteria, fontsize=11, weight='bold')

draw_box(ax, 7.5, y_pos - 1.5, 4, 2.8,
        ['① Sở thích chính: 23%',
         '② Định hướng tương lai: 20%',
         '③ Kỹ năng nổi bật: 16%',
         '④ Tính cách: 14%',
         '⑤ Môi trường làm việc: 12%',
         '⑥ Môn học yêu thích: 8%',
         '⑦ Mô tả bản thân: 4%',
         '⑧ Mục tiêu nghề nghiệp: 3%'],
        '#81D4FA', fontsize=8.5)

# Mũi tên gộp lại
draw_arrow(ax, 2.5, 16 - 1.8, 4.3, 14.2)
draw_arrow(ax, 7.5, 16 - 1.5, 5.7, 14.2)

# 6. CÔNG THỨC TÍNH FINAL SCORE
y_pos = 13.5
draw_box(ax, 5, y_pos, 4, 1.2,
        ['FINAL SCORE = 0.60 × ModelScore',
         '                    + 0.40 × CriteriaScore',
         'Kết quả: 0 - 100 điểm'],
        '#FFE082', fontsize=10, weight='bold')

draw_arrow(ax, 5, y_pos - 0.6, 5, y_pos - 1.3)

# 7. TÍNH CONFIDENCE
y_pos = 11.5
draw_box(ax, 5, y_pos, 4.5, 1.2,
        ['Confidence Score = Fit Score ngành',
         '                    + Chênh lệch ngành kế tiếp',
         'Nhãn: Cao / Trung bình / Tham khảo'],
        color_decision, fontsize=9)

draw_arrow(ax, 5, y_pos - 0.6, 5, y_pos - 1.3)

# 8. TOP 3 RANKING
y_pos = 9.5
draw_box(ax, 5, y_pos, 4, 1.2,
        ['Xếp Hạng Top 3 Ngành',
         'Sắp xếp theo Final Score',
         'Giảm dần (từ cao → thấp)'],
        color_output, fontsize=10, weight='bold', style='square')

draw_arrow(ax, 5, y_pos - 0.6, 5, y_pos - 1.3)

# 9. OUTPUT
y_pos = 7.5
draw_box(ax, 5, y_pos, 4.5, 1.5,
        ['OUTPUT JSON:',
         '• major: Tên ngành (không dấu)',
         '• score: Điểm cuối (0-100)',
         '• score_model: Điểm từ ML',
         '• score_criteria: Điểm 8 tiêu chí',
         '• confidence: Mức tin cậy',
         '• suggestion: Lời khuyên'],
        color_output, fontsize=8.5, style='square')

# Thêm ghi chú
y_pos = 5
ax.text(5, y_pos, 'GHI CHÚ:', ha='center', fontsize=10, weight='bold')
notes = [
    '• Model được train từ dữ liệu synthetic 29,200 mẫu (71 ngành)',
    '• Nhưng chỉ train 15 ngành có trong majors.json (vì tên không khớp)',
    '• Score_relative: Tỉ lệ so sánh giữa 3 ngành trong lượt dự đoán này',
    '• Chatbot có tích hợp LLM (Claude/OpenAI/Deepseek) để giải thích chi tiết'
]

for i, note in enumerate(notes):
    ax.text(0.2, y_pos - 0.4 - i*0.35, note, fontsize=8, 
           bbox=dict(boxstyle='round,pad=0.3', facecolor='#F5F5F5', alpha=0.7))

plt.tight_layout()
plt.savefig('AI_LOGIC_DIAGRAM.png', dpi=300, bbox_inches='tight', 
           facecolor='white', edgecolor='none')
import sys
sys.stdout.reconfigure(encoding='utf-8')
print("[OK] So do duoc tao thanh cong: AI_LOGIC_DIAGRAM.png")
print("    Kich thuoc: 14x20 inches @ 300 DPI")
print("    Vi tri: c:\\Users\\huyen\\Downloads\\major-recommendation\\AI_LOGIC_DIAGRAM.png")
plt.close()

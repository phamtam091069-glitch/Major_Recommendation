import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Thiết lập figure và axis
fig, ax = plt.subplots(figsize=(20, 10))
ax.set_xlim(0, 20)
ax.set_ylim(0, 10)
ax.axis('off')

# Màu sắc
color_input = '#E8F4F8'
color_step = '#B3E5FC'
color_output = '#81D4FA'
color_final = '#4FC3F7'
color_text_dark = '#01579B'
color_text_light = '#FFFFFF'

# Hàm vẽ box
def draw_box(ax, x, y, width, height, text, color, text_color='black'):
    box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                          boxstyle="round,pad=0.1", 
                          edgecolor=color_text_dark, 
                          facecolor=color, 
                          linewidth=2)
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center', fontsize=9, 
            fontweight='bold', color=text_color, wrap=True)

# Hàm vẽ arrow
def draw_arrow(ax, x1, y1, x2, y2):
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle='->', mutation_scale=30, 
                           linewidth=2.5, color=color_text_dark)
    ax.add_patch(arrow)

# Tọa độ Y chính
y_main = 5

# 1. Input CSV
draw_box(ax, 1, y_main, 1.2, 0.8, 'Input CSV\n(Raw data)', color_input, color_text_dark)
draw_arrow(ax, 1.6, y_main, 2.2, y_main)

# 2. Step 1: Data Cleaning
draw_box(ax, 2.8, y_main, 1.2, 0.8, 'Step 1\nData Cleaning', color_step, color_text_light)
draw_box(ax, 2.8, y_main - 1.2, 1.2, 0.6, '1210 rows', color_output, color_text_dark)
draw_arrow(ax, 3.4, y_main, 4.0, y_main)

# 3. Step 2: Vietnamese Normalization
draw_box(ax, 4.6, y_main, 1.2, 0.8, 'Step 2\nVN Normalize', color_step, color_text_light)
draw_box(ax, 4.6, y_main - 1.2, 1.2, 0.6, 'Normalized\ntext', color_output, color_text_dark)
draw_arrow(ax, 5.2, y_main, 5.8, y_main)

# 4. Step 3: Categorical Normalization
draw_box(ax, 6.4, y_main, 1.2, 0.8, 'Step 3\nCat. Norm', color_step, color_text_light)
draw_box(ax, 6.4, y_main - 1.2, 1.2, 0.6, 'Standardized\ncategories', color_output, color_text_dark)
draw_arrow(ax, 7.0, y_main, 7.6, y_main)

# 5. Step 4: One-Hot Encoding
draw_box(ax, 8.2, y_main, 1.2, 0.8, 'Step 4\nOne-Hot\nEncoding', color_step, color_text_light)
draw_box(ax, 8.2, y_main - 1.2, 1.2, 0.6, '48 binary\nfeatures', color_output, color_text_dark)
draw_arrow(ax, 8.8, y_main, 9.4, y_main)

# 6. Step 5: TF-IDF Vectorization
draw_box(ax, 10.0, y_main, 1.2, 0.8, 'Step 5\nTF-IDF\nVectorize', color_step, color_text_light)
draw_box(ax, 10.0, y_main - 1.2, 1.2, 0.6, '500 TF-IDF\nfeatures', color_output, color_text_dark)
draw_arrow(ax, 10.6, y_main, 11.2, y_main)

# 7. Step 6: Feature Combination
draw_box(ax, 11.8, y_main, 1.2, 0.8, 'Step 6\nFeature\nCombo', color_step, color_text_light)
draw_box(ax, 11.8, y_main - 1.2, 1.2, 0.6, '548 total\nfeatures', color_output, color_text_dark)
draw_arrow(ax, 12.4, y_main, 13.0, y_main)

# 8. Step 7: Synthetic Data (Optional)
draw_box(ax, 13.6, y_main, 1.2, 0.8, 'Step 7\nSynthetic\nData', color_step, color_text_light)
draw_box(ax, 13.6, y_main - 1.2, 1.2, 0.6, 'Balanced\ndataset', color_output, color_text_dark)
draw_arrow(ax, 14.2, y_main, 14.8, y_main)

# 9. Step 8: Train Model
draw_box(ax, 15.4, y_main, 1.2, 0.8, 'Step 8\nTrain Model', color_step, color_text_light)
draw_box(ax, 15.4, y_main - 1.2, 1.2, 0.6, 'Trained\nModel', color_output, color_text_dark)
draw_arrow(ax, 16.0, y_main, 16.6, y_main)

# Output
draw_box(ax, 17.2, y_main, 1.2, 0.8, 'Output Model\n(Ready for\nPrediction)', color_final, color_text_light)

# Thêm tiêu đề
ax.text(10, 9.2, 'Data Preprocessing Pipeline - Quy Trình Tiền Xử Lý Dữ Liệu', 
        ha='center', fontsize=16, fontweight='bold', color=color_text_dark)

# Thêm legend/giải thích
ax.text(1, 0.5, 'Step 1: Remove missing values, outliers, duplicates', 
        ha='left', fontsize=8, color=color_text_dark)
ax.text(1, 0.1, 'Step 2-3: Normalize Vietnamese text & categorical values', 
        ha='left', fontsize=8, color=color_text_dark)

plt.tight_layout()
plt.savefig('c:/Users/huyen/Downloads/major-recommendation/DATA_PREPROCESSING_PIPELINE.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
print("✅ Sơ đồ đã được tạo: DATA_PREPROCESSING_PIPELINE.png")
plt.show()

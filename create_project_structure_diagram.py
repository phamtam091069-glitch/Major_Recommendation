#!/usr/bin/env python3
"""
Script to create a project structure diagram as PNG image using matplotlib.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# Set up the figure with a larger size for better visibility
fig, ax = plt.subplots(figsize=(16, 20), dpi=100)
ax.set_xlim(0, 10)
ax.set_ylim(0, 26)
ax.axis('off')

# Color scheme
colors = {
    'title': '#2C3E50',
    'folder': '#3498DB',
    'py_code': '#9B59B6',
    'data': '#27AE60',
    'config': '#F39C12',
    'static': '#E74C3C',
    'doc': '#95A5A6',
    'text': '#2C3E50',
}

# Title
ax.text(0.5, 25.2, 'Major Recommendation System - Project Structure', 
        fontsize=20, fontweight='bold', color=colors['title'])
ax.text(0.5, 24.6, 'Flask + Hybrid ML (Random Forest + TF-IDF) + Chatbot', 
        fontsize=12, color=colors['text'], style='italic')

# Project structure items
y_start = 24.0
line_height = 0.45

tree_items = [
    (0.5, y_start - 0*line_height, "📦 major-recommendation/", colors['title'], True),
    (1.0, y_start - 1*line_height, "🐍 app.py - Flask server, /predict & /health", colors['py_code'], False),
    (1.0, y_start - 2*line_height, "🤖 train_model.py - Model training & calibration", colors['py_code'], False),
    (1.0, y_start - 3*line_height, "⚙️  requirements.txt", colors['config'], False),
    (1.0, y_start - 4*line_height, "📖 README.md", colors['doc'], False),
    (1.0, y_start - 5*line_height, "🔑 .env - API keys configuration", colors['config'], False),
    
    (1.0, y_start - 6.2*line_height, "📁 data/ - Data pipeline", colors['folder'], True),
    (1.5, y_start - 7*line_height, "📊 raw/students.csv - Training dataset", colors['data'], False),
    (1.5, y_start - 7.5*line_height, "🐍 generate_balanced_students.py", colors['py_code'], False),
    (1.5, y_start - 8*line_height, "🐍 audit_dataset.py - Data quality check", colors['py_code'], False),
    (1.5, y_start - 8.5*line_height, "{} majors_profiles.json", colors['data'], False),
    (1.5, y_start - 9*line_height, "{} salary_benchmarks.json", colors['data'], False),
    
    (1.0, y_start - 10*line_height, "📁 models/ - ML Artifacts", colors['folder'], True),
    (1.5, y_start - 10.8*line_height, "🧠 rf_model.pkl - Random Forest model", colors['data'], False),
    (1.5, y_start - 11.3*line_height, "🧠 ohe.pkl - One-Hot Encoder", colors['data'], False),
    (1.5, y_start - 11.8*line_height, "🧠 tfidf.pkl - TF-IDF Vectorizer", colors['data'], False),
    (1.5, y_start - 12.3*line_height, "🧠 classes.pkl - Major classes", colors['data'], False),
    (1.5, y_start - 12.8*line_height, "{} majors.json - 60+ majors metadata", colors['data'], False),
    (1.5, y_start - 13.3*line_height, "⚙️  hybrid_config.json - Weight config", colors['config'], False),
    
    (1.0, y_start - 14.5*line_height, "📁 utils/ - Core Logic", colors['folder'], True),
    (1.5, y_start - 15.2*line_height, "🐍 predictor.py - Hybrid scoring (60% ML + 40% criteria)", colors['py_code'], False),
    (1.5, y_start - 15.7*line_height, "🐍 chatbot.py - Context-aware Q&A engine", colors['py_code'], False),
    (1.5, y_start - 16.2*line_height, "🐍 features.py - One-hot + TF-IDF extraction", colors['py_code'], False),
    (1.5, y_start - 16.7*line_height, "⚙️  constants.py - Mapping & config", colors['config'], False),
    (1.5, y_start - 17.2*line_height, "🐍 text_enrichment.py", colors['py_code'], False),
    (1.5, y_start - 17.7*line_height, "🐍 response_validator.py", colors['py_code'], False),
    (1.5, y_start - 18.2*line_height, "🐍 claude_fallback_api.py - Claude API fallback", colors['py_code'], False),
    (1.5, y_start - 18.7*line_height, "🐍 openai_fallback_api.py - OpenAI fallback", colors['py_code'], False),
    
    (1.0, y_start - 19.8*line_height, "📁 templates/ - HTML", colors['folder'], True),
    (1.5, y_start - 20.5*line_height, "🌐 index.html - Form + Dashboard UI", colors['static'], False),
    (1.5, y_start - 21*line_height, "🌐 chatbot.html - Chatbot page", colors['static'], False),
    
    (1.0, y_start - 21.8*line_height, "📁 static/ - Frontend Assets", colors['folder'], True),
    (1.5, y_start - 22.4*line_height, "🎨 style.css - Main styling", colors['static'], False),
    (1.5, y_start - 22.9*line_height, "⚡ script.js - Form handling & API calls", colors['static'], False),
    
    (1.0, y_start - 23.7*line_height, "📁 reports/ - Evaluation Results", colors['folder'], True),
    (1.5, y_start - 24.3*line_height, "📄 evaluation.txt - Model metrics", colors['doc'], False),
    (1.5, y_start - 24.8*line_height, "📊 confusion_matrix.csv", colors['data'], False),
    
    (1.0, y_start - 25.6*line_height, "📁 tests/ - Unit Tests", colors['folder'], True),
]

# Draw tree items
for x, y, text, color, is_bold in tree_items:
    fontweight = 'bold' if is_bold else 'normal'
    ax.text(x, y, text, fontsize=11, color=color, fontweight=fontweight, family='monospace')

# Add legend
legend_y = 1.2
ax.text(0.5, legend_y + 0.8, 'Legend:', fontsize=12, fontweight='bold', color=colors['title'])

legend_items = [
    (0.5, legend_y, "🐍 Python Code", colors['py_code']),
    (3.5, legend_y, "📁 Folders", colors['folder']),
    (6.0, legend_y, "📊 Data Files", colors['data']),
    (0.5, legend_y - 0.5, "⚙️  Configuration", colors['config']),
    (3.5, legend_y - 0.5, "🌐 Web (HTML/JS)", colors['static']),
    (6.0, legend_y - 0.5, "📄 Documents", colors['doc']),
]

for x, y, label, color in legend_items:
    ax.text(x, y, label, fontsize=10, color=color)

plt.tight_layout()
output_file = 'PROJECT_STRUCTURE_DIAGRAM.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
print(f"✅ Diagram created successfully: {output_file}")
print(f"📊 Image size: 1600x2000 pixels (at 150 DPI)")
print(f"📂 Saved to: c:/Users/huyen/Downloads/major-recommendation/{output_file}")

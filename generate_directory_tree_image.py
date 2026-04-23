"""
Generate a beautiful directory tree structure image as PNG.
Shows the project structure in a readable tree format.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os

def get_tree_structure():
    """Generate directory tree structure as text."""
    tree = """📁 major-recommendation/
├── 📄 app.py (1102 lines) - Flask main application
├── 📄 train_model.py - Train ML model
├── 📄 requirements.txt - Dependencies
├── 📄 README.md - Documentation
├── 📄 .env - Environment variables
├── 📄 .env.example - Example env file
│
├── 📁 data/
│   ├── 📄 raw/students.csv - Training dataset
│   ├── 📄 generate_balanced_students.py
│   ├── 📄 majors_profiles.json - Major descriptions
│   ├── 📄 salary_benchmarks.json
│   ├── 📄 audit_dataset.py
│   ├── 📄 clean_data.py
│   └── 📄 fallback_pending_samples.json
│
├── 📁 models/
│   ├── 📄 rf_model.pkl - Random Forest model
│   ├── 📄 ohe.pkl - OneHotEncoder
│   ├── 📄 tfidf.pkl - TF-IDF vectorizer
│   ├── 📄 classes.pkl - Class labels
│   ├── 📄 majors.json - Major info
│   └── 📄 hybrid_config.json - Hybrid config
│
├── 📁 utils/
│   ├── 📄 predictor.py (764 lines) - Main prediction logic
│   ├── 📄 chatbot.py (1848 lines) - Chatbot module
│   ├── 📄 features.py - Feature extraction
│   ├── 📄 constants.py - Constants & config
│   ├── 📄 response_validator.py - Response validation
│   ├── 📄 claude_fallback_api.py - Claude API
│   ├── 📄 openai_fallback_api.py - OpenAI API
│   ├── 📄 deepseek_fallback_api.py - Deepseek API
│   ├── 📄 chiasegpu_fallback_api.py - ChiaSegpu API
│   ├── 📄 fallback_api.py - Fallback API
│   └── 📄 __init__.py
│
├── 📁 templates/
│   ├── 📄 index.html - Form & results page
│   └── 📄 chatbot.html - Chatbot page
│
├── 📁 static/
│   ├── 📄 script.js - Frontend logic
│   ├── 📄 chatbot-page.js - Chatbot UI
│   ├── 📄 style.css - Styling
│   └── 📄 chatbot-page.css - Chatbot styling
│
├── 📁 tests/
│   ├── 📄 test_chatbot_context.py
│   ├── 📄 test_chatbot_context_unittest.py
│   ├── 📄 test_chatbot_ambiguity_unittest.py
│   ├── 📄 test_api_smoke.py
│   ├── 📄 test_predictor_regression.py
│   └── 📄 test_marine_alias_unittest.py
│
├── 📁 reports/
│   ├── 📄 evaluation.txt - Model evaluation
│   ├── 📄 confusion_matrix.csv
│   ├── 📄 per_class_metrics.csv
│   ├── 📄 data_audit.txt
│   ├── 📄 data_audit.json
│   └── 📄 data_distribution_analysis.json
│
├── 📁 (Test files - 15+ files)
│   ├── 📄 test_chatbot.py
│   ├── 📄 test_claude_api.py
│   ├── 📄 test_fallback_*.py
│   ├── 📄 test_critical_fixes.py
│   └── ...more test files...
│
└── 📁 (Utility & Documentation files)
    ├── 📄 SUMMARY.txt
    ├── 📄 PREDICTION_MODULE_DETAILED_GUIDE.md
    ├── 📄 gen_architecture_diagram.py
    ├── 📄 gen_dataflow_diagram.py
    ├── 📄 generate_prediction_diagram.py
    └── ...more generation scripts...

═══════════════════════════════════════════════════════════

🎯 KEY FILES & PURPOSES:

📊 CORE APPLICATION:
  • app.py - Main Flask application (routes, API)
  • predictor.py - ML model predictions
  • chatbot.py - Conversational AI module

🤖 MACHINE LEARNING:
  • train_model.py - Model training pipeline
  • models/ - Trained models & encoders
  • data/raw/students.csv - Training data

💬 CHATBOT INTEGRATION:
  • chatbot.py - Chatbot logic (1848 lines)
  • *_fallback_api.py - API fallbacks (Claude, OpenAI, Deepseek)
  • response_validator.py - Response validation

🌐 WEB INTERFACE:
  • templates/ - HTML pages
  • static/ - CSS & JavaScript
  • forms + results display

📚 UTILITIES:
  • utils/constants.py - Config & constants
  • utils/features.py - Feature extraction
  • tests/ - Unit tests

═══════════════════════════════════════════════════════════"""
    return tree

def create_tree_image(output_path="PROJECT_DIRECTORY_STRUCTURE.png"):
    """Create and save directory tree image."""
    
    # Get tree structure
    tree_text = get_tree_structure()
    lines = tree_text.split('\n')
    
    # Image settings
    img_width = 1400
    line_height = 22
    margin = 40
    img_height = (len(lines) + 5) * line_height + 2 * margin
    
    # Create image
    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a monospace font, fallback to default
    try:
        # Try to use a system monospace font
        font = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 12)
        title_font = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 14)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    
    # Colors
    bg_color = (245, 245, 250)  # Light lavender
    text_color = (40, 40, 40)   # Dark gray
    accent_color = (70, 130, 180)  # Steel blue
    
    # Redraw background with gradient-like effect
    draw.rectangle([0, 0, img_width, img_height], fill=bg_color)
    
    # Draw title
    title = "📁 PROJECT DIRECTORY STRUCTURE - major-recommendation"
    y_pos = margin
    draw.text((margin, y_pos), title, fill=accent_color, font=title_font)
    y_pos += line_height * 1.5
    
    # Draw separator line
    draw.line([(margin, y_pos), (img_width - margin, y_pos)], fill=accent_color, width=2)
    y_pos += line_height
    
    # Draw tree structure
    for line in lines:
        if line.strip():
            # Color special lines differently
            if "═" in line:
                draw.text((margin, y_pos), line, fill=accent_color, font=font)
            elif "🎯" in line or "📊" in line or "🤖" in line or "💬" in line or "🌐" in line or "📚" in line:
                draw.text((margin, y_pos), line, fill=accent_color, font=title_font)
            else:
                draw.text((margin, y_pos), line, fill=text_color, font=font)
        y_pos += line_height
    
    # Save image
    img.save(output_path)
    print(f"✅ Directory tree image created successfully!")
    print(f"📁 Saved to: {output_path}")
    print(f"📐 Image size: {img_width}x{img_height} pixels")
    
    return output_path

if __name__ == "__main__":
    # Generate image
    output_file = create_tree_image()
    
    # Try to open the image
    try:
        import subprocess
        subprocess.Popen(['start', output_file], shell=True)
    except:
        print(f"Please open {output_file} to view the image")

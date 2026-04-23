#!/usr/bin/env python3
"""Generate project structure diagram as HTML then convert to PNG using built-in tools."""

html_content = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Major Recommendation - Project Structure</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Courier New', monospace; background: #f5f5f5; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; margin-bottom: 10px; font-size: 32px; }
        .subtitle { color: #7f8c8d; font-style: italic; margin-bottom: 30px; }
        .section { margin: 30px 0; }
        .section-title { color: #2c3e50; font-size: 18px; font-weight: bold; margin-bottom: 15px; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .tree { font-size: 13px; line-height: 1.8; color: #2c3e50; margin-left: 20px; }
        .tree-item { margin: 3px 0; }
        .folder { color: #3498db; font-weight: bold; }
        .python { color: #9b59b6; }
        .data { color: #27ae60; }
        .config { color: #f39c12; }
        .web { color: #e74c3c; }
        .doc { color: #95a5a6; }
        .legend { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 20px; }
        .legend-item { padding: 10px; background: #f9f9f9; border-left: 4px solid #ccc; }
        .legend-item.python { border-left-color: #9b59b6; }
        .legend-item.folder { border-left-color: #3498db; }
        .legend-item.data { border-left-color: #27ae60; }
        .legend-item.config { border-left-color: #f39c12; }
        .legend-item.web { border-left-color: #e74c3c; }
        .legend-item.doc { border-left-color: #95a5a6; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #ecf0f1; color: #2c3e50; font-weight: bold; }
        tr:hover { background: #f9f9f9; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Major Recommendation System</h1>
        <p class="subtitle">Project Structure & Architecture Overview</p>
        
        <div class="section">
            <div class="section-title">System Overview</div>
            <p>Flask + Hybrid ML (Random Forest + TF-IDF) + Chatbot AI</p>
        </div>
        
        <div class="section">
            <div class="section-title">📁 Project Directory Structure</div>
            <div class="tree">
                <div class="tree-item"><span class="folder">📦 major-recommendation/</span></div>
                <div class="tree-item" style="margin-left: 30px;"><span class="python">🐍 app.py</span> - Flask server, /predict & /health endpoints</div>
                <div class="tree-item" style="margin-left: 30px;"><span class="python">🤖 train_model.py</span> - Model training & calibration</div>
                <div class="tree-item" style="margin-left: 30px;"><span class="config">⚙️ requirements.txt</span> - Dependencies</div>
                <div class="tree-item" style="margin-left: 30px;"><span class="doc">📖 README.md</span> - Documentation</div>
                <div class="tree-item" style="margin-left: 30px;"><span class="config">🔑 .env</span> - API keys configuration</div>
                
                <div class="tree-item" style="margin-top: 15px;"><span class="folder">📁 data/</span> - Data Pipeline & Management</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="data">📊 raw/students.csv</span> - Training dataset (~1200 rows)</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="python">🐍 generate_balanced_students.py</span> - Create synthetic data</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="python">🐍 audit_dataset.py</span> - Data quality assessment</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="data">{} majors_profiles.json</span> - Major descriptions</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="data">{} salary_benchmarks.json</span> - Salary data</div>
                
                <div class="tree-item" style="margin-top: 15px;"><span class="folder">📁 models/</span> - ML Artifacts & Config</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="data">🧠 rf_model.pkl</span> - Random Forest classifier</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="data">🧠 ohe.pkl</span> - One-Hot Encoder</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="data">🧠 tfidf.pkl</span> - TF-IDF Vectorizer</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="data">{} majors.json</span> - 60+ majors metadata</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="config">⚙️ hybrid_config.json</span> - Weight configuration</div>
                
                <div class="tree-item" style="margin-top: 15px;"><span class="folder">📁 utils/</span> - Core Logic & Services</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="python">🐍 predictor.py</span> - Hybrid scoring (60% ML + 40% criteria)</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="python">🐍 chatbot.py</span> - Context-aware Q&A engine</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="python">🐍 features.py</span> - Feature extraction</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="config">⚙️ constants.py</span> - Mapping & config</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="python">🐍 claude_fallback_api.py</span> - Claude API integration</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="python">🐍 openai_fallback_api.py</span> - OpenAI API integration</div>
                
                <div class="tree-item" style="margin-top: 15px;"><span class="folder">📁 templates/</span> - HTML Templates</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="web">🌐 index.html</span> - Form + Dashboard UI</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="web">🌐 chatbot.html</span> - Chatbot interface</div>
                
                <div class="tree-item" style="margin-top: 15px;"><span class="folder">📁 static/</span> - Frontend Assets</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="web">🎨 style.css</span> - Main styling</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="web">⚡ script.js</span> - Form handling & API calls</div>
                
                <div class="tree-item" style="margin-top: 15px;"><span class="folder">📁 reports/</span> - Evaluation Results</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="doc">📄 evaluation.txt</span> - Model metrics</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="data">📊 confusion_matrix.csv</span> - Classification matrix</div>
                
                <div class="tree-item" style="margin-top: 15px;"><span class="folder">📁 tests/</span> - Unit Tests</div>
                <div class="tree-item" style="margin-left: 60px;"><span class="python">🐍 test_chatbot_context.py</span></div>
                <div class="tree-item" style="margin-left: 60px;"><span class="python">🐍 test_predictor_regression.py</span></div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">🎯 Key Modules</div>
            <table>
                <tr>
                    <th>Module</th>
                    <th>Function</th>
                    <th>Key Features</th>
                </tr>
                <tr>
                    <td><strong>app.py</strong></td>
                    <td>Flask server & routing</td>
                    <td>POST /predict, GET /health, template rendering</td>
                </tr>
                <tr>
                    <td><strong>predictor.py</strong></td>
                    <td>Core prediction logic</td>
                    <td>Hybrid scoring, feature extraction, major matching</td>
                </tr>
                <tr>
                    <td><strong>chatbot.py</strong></td>
                    <td>Q&A engine</td>
                    <td>Context awareness, fallback APIs, personality fit</td>
                </tr>
                <tr>
                    <td><strong>train_model.py</strong></td>
                    <td>Model lifecycle</td>
                    <td>Training, calibration, artifact serialization</td>
                </tr>
                <tr>
                    <td><strong>features.py</strong></td>
                    <td>Feature engineering</td>
                    <td>One-hot encoding, TF-IDF extraction</td>
                </tr>
                <tr>
                    <td><strong>index.html</strong></td>
                    <td>Dashboard UI</td>
                    <td>Form inputs, result display, Top 3 visualization</td>
                </tr>
                <tr>
                    <td><strong>script.js</strong></td>
                    <td>Frontend logic</td>
                    <td>Form validation, API calls, result rendering</td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">Legend</div>
            <div class="legend">
                <div class="legend-item python">🐍 Python Code - Core application logic</div>
                <div class="legend-item folder">📁 Folders - Directory organization</div>
                <div class="legend-item data">📊 Data Files - CSV, JSON, PKL artifacts</div>
                <div class="legend-item config">⚙️ Configuration - Settings & constants</div>
                <div class="legend-item web">🌐 Web Assets - HTML, CSS, JavaScript</div>
                <div class="legend-item doc">📄 Documentation - Markdown & text files</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">📊 Scoring Formula</div>
            <p style="font-family: monospace; background: #f9f9f9; padding: 15px; border-radius: 4px; margin-top: 10px;">
                Final Score = 0.60 × ModelScore + 0.40 × CriteriaScore
            </p>
        </div>
    </div>
</body>
</html>"""

# Write HTML file
with open('PROJECT_STRUCTURE.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("[OK] HTML file created: PROJECT_STRUCTURE.html")
print("[INFO] Open this file in a browser and use Print > Save as PDF > Then convert PDF to PNG")
print("   Or use: wkhtmltoimage PROJECT_STRUCTURE.html PROJECT_STRUCTURE_DIAGRAM.png")

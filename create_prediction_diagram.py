#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create a detailed block diagram of the prediction module using Graphviz
"""

import subprocess
import os
from pathlib import Path

# Mermaid diagram definition for the prediction module
mermaid_diagram = '''graph TD
    Start["🎓 DỮ LIỆU ĐẦU VÀO<br/>(Hồ sơ học sinh)"]
    
    Input1["📋 Trường Categorical<br/>- Sở thích chính<br/>- Môn học yêu thích<br/>- Tính cách<br/>- Kỹ năng nổi bật<br/>- Môi trường làm việc<br/>- Mục tiêu nghề nghiệp"]
    
    Input2["📝 Trường Text<br/>- Mô tả bản thân<br/>- Định hướng tương lai"]
    
    Start --> Input1
    Start --> Input2
    
    Input1 --> OnehHot["🔄 ONE-HOT ENCODING<br/>- Chuyển categorical thành vector<br/>- Chuẩn hóa dữ liệu"]
    Input2 --> TFIDF["📊 TF-IDF VECTORIZATION<br/>- Biến đổi text thành vector<br/>- Trích xuất đặc trưng từ khóa"]
    
    OnehHot --> Feature["🎯 FEATURE VECTOR<br/>(One-hot + TF-IDF kết hợp)"]
    TFIDF --> Feature
    
    Feature --> ModelScore["⚙️ MODEL SCORE (30%)<br/>"]
    Feature --> CriteriaScore["📐 CRITERIA SCORE (40%)<br/>"]
    Feature --> RuleBoost["🔧 RULE BOOST (30%)"]
    
    ModelScore --> MS1["🤖 Machine Learning<br/>- RandomForest Classifier<br/>- CalibratedProbability"]
    ModelScore --> MS2["📏 Cosine Similarity<br/>- So sánh với mô tả ngành<br/>- TF-IDF vectors"]
    
    MS1 --> MS_Calc["TÍNH TOÁN:<br/>ML_Score = 60% RF +<br/>40% Cosine"]
    MS2 --> MS_Calc
    
    CriteriaScore --> CS1["1️⃣ Sở thích chính: 23%"]
    CriteriaScore --> CS2["2️⃣ Định hướng tương lai: 20%"]
    CriteriaScore --> CS3["3️⃣ Kỹ năng nổi bật: 16%"]
    CriteriaScore --> CS4["4️⃣ Tính cách: 14%"]
    CriteriaScore --> CS5["5️⃣ Môi trường làm việc: 12%"]
    CriteriaScore --> CS6["6️⃣ Môn học yêu thích: 8%"]
    CriteriaScore --> CS7["7️⃣ Mô tả bản thân: 4%"]
    CriteriaScore --> CS8["8️⃣ Mục tiêu nghề nghiệp: 3%"]
    
    CS1 --> CS_Calc["TÍNH TOÁN:<br/>Criteria_Score = Σ(Trọng số × Điểm khớp)<br/>Kết quả: 0-100"]
    CS2 --> CS_Calc
    CS3 --> CS_Calc
    CS4 --> CS_Calc
    CS5 --> CS_Calc
    CS6 --> CS_Calc
    CS7 --> CS_Calc
    CS8 --> CS_Calc
    
    RuleBoost --> RB1["💡 Phát hiện Tech Signals<br/>(3+ signals → Boost Tech majors)"]
    RuleBoost --> RB2["🌐 Phát hiện Language Signals<br/>(2+ signals → Boost Language majors)"]
    RuleBoost --> RB3["📚 Phát hiện Education Signals<br/>(Sư phạm majors boost)"]
    
    RB1 --> RB_Calc["BOOST CALCULATION:<br/>- TECH_BOOST: Data Science +18%<br/>- LANG_BOOST: Language +20%<br/>- CAP: Giới hạn max boost"]
    RB2 --> RB_Calc
    RB3 --> RB_Calc
    
    MS_Calc --> Blend["⚡ BLENDING SCORES<br/>Model: 30% | Criteria: 70%"]
    CS_Calc --> Blend
    RB_Calc --> Blend
    
    Blend --> FinalScore["🎲 FINAL SCORE CALCULATION<br/>FinalScore = 0.30 × Model +<br/>0.70 × Criteria + RuleBoost<br/>Kết quả: 0-100"]
    
    FinalScore --> AllMajors["📊 SCORE TẤT CẢ NGÀNH (15 lớp)<br/>- Công nghệ thông tin<br/>- Khoa học dữ liệu<br/>- Quản trị kinh doanh<br/>- ... và 12 ngành khác"]
    
    AllMajors --> Sort["🔢 SORT & RANK<br/>Sắp xếp theo score giảm dần"]
    
    Sort --> TopN["🏆 TOP 3 NGÀNH<br/>- Ngành 1: Score<br/>- Ngành 2: Score<br/>- Ngành 3: Score"]
    
    TopN --> Confidence["📈 CONFIDENCE CALCULATION<br/>- Dựa trên fit score<br/>- Độ tách biệt với ngành kế tiếp<br/>- Nhãn: Cao/Trung bình/Tham khảo"]
    
    Confidence --> Response["✅ RESPONSE JSON<br/>- major: Tên ngành<br/>- score: Điểm cuối (0-100)<br/>- score_model: Điểm ML<br/>- score_criteria: Điểm tiêu chí<br/>- confidence_score: Độ tin cậy<br/>- suggestion: Lời khuyên"]
    
    Response --> End["📤 TRUYỀN KỲ VỀ FRONTEND<br/>(top_3 + điểm + giải thích)"]
    
    style Start fill:#FFE5B4
    style Feature fill:#B4D7FF
    style ModelScore fill:#D7FFB4
    style CriteriaScore fill:#FFD7B4
    style RuleBoost fill:#D7B4FF
    style Blend fill:#FFB4D7
    style FinalScore fill:#B4FFD7,stroke:#000,stroke-width:3px
    style TopN fill:#FFE5B4,stroke:#000,stroke-width:3px
    style End fill:#90EE90,stroke:#000,stroke-width:2px
'''

def create_png_with_mermaid(diagram_text, output_path):
    """Create PNG using mermaid-cli"""
    try:
        import mmdc
        print("✓ Mermaid module found, generating diagram...")
    except ImportError:
        print("⚠ Installing mermaid-cli...")
        subprocess.run(['npm', 'install', '-g', '@mermaid-js/mermaid-cli'], check=True)
    
    # Save mermaid file
    mmd_file = output_path.replace('.png', '.mmd')
    with open(mmd_file, 'w', encoding='utf-8') as f:
        f.write(diagram_text)
    
    print(f"✓ Saved mermaid file: {mmd_file}")
    
    # Generate PNG
    try:
        cmd = ['mmdc', '-i', mmd_file, '-o', output_path, '-s', '2', '--theme', 'default']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✓ Generated PNG: {output_path}")
            return True
        else:
            print(f"⚠ mmdc error: {result.stderr}")
            return False
    except Exception as e:
        print(f"⚠ Error generating PNG: {e}")
        return False

def create_svg_alternative(diagram_text, output_path):
    """Create SVG as alternative using graphviz"""
    try:
        from graphviz import Digraph
        print("⚠ Graphviz Python not available, trying alternative...")
    except ImportError:
        pass
    
    # Create DOT format
    dot_content = convert_mermaid_to_dot(diagram_text)
    
    try:
        result = subprocess.run(['dot', '-Tsvg', '-o', output_path], 
                              input=dot_content, 
                              text=True, 
                              capture_output=True,
                              timeout=30)
        if result.returncode == 0:
            print(f"✓ Generated SVG: {output_path}")
            return True
    except Exception as e:
        print(f"⚠ Graphviz error: {e}")
    
    return False

def convert_mermaid_to_dot(mermaid_text):
    """Simple conversion of mermaid to dot format"""
    dot = 'digraph {\n'
    dot += '  rankdir=TB;\n'
    dot += '  node [shape=box, style="rounded,filled", fillcolor="lightblue", fontname="Helvetica"];\n'
    dot += '  edge [fontname="Helvetica"];\n'
    
    for line in mermaid_text.split('\n'):
        if '-->' in line or '-.->' in line:
            parts = line.strip().split('--')
            if len(parts) >= 2:
                src = parts[0].strip()
                rest = '--'.join(parts[1:]).strip()
                dst = rest.split('[')[0].strip() if '[' in rest else rest
                dot += f'  "{src}" -> "{dst}";\n'
    
    dot += '}\n'
    return dot

if __name__ == '__main__':
    output_dir = Path(__file__).parent
    output_path = str(output_dir / 'prediction_module_diagram.png')
    
    print("🎨 Creating prediction module diagram...")
    print(f"📍 Output: {output_path}\n")
    
    # Try mermaid first
    if not create_png_with_mermaid(mermaid_diagram, output_path):
        print("\n⚠ Mermaid PNG generation failed, trying SVG alternative...")
        svg_path = output_path.replace('.png', '.svg')
        if create_svg_alternative(mermaid_diagram, svg_path):
            print(f"\n✅ Diagram created as SVG instead: {svg_path}")
        else:
            print("\n❌ Could not generate diagram. Trying simple text version...")
            # Save as text diagram
            txt_path = output_path.replace('.png', '_description.txt')
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(mermaid_diagram)
            print(f"✓ Saved text version: {txt_path}")
    else:
        print(f"\n✅ Diagram successfully created: {output_path}")

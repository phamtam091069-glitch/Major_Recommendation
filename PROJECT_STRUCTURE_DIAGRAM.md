# 📊 Major Recommendation System - Project Structure

## System Architecture Overview

```
Flask + Hybrid ML (Random Forest + TF-IDF) + Chatbot
```

---

## 📁 Project Tree Structure

```
major-recommendation/
│
├── 🐍 app.py                          (Flask server, /predict & /health endpoints)
├── 🤖 train_model.py                  (Model training & calibration)
├── ⚙️  requirements.txt                (Dependencies)
├── 📖 README.md                       (Documentation)
├── 🔑 .env                            (API keys configuration)
│
├── 📁 data/                           (Data Pipeline & Management)
│   ├── 📊 raw/
│   │   └── students.csv               (Training dataset ~1200 rows)
│   ├── 🐍 generate_balanced_students.py    (Create synthetic data)
│   ├── 🐍 audit_dataset.py                 (Data quality assessment)
│   ├── 🐍 clean_data.py                    (Data preprocessing)
│   ├── {} majors_profiles.json             (Detailed major descriptions)
│   └── {} salary_benchmarks.json           (Salary data by major)
│
├── 📁 models/                         (ML Artifacts & Configuration)
│   ├── 🧠 rf_model.pkl                (Random Forest classifier)
│   ├── 🧠 ohe.pkl                     (One-Hot Encoder)
│   ├── 🧠 tfidf.pkl                   (TF-IDF Vectorizer)
│   ├── 🧠 classes.pkl                 (Major class labels)
│   ├── {} majors.json                 (60+ majors metadata)
│   └── ⚙️  hybrid_config.json          (Weight configuration)
│
├── 📁 utils/                          (Core Logic & Services)
│   ├── 🐍 predictor.py                (Hybrid scoring: 60% ML + 40% criteria)
│   ├── 🐍 chatbot.py                  (Context-aware Q&A engine)
│   ├── 🐍 features.py                 (One-hot + TF-IDF feature extraction)
│   ├── ⚙️  constants.py                (Mapping & global configuration)
│   ├── 🐍 text_enrichment.py          (Optional text expansion)
│   ├── 🐍 response_validator.py       (Response quality validation)
│   ├── 🐍 claude_fallback_api.py      (Claude API integration)
│   ├── 🐍 openai_fallback_api.py      (OpenAI API integration)
│   ├── 🐍 deepseek_fallback_api.py    (Deepseek API integration)
│   └── 🐍 chiasegpu_fallback_api.py   (ChiaSeGPU API integration)
│
├── 📁 templates/                      (HTML Templates)
│   ├── 🌐 index.html                  (Form + Dashboard UI)
│   └── 🌐 chatbot.html                (Chatbot interface)
│
├── 📁 static/                         (Frontend Assets)
│   ├── 🎨 style.css                   (Main styling)
│   ├── 🎨 chatbot-page.css            (Chatbot styling)
│   ├── ⚡ script.js                   (Form handling & API calls)
│   └── ⚡ chatbot-page.js             (Chatbot frontend logic)
│
├── 📁 reports/                        (Evaluation & Analysis)
│   ├── 📄 evaluation.txt              (Model metrics: accuracy, precision, recall)
│   ├── 📊 confusion_matrix.csv        (Classification matrix by major)
│   ├── 📊 per_class_metrics.csv       (Per-major performance metrics)
│   └── 📊 data_audit.json             (Data quality assessment results)
│
└── 📁 tests/                          (Unit & Integration Tests)
    ├── 🐍 test_chatbot_context.py     (Chatbot context handling)
    ├── 🐍 test_predictor_regression.py (Predictor regression tests)
    ├── 🐍 test_api_smoke.py           (API endpoint smoke tests)
    └── 🐍 test_chatbot_ambiguity_unittest.py
```

---

## 🎯 Key Modules & Their Functions

| Module             | Function               | Key Features                                          |
| ------------------ | ---------------------- | ----------------------------------------------------- |
| **app.py**         | Flask server & routing | POST `/predict`, GET `/health`, template rendering    |
| **predictor.py**   | Core prediction logic  | Hybrid scoring, feature extraction, major matching    |
| **chatbot.py**     | Q&A engine             | Context awareness, fallback APIs, personality fit     |
| **train_model.py** | Model lifecycle        | Training, calibration, artifact serialization         |
| **features.py**    | Feature engineering    | One-hot encoding, TF-IDF extraction, profile building |
| **constants.py**   | Configuration          | Major mappings, weights, aliases, categorical fields  |
| **index.html**     | Dashboard UI           | Form inputs, result display, Top 3 visualization      |
| **script.js**      | Frontend logic         | Form validation, API calls, result rendering          |

---

## 📊 Data Flow Diagram

```
┌─────────────────────┐
│   User Input Form   │
│  (index.html form)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────┐
│  script.js                  │
│  ✓ Normalize Vietnamese     │
│  ✓ Remove diacritical marks │
│  ✓ POST /predict API call   │
└──────────┬──────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  app.py (/predict endpoint)  │
│  ✓ Validate input            │
│  ✓ Call predictor.py         │
└──────────┬───────────────────┘
           │
           ▼
┌────────────────────────────────────┐
│  predictor.py (Hybrid Scoring)     │
│  ┌──────────────────────────────┐  │
│  │ 1. Feature Extraction        │  │
│  │    - One-hot encoding (6)    │  │
│  │    - TF-IDF vectors (2 text) │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │ 2. Model Score (60%)         │  │
│  │    - RF prediction           │  │
│  │    - Cosine similarity       │  │
│  │    - Rule boost (capped)     │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │ 3. Criteria Score (40%)      │  │
│  │    - 8-field weighted score  │  │
│  │    - Personality filtering   │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │ 4. Final Score               │  │
│  │    = 60% MS + 40% CS         │  │
│  └──────────────────────────────┘  │
└──────────┬───────────────────────────┘
           │
           ▼
┌───────────────────────────────┐
│ chatbot.py (Explanation)      │
│ ✓ TF-IDF matching             │
│ ✓ Fallback API if needed      │
│ ✓ Confidence calculation      │
│ ✓ Suggestion generation       │
└──────────┬────────────────────┘
           │
           ▼
┌────────────────────┐
│  JSON Response     │
│  - top_3 majors    │
│  - scores          │
│  - confidence      │
│  - feedback        │
│  - suggestion      │
└──────────┬─────────┘
           │
           ▼
┌──────────────────────────────┐
│  script.js (Render)          │
│  ✓ Display Top 3 cards       │
│  ✓ Show confidence meter     │
│  ✓ Render suggestions        │
│  ✓ Animate progress bar      │
└──────────────────────────────┘
```

---

## 🏗️ Architecture Components

### Backend (Python)

- **Flask Server**: REST API endpoints
- **ML Pipeline**: Scikit-learn (Random Forest, TF-IDF, OneHotEncoder)
- **Hybrid Scoring**: Combined model + criteria-based scoring
- **Chatbot**: Context-aware NLP with fallback APIs
- **Data Management**: CSV processing, JSON metadata

### Frontend (HTML/CSS/JS)

- **Responsive Dashboard**: Modern UI with grid layout
- **Form Validation**: Client-side input validation
- **Real-time API Integration**: Fetch-based async calls
- **Result Visualization**: Cards, progress bars, confidence meters

### Data Layer

- **Training Data**: Synthetic student profiles (1200+ rows)
- **Model Artifacts**: Serialized ML components (PKL files)
- **Configuration**: JSON-based major metadata & weights
- **Reports**: CSV evaluation metrics & confusion matrices

---

## 📈 Scoring Formula

```
Final Score = 0.60 × ModelScore + 0.40 × CriteriaScore

Where:
  ModelScore = RF Probability + Cosine Similarity + Rule Boost

  CriteriaScore = Σ (Weight_i × FieldScore_i)
    - Sở thích chính: 23%
    - Định hướng tương lai: 20%
    - Kỹ năng nổi bật: 16%
    - Tính cách: 14%
    - Môi trường làm việc: 12%
    - Môn học yêu thích: 8%
    - Mô tả bản thân: 4%
    - Mục tiêu nghề nghiệp: 3%
```

---

## 🔧 Development Workflow

### 1. Data Preparation

```bash
python data/generate_balanced_students.py    # Create dataset
python data/audit_dataset.py                 # Verify quality
```

### 2. Model Training

```bash
python train_model.py                        # Train & save artifacts
```

### 3. Run Application

```bash
python app.py                                # Start Flask server
# Access http://127.0.0.1:5000
```

### 4. Testing

```bash
python -m pytest tests/                      # Run unit tests
```

---

## 🔌 API Fallback Strategy

If primary model fails or needs explanation:

1. **Claude API** (Primary fallback) - Best quality responses
2. **OpenAI API** (Secondary fallback)
3. **Deepseek API** (Tertiary fallback)
4. **ChiaSeGPU API** (Quaternary fallback)

Each fallback caches responses for 30 minutes to optimize costs.

---

## 📝 Configuration Files

- **.env**: API keys (Claude, OpenAI, Deepseek)
- **majors.json**: 60+ major profiles with descriptions
- **hybrid_config.json**: Model weights & selection
- **salary_benchmarks.json**: Average salary by major
- **constants.py**: Mapping tables, categorical fields

---

## 🎓 Supported Majors (60+)

**Technology**: Công nghệ thông tin, Khoa học dữ liệu, Kỹ thuật phần mềm, etc.

**Business**: Quản trị kinh doanh, Marketing, Kế toán, Tài chính, etc.

**Healthcare**: Điều dưỡng, Dược học, Dinh dưỡng, etc.

**Languages**: Ngôn ngữ Anh, Ngôn ngữ Trung, Ngôn ngữ Nhật, etc.

**Creative**: Thiết kế đồ họa, Báo chí, Du lịch, Kiến trúc, etc.

**Education**: Sư phạm (multiple subjects)

**Law & Social**: Luật, Xã hội học, etc.

---

## ✅ Quality Metrics

- **Model Accuracy**: ~85-92% (on test set)
- **Prediction Confidence**: 0-100 scale with reliability labels
- **Response Time**: <500ms average
- **API Success Rate**: 99%+
- **Cache Hit Rate**: ~60%

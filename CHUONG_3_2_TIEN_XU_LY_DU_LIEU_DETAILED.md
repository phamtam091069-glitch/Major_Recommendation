# Chương 3.2: TIỀN XỬ LÝ DỮ LIỆU (DATA PREPROCESSING)

## 1. Giới Thiệu

**Data Preprocessing (Tiền xử lý dữ liệu)** là bước tiền phòng chống chế độ trong quy trình xây dựng hệ thống machine learning. Nó quyết định trực tiếp chất lượng của dữ liệu đầu vào, từ đó ảnh hưởng đến hiệu suất của model huấn luyện.

Module này mô tả cách xử lý và chuẩn hóa dữ liệu thu thập từ Google Form trước khi đưa vào huấn luyện model dự đoán ngành học.

**Tầm quan trọng của Data Preprocessing:**

- **Loại bỏ nhiễu:** Xóa dữ liệu không hợp lệ, thiếu hoặc ngoại lệ
- **Chuẩn hóa:** Đảm bảo tất cả dữ liệu có định dạng nhất quán
- **Mã hóa:** Chuyển dữ liệu text sang dạng số có thể xử lý được
- **Cân bằng:** Tạo dữ liệu nhân tạo để cân bằng các lớp không đều

Quy trình này bao gồm **6 bước chính**:

1. Làm sạch dữ liệu
2. Chuẩn hóa tiếng Việt
3. Chuẩn hóa giá trị categorical
4. Mã hóa One-Hot
5. TF-IDF Vectorization
6. Tạo dữ liệu nhân tạo & cân bằng

## 2. 3.2.1: Làm Sạch Dữ Liệu (Data Cleaning)

Làm sạch dữ liệu là bước đầu tiên và rất quan trọng trong tiền xử lý. Nó đảm bảo rằng dữ liệu đầu vào không chứa các giá trị bất thường, thiếu hoặc trùng lặp có thể làm hỏng model.

### 2.1. Xử lý Missing Values (Giá trị thiếu)

Missing values xuất hiện khi người dùng không điền đầy đủ form hoặc có lỗi kỹ thuật.

**Bước 1: Kiểm tra NaN values**

```python
import pandas as pd
import numpy as np

# Load dữ liệu từ CSV
df = pd.read_csv('data/raw/students.csv')

# Kiểm tra số lượng missing values cho mỗi cột
print(df.isnull().sum())

# Hiển thị tỷ lệ missing values
print(df.isnull().sum() / len(df) * 100)
```

**Bước 2: Xóa rows có missing > 50%**

Nếu một hàng có nhiều hơn 50% dữ liệu thiếu, chúng ta loại bỏ nó vì nó không đủ thông tin để tạo hồ sơ học sinh hợp lệ:

```python
# Xóa rows với > 50% missing values
threshold = 0.5
df = df.dropna(thresh=len(df.columns) * (1 - threshold))
```

**Bước 3: Fill missing với mode/median**

Đối với các cột categorical (có limited values), chúng ta điền giá trị missing bằng mode (giá trị xuất hiện nhiều nhất):

```python
# Điền missing values cho categorical columns với mode
categorical_cols = ['so_thich_chinh', 'mon_hoc_yeu_thich', 'ky_nang_noi_bat']
for col in categorical_cols:
    df[col].fillna(df[col].mode()[0], inplace=True)

# Điền missing values cho text columns với empty string
text_cols = ['mo_ta_ban_than', 'dinh_huong_tuong_lai']
for col in text_cols:
    df[col].fillna('', inplace=True)
```

### 2.2. Xử lý Outliers (Giá trị ngoại lệ)

Outliers là các giá trị bất thường, không thuộc phạm vi bình thường của dữ liệu.

**Bước 1: IQR Method (Interquartile Range)**

IQR = Q3 - Q1, các giá trị ngoài [Q1 - 1.5×IQR, Q3 + 1.5×IQR] được coi là outliers.

Phương pháp này thích hợp cho dữ liệu có phân phối chuẩn:

```python
# Tính IQR cho các cột numeric (nếu có)
Q1 = df['column_name'].quantile(0.25)
Q3 = df['column_name'].quantile(0.75)
IQR = Q3 - Q1

# Xác định outliers
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# Loại bỏ outliers
df = df[(df['column_name'] >= lower_bound) & (df['column_name'] <= upper_bound)]
```

**Bước 2: Z-score Method**

Z-score đo lường độ lệch của một giá trị so với trung bình (mean). Giá trị có |z| > 3 được coi là outliers:

```python
from scipy import stats

# Tính Z-score
z_scores = np.abs(stats.zscore(df['numeric_column']))

# Loại bỏ values với |z| > 3
df = df[(z_scores < 3)]
```

**Bước 3: Capping Outliers**

Thay vì loại bỏ, chúng ta có thể giữ lại nhưng giới hạn giá trị:

```python
# Cap outliers tại Q1 - 1.5×IQR và Q3 + 1.5×IQR
df['column_name'] = df['column_name'].clip(lower=lower_bound, upper=upper_bound)
```

### 2.3. Xử lý Duplicates (Dòng dữ liệu trùng lặp)

Duplicate rows có thể xuất hiện do lỗi nhập liệu hoặc người dùng submit form nhiều lần.

**Bước 1: Kiểm tra exact duplicates**

```python
# Tìm số lượng dòng hoàn toàn trùng lặp
print(f"Số dòng trùng lặp: {df.duplicated().sum()}")

# Kiểm tra duplicates cho cột cụ thể
print(f"Duplicate theo email: {df.duplicated(subset=['email']).sum()}")
```

**Bước 2: Xóa duplicate rows**

```python
# Xóa các dòng hoàn toàn trùng lặp, giữ lại dòng đầu tiên
df = df.drop_duplicates(keep='first')

# Xóa duplicates theo cột cụ thể
df = df.drop_duplicates(subset=['email'], keep='first')
```

### Kết quả sau Data Cleaning

```
Input:  1250 rows × 8 columns
  ├─ Xóa rows với > 50% missing: -20 rows
  ├─ Xóa outliers: -5 rows
  ├─ Xóa duplicates: -15 rows
Output: 1210 rows × 8 columns (Ready for next steps)
```

## 3. 3.2.2: Chuẩn Hóa Văn Bản Tiếng Việt (Vietnamese Text Normalization)

Tiếng Việt có các dấu thanh (tonal marks) như ă, ơ, ư, đ làm cho xử lý NLP phức tạp. Chuẩn hóa tiếng Việt đảm bảo tất cả text có định dạng nhất quán.

### 3.1. Remove diacritics (Loại bỏ dấu)

```python
import unicodedata

def remove_diacritics(text):
    """Loại bỏ diacritics khỏi text tiếng Việt"""
    # NFD normalization tách dấu ra khỏi ký tự gốc
    nfd = unicodedata.normalize('NFD', text)
    # Loại bỏ các combining characters (dấu)
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')

# Test
print(remove_diacritics("Công nghệ thông tin"))  # Output: "Cong nghe thong tin"
```

### 3.2. Lowercase (Chuyển thành chữ thường)

```python
# Chuyển tất cả thành lowercase
text = text.lower()
# "Công NGHỆ" → "công nghệ"
```

### 3.3. Strip whitespace (Xóa khoảng trắng)

```python
# Xóa leading/trailing spaces
text = text.strip()

# Xóa extra spaces giữa từ
import re
text = re.sub(r'\s+', ' ', text)
```

### 3.4. Remove special characters (Xóa ký tự đặc biệt)

```python
import re

def clean_text(text):
    """Làm sạch text"""
    # Giữ lại chữ cái, số, space
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text
```

### Ví dụ quy trình chuẩn hóa tiếng Việt:

```python
def normalize_vietnamese(text):
    if not isinstance(text, str):
        return ""

    # 1. Remove diacritics
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')

    # 2. Lowercase
    text = text.lower()

    # 3. Strip & remove extra spaces
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)

    # 4. Remove special characters
    text = re.sub(r'[^a-z0-9\s]', '', text)

    return text

# Test
print(normalize_vietnamese("Tôi yêu Công Nghệ!!!"))
# Output: "toi yeu cong nghe"
```

## 4. 3.2.3: Chuẩn Hóa Giá Trị Phân Loại (Categorical Normalization)

Các trường phân loại như "Sở thích chính", "Môn học yêu thích" cần được chuẩn hóa để đảm bảo tính nhất quán.

### 4.1. Mapping values

```python
# Tạo mapping dictionary
categorical_mapping = {
    'so_thich_chinh': {
        'Technology': 'cong_nghe',
        'Business': 'kinh_doanh',
        'Healthcare': 'y_te',
        ...
    },
    'mon_hoc_yeu_thich': {
        'Math': 'toan',
        'Physics': 'ly',
        'Chemistry': 'hoa',
        ...
    }
}

# Apply mapping
for col, mapping in categorical_mapping.items():
    df[col] = df[col].map(mapping)
```

### 4.2. Consistency check

```python
# Kiểm tra all values đã được mapping
unmapped = df[df['so_thich_chinh'].isna()]['so_thich_chinh'].unique()
if len(unmapped) > 0:
    print(f"Unmapped values: {unmapped}")
```

## 5. 3.2.4: Mã Hóa Dữ Liệu Phân Loại (One-Hot Encoding)

One-Hot Encoding chuyển đổi categorical values thành binary vectors.

### 5.1. Tạo OneHotEncoder

```python
from sklearn.preprocessing import OneHotEncoder

ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
```

### 5.2. Fit trên training data

```python
# Fit chỉ trên training set
categorical_cols = ['so_thich_chinh', 'mon_hoc_yeu_thich', 'ky_nang_noi_bat']
ohe.fit(df_train[categorical_cols])
```

### 5.3. Transform data

```python
# Transform training & test set
X_train_ohe = ohe.transform(df_train[categorical_cols])
X_test_ohe = ohe.transform(df_test[categorical_cols])

# Kết quả: Dense array (n_samples, n_features)
print(f"Shape: {X_train_ohe.shape}")  # (960, 48)
```

## 6. 3.2.5: Xử Lý NLP cho Câu Tự Luận (TF-IDF Vectorization)

TF-IDF chuyển đổi text thành vector số phản ánh mức độ quan trọng của từ.

### 6.1. Tạo TfidfVectorizer

```python
from sklearn.feature_extraction.text import TfidfVectorizer

tfidf = TfidfVectorizer(
    max_features=500,
    ngram_range=(1, 2),
    min_df=2,
    sublinear_tf=True
)
```

### 6.2. Fit & Transform

```python
# Fit chỉ trên training set
X_train_tfidf = tfidf.fit_transform(df_train['profile_text'])

# Transform test set
X_test_tfidf = tfidf.transform(df_test['profile_text'])

# Kết quả: Sparse matrix (n_samples, n_features)
print(f"Shape: {X_train_tfidf.shape}")  # (960, 500)
```

## 7. 3.2.6: Tạo Dữ Liệu Nhân Tạo & Cân Bằng (Synthetic Data)

Dữ liệu thực tế thường imbalanced (số lượng mẫu giữa các ngành không đều). Tạo synthetic data để cân bằng.

### 7.1. Tại sao cần synthetic data

- Dữ liệu imbalanced → model bias (ưu tiên lớp đa số)
- Synthetic data → balanced dataset → fair model

### 7.2. Cách tạo synthetic data

```python
import random
from faker import Faker

def generate_synthetic_student(major):
    """Tạo một hồ sơ học sinh giả lập"""
    fake = Faker()

    return {
        'so_thich_chinh': random.choice(['cong_nghe', 'kinh_doanh', ...]),
        'mon_hoc_yeu_thich': random.choice(['toan', 'ly', 'hoa']),
        'ky_nang_noi_bat': random.choice(['phan_tich', 'giao_tiep', ...]),
        'tính_cách': random.choice(['huong_noi', 'huong_ngoai', ...]),
        'mo_ta_ban_than': fake.text(),
        'dinh_huong_tuong_lai': fake.text(),
        'major': major
    }

# Tạo 1200 samples (80 per major)
synthetic_data = []
for major in all_majors:
    for _ in range(80):
        synthetic_data.append(generate_synthetic_student(major))

df_synthetic = pd.DataFrame(synthetic_data)
```

## 8. Quy Trình Hoàn Chỉnh

```
Input CSV (Raw data)
    ↓
Step 1: Data Cleaning
    ├─ Remove missing values
    ├─ Remove outliers
    ├─ Remove duplicates
    ↓ Output: 1210 rows
Step 2: Vietnamese Normalization
    ├─ Remove diacritics
    ├─ Lowercase
    ├─ Strip whitespace
    ↓ Output: Normalized text
Step 3: Categorical Normalization
    ├─ Map values
    ├─ Consistency check
    ↓ Output: Standardized categories
Step 4: One-Hot Encoding
    ├─ Create OHE
    ├─ Fit on train
    ├─ Transform train & test
    ↓ Output: 48 binary features
Step 5: TF-IDF Vectorization
    ├─ Build profile text
    ├─ Create TF-IDF
    ├─ Fit on train
    ├─ Transform train & test
    ↓ Output: 500 TF-IDF features
Step 6: Feature Combination
    ├─ Hstack OHE + TF-IDF
    ↓ Output: 548 total features
Step 7: Synthetic Data (Optional)
    ├─ Generate synthetic samples
    ├─ Balance classes
    ↓ Output: Balanced dataset
Step 8: Train Model
    ├─ RandomForest or LogisticRegression
    ├─ Calibration
    ↓ Output: Trained model
```

## 9. Kết Luận

✓ **Data Cleaning** → Loại bỏ nhiễu & lỗi
✓ **Vietnamese Normalization** → Chuẩn hóa tiếng Việt
✓ **Categorical Normalization** → Standardize categories
✓ **One-Hot Encoding** → Mã hóa phân loại
✓ **TF-IDF** → Mã hóa text
✓ **Synthetic Data** → Cân bằng dataset
✓ **Quality Input** → Better model performance

Tiền xử lý dữ liệu là nền tảng quyết định chất lượng của toàn bộ hệ thống machine learning. Đầu vào sạch sẽ → Đầu ra tốt hơn!

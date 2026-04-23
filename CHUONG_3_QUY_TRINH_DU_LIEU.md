# Chương 3: QUY TRÌNH DỮ LIỆU

## 3.1. Thu thập & Số hóa dữ liệu (Data Collection)

### 3.1.1. Thiết kế biểu mẫu Google Form phục vụ thu thập dữ liệu huấn luyện

Trong giai đoạn khởi đầu, dữ liệu là yếu tố then chốt quyết định chất lượng của mô hình máy học. Để thu thập dữ liệu có chất lượng cao và đầy đủ cho hệ thống tư vấn ngành học, chúng ta thiết kế một biểu mẫu Google Form với các trường thông tin bắt buộc và tùy chọn.

**Các trường bắt buộc (Required Fields):**

- **Sở thích chính (so_thich_chinh):** Lựa chọn từ 8 lĩnh vực: Công nghệ, Kinh doanh, Du lịch, Nghệ thuật, Y tế, Ngôn ngữ, Pháp lý, Giáo dục
- **Môn học yêu thích (mon_hoc_yeu_thich):** Chọn từ 9 môn: Toán, Văn, Anh, Tin học, Sinh, Hóa, Sử, Địa, Lý
- **Kỹ năng nổi bật (ky_nang_noi_bat):** Gồm 10 kỹ năng như Phân tích dữ liệu, Giao tiếp, Thuyết trình, Sáng tạo, Lãnh đạo, v.v.
- **Tính cách (tinh_cach):** 9 đặc điểm như Hướng nội, Hướng ngoại, Tỉ mỉ, Năng động, Kiên nhẫn, v.v.
- **Môi trường làm việc mong muốn (moi_truong_lam_viec_mong_muon):** 5 tùy chọn: Kỹ thuật, Văn phòng, Linh hoạt, Bệnh viện, Trường học
- **Mục tiêu nghề nghiệp (muc_tieu_nghe_nghiep):** 7 tùy chọn: Ổn định, Phát triển chuyên môn, Thu nhập cao, Theo đam mê, v.v.

**Các trường tùy chọn (Optional Fields) - khuyến nghị điền:**

- **Mô tả bản thân (mo_ta_ban_than):** Văn bản tự do để học sinh mô tả thêm về bản thân, sở thích, kinh nghiệm
- **Định hướng tương lai (dinh_huong_tuong_lai):** Mô tả về mục tiêu và tầm nhìn trong tương lai của học sinh

Cách tiếp cận này đảm bảo rằng dữ liệu thu thập vừa có tính cấu trúc (structured data từ các trường dropdown), vừa có tính linh hoạt (unstructured text từ hai trường mô tả).

### 3.1.2. Tải về lưu trữ dữ liệu thô (data.csv)

Sau khi thu thập đủ dữ liệu (ít nhất 1200 mẫu để đảm bảo mỗi ngành có ít nhất 20 mẫu), chúng ta tiến hành tải dữ liệu từ Google Form về dạng file CSV. File CSV này chứa toàn bộ các cột tương ứng với các trường form và mỗi hàng đại diện cho một hồ sơ học sinh.

Cấu trúc file data.csv:

- Hàng đầu tiên: Tên các cột (header)
- Các hàng tiếp theo: Dữ liệu học sinh, mỗi hàng là một mẫu dữ liệu

Việc lưu trữ dữ liệu thô dưới dạng CSV cho phép dễ dàng chuyển đổi, xử lý và bảo quản. File này sẽ được lưu tại `data/raw/students.csv`.

## 3.2. Tiền xử lý dữ liệu (Data Preprocessing)

Tiền xử lý dữ liệu là giai đoạn quan trọng đảm bảo chất lượng dữ liệu đầu vào trước khi đưa vào model huấn luyện. Quá trình này bao gồm làm sạch dữ liệu, mã hóa, chuẩn hóa ngôn ngữ và xây dựng các đặc trưng.

### 3.2.1. Làm sạch dữ liệu (Xóa dòng trống, xử lý nhiễu)

Bước đầu tiên của tiền xử lý là loại bỏ các dòng dữ liệu không hợp lệ hoặc không đầy đủ:

- **Xóa dòng với giá trị thiếu (Missing Values):** Sử dụng `dropna(subset=[TARGET_COL])` để loại bỏ các mẫu không có nhãn ngành
- **Xóa dòng trùng lặp:** Phát hiện và xóa các hàng dữ liệu hoàn toàn giống nhau
- **Xử lý outliers:** Xác định và xử lý các giá trị bất thường hoặc không phù hợp
- **Kiểm chứng tính hợp lệ:** Đảm bảo mỗi trường categorical chỉ chứa các giá trị được phép

Ví dụ trong code:

```python
df = df.dropna(subset=[TARGET_COL]).copy()
```

### 3.2.2. Mã hóa dữ liệu categorical (Label/One-hot Encoding)

6 trường categorical cần được chuyển đổi từ text sang dạng số để model có thể xử lý. Chúng ta sử dụng **One-Hot Encoding** để tránh các vấn đề với encoding ordinal:

- **Sở thích chính** (8 giá trị) → 8 cột binary
- **Môn học yêu thích** (9 giá trị) → 9 cột binary
- **Kỹ năng nổi bật** (10 giá trị) → 10 cột binary
- **Tính cách** (9 giá trị) → 9 cột binary
- **Môi trường làm việc** (5 giá trị) → 5 cột binary
- **Mục tiêu nghề nghiệp** (7 giá trị) → 7 cột binary

Mã hóa này được thực hiện bằng `OneHotEncoder` từ scikit-learn với `sparse_output=True` để tiết kiệm bộ nhớ:

```python
encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=True)
x_cat_encoded = encoder.fit_transform(x_cat)
```

### 3.2.3. Chuẩn hóa tiếng Việt và xử lý text (TF-IDF Vectorizer)

Hai trường text (mô tả bản thân và định hướng tương lai) cần phải được xử lý đặc biệt vì chúng chứa tiếng Việt có dấu và các ký tự đặc biệt:

**Bước 1: Chuẩn hóa tiếng Việt**

- Loại bỏ dấu (NFD normalization + removing combining characters)
- Chuyển thành chữ thường
- Xử lý ký tự đặc biệt (thay "&" bằng "và", xóa các ký tự không cần thiết)

**Bước 2: Xây dựng Profile Text**
Kết hợp tất cả 8 trường thành một đoạn văn bản nhất quán để TF-IDF có thể phân tích toàn bộ profile:

```python
profile_text = combine(6_categorical_fields + mo_ta_ban_than + dinh_huong_tuong_lai)
```

**Bước 3: TF-IDF Vectorization**

- Chuyển đổi profile text thành vector số sử dụng TF-IDF
- Số lượng features tối đa được chọn là 500-1200 tuỳ theo kích thước dataset
- Sử dụng bi-gram (1-2 từ liên tiếp) để capture các mối quan hệ giữa các từ
- `min_df=2` để bỏ qua các từ xuất hiện quá hiếm

```python
tfidf = TfidfVectorizer(max_features=tfidf_size, ngram_range=(1, 2), min_df=2)
x_text = tfidf.fit_transform(df["profile_text"])
```

### 3.2.4. Chuẩn hóa tiếng Việt (Vietnamese Text Normalization)

Đây là một bước rất quan trọng đặc thù cho dữ liệu tiếng Việt. Tiếng Việt có các dấu (tonal marks) và việc chuẩn hóa chúng là cần thiết để:

- Đảm bảo tính nhất quán khi so khớp dữ liệu
- Tránh các vấn đề do encoding khác nhau
- Làm sạch dữ liệu đầu vào từ người dùng

Quá trình chuẩn hóa bao gồm:

```python
def _normalize_text(value):
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("đ", "d")
    return text
```

## 3.3. Phân tách dữ liệu (Data Splitting)

Sau khi tiền xử lý dữ liệu, bước tiếp theo là chia dữ liệu thành hai tập hợp: tập huấn luyện (training set) và tập kiểm tra (test set). Việc này đảm bảo rằng model được đánh giá trên dữ liệu chưa từng thấy trước đó.

### 3.3.1. Tập huấn luyện (Train Set) - 80% dữ liệu để AI học

Tập huấn luyện chứa 80% của toàn bộ dữ liệu và được sử dụng để:

- Huấn luyện các trọng số (weights) của model
- Tối ưu hóa các tham số (parameters) của thuật toán
- Calibrate xác suất dự đoán

Sử dụng `train_test_split` từ scikit-learn với `test_size=0.2` và `random_state=42` để đảm bảo tính lặp lại:

```python
x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=42, stratify=y
)
```

**Tầm quan trọng của Stratified Split:**

- `stratify=y` đảm bảo tỷ lệ của mỗi ngành được giữ nguyên trong cả train và test set
- Điều này rất quan trọng khi dữ liệu không cân bằng (imbalanced)
- Nếu ngành A chiếm 20% trong dữ liệu gốc, nó cũng sẽ chiếm 20% trong train set

### 3.3.2. Tập kiểm tra (Test Set) - 20% dữ liệu để đánh giá

Tập kiểm tra chứa 20% dữ liệu còn lại và được sử dụng để:

- Đánh giá hiệu suất của model trên dữ liệu chưa từng thấy
- Phát hiện hiện tượng overfitting (nếu train accuracy cao nhưng test accuracy thấp)
- Lựa chọn giữa các model tốt nhất

Dữ liệu trong test set **không bao giờ** được dùng trong quá trình huấn luyện. Độ chính xác (accuracy) trên test set là chỉ báo đáng tin cậy nhất cho hiệu suất của model trong thực tế.

### 3.3.3. Stratified K-Fold Cross-Validation

Ngoài train-test split, chúng ta cũng sử dụng **Cross-Validation** để có đánh giá robust hơn:

```python
from sklearn.model_selection import StratifiedKFold

skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
for train_idx, val_idx in skf.split(x, y):
    x_tr = x[train_idx]
    x_va = x[val_idx]
    y_tr = y.iloc[train_idx]
    y_va = y.iloc[val_idx]
    # Train and evaluate
```

**Lợi ích:**

- Sử dụng tất cả dữ liệu cho cả training và validation
- Giảm variance trong đánh giá hiệu suất
- Phát hiện overfitting hiệu quả hơn
- Số splits được điều chỉnh dựa trên kích thước class nhỏ nhất

## 3.4. Trích xuất & Lựa chọn đặc trưng (Feature Extraction & Selection)

Trích xuất đặc trưng (feature extraction) là quá trình chuyển đổi dữ liệu thô thành các đặc trưng (features) có ý nghĩa mà model có thể học. Lựa chọn đặc trưng (feature selection) là quy trình loại bỏ những đặc trưng không quan trọng để cải thiện hiệu suất.

### 3.4.1. Mã hóa dữ liệu categorical (One-hot Encoding) trên tập Train

Trên tập dữ liệu huấn luyện, chúng ta áp dụng One-hot Encoding để chuyển đổi 6 trường categorical:

```python
# Fit encoder chỉ trên training set
encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=True)
x_cat_train = encoder.fit_transform(x_train[CATEGORICAL_COLS])

# Transform test set sử dụng encoder được fit trên training set
x_cat_test = encoder.transform(x_test[CATEGORICAL_COLS])
```

**Tầm quan trọng của việc fit chỉ trên training set:**

- Ngăn chặn data leakage (rò rỉ thông tin từ test set vào model)
- Đảm bảo model chỉ học từ training data
- Nếu có một giá trị categorical xuất hiện chỉ trong test set, `handle_unknown="ignore"` sẽ xử lý nó

Kết quả của bước này là một ma trận thưa (sparse matrix) với hàng triệu cột binary (một cho mỗi giá trị categorical).

### 3.4.2. Xử lý NLP cho câu hỏi tự do (TF-IDF Vectorizer) trên tập Train

Tương tự như categorical encoding, TF-IDF cũng phải được fit chỉ trên training set:

```python
# Fit TF-IDF chỉ trên training set
tfidf = TfidfVectorizer(
    max_features=tfidf_size,
    ngram_range=(1, 2),
    min_df=2,
    sublinear_tf=True
)
x_text_train = tfidf.fit_transform(x_train["profile_text"])

# Transform test set sử dụng TF-IDF được fit trên training set
x_text_test = tfidf.transform(x_test["profile_text"])
```

**Các tham số quan trọng:**

- `max_features`: Giới hạn số lượng features (từ) để tránh quá nhiều đặc trưng
- `ngram_range=(1, 2)`: Sử dụng unigrams (1 từ) và bigrams (2 từ liên tiếp)
- `min_df=2`: Bỏ qua các từ xuất hiện chỉ 1 lần (noise)
- `sublinear_tf=True`: Sử dụng sublinear term frequency scaling để giảm ảnh hưởng của các từ tần suất cao

### 3.4.3. Lựa chọn đặc trưng cơ bản (Sở thích, Kỹ năng, Tính cách)

Sau khi đã có các đặc trưng từ One-hot Encoding và TF-IDF, chúng ta kết hợp chúng vào một ma trận đặc trưng chung:

```python
from scipy.sparse import hstack

# Kết hợp one-hot encoded categorical + TF-IDF text
x_train = hstack([x_cat_train, x_text_train])
x_test = hstack([x_cat_test, x_text_test])
```

**Cấu trúc ma trận đặc trưng cuối cùng:**

- Cột 1-48: One-hot encoded categorical features (8+9+10+9+5+7 = 48 cột)
- Cột 49-end: TF-IDF features (500-1200 cột tuỳ kích thước dataset)
- **Tổng cộng:** ~550-1250 features cho mỗi mẫu

**Tầm quan trọng của việc lựa chọn đặc trưng:**

- Giảm kích thước model (ít tham số → fit nhanh hơn)
- Cải thiện generalization (model không overfit vào noise)
- Tăng khả năng giải thích của model (ít features → dễ hiểu hơn)

### 3.4.4. Loại bỏ đặc trưng không quan trọng

Mặc dù chúng ta sử dụng tất cả 48 one-hot features (vì chúng đều có ý nghĩa lâm sàng), chúng ta có thể lựa chọn top TF-IDF features dựa trên:

1. **Variance:** Loại bỏ features có variance thấp (ít thay đổi)
2. **Correlation:** Loại bỏ features có correlation cao với nhau (redundant)
3. **Feature Importance:** Sử dụng importances từ model (sau khi train)

Trong dự án này, chúng ta sử dụng `max_features` trong TF-IDF để giới hạn số lượng TF-IDF features, và giữ lại tất cả categorical features vì chúng đại diện cho các khía cạnh quan trọng của hồ sơ học sinh.

### Tóm tắt quy trình Feature Extraction & Selection

```
Input Data (1200 rows × 8 fields)
          ↓
1. One-Hot Encode 6 categorical fields
          ↓
2. Build profile_text từ tất cả 8 fields
          ↓
3. TF-IDF Vectorize profile_text
          ↓
4. Hstack kết hợp: OneHot (48 cols) + TF-IDF (500-1200 cols)
          ↓
Output Feature Matrix (1200 rows × 548-1248 cols)
          ↓
Train/Test Split → Huấn luyện Model → Dự đoán ngành
```

Quá trình này đảm bảo rằng tất cả thông tin trong hồ sơ học sinh được chuyển thành các đặc trưng số có thể được xử lý bởi các thuật toán machine learning, đồng thời loại bỏ noise và giữ lại các đặc trưng quan trọng nhất.

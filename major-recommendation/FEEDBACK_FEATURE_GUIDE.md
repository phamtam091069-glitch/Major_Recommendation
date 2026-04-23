# 📊 Hướng Dẫn Tính Năng Feedback từ Người Dùng

## 🎯 Giới Thiệu

Tính năng **Feedback** cho phép người dùng đánh giá độ chính xác của dự đoán ngành học. Dữ liệu này được lưu trữ để:

- Cải thiện chất lượng model trong tương lai
- Phân tích hiệu suất của từng ngành
- Xây dựng dataset feedback thực tế

---

## ✨ Các Tính Năng

### 1. **⭐ Đánh Giá Sao (Star Rating)**

- Người dùng có thể chọn từ **1 đến 5 sao** để đánh giá
- **Hover trên sao**: Hiển thị xem trước rating
- **Click trên sao**: Lưu lựa chọn và hiển thị tất cả sao được chọn
- CSS animation: Sao sáng lên khi được chọn

### 2. **💬 Bình Luận Tùy Chọn**

- Textarea cho phép người dùng ghi chú thêm
- Placeholder gợi ý: "Ví dụ: Rất phù hợp! / Không chính xác lắm"
- Tùy chọn - không bắt buộc

### 3. **✓ Gửi Feedback**

- Nút "Gửi đánh giá" gửi dữ liệu đến `POST /feedback`
- Kiểm tra validation: rating phải từ 1-5
- Hiển thị message thành công sau khi gửi
- Nút bị disable sau khi gửi để tránh spam

### 4. **Bỏ Qua**

- Nút "Bỏ qua" để người dùng không muốn đánh giá
- Làm mờ feedback section sau khi bỏ qua

---

## 🔧 API Endpoints

### **POST /feedback** - Gửi Đánh Giá

**Request:**

```json
{
  "major": "Cong nghe thong tin",
  "major_display": "Công nghệ thông tin",
  "rating": 5,
  "comment": "Rất phù hợp với định hướng của tôi"
}
```

**Response (Success - 200):**

```json
{
  "success": true,
  "message": "Cảm ơn đánh giá của bạn!"
}
```

**Response (Error - 400/500):**

```json
{
  "error": "Lý do lỗi..."
}
```

---

### **GET /feedback-stats** - Lấy Thống Kê

**Response (200):**

```json
{
  "total_feedbacks": 150,
  "majors": {
    "Cong nghe thong tin": {
      "major": "Công nghệ thông tin",
      "count": 45,
      "average": 4.6,
      "ratings": [5, 5, 4, 4, 5, ...]
    },
    "Khoa hoc du lieu": {
      "major": "Khoa học dữ liệu",
      "count": 38,
      "average": 4.2,
      "ratings": [4, 4, 5, 3, 4, ...]
    }
  }
}
```

---

## 📁 Cấu Trúc Dữ Liệu

### **user_feedback.json**

```json
{
  "feedbacks": [
    {
      "id": "f_0001",
      "timestamp": "2026-04-14T17:30:45.123456",
      "major": "Cong nghe thong tin",
      "major_display": "Công nghệ thông tin",
      "rating": 5,
      "comment": "Rất phù hợp!"
    },
    {
      "id": "f_0002",
      "timestamp": "2026-04-14T17:35:20.654321",
      "major": "Khoa hoc du lieu",
      "major_display": "Khoa học dữ liệu",
      "rating": 4,
      "comment": "Tuyệt vời, đúng với định hướng"
    }
  ]
}
```

---

## 🎨 Giao Diện UI

### **Feedback Section (Hiển thị trên mỗi ngành trong Top 3)**

```
⭐ Bạn thấy sao về dự đoán này?

[⭐] [⭐] [⭐] [⭐] [⭐]

[Textarea: Bình luận tùy chọn...]

[✓ Gửi đánh giá] [Bỏ qua]
```

### **CSS Classes**

- `.feedback-section` - Container chứa feedback form
- `.star-rating` - Container chứa các button sao
- `.star` - Mỗi nút sao (có class `.active` khi được chọn)
- `.feedback-comment` - Textarea bình luận
- `.feedback-success` - Thông báo gửi thành công
- `.feedback-stats-box` - Container thống kê

---

## 🚀 Cách Sử Dụng

### **Từ Frontend (script.js)**

```javascript
// Hàm gửi feedback (được gọi khi click "Gửi đánh giá")
async function submitFeedback(majorKey, majorName, rating, comment) {
  const response = await fetch("/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      major: majorKey,
      major_display: majorName,
      rating: rating,
      comment: comment || "",
    }),
  });

  const data = await response.json();
  if (response.ok) {
    console.log("Feedback submitted successfully!");
  } else {
    alert("Error: " + data.error);
  }
}
```

### **Từ Backend (app.py)**

```python
# Lấy thống kê feedback
@app.route("/feedback-stats", methods=["GET"])
def get_feedback_stats():
    feedback_data = load_user_feedback()
    feedbacks = feedback_data.get("feedbacks", [])
    # Tính toán thống kê...
    return jsonify({"total_feedbacks": len(feedbacks), "majors": stats})
```

---

## 📊 Thống Kê Feedback

### **Xem Thống Kê**

```bash
curl http://127.0.0.1:5000/feedback-stats | python -m json.tool
```

### **Phân Tích Dữ Liệu**

```python
import json

with open('user_feedback.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Tính rating trung bình cho mỗi ngành
from collections import defaultdict

ratings_by_major = defaultdict(list)
for fb in data['feedbacks']:
    major = fb['major_display']
    ratings_by_major[major].append(fb['rating'])

for major, ratings in sorted(ratings_by_major.items()):
    avg = sum(ratings) / len(ratings)
    print(f"{major}: {avg:.1f}⭐ ({len(ratings)} votes)")
```

---

## ⚙️ Cấu Hình

### **Validation Rules**

- `rating`: Phải từ 1-5
- `comment`: Tùy chọn, tối đa 500 ký tự
- `major`: Bắt buộc, phải khớp với danh sách ngành

### **Limits**

- Mỗi người dùng có thể gửi feedback cho mỗi ngành nhiều lần (nếu muốn cập nhật)
- Không có rate limiting (có thể thêm sau)

---

## 🔐 Bảo Mật

- ✅ Input validation trên backend
- ✅ Sanitize comment text (tránh XSS)
- ✅ Logging tất cả feedback submissions
- ⚠️ **TODO**: Thêm authentication để theo dõi người dùng

---

## 📈 Cải Tiến Tương Lai

1. **Database Integration**
   - Chuyển từ JSON sang PostgreSQL/MongoDB
   - Thêm indexing để tìm kiếm nhanh

2. **User Authentication**
   - Theo dõi feedback theo user ID
   - Cho phép người dùng edit/delete feedback của họ

3. **Advanced Analytics**
   - Biểu đồ rating theo thời gian
   - So sánh rating với model accuracy
   - Suggestion để cải thiện model

4. **Feedback Analytics Dashboard**
   - UI riêng để xem thống kê feedback
   - Visualization: charts, graphs, heatmaps

5. **Auto Model Retraining**
   - Kích hoạt retraining model khi có đủ feedback mới
   - So sánh hiệu suất model trước/sau

---

## 🐛 Troubleshooting

### **Error: "Vui lòng chọn số sao trước khi gửi"**

- Người dùng chưa chọn sao
- **Giải pháp**: Chọn ít nhất 1 sao

### **Error: "Rating phải từ 1 đến 5"**

- Backend validation thất bại
- **Giải pháp**: Check request data

### **Error: "Thiếu thông tin ngành"**

- Field `major` hoặc `major_display` trống
- **Giải pháp**: Check API request

### **Feedback không được lưu**

- **Check**: `user_feedback.json` có write permission không?
- **Check**: Disk space có đủ không?
- **Check**: Log trong console app.py

---

## 📝 Ví Dụ Đầy Đủ

### **Test Endpoint bằng curl**

```bash
curl -X POST http://127.0.0.1:5000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "major": "Cong nghe thong tin",
    "major_display": "Công nghệ thông tin",
    "rating": 5,
    "comment": "Rất phù hợp với định hướng của tôi!"
  }'
```

### **Lấy Thống Kê**

```bash
curl http://127.0.0.1:5000/feedback-stats | python -m json.tool
```

---

## 📚 File Liên Quan

- `templates/index.html` - Feedback UI
- `static/style.css` - Feedback styling
- `static/script.js` - Feedback logic
- `app.py` - API endpoints
- `user_feedback.json` - Dữ liệu feedback

---

**Phiên bản**: 1.0  
**Cập nhật**: 2026-04-14  
**Trạng thái**: ✅ Hoàn thành

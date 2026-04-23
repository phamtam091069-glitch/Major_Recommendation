# 🎬 Hướng Dẫn Hiệu Ứng Hình Ảnh - Quick Start

## 🚀 Bắt Đầu Nhanh

### Step 1: Chạy ứng dụng

```bash
python app.py
```

### Step 2: Truy cập trang web

```
http://127.0.0.1:5000
```

### Step 3: Trải nghiệm các hiệu ứng

Trang web sẽ hiển thị với avatar robot sống động! 🤖

---

## 👀 Các Hiệu Ứng Bạn Sẽ Thấy

### **🤖 Avatar Robot - Mascot Chính**

Ở đầu trang, bạn sẽ thấy:

- **Robot xinh xắn** với đầu xanh dương sáng
- **Mắt nhấp nháy** tự động
- **Miệng nói chuyện** (lèo lái miệng)
- **Cánh tay vẫy vẫy** nhẹ nhàng
- **Antenna lắc lư** trên đầu
- **Nút xanh sáng lên** trên ngực

#### **Khi bạn di chuyển chuột:**

→ Mắt robot **sẽ theo dõi con trỏ chuột** của bạn!

#### **Khi bạn nhấn "Dự đoán ngay":**

→ Robot vào trạng thái **"thinking"** - antenna lắc mạnh hơn, mắt sáng hơn

#### **Khi kết quả hiển thị:**

→ Robot **trở lại trạng thái bình thường**, kết quả slide lên từ dưới

---

### **✨ Hiệu Ứng Form (Trường Nhập Liệu)**

#### **Hover vào dropdown/textarea:**

```
Border sáng lên → Background nhạo hơn → Mượt mà transition
```

#### **Click vào field (focus):**

```
Background sáng lên từ từ (shimmer effect)
→ Border glow xanh dương
→ Box-shadow xanh dương nhẹ
```

---

### **🎯 Hiệu Ứng Buttons (Nút Bấm)**

#### **Hover button:**

```
✓ Nâng lên nhẹ (translateY -1px)
✓ Shadow tăng sáng
✓ Smooth 0.15s transition
```

#### **Click button:**

```
✓ Scale down một chút
✓ Cảm giác "bấm được"
```

---

### **🎴 Hiệu Ứng Cards (Thẻ Form & Result)**

#### **Hover vào card:**

```
1. Nâng lên cao (translateY -6px)
2. Shadow tăng + có glow xanh dương
3. Border sáng lên
4. Transition smooth với cubic-bezier
```

#### **Lúc load trang:**

```
Cards slide in từ dưới lên trên với fadeIn
→ Form card: 0.6s
→ Result card: 0.6s delay 0.1s
```

---

### **📊 Hiệu Ứng Result Items (Kết Quả)**

#### **Lúc hiển thị kết quả:**

```
✓ Slide in từ dưới (slideInUp animation)
✓ Fade in opacity
✓ Staggered timing (mỗi item lệch nhau)
```

#### **Hover vào result item:**

```
✓ Border sáng lên
✓ Background đổi sang xanh dương mờ
✓ Nâng lên (translateY -3px)
✓ Shadow glow xanh dương
✓ Mượt mà transition 0.3s
```

---

### **🔢 Hiệu Ứng Rank Badge (Số 1, 2, 3)**

#### **Liên tục:**

```
Pulse animation:
- Scale 1 → 1.05 (giật nhẹ)
- Ring glow xuất hiện & biến mất
- Timing: 2s ease-in-out infinite
```

---

### **📈 Hiệu Ứng Progress Bar (Thanh Tiến Độ)**

#### **Lúc hiển thị:**

```
✓ Fill từ 0% → [score]%
✓ Animation: 1s ease-out
✓ Glow xanh dương phía dưới
✓ Gradient từ xanh dương → tím
```

---

## 📝 Bảng Tóm Tắt Hiệu Ứng

| Element      | Hover/Focus          | Animation                | Timing      |
| ------------ | -------------------- | ------------------------ | ----------- |
| Robot Mascot | N/A                  | Idle bounce, blink, talk | 2-4s loops  |
| Form Field   | Border glow, shimmer | fieldShimmer             | 0.6s        |
| Button       | Scale, shadow up     | Transform                | 0.15s       |
| Card         | Lift, glow shadow    | cardLift + cardHoverGlow | 0.4s        |
| Result Item  | Border light, lift   | slideInUp + hover effect | 0.6s + 0.3s |
| Rank Badge   | N/A                  | badgePulse               | 2s infinite |
| Progress Bar | N/A                  | progressFill             | 1s          |

---

## 🎨 Màu Sắc Chính

```
🔵 Xanh Dương Chính: #66e3ff (Primary - Glow, mascot eyes)
🟣 Tím: #8f7cff (Secondary - Gradients)
🟦 Xanh Nước Biển: #59d8ff (Mascot body)
🟦 Xanh Đậm: #2d88ff (Outlines, accents)
🟢 Xanh Lá: #4ade80 (Success - mascot button)
⬛ Nền Tối: #081120 (Dark background)
```

---

## 🔊 Animation Speeds

| Speed       | Sử Dụng Cho                         |
| ----------- | ----------------------------------- |
| 0.15s       | Button interactions (fast feedback) |
| 0.2s        | Input focus transitions             |
| 0.3s        | Hover states                        |
| 0.6s        | Form slides                         |
| 1s          | Progress bar fill                   |
| 2-4s        | Mascot idle animations (loops)      |
| 0.3s → 0.6s | Chat animations                     |

---

## 🎭 Mascot States

### **State 1: Idle (Trạng thái bình thường)**

```
✓ Nổi lên xuống nhẹ
✓ Mắt nhấp nháy
✓ Miệng nói
✓ Antenna lắc
✓ Cánh tay vẫy
✓ Nút sáng lên
```

### **State 2: Thinking (Khi đang phân tích)**

```
✓ Antenna lắc mạnh hơn
✓ Mắt sáng lên hơn (glowing)
✓ Toàn bộ animation tăng intensity
```

### **State 3: Happy (Khi có kết quả)**

```
✓ (Hiện chưa implement, có thể thêm)
✓ Miệng cười hạnh phúc
✓ Animation vui vẻ hơn
```

---

## 💡 Developer Tips

### **Muốn tắt mascot eye following?**

Tìm đoạn này trong `static/script.js`:

```javascript
document.addEventListener("mousemove", (e) => {
  // Xóa đoạn này nếu muốn tắt
});
```

### **Muốn thay đổi mascot size?**

Chỉnh trong `static/style.css`:

```css
.hero__mascot {
  width: 160px; /* Thay từ 140px */
  height: 160px; /* Thay từ 140px */
}
```

### **Muốn tăng/giảm animation speed?**

Ví dụ thay đổi `mascotIdle`:

```css
@keyframes mascotIdle {
  /* Thay 3s thành 4s nếu muốn chậm hơn */
  animation: mascotIdle 4s ease-in-out infinite;
}
```

### **Muốn thay mascot color?**

Tìm trong `templates/index.html`:

```html
<circle cx="100" cy="70" r="45" fill="#66e3ff" class="mascot-head" />
<!-- Thay #66e3ff thành màu khác -->
```

---

## ✅ Checklist Kiểm Tra

Khi truy cập trang, đảm bảo bạn thấy:

- [ ] **Robot mascot** ở đầu trang
- [ ] Robot **nhấp nháy mắt**
- [ ] Robot **vẫy tay** nhẹ
- [ ] Robot **antenna lắc lư**
- [ ] Khi **di chuột**, mắt robot **theo dõi**
- [ ] Khi **hover button**, button **nâng lên**
- [ ] Khi **focus field**, background **shimmer**
- [ ] Khi **hover card**, card **nâng lên** với glow
- [ ] Khi **nhấn "Dự đoán ngay"**, robot vào **thinking state**
- [ ] Khi **kết quả hiển thị**, items **slide in**
- [ ] Rank badges **pulse** liên tục
- [ ] Progress bars **fill mượt mà**

---

## 🎥 Video Demo (Tưởng Tượng)

```
[Trang load] → Robot nổi lên xuống, nhấp nháy, vẫy tay
    ↓
[User hover button] → Button nâng lên sáng hơn
    ↓
[User focus field] → Background shimmer
    ↓
[User nhấn Dự đoán] → Robot vào thinking, antenna lắc mạnh
    ↓
[API responds] → Robot quay lại idle
    ↓
[Results slide in] → Cards nổi lên, progress bar fill
    ↓
[User hover result] → Result item sáng lên, nâng lên
```

---

## 🚨 Troubleshooting

### **Robot không hiển thị?**

- Kiểm tra browser console (F12)
- Xóa cache & reload page (Ctrl+Shift+Del)
- Kiểm tra `templates/index.html` có SVG không

### **Animations bị lag?**

- Kiểm tra GPU acceleration (Chrome DevTools → Rendering)
- CSS animations sử dụng `transform` & `opacity` (tối ưu)
- Nếu vẫn lag, giảm số lượng animations hoặc reduce durations

### **Mascot eye tracking không hoạt động?**

- Kiểm tra `static/script.js` có event listener không
- Xóa extension browser nếu conflict
- Test trên tab incognito

### **Colors khác expected?**

- Kiểm tra CSS variables trong `:root`
- Clear browser cache
- Kiểm tra SVG fill values

---

## 📚 File Structure

```
major-recommendation/
├── templates/
│   └── index.html          ← SVG mascot (lines 24-70)
├── static/
│   ├── style.css          ← Animations (lines 135-560)
│   ├── script.js          ← Mascot control (lines 18-56)
│   └── ...
├── ENHANCEMENT_SUMMARY.md  ← Detailed documentation
└── VISUAL_EFFECTS_GUIDE.md ← This file!
```

---

## 🎓 Learning Resources

Nếu bạn muốn học thêm:

- **CSS Animations:** https://developer.mozilla.org/en-US/docs/Web/CSS/animation
- **SVG:** https://developer.mozilla.org/en-US/docs/Web/SVG
- **JavaScript mousemove:** https://developer.mozilla.org/en-US/docs/Web/API/Element/mousemove_event
- **Transform & Performance:** https://web.dev/animations-guide/

---

## 🎉 Kết Thúc

Giờ bạn đã sẵn sàng thưởng thức trang web với:

- 🤖 Avatar mascot thân thiện
- ✨ Hiệu ứng hover sống động
- 🎨 UI/UX professional
- 📱 Responsive trên mọi thiết bị

**Chúc bạn trải nghiệm tuyệt vời!** 🚀

---

**Phiên bản:** 1.0  
**Ngày:** 15/4/2026  
**Made with ❤️ by AI Enhancement Suite**

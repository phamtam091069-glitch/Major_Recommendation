// ============= PAGE LOADING SPINNER =============
document.addEventListener('DOMContentLoaded', () => {
  const loadingContainer = document.getElementById('pageLoadingSpinner');
  if (loadingContainer) {
    setTimeout(() => {
      loadingContainer.classList.add('fade-out');
      // Remove from DOM after fade out completes
      setTimeout(() => {
        loadingContainer.remove();
      }, 500);
    }, 300);
  }
});
// ============= END LOADING SPINNER =============

window.MODEL_READY = document.body.dataset.modelReady === 'true';

const form = document.getElementById('predictionForm');
const placeholder = document.getElementById('placeholder');
const loading = document.getElementById('loading');
const resultBox = document.getElementById('result');
const top3 = document.getElementById('top3');
const reasons = document.getElementById('reasons');
const debugBox = document.getElementById('debugBox');
const debugTop5 = document.getElementById('debugTop5');

const normalizeMap = {
  'Công nghệ': 'Cong nghe',
  'Cơ khí – Kỹ thuật chế tạo': 'Ky thuat',
  'Kinh doanh': 'Kinh doanh',
  'Kế toán – Tài chính': 'Ke toan',
  'Du lịch & Dịch vụ': 'Du lich',
  'Truyền thông & Báo chí': 'Truyen thong',
  'Nghệ thuật': 'Nghe thuat',
  'Kiến trúc – Xây dựng': 'Kien truc',
  'Sáng tạo nội dung & Media': 'Sang tao noi dung',
  'Y tế': 'Y te',
  'Ngôn ngữ': 'Ngon ngu',
  'Pháp lý': 'Phap ly',
  'Giáo dục': 'Giao duc',
  'Toán': 'Toan',
  'Văn': 'Van',
  'Anh': 'Anh',
  'Tin học': 'Tin hoc',
  'Sinh': 'Sinh',
  'Lý': 'Ly',
  'Phân tích dữ liệu': 'Phan tich du lieu',
  'Giao tiếp': 'Giao tiep',
  'Thuyết trình': 'Thuyet trinh',
  'Sáng tạo': 'Sang tao',
  'Lãnh đạo': 'Lanh dao',
  'Tổ chức & Lập kế hoạch': 'To chuc va lap ke hoach',
  'Tư duy logic': 'Tu duy logic',
  'Giải quyết vấn đề': 'Giai quyet van de',
  'Cẩn thận': 'Can than',
  'Làm việc nhóm': 'Lam viec nhom',
  'Hướng nội': 'Huong noi',
  'Quyết đoán': 'Quyet doan',
  'Hướng ngoại': 'Huong ngoai',
  'Tỉ mỉ': 'Ti mi',
  'Năng động': 'Nang dong',
  'Kiên nhẫn': 'Kien nhan',
  'Kỷ luật': 'Ky luat',
  'Trách nhiệm': 'Trach nhiem',
  'Bản lĩnh': 'Ban linh',
  'Quyết đoán': 'Quyet doan',
  'Kỹ thuật': 'Ky thuat',
  'Quay phim - Dựng phim': 'Quay phim - Dung phim',
  'Xưởng / Nhà máy': 'Ky thuat',
  'Công trường': 'Ky thuat',
  'Văn phòng': 'Van phong',
  'Khách sạn & Sự kiện': 'Linh hoat',
  'Bệnh viện': 'Benh vien',
  'Trường học': 'Truong hoc',
  'Linh hoạt': 'Linh hoat',
  'Ổn định': 'On dinh',
  'Phát triển chuyên môn': 'On dinh',
  'Thu nhập cao': 'Thu nhap cao',
  'Theo đam mê': 'Theo dam me',
  'Trải nghiệm quốc tế': 'Theo dam me',
  'Khởi nghiệp': 'Khoi nghiep',
  'Cống hiến xã hội': 'Cong hien xa hoi'
};

function normalize(value) {
  return normalizeMap[value] || value;
}

function makeReadableMultiline(text) {
  if (!text) return '';
  return String(text)
    .replace(/\.\s+/g, '.\n')
    .replace(/;\s+/g, ';\n')
    .trim();
}

function splitIntoBullets(text) {
  return String(text || '')
    .split(/\n+/)
    .map(line => line.trim())
    .filter(Boolean)
    .flatMap(line => line.split(/\s*•\s*/).map(item => item.trim()).filter(Boolean));
}

function renderMiniList(items, className = 'mini-list') {
  if (!items.length) return '';
  return `
    <ul class="${className}">
      ${items.map(item => `<li>${item}</li>`).join('')}
    </ul>
  `;
}

function renderResult(data) {
   top3.innerHTML = '';
   reasons.innerHTML = '';
   if (debugTop5) {
     debugTop5.innerHTML = '';
   }

   const topItems = Array.isArray(data.top_3) ? data.top_3 : [];

   topItems.forEach((item, index) => {
     const majorName = item.major || item.nganh || 'N/A';
     const majorKey = item.nganh || '';
     const score = Number(item.score || 0);
     const groupName = item.group || '';
     const feedback = makeReadableMultiline(item.feedback || '');
     const suggestion = makeReadableMultiline(item.suggestion || '');
     const confidenceText = makeReadableMultiline(item.confidence_text || '');

     const el = document.createElement('div');
     el.className = 'result-item';

     const feedbackItems = splitIntoBullets(feedback);
     const suggestionItems = splitIntoBullets(suggestion);
     const confidenceItems = splitIntoBullets(confidenceText);

     const feedbackBlock = feedbackItems.length
       ? `<div class="score-breakdown multiline-text"><strong>Giải thích:</strong>${renderMiniList(feedbackItems)}</div>`
       : '';

     const suggestionBlock = suggestionItems.length
       ? `<div class="score-breakdown multiline-text"><strong>Gợi ý:</strong>${renderMiniList(suggestionItems, 'mini-list mini-list--accent')}</div>`
       : '';

     const confidenceBlock = confidenceItems.length
       ? `<div class="score-breakdown multiline-text"><strong>Độ tin cậy:</strong>${renderMiniList(confidenceItems, 'mini-list mini-list--soft')}</div>`
       : '';

     el.innerHTML = `
       <div class="result-item__top">
         <div class="major-meta">
           <div class="major-meta__head">
             <div class="rank-badge">${index + 1}</div>
             <div>
               <h3>${majorName}</h3>
               ${groupName ? `<div class="major-group">${groupName}</div>` : ''}
             </div>
           </div>
         </div>
         <strong>${score}%</strong>
       </div>
       <div class="progress"><span style="width:${Math.min(score, 100)}%"></span></div>
       <div class="score-label">Điểm phù hợp: ${score}/100</div>
       ${confidenceBlock}
       ${feedbackBlock}
       ${suggestionBlock}
       <div class="feedback-section" data-major="${majorKey}">
         <p style="margin: 0 0 12px; font-size: 0.9rem; color: var(--muted); font-weight: 600;">
           ⭐ Bạn thấy sao về dự đoán này?
         </p>
         <div class="star-rating">
           <button class="star" data-rating="1" data-major="${majorKey}">⭐</button>
           <button class="star" data-rating="2" data-major="${majorKey}">⭐</button>
           <button class="star" data-rating="3" data-major="${majorKey}">⭐</button>
           <button class="star" data-rating="4" data-major="${majorKey}">⭐</button>
           <button class="star" data-rating="5" data-major="${majorKey}">⭐</button>
         </div>
         <textarea 
           class="feedback-comment" 
           data-major="${majorKey}"
           placeholder="Bình luận (tùy chọn)... Ví dụ: Rất phù hợp! / Không chính xác lắm"
         ></textarea>
         <div style="display: flex; gap: 8px;">
           <button class="btn btn--primary feedback-submit" data-major="${majorKey}" style="flex: 1; padding: 10px 14px; font-size: 0.9rem;">
             ✓ Gửi đánh giá
           </button>
           <button class="btn btn--ghost feedback-skip" data-major="${majorKey}" style="flex: 1; padding: 10px 14px; font-size: 0.9rem;">
             Bỏ qua
           </button>
         </div>
         <div class="feedback-status hidden"></div>
       </div>
     `;
     top3.appendChild(el);

     // Attach star rating event listeners
     const feedbackSection = el.querySelector('.feedback-section');
     const stars = feedbackSection.querySelectorAll('.star');
     const comment = feedbackSection.querySelector('.feedback-comment');
     const submitBtn = feedbackSection.querySelector('.feedback-submit');
     const skipBtn = feedbackSection.querySelector('.feedback-skip');

     let selectedRating = 0;
     stars.forEach(star => {
       star.addEventListener('click', () => {
         selectedRating = parseInt(star.dataset.rating);
         stars.forEach(s => {
           s.classList.toggle('active', parseInt(s.dataset.rating) <= selectedRating);
         });
       });
       star.addEventListener('mouseenter', () => {
         stars.forEach(s => {
           s.style.opacity = parseInt(s.dataset.rating) <= parseInt(star.dataset.rating) ? '1' : '0.4';
         });
       });
     });

     feedbackSection.addEventListener('mouseleave', () => {
       stars.forEach(s => {
         s.style.opacity = s.classList.contains('active') ? '1' : '0.4';
       });
     });

     submitBtn.addEventListener('click', async () => {
       if (selectedRating === 0) {
         alert('Vui lòng chọn số sao trước khi gửi.');
         return;
       }
       await submitFeedback(majorKey, majorName, selectedRating, comment.value);
       submitBtn.disabled = true;
       submitBtn.textContent = '✓ Đã gửi';
       comment.disabled = true;
       stars.forEach(s => s.disabled = true);
       skipBtn.style.display = 'none';
     });

     skipBtn.addEventListener('click', () => {
       feedbackSection.style.opacity = '0.5';
       submitBtn.disabled = true;
       skipBtn.disabled = true;
     });
   });

  if (topItems.length) {
    const li = document.createElement('li');
    li.textContent = 'Các ngành được đề xuất dựa trên mức độ phù hợp của hồ sơ bạn đã nhập.';
    reasons.appendChild(li);
  }

  const debugItems = Array.isArray(data.top_5_diem_tho) ? data.top_5_diem_tho : [];
  if (debugBox && debugTop5 && debugItems.length) {
    debugBox.classList.remove('hidden');
    debugItems.forEach((item, index) => {
      const row = document.createElement('div');
      row.className = 'debug-row';
      row.innerHTML = `
        <div class="debug-rank">#${index + 1}</div>
        <div class="debug-major">${item.nganh}</div>
        <div class="debug-metrics">thô: ${item.diem_tho} · ML: ${item.phan_hoc_may} · cosine: ${item.phan_noi_dung}</div>
      `;
      debugTop5.appendChild(row);
    });
  } else if (debugBox) {
    debugBox.classList.add('hidden');
  }

  placeholder.classList.add('hidden');
  loading.classList.add('hidden');
  resultBox.classList.remove('hidden');
}

function setLoadingState(isLoading) {
  if (isLoading) {
    placeholder.classList.add('hidden');
    resultBox.classList.add('hidden');
    loading.classList.remove('hidden');
  } else {
    loading.classList.add('hidden');
  }
}

// 5 Ngành mẫu có sẵn (Random chọn)
const DEMO_SAMPLES = [
  {
    // 1. Công nghệ thông tin
    so_thich_chinh: 'Công nghệ',
    mon_hoc_yeu_thich: 'Tin học',
    ky_nang_noi_bat: 'Phân tích dữ liệu',
    tinh_cach: 'Kỷ luật',
    moi_truong_lam_viec_mong_muon: 'Kỹ thuật',
    muc_tieu_nghe_nghiep: 'Thu nhập cao',
    mo_ta_ban_than: 'Em thích máy tính, logic và phân tích dữ liệu.',
    dinh_huong_tuong_lai: 'Em muốn học AI, data hoặc phát triển phần mềm.',
  },
  {
    // 2. Khoa học dữ liệu
    so_thich_chinh: 'Công nghệ',
    mon_hoc_yeu_thich: 'Toán',
    ky_nang_noi_bat: 'Phân tích dữ liệu',
    tinh_cach: 'Tỉ mỉ',
    moi_truong_lam_viec_mong_muon: 'Văn phòng',
    muc_tieu_nghe_nghiep: 'Phát triển chuyên môn',
    mo_ta_ban_than: 'Em thích làm việc với số liệu và tìm ra quy luật trong dữ liệu.',
    dinh_huong_tuong_lai: 'Em muốn trở thành Data Scientist hoặc Business Analyst.',
  },
  {
    // 3. Du lịch và lữ hành
    so_thich_chinh: 'Du lịch & Dịch vụ',
    mon_hoc_yeu_thich: 'Anh',
    ky_nang_noi_bat: 'Giao tiếp',
    tinh_cach: 'Hướng ngoại',
    moi_truong_lam_viec_mong_muon: 'Linh hoạt',
    muc_tieu_nghe_nghiep: 'Trải nghiệm quốc tế',
    mo_ta_ban_than: 'Em thích giao tiếp, giới thiệu điểm đến và văn hóa địa phương.',
    dinh_huong_tuong_lai: 'Em muốn làm hướng dẫn viên du lịch hoặc quản lý tour.',
  },
  {
    // 4. Quản trị kinh doanh
    so_thich_chinh: 'Kinh doanh',
    mon_hoc_yeu_thich: 'Toán',
    ky_nang_noi_bat: 'Lãnh đạo',
    tinh_cach: 'Bản lĩnh',
    moi_truong_lam_viec_mong_muon: 'Văn phòng',
    muc_tieu_nghe_nghiep: 'Thu nhập cao',
    mo_ta_ban_than: 'Em thích quản lý, lập kế hoạch và lãnh đạo đội nhóm.',
    dinh_huong_tuong_lai: 'Em muốn trở thành Quản lý hoặc Giám đốc doanh nghiệp.',
  },
  {
    // 5. Thiết kế đồ họa
    so_thich_chinh: 'Sáng tạo nội dung & Media',
    mon_hoc_yeu_thich: 'Văn',
    ky_nang_noi_bat: 'Sáng tạo',
    tinh_cach: 'Tỉ mỉ',
    moi_truong_lam_viec_mong_muon: 'Sáng tạo',
    muc_tieu_nghe_nghiep: 'Theo đam mê',
    mo_ta_ban_than: 'Em thích thiết kế, màu sắc, hình ảnh và tạo nội dung sáng tạo.',
    dinh_huong_tuong_lai: 'Em muốn làm UI/UX Designer hoặc Graphic Designer.',
  },
];

function fillRandomDemo() {
  const randomIndex = Math.floor(Math.random() * DEMO_SAMPLES.length);
  const sample = DEMO_SAMPLES[randomIndex];
  
  // Điền form với sample được chọn
  form.so_thich_chinh.value = sample.so_thich_chinh;
  form.mon_hoc_yeu_thich.value = sample.mon_hoc_yeu_thich;
  form.ky_nang_noi_bat.value = sample.ky_nang_noi_bat;
  form.tinh_cach.value = sample.tinh_cach;
  form.moi_truong_lam_viec_mong_muon.value = sample.moi_truong_lam_viec_mong_muon;
  form.muc_tieu_nghe_nghiep.value = sample.muc_tieu_nghe_nghiep;
  form.mo_ta_ban_than.value = sample.mo_ta_ban_than;
  form.dinh_huong_tuong_lai.value = sample.dinh_huong_tuong_lai;
}

document.getElementById('randomDemoBtn').addEventListener('click', fillRandomDemo);

// Chatbot button in form
document.getElementById('chatbotFormBtn').addEventListener('click', () => {
  // Open new tab with chatbot page (same as floating button)
  window.open('/chatbot', '_blank');
});

// ========== CHATBOT FUNCTIONALITY ==========

// Chat state
let chatHistory = [];
let isChatOpen = false;

// DOM elements
const chatFloatBtn = document.getElementById('chatFloatBtn');
const chatModal = document.getElementById('chatModal');
const chatCloseBtn = document.getElementById('chatCloseBtn');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const chatSendBtn = document.getElementById('chatSendBtn');
const chatBackToFormBtn = document.getElementById('chatBackToFormBtn');
const predictionForm = document.getElementById('predictionForm');
const formCard = document.querySelector('.form-card');

// Toggle chat
function toggleChat(open) {
  isChatOpen = open;
  if (open) {
    chatModal.classList.remove('hidden');
    chatFloatBtn.classList.add('hidden');
    formCard.classList.add('hidden');
    chatInput.focus();
  } else {
    chatModal.classList.add('hidden');
    chatFloatBtn.classList.remove('hidden');
    formCard.classList.remove('hidden');
    chatHistory = [];
    chatMessages.innerHTML = `
      <div class="chat-bubble bot">
        <p>Xin chào! 👋 Mình là chatbot tư vấn ngành học. Bạn muốn biết gì về các ngành học?</p>
      </div>
    `;
  }
}

// Add message to chat
function addMessage(text, sender) {
  const messageEl = document.createElement('div');
  messageEl.className = `chat-bubble ${sender}`;
  messageEl.innerHTML = `<p>${escapeHtml(text)}</p>`;
  chatMessages.appendChild(messageEl);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  chatHistory.push({ role: sender, content: text });
}

// Escape HTML
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Send message
async function sendChatMessage() {
  const message = chatInput.value.trim();
  if (!message) return;

  // Clear input
  chatInput.value = '';

  // Add user message
  addMessage(message, 'user');

  // Show loading state
  const typingEl = document.createElement('div');
  typingEl.className = 'chat-bubble bot';
  typingEl.innerHTML = '<p>⏳ Đang suy nghĩ...</p>';
  chatMessages.appendChild(typingEl);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: message })
    });

    const data = await response.json();

    // Remove loading state
    typingEl.remove();

    if (response.ok && data.reply) {
      addMessage(data.reply, 'bot');
    } else {
      addMessage('Xin lỗi, mình không hiểu được câu hỏi của bạn. Hãy thử hỏi lại!', 'bot');
    }
  } catch (error) {
    typingEl.remove();
    console.error('Chat error:', error);
    addMessage('Có lỗi xảy ra. Vui lòng thử lại!', 'bot');
  }
}

// Event listeners
chatFloatBtn.addEventListener('click', () => {
  // Open new tab with chatbot page
  window.open('/chatbot', '_blank');
});
chatCloseBtn.addEventListener('click', () => toggleChat(false));
chatBackToFormBtn.addEventListener('click', () => toggleChat(false));

chatSendBtn.addEventListener('click', sendChatMessage);
chatInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendChatMessage();
  }
});

// Hàm gửi feedback
async function submitFeedback(majorKey, majorName, rating, comment) {
  try {
    const response = await fetch('/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        major: majorKey,
        major_display: majorName,
        rating: rating,
        comment: comment || ''
      })
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Không thể gửi đánh giá.');
    }

    console.log('Feedback submitted:', data);
  } catch (error) {
    console.error('Feedback error:', error);
    alert('Lỗi khi gửi đánh giá: ' + error.message);
  }
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  // Auto-close chatbot modal when user clicks predict
  if (isChatOpen) {
    toggleChat(false);
  }
  
  if (!window.MODEL_READY) {
    alert('Model chưa sẵn sàng. Hãy chạy python train_model.py trước.');
    return;
  }

  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());
  Object.keys(payload).forEach((key) => {
    payload[key] = normalize(payload[key]);
  });

  setLoadingState(true);

  try {
    const response = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Không thể dự đoán lúc này.');
    }

    renderResult(data);
  } catch (error) {
    setLoadingState(false);
    placeholder.classList.remove('hidden');
    resultBox.classList.add('hidden');
    alert(error.message);
  }
});

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

function normalizeVietnameseText(value) {
  return String(value || '')
    .trim()
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/&/g, ' va ')
    .replace(/[\/-]/g, ' ')
    .replace(/[^\w\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

const normalizeMap = {
  'Công nghệ': 'Cong nghe',
  'Kinh doanh': 'Kinh doanh',
  'Du lịch': 'Du lich',
  'Nghệ thuật': 'Nghe thuat',
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
  'Tổ chức & lập kế hoạch': 'To chuc va lap ke hoach',
  'Tư duy logic': 'Tu duy logic',
  'Giải quyết vấn đề': 'Giai quyet van de',
  'Cẩn thận': 'Can than',
  'Làm việc nhóm': 'Lam viec nhom',
  'Hướng nội': 'Huong noi',
  'Hướng ngoại': 'Huong ngoai',
  'Tỉ mỉ': 'Ti mi',
  'Năng động': 'Nang dong',
  'Kiên nhẫn': 'Kien nhan',
  'Kỷ luật': 'Ky luat',
  'Trách nhiệm': 'Trach nhiem',
  'Bản lĩnh': 'Ban linh',
  'Kỹ thuật': 'Ky thuat',
  'Quay phim - Dựng phim': 'Quay phim Dung phim',
  'Văn phòng': 'Van phong',
  'Bệnh viện': 'Benh vien',
  'Trường học': 'Truong hoc',
  'Linh hoạt': 'Linh hoat',
  'Ổn định': 'On dinh',
  'Phát triển chuyên môn': 'Phat trien chuyen mon',
  'Thu nhập cao': 'Thu nhap cao',
  'Theo đam mê': 'Theo dam me',
  'Trải nghiệm quốc tế': 'Trai nghiem quoc te',
  'Khởi nghiệp': 'Khoi nghiep',
  'Cống hiến xã hội': 'Cong hien xa hoi'
};

function normalize(value) {
  return normalizeMap[value] || normalizeVietnameseText(value);
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

function toNaturalLanguage(text) {
  return String(text || '')
    .replace(/^\s*[•*-]\s*/gm, '')
    .replace(/^\s*\d+[).:-]\s*/gm, '')
    .replace(/\n+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function explainConfidence(score, majorName) {
  const major = majorName ? `cho ngành ${majorName}` : 'cho ngành này';
  if (score >= 28) {
    return `Mức phù hợp khá cao ${major}.`;
  }
  if (score >= 20) {
    return `Mức phù hợp ở mức khá ${major}.`;
  }
  if (score >= 12) {
    return `Đây là gợi ý tham khảo ${major}.`;
  }
  return `Mức phù hợp hiện thấp ${major}, nên xem như lựa chọn dự phòng.`;
}

function explainNextSteps(item) {
  const suggestions = [];
  const majorName = item.major_display || item.major || item.nganh || 'ngành này';
  const score = Number(item.score_display ?? item.score ?? 0);

  if (score >= 28) {
    suggestions.push(`Tìm hiểu sâu hơn về ${majorName}.`);
  } else if (score >= 20) {
    suggestions.push(`So sánh ${majorName} với 1-2 ngành liên quan.`);
  } else {
    suggestions.push(`Xem ${majorName} như một phương án tham khảo.`);
  }

  if (item.suggestion) {
    suggestions.push(`Điểm cần xem thêm: ${toNaturalLanguage(item.suggestion)}`);
  }

  return suggestions;
}

function buildExplanationItems({
  majorName,
  score,
  confidenceNatural,
  feedback,
}) {
  const items = [];

  const pushUnique = (text) => {
    const cleaned = toNaturalLanguage(text || '');
    if (!cleaned) return;
    if (items.some(existing => normalizeVietnameseText(existing) === normalizeVietnameseText(cleaned))) {
      return;
    }
    items.push(cleaned);
  };

  pushUnique(confidenceNatural);
  splitIntoBullets(feedback).forEach(pushUnique);

  if (items.length < 3) {
    if (score >= 28) {
      pushUnique(`Ngành ${majorName} đang có mức tương thích cao với hồ sơ hiện tại của bạn.`);
    } else if (score >= 20) {
      pushUnique(`Ngành ${majorName} phù hợp ở mức khá và có thể ưu tiên tìm hiểu sâu hơn.`);
    } else if (score >= 12) {
      pushUnique(`Ngành ${majorName} phù hợp ở mức tham khảo, bạn nên so sánh thêm với các ngành gần.`);
    } else {
      pushUnique(`Ngành ${majorName} hiện phù hợp thấp, nên xem như phương án dự phòng.`);
    }
  }

  if (items.length < 4) {
    pushUnique('Kết quả được tổng hợp từ thông tin bạn nhập và mức độ tương đồng với mô tả ngành.');
  }

  return items.slice(0, 4);
}

function renderMiniList(items, className = 'mini-list') {
  if (!items.length) return '';
  return `
    <ul class="${className}">
      ${items.map(item => `<li>${item}</li>`).join('')}
    </ul>
  `;
}

function scoreToVisualProgress(score) {
  const s = Math.max(0, Math.min(Number(score) || 0, 100));

  if (s < 12) {
    // <12 điểm -> vùng "Không phù hợp" theo progress (<30%)
    return 10 + (s / 12) * 19;
  }
  if (s < 20) {
    // 12-20 điểm -> vùng "Tham khảo" theo progress (30-49%)
    return 30 + ((s - 12) / 8) * 19;
  }
  if (s < 28) {
    // 20-28 điểm -> vùng "Khá phù hợp" theo progress (50-69%)
    return 50 + ((s - 20) / 8) * 19;
  }

  // >=28 điểm -> vùng "Rất phù hợp" theo progress (70-95%)
  return Math.min(95, 70 + ((s - 28) / 22) * 25);
}

function renderResult(data) {
   top3.innerHTML = '';
   reasons.innerHTML = '';
   if (debugTop5) {
     debugTop5.innerHTML = '';
   }

   const topItems = Array.isArray(data.top_3) ? data.top_3 : [];
   const trendClassFromScore = (score) => {
     if (score >= 28) return 'trend-high';
     if (score >= 20) return 'trend-medium';
     if (score >= 12) return 'trend-low';
     return 'trend-verylow';
   };
   const formatPercent = (value) => `${Number(value || 0).toFixed(2)}%`;

   topItems.forEach((item, index) => {
     const majorName = item.major_display || item.major || item.nganh || 'N/A';
     const majorKey = item.major_key || item.nganh || '';
     const score = Number(item.score_display ?? item.score ?? 0);
     const visualProgress = scoreToVisualProgress(score);
     const groupName = item.group || '';
     const feedback = makeReadableMultiline(item.feedback || '');
     const suggestion = makeReadableMultiline(item.suggestion || '');
     const confidenceText = makeReadableMultiline(item.confidence_text || '');
     const trendClass = trendClassFromScore(score);

     const el = document.createElement('article');
     el.className = `result-item ${trendClass}`;

     const confidenceNatural = explainConfidence(score, majorName);
     const confidenceItems = splitIntoBullets(confidenceText).slice(0, 2);
     const nextStepItems = explainNextSteps(item).slice(0, 3);

     const usedSectionTexts = new Set();
     const pickUniqueForSection = (candidates, maxCount) => {
       const picked = [];
       for (const raw of candidates || []) {
         const cleaned = toNaturalLanguage(raw || '');
         const key = normalizeVietnameseText(cleaned);
         if (!cleaned || !key || usedSectionTexts.has(key)) continue;
         usedSectionTexts.add(key);
         picked.push(cleaned);
         if (picked.length >= maxCount) break;
       }
       return picked;
     };

     const confidenceBody = pickUniqueForSection(
       [confidenceNatural, ...confidenceItems],
       2
     );

     const explanationItems = buildExplanationItems({
       majorName,
       score,
       confidenceNatural,
       feedback,
     });

     let explanationBody = pickUniqueForSection(explanationItems, 4);
     if (explanationBody.length < 2) {
       const fallbackExplain = [
         `Ngành ${majorName} được đề xuất dựa trên mức độ phù hợp của hồ sơ bạn đã nhập.`,
         'Bạn có thể dùng phần Hướng phát triển để xem bước hành động tiếp theo.',
       ];
       explanationBody = [...explanationBody, ...pickUniqueForSection(fallbackExplain, 2 - explanationBody.length)];
     }

     let growthBody = pickUniqueForSection(nextStepItems, 3);
     if (!growthBody.length) {
       growthBody = pickUniqueForSection(
         ['Bạn nên tìm hiểu thêm chương trình đào tạo và cơ hội việc làm của ngành này.'],
         1
       );
     }

     const summarySections = [
       {
         key: 'confidence',
         title: 'Độ tin cậy',
         body: confidenceBody,
       },
       {
         key: 'explain',
         title: 'Giải thích (2 - 4 câu)',
         body: explanationBody,
       },
       {
         key: 'growth',
         title: 'Hướng phát triển',
         body: growthBody,
       },
     ];

     const summaryBlock = `
       <div class="summary-sections">
         ${summarySections.map((section, sectionIndex) => `
           <section class="summary-section">
             <div class="summary-section__summary">
               <span class="summary-section__title">${section.title}</span>
             </div>
             <div class="summary-section__body">
               ${section.body.length ? renderMiniList(section.body, 'mini-list mini-list--compact') : '<div class="summary-section__empty">Không có nội dung thêm.</div>'}
             </div>
           </section>
         `).join('')}
       </div>
     `;

      const scoreLabel = score >= 28
       ? 'Rất phù hợp'
       : score >= 20
         ? 'Khá phù hợp'
         : score >= 12
           ? 'Tham khảo'
           : 'Không phù hợp';

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
         <div class="major-score-pill">${formatPercent(visualProgress)}</div>
       </div>
        <div class="score-legend">
          <span class="score-legend__label">${scoreLabel}</span>
          <span class="score-legend__meta"></span>
        </div>
       <div class="progress"><span style="width:${visualProgress.toFixed(2)}%" title="Mức phù hợp trực quan: ${visualProgress.toFixed(2)}% · Điểm hệ thống gốc: ${score.toFixed(2)}"></span></div>
       <div class="score-label">Mức phù hợp trực quan: ${visualProgress.toFixed(2)}%</div>
       <div class="score-meta" style="opacity:.8;font-size:.92em;margin-top:4px;">Điểm hệ thống gốc: ${score.toFixed(2)}</div>
       ${summaryBlock}
       <div class="feedback-section" data-major="${majorKey}">
         <p class="feedback-question">⭐ Bạn thấy kết quả này thế nào?</p>
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
           placeholder="Bình luận (tùy chọn)... Ví dụ: Rất phù hợp! / Cần xem thêm"
         ></textarea>
         <div class="feedback-actions">
           <button class="btn btn--primary feedback-submit" data-major="${majorKey}">
             ✓ Gửi đánh giá
           </button>
           <button class="btn btn--ghost feedback-skip" data-major="${majorKey}">
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
    const explanationItems = Array.isArray(data.giai_thich) ? data.giai_thich : [];
    explanationItems.forEach((text) => {
      const li = document.createElement('li');
      li.textContent = text;
      reasons.appendChild(li);
    });

    if (!reasons.children.length) {
      const li = document.createElement('li');
      li.textContent = 'Các ngành được đề xuất dựa trên mức độ phù hợp của hồ sơ bạn đã nhập.';
      reasons.appendChild(li);
    }
  }

  const debugItems = Array.isArray(data.top_5_diem_tho) ? data.top_5_diem_tho : [];
  if (debugBox && debugTop5 && debugItems.length) {
    debugBox.classList.remove('hidden');
    debugItems.forEach((item, index) => {
      const debugMajorName = item.major_display || item.major || item.nganh || 'N/A';
      const debugMajorKey = item.major_key || item.nganh || '';
      const row = document.createElement('div');
      row.className = 'debug-row';
      row.innerHTML = `
        <div class="debug-rank">#${index + 1}</div>
        <div class="debug-major">${debugMajorName}${debugMajorKey ? ` <small>(${debugMajorKey})</small>` : ''}</div>
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

// Fallback local samples (chỉ dùng khi API lỗi)
const LOCAL_FALLBACK_SAMPLES = [
  {
    // 0. Mẫu giáo viên Hóa (ưu tiên cho nút Mẫu gợi ý)
    so_thich_chinh: 'Giáo dục',
    mon_hoc_yeu_thich: 'Hóa',
    ky_nang_noi_bat: 'Thuyết trình',
    tinh_cach: 'Hướng ngoại',
    moi_truong_lam_viec_mong_muon: 'Trường học',
    muc_tieu_nghe_nghiep: 'Theo đam mê',
    mo_ta_ban_than: 'Em yêu thích giảng dạy, đặc biệt là môn Hóa, và muốn truyền cảm hứng học tập cho học sinh.',
    dinh_huong_tuong_lai: 'Em muốn trở thành giáo viên môn Hóa trong môi trường giáo dục.',
  },
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
    so_thich_chinh: 'Du lịch',
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
    so_thich_chinh: 'Nghệ thuật',
    mon_hoc_yeu_thich: 'Văn',
    ky_nang_noi_bat: 'Sáng tạo',
    tinh_cach: 'Tỉ mỉ',
    moi_truong_lam_viec_mong_muon: 'Linh hoạt',
    muc_tieu_nghe_nghiep: 'Theo đam mê',
    mo_ta_ban_than: 'Em thích thiết kế, màu sắc, hình ảnh và tạo nội dung sáng tạo.',
    dinh_huong_tuong_lai: 'Em muốn làm UI/UX Designer hoặc Graphic Designer.',
  },
];

function applySampleToForm(sample) {
  if (!sample) return;

  const setSelectValue = (fieldName, value) => {
    const selectEl = form[fieldName];
    if (!selectEl) return;
    const normalizedValue = normalize(value);
    const hasOption = Array.from(selectEl.options || []).some(opt => normalize(opt.value) === normalizedValue);
    if (!hasOption) {
      selectEl.value = '';
      return;
    }
    const matchedOption = Array.from(selectEl.options || []).find(opt => normalize(opt.value) === normalizedValue);
    selectEl.value = matchedOption ? matchedOption.value : '';
  };

  setSelectValue('so_thich_chinh', sample.so_thich_chinh);
  setSelectValue('mon_hoc_yeu_thich', sample.mon_hoc_yeu_thich);
  setSelectValue('ky_nang_noi_bat', sample.ky_nang_noi_bat);
  setSelectValue('tinh_cach', sample.tinh_cach);
  setSelectValue('moi_truong_lam_viec_mong_muon', sample.moi_truong_lam_viec_mong_muon);
  setSelectValue('muc_tieu_nghe_nghiep', sample.muc_tieu_nghe_nghiep);
  form.mo_ta_ban_than.value = sample.mo_ta_ban_than;
  form.dinh_huong_tuong_lai.value = sample.dinh_huong_tuong_lai;
}

async function fillRandomDemo() {
  try {
    const response = await fetch('/sample-profiles');
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Không thể lấy dữ liệu mẫu từ server.');
    }

    const apiSamples = Array.isArray(data.samples) ? data.samples : [];
    if (!apiSamples.length) {
      throw new Error('API không trả về hồ sơ mẫu hợp lệ.');
    }

    const randomIndex = Math.floor(Math.random() * apiSamples.length);
    applySampleToForm(apiSamples[randomIndex]);
  } catch (error) {
    console.warn('Lấy sample từ API thất bại, dùng fallback local:', error);
    const randomIndex = Math.floor(Math.random() * LOCAL_FALLBACK_SAMPLES.length);
    applySampleToForm(LOCAL_FALLBACK_SAMPLES[randomIndex]);
  }
}

document.getElementById('randomDemoBtn').addEventListener('click', () => {
  fillRandomDemo();
});

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
        <p>Xin chào! 👋 Để mình tư vấn ngành học sát với bạn hơn, hãy gửi 2 ý này trước nhé:<br>• Mô tả bản thân (Sở thích, tính cách, kỹ năng)<br>• Định hướng tương lai</p>
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

// Save user profile to localStorage for chatbot to access
function saveUserProfileToStorage(payload) {
  try {
    localStorage.setItem('userProfile', JSON.stringify(payload));
    console.log('✅ User profile saved to localStorage:', payload);
  } catch (error) {
    console.warn('Could not save to localStorage:', error);
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
  
  // Save profile to localStorage for chatbot to use later
  saveUserProfileToStorage(payload);
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

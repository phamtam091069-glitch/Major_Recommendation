// Chatbot Page Logic
const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');

const STORAGE_KEY = 'major_recommendation_chat_history_v1';
const INITIAL_GREETING = {
  role: 'assistant',
  content: 'Xin chào! 👋 Mình là chatbot tư vấn ngành học. Bạn muốn biết gì về các ngành học?'
};

let chatHistory = [INITIAL_GREETING];

function isValidMessage(item) {
  return item && typeof item === 'object' && typeof item.content === 'string' && item.content.trim();
}

function normalizeHistory(history) {
  if (!Array.isArray(history)) return [INITIAL_GREETING];

  const cleaned = history
    .filter(isValidMessage)
    .map(item => ({
      role: item.role === 'assistant' ? 'assistant' : 'user',
      content: String(item.content).trim()
    }));

  return cleaned.length ? cleaned : [INITIAL_GREETING];
}

function loadSavedHistory() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;

    const parsed = JSON.parse(raw);
    const normalized = normalizeHistory(parsed);
    return normalized.slice(-50);
  } catch (error) {
    console.warn('Không load được lịch sử chat từ localStorage:', error);
    return null;
  }
}

function persistHistory() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(chatHistory.slice(-50)));
  } catch (error) {
    console.warn('Không lưu được lịch sử chat:', error);
  }
}

function renderInitialHistory() {
  const savedHistory = loadSavedHistory();

  if (savedHistory && savedHistory.length) {
    chatHistory = savedHistory;
    chatContainer.innerHTML = '';
    chatHistory.forEach(item => {
      addMessageToChat(item.content, item.role === 'user' ? 'user' : 'assistant');
    });
  } else {
    chatHistory = [INITIAL_GREETING];
    persistHistory();
  }
}

function pushMessage(role, content) {
  chatHistory.push({ role, content });
  chatHistory = chatHistory.slice(-50);
  persistHistory();
}

// Restore chat history when the page loads
renderInitialHistory();

// Send message on button click
sendBtn.addEventListener('click', sendMessage);

// Send message on Enter key
messageInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Auto-focus input
messageInput.focus();

async function sendMessage() {
  const message = messageInput.value.trim();

  if (!message) return;

  // Add user message to chat
  addMessageToChat(message, 'user');
  pushMessage('user', message);

  // Clear input
  messageInput.value = '';
  messageInput.focus();

  // Disable send button
  sendBtn.disabled = true;

  // Show typing indicator
  const loadingEl = addLoadingIndicator();

  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message: message, history: chatHistory })
    });

    const data = await response.json();

    // Remove loading indicator
    loadingEl.remove();

    if (response.ok && data.reply) {
      // Log response for debugging
      console.log('📨 Bot Response:', {
        length: data.reply.length,
        preview: data.reply.substring(0, 100) + '...',
        source: data.source,
        confidence: data.confidence,
        fullText: data.reply
      });
      addMessageToChat(data.reply, 'assistant');
      pushMessage('assistant', data.reply);
    } else {
      console.error('❌ Error response:', response.status, data);
      const fallbackReply = 'Xin lỗi, tôi không hiểu được câu hỏi của bạn. Hãy thử hỏi lại!';
      addMessageToChat(fallbackReply, 'assistant');
      pushMessage('assistant', fallbackReply);
    }
  } catch (error) {
    console.error('Chat error:', error);
    loadingEl.remove();
    const errorReply = 'Có lỗi xảy ra. Vui lòng thử lại!';
    addMessageToChat(errorReply, 'assistant');
    pushMessage('assistant', errorReply);
  } finally {
    // Re-enable send button
    sendBtn.disabled = false;
    messageInput.focus();
  }
}

function formatMarkdown(text) {
  // Escape HTML special characters first
  text = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // Convert markdown bold (**text**) to <strong>
  text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  // Convert markdown italic (*text*) to <em>
  text = text.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>');

  // Convert markdown line breaks (--- or ***)
  text = text.replace(/^([-_]){3,}$/gm, '<hr>');

  return text;
}

function capitalizeSentence(text) {
  const value = String(text || '').trim();
  if (!value) return value;
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function detectMajorTheme(text) {
  const normalized = String(text || '').toLowerCase();
  if (normalized.includes('tàu biển') || normalized.includes('tàu thủy') || normalized.includes('hàng hải') || normalized.includes('maritime') || normalized.includes('marine') || normalized.includes('ship')) {
    return 'marine';
  }
  if (normalized.includes('công nghệ thông tin') || normalized.includes('lập trình') || normalized.includes('data') || normalized.includes('ai') || normalized.includes('machine learning')) {
    return 'tech';
  }
  if (normalized.includes('marketing') || normalized.includes('quản trị kinh doanh') || normalized.includes('thương mại điện tử')) {
    return 'business';
  }
  if (normalized.includes('y đa khoa') || normalized.includes('điều dưỡng') || normalized.includes('dược') || normalized.includes('y tế')) {
    return 'health';
  }
  return 'default';
}

function addMessageToChat(text, sender) {
  const normalizedSender = sender === 'assistant' ? 'bot' : sender;
  const messageEl = document.createElement('div');
  messageEl.className = `message ${normalizedSender}-message`;

  if (sender === 'assistant') {
    messageEl.classList.add(`message-theme--${detectMajorTheme(text)}`);
  }

  const avatar = document.createElement('div');
  avatar.className = 'message-avatar';
  avatar.textContent = sender === 'user' ? '👤' : '🤖';

  const contentEl = document.createElement('div');
  contentEl.className = 'message-content';

  const lines = String(text || '').split('\n');
  let bulletListEl = null;

  function flushBulletList() {
    if (bulletListEl && bulletListEl.children.length) {
      contentEl.appendChild(bulletListEl);
    }
    bulletListEl = null;
  }

  lines.forEach((line, index) => {
    const trimmedLine = line.trim();

    if (!trimmedLine) {
      flushBulletList();
      if (index > 0 && index < lines.length - 1) {
        const spacer = document.createElement('div');
        spacer.className = 'message-spacer';
        contentEl.appendChild(spacer);
      }
      return;
    }

    const headerMatch = trimmedLine.match(/^(#+)\s+(.+)$/);
    const bulletMatch = trimmedLine.match(/^(?:[-*•]|\d+[).])\s+(.+)$/);

    if (headerMatch) {
      flushBulletList();
      const level = Math.min(headerMatch[1].length, 3);
      const headerText = formatMarkdown(headerMatch[2]);
      const header = document.createElement(`h${level + 2}`);
      header.innerHTML = headerText;
      header.className = 'markdown-header';
      contentEl.appendChild(header);
      return;
    }

    if (bulletMatch) {
      if (!bulletListEl) {
        bulletListEl = document.createElement('ul');
        bulletListEl.className = 'chat-bullet-list';
      }
      const li = document.createElement('li');
      li.innerHTML = formatMarkdown(capitalizeSentence(bulletMatch[1]));
      bulletListEl.appendChild(li);
      return;
    }

    flushBulletList();
    const p = document.createElement('p');
    p.innerHTML = formatMarkdown(capitalizeSentence(trimmedLine));
    contentEl.appendChild(p);
  });

  flushBulletList();

  if (contentEl.children.length === 0) {
    const p = document.createElement('p');
    p.textContent = text || '(Trống)';
    contentEl.appendChild(p);
  }

  messageEl.appendChild(avatar);
  messageEl.appendChild(contentEl);
  chatContainer.appendChild(messageEl);
  scrollToBottom();
}

function addLoadingIndicator() {
  const messageEl = document.createElement('div');
  messageEl.className = 'message loading-message';

  const avatar = document.createElement('div');
  avatar.className = 'message-avatar';
  avatar.textContent = '🤖';

  const contentEl = document.createElement('div');
  contentEl.className = 'message-content';
  const typingDiv = document.createElement('div');
  typingDiv.className = 'typing-indicator';
  typingDiv.innerHTML = '<span></span><span></span><span></span>';
  contentEl.appendChild(typingDiv);

  messageEl.appendChild(avatar);
  messageEl.appendChild(contentEl);
  chatContainer.appendChild(messageEl);
  scrollToBottom();

  return messageEl;
}

function scrollToBottom() {
  const mainEl = document.querySelector('.chatbot-main');
  if (mainEl) {
    setTimeout(() => {
      mainEl.scrollTop = mainEl.scrollHeight;
    }, 0);
  }
}

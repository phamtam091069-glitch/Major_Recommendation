// Chatbot Page Logic
const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');

const INITIAL_GREETING = {
  role: 'assistant',
  content: 'Xin chào! 👋 Để mình tư vấn ngành học sát với bạn hơn, hãy gửi 2 ý này trước nhé:\n• Mô tả bản thân (Sở thích, tính cách, kỹ năng)\n• Định hướng tương lai'
};

let chatHistory = [INITIAL_GREETING];
let chatContext = {
  active_major: '',
  active_topic: ''
};

// ===== NEW: sessionStorage persistence functions =====
// FIX: Using sessionStorage instead of localStorage
// sessionStorage auto-clears when browser closes or page reloads
function saveChatHistoryToSessionStorage() {
  try {
    sessionStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    sessionStorage.setItem('chatContext', JSON.stringify(chatContext));
    console.log('💾 Chat history saved to sessionStorage');
  } catch (error) {
    console.warn('Could not save to sessionStorage:', error);
  }
}

function loadChatHistoryFromSessionStorage() {
  try {
    const savedHistory = sessionStorage.getItem('chatHistory');
    const savedContext = sessionStorage.getItem('chatContext');

    if (savedHistory && savedHistory !== '[]') {
      chatHistory = JSON.parse(savedHistory);
      console.log('✅ Restored chat history from sessionStorage:', chatHistory.length, 'messages');
    } else {
      chatHistory = [INITIAL_GREETING];
    }

    if (savedContext) {
      chatContext = JSON.parse(savedContext);
      console.log('✅ Restored chat context from sessionStorage:', chatContext);
    } else {
      chatContext = { active_major: '', active_topic: '' };
    }

    return chatHistory;
  } catch (error) {
    console.warn('Could not load from sessionStorage:', error);
    chatHistory = [INITIAL_GREETING];
    chatContext = { active_major: '', active_topic: '' };
    return chatHistory;
  }
}

function clearChatHistoryFromSessionStorage() {
  try {
    sessionStorage.removeItem('chatHistory');
    sessionStorage.removeItem('chatContext');
    console.log('🗑️ Chat history cleared from sessionStorage');
  } catch (error) {
    console.warn('Could not clear sessionStorage:', error);
  }
}

function pushMessage(role, content) {
  chatHistory.push({ role, content });
  chatHistory = chatHistory.slice(-50);
  
  // NEW: Auto-save to sessionStorage after each message
  // FIX: Changed from localStorage to sessionStorage for auto-clear on reload
  saveChatHistoryToSessionStorage();
}

// NEW: Clear chat history on page load (whenever user reloads)
// FIX: This ensures fresh start, not restoring from previous session
clearChatHistoryFromSessionStorage();
console.log('🔄 Chat history cleared on page load - starting fresh');

// Initialize with greeting message only
chatHistory = [INITIAL_GREETING];
chatContext = { active_major: '', active_topic: '' };

// Render initial state
chatContainer.innerHTML = '';
addMessageToChat(INITIAL_GREETING.content, INITIAL_GREETING.role);

// Scroll to bottom to show latest messages
setTimeout(scrollToBottom, 100);

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
    // Get user profile from localStorage (saved from form submission)
    let userProfile = null;
    try {
      const profileData = localStorage.getItem('userProfile');
      if (profileData) {
        userProfile = JSON.parse(profileData);
        console.log('📋 Using saved user profile from localStorage:', userProfile);
      }
    } catch (error) {
      console.warn('Could not retrieve user profile from localStorage:', error);
    }

    const response = await fetch('/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: message,
        history: chatHistory,
        active_major: chatContext.active_major,
        active_topic: chatContext.active_topic,
        user_profile: userProfile  // Send the saved profile to backend
      })
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
        resolved_major: data.resolved_major,
        resolved_topic: data.resolved_topic,
        fullText: data.reply
      });

      chatContext = {
        active_major: typeof data.resolved_major === 'string' ? data.resolved_major.trim() : chatContext.active_major,
        active_topic: typeof data.resolved_topic === 'string' ? data.resolved_topic.trim() : chatContext.active_topic
      };
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

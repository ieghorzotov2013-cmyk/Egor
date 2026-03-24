'use strict';

// ── Storage helpers ──────────────────────────────────────────────────────────
const STORAGE_KEY = 'egor_chats_v1';

function loadChats() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
  } catch {
    return [];
  }
}

function saveChats(chats) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(chats));
}

// ── State ────────────────────────────────────────────────────────────────────
let chats = loadChats();         // [{ id, name, messages: [{id,text,ts,out}] }]
let activeChatId = null;

// ── DOM refs ─────────────────────────────────────────────────────────────────
const chatListEl     = document.getElementById('chatList');
const chatHeaderName = document.getElementById('chatHeaderName');
const messagesArea   = document.getElementById('messagesArea');
const emptyState     = document.getElementById('emptyState');
const inputForm      = document.getElementById('inputForm');
const messageInput   = document.getElementById('messageInput');
const btnSend        = document.getElementById('btnSend');
const btnNewChat     = document.getElementById('btnNewChat');
const btnRenameChat  = document.getElementById('btnRenameChat');
const btnDeleteChat  = document.getElementById('btnDeleteChat');
const searchInput    = document.getElementById('searchInput');

// ── Utilities ────────────────────────────────────────────────────────────────
function uid() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2);
}

function formatTime(ts) {
  const d = new Date(ts);
  return d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
}

function formatDate(ts) {
  const d = new Date(ts);
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);

  if (d.toDateString() === today.toDateString()) return 'Сегодня';
  if (d.toDateString() === yesterday.toDateString()) return 'Вчера';
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' });
}

function avatarLetter(name) {
  return (name || '?')[0].toUpperCase();
}

// ── Render sidebar ────────────────────────────────────────────────────────────
function renderChatList(filter = '') {
  const q = filter.toLowerCase().trim();
  const filtered = q
    ? chats.filter(c => c.name.toLowerCase().includes(q))
    : chats;

  chatListEl.innerHTML = '';
  filtered.forEach(chat => {
    const last = chat.messages[chat.messages.length - 1];
    const li = document.createElement('li');
    li.className = 'chat-item' + (chat.id === activeChatId ? ' active' : '');
    li.dataset.id = chat.id;
    li.innerHTML = `
      <div class="chat-avatar">${avatarLetter(chat.name)}</div>
      <div class="chat-info">
        <div class="chat-name">${escHtml(chat.name)}</div>
        <div class="chat-preview">${last ? escHtml(last.text.replace(/\n/g, ' ').slice(0, 60)) : 'Нет сообщений'}</div>
      </div>
      <div class="chat-meta">
        <span class="chat-time">${last ? formatTime(last.ts) : ''}</span>
      </div>
    `;
    li.addEventListener('click', () => openChat(chat.id));
    chatListEl.appendChild(li);
  });
}

// ── Render messages ───────────────────────────────────────────────────────────
function renderMessages(chat) {
  messagesArea.innerHTML = '';

  if (!chat || chat.messages.length === 0) {
    messagesArea.appendChild(emptyState);
    emptyState.querySelector('p').textContent = chat
      ? 'Сообщений пока нет. Напишите что-нибудь!'
      : 'Создайте новый чат или выберите существующий';
    return;
  }

  let lastDateStr = null;

  chat.messages.forEach(msg => {
    const dateStr = formatDate(msg.ts);
    if (dateStr !== lastDateStr) {
      const div = document.createElement('div');
      div.className = 'date-divider';
      div.textContent = dateStr;
      messagesArea.appendChild(div);
      lastDateStr = dateStr;
    }

    const group = document.createElement('div');
    group.className = 'msg-group ' + (msg.out ? 'out' : 'in');
    group.innerHTML = `
      <div class="msg-bubble">${escHtml(msg.text)}</div>
      <div class="msg-time">${formatTime(msg.ts)}</div>
    `;
    messagesArea.appendChild(group);
  });

  messagesArea.scrollTop = messagesArea.scrollHeight;
}

// ── Open chat ─────────────────────────────────────────────────────────────────
function openChat(id) {
  activeChatId = id;
  const chat = chats.find(c => c.id === id);
  if (!chat) return;

  chatHeaderName.textContent = chat.name;
  btnRenameChat.style.display = '';
  btnDeleteChat.style.display = '';
  messageInput.disabled = false;
  btnSend.disabled = false;
  messageInput.focus();

  renderMessages(chat);
  renderChatList(searchInput.value);
}

// ── New chat ──────────────────────────────────────────────────────────────────
function createChat(name) {
  const chat = { id: uid(), name: name.trim(), messages: [] };
  chats.unshift(chat);
  saveChats(chats);
  openChat(chat.id);
  renderChatList(searchInput.value);
}

btnNewChat.addEventListener('click', () => {
  const name = prompt('Имя нового чата:', 'Чат ' + (chats.length + 1));
  if (name && name.trim()) createChat(name);
});

// ── Rename / Delete ───────────────────────────────────────────────────────────
btnRenameChat.addEventListener('click', () => {
  const chat = chats.find(c => c.id === activeChatId);
  if (!chat) return;
  const name = prompt('Новое имя чата:', chat.name);
  if (name && name.trim()) {
    chat.name = name.trim();
    saveChats(chats);
    chatHeaderName.textContent = chat.name;
    renderChatList(searchInput.value);
  }
});

btnDeleteChat.addEventListener('click', () => {
  const chat = chats.find(c => c.id === activeChatId);
  if (!chat) return;
  if (!confirm(`Удалить чат «${chat.name}»?`)) return;
  chats = chats.filter(c => c.id !== activeChatId);
  saveChats(chats);
  activeChatId = null;
  chatHeaderName.textContent = 'Выберите чат';
  btnRenameChat.style.display = 'none';
  btnDeleteChat.style.display = 'none';
  messageInput.disabled = true;
  btnSend.disabled = true;
  messagesArea.innerHTML = '';
  messagesArea.appendChild(emptyState);
  emptyState.querySelector('p').textContent = 'Создайте новый чат или выберите существующий';
  renderChatList(searchInput.value);
});

// ── Send message ──────────────────────────────────────────────────────────────
inputForm.addEventListener('submit', e => {
  e.preventDefault();
  sendMessage();
});

messageInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Auto-resize textarea
messageInput.addEventListener('input', () => {
  messageInput.style.height = 'auto';
  messageInput.style.height = Math.min(messageInput.scrollHeight, 140) + 'px';
});

function sendMessage() {
  const text = messageInput.value.trim();
  if (!text || !activeChatId) return;

  const chat = chats.find(c => c.id === activeChatId);
  if (!chat) return;

  const msg = { id: uid(), text, ts: Date.now(), out: true };
  chat.messages.push(msg);
  saveChats(chats);

  messageInput.value = '';
  messageInput.style.height = 'auto';

  renderMessages(chat);
  renderChatList(searchInput.value);
}

// ── Search ────────────────────────────────────────────────────────────────────
searchInput.addEventListener('input', () => {
  renderChatList(searchInput.value);
});

// ── Escape HTML ───────────────────────────────────────────────────────────────
function escHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Init ──────────────────────────────────────────────────────────────────────
messagesArea.appendChild(emptyState);
renderChatList();

// Open first chat automatically if exists
if (chats.length > 0) {
  openChat(chats[0].id);
}

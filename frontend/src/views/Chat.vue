<template>
  <div class="chat-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="brand">
          <span class="brand-icon">🌊</span>
          <span class="brand-name">心灵回声</span>
        </div>
        <div class="user-info" v-if="authStore.user">
          <div class="avatar">
            {{ getInitial(authStore.user.nickname || authStore.user.username) }}
          </div>
          <div>
            <div class="user-name">
              {{ authStore.user.nickname || authStore.user.username }}
            </div>
            <div class="user-sub">大学生用户</div>
          </div>
        </div>
      </div>

      <div class="sidebar-actions">
        <button class="btn-new" @click="startNewConversation">
          ✏️ 新建对话
        </button>
      </div>

      <nav class="nav-links">
        <router-link to="/chat" class="nav-link active-link">
          💬 心理咨询
        </router-link>
        <router-link to="/emotions" class="nav-link"> 📊 情绪记录 </router-link>
      </nav>

      <div class="conversation-list">
        <div class="list-title">最近对话</div>
        <div
          v-for="conv in conversations"
          :key="conv.id"
          class="conv-item"
          :class="{ active: currentConversationId === conv.id }"
          @click="loadConversation(conv.id)"
        >
          <span class="conv-icon">💬</span>
          <span class="conv-title">{{ conv.title || "新对话" }}</span>
        </div>
        <div v-if="conversations.length === 0" class="no-conv">
          还没有对话记录
        </div>
      </div>

      <div class="sidebar-footer">
        <button class="btn-logout" @click="handleLogout">退出登录</button>
      </div>
    </aside>

    <!-- Main chat area -->
    <main class="chat-main">
      <!-- Chat header -->
      <header class="chat-header">
        <div class="header-left">
          <h2>心理健康助手</h2>
          <span class="status-dot"></span>
          <span class="status-text">在线，随时倾听</span>
        </div>
        <div class="emotion-badge" v-if="lastEmotion">
          <span>{{ emotionEmoji[lastEmotion] }}</span>
          <span>{{ emotionLabels[lastEmotion] }}</span>
        </div>
      </header>

      <!-- Crisis alert -->
      <transition name="fade">
        <div v-if="showCrisisAlert" class="crisis-alert">
          <div class="crisis-icon">🆘</div>
          <div class="crisis-content">
            <div class="crisis-title">我们非常关心你的安全</div>
            <div class="crisis-body">
              如果你正在经历危机，请立即拨打：
              <strong>北京心理危机热线：010-82951332</strong> |
              <strong>全国援助热线：400-161-9995</strong>
            </div>
          </div>
          <button class="crisis-close" @click="showCrisisAlert = false">
            ✕
          </button>
        </div>
      </transition>

      <!-- Messages -->
      <div class="messages-container" ref="messagesContainer">
        <!-- Welcome message -->
        <div v-if="messages.length === 0" class="welcome">
          <div class="welcome-icon">🌟</div>
          <h3>你好，我是你的心灵伙伴</h3>
          <p>
            无论你有什么烦恼、压力、或者只是想聊聊，我都在这里倾听。<br />你的感受对我来说很重要，请放心分享。💙
          </p>
          <div class="quick-starts">
            <button
              v-for="q in quickStarts"
              :key="q"
              class="quick-btn"
              @click="sendQuickMessage(q)"
            >
              {{ q }}
            </button>
          </div>
        </div>

        <!-- Message list -->
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="message-row"
          :class="msg.role === 'user' ? 'user-row' : 'assistant-row'"
        >
          <div v-if="msg.role === 'assistant'" class="avatar-ai">🌊</div>
          <div
            class="message-bubble"
            :class="msg.role === 'user' ? 'user-bubble' : 'ai-bubble'"
          >
            <div class="message-text" v-html="formatMessage(msg.content)"></div>
            <div class="message-meta">
              <span
                v-if="msg.role === 'user' && msg.emotion"
                class="emotion-tag"
              >
                {{ emotionEmoji[msg.emotion] }} {{ emotionLabels[msg.emotion] }}
              </span>
              <span
                v-if="msg.role === 'assistant' && msg.processor_time"
                class="processor-time"
              >
                ⏱️ {{ msg.processor_time.toFixed(2) }}s
              </span>
              <span class="message-time">{{ formatTime(msg.created_at) }}</span>
            </div>
          </div>
        </div>

        <!-- Typing indicator -->
        <div v-if="isTyping" class="message-row assistant-row">
          <div class="avatar-ai">🌊</div>
          <div class="message-bubble ai-bubble typing-bubble">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
        </div>
      </div>

      <!-- Input area -->
      <div class="input-area">
        <div class="quick-moods">
          <button
            class="mood-btn"
            @click="quickCheckIn('stress')"
            :disabled="isTyping"
          >
            😮‍💨 压力
          </button>
          <button
            class="mood-btn"
            @click="quickCheckIn('sad')"
            :disabled="isTyping"
          >
            😔 难过
          </button>
          <button
            class="mood-btn"
            @click="quickCheckIn('angry')"
            :disabled="isTyping"
          >
            😣 生气
          </button>
        </div>
        <div v-if="quickSupport" class="quick-support">
          <div class="support-title">即时支持</div>
          <div class="support-body">{{ quickSupport }}</div>
        </div>
        <div class="input-wrapper">
          <textarea
            v-model="inputText"
            placeholder="写下你的心情或困扰…（Shift+Enter 换行，Enter 发送）"
            @keydown.enter.exact.prevent="sendMessage"
            @keydown.shift.enter="() => {}"
            rows="1"
            ref="textarea"
            @input="autoResize"
          ></textarea>
          <button
            class="send-btn"
            @click="sendMessage"
            :disabled="!inputText.trim() || isTyping"
          >
            发送
          </button>
        </div>
        <div class="input-hint">Enter 发送 · Shift+Enter 换行</div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import api from "../api";

const router = useRouter();
const authStore = useAuthStore();

const messages = ref([]);
const conversations = ref([]);
const currentConversationId = ref(null);
const inputText = ref("");
const isTyping = ref(false);
const showCrisisAlert = ref(false);
const lastEmotion = ref(null);
const messagesContainer = ref(null);
const textarea = ref(null);
const quickSupport = ref("");

const emotionLabels = {
  happy: "开心",
  sad: "悲伤",
  anxious: "焦虑",
  angry: "愤怒",
  neutral: "平静",
  fear: "恐惧",
  lonely: "孤独",
};

const emotionEmoji = {
  happy: "😊",
  sad: "😢",
  anxious: "😰",
  angry: "😤",
  neutral: "😌",
  fear: "😨",
  lonely: "🥺",
};

const quickStarts = [
  "我最近压力很大",
  "考试让我很焦虑",
  "我感到很孤独",
  "我想聊聊心情",
];

function getInitial(name) {
  return name ? name[0].toUpperCase() : "?";
}

function formatTime(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" });
}

function formatMessage(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br>");
}

async function loadConversations() {
  try {
    const res = await api.get("/api/chat/conversations");
    conversations.value = res.data;
  } catch (e) {
    console.error("Failed to load conversations", e);
  }
}

async function loadConversation(id) {
  try {
    const res = await api.get(`/api/chat/conversations/${id}`);
    currentConversationId.value = id;
    messages.value = res.data.messages;
    if (messages.value.length > 0) {
      const lastUserMsg = [...messages.value]
        .reverse()
        .find((m) => m.role === "user");
      if (lastUserMsg?.emotion) lastEmotion.value = lastUserMsg.emotion;
    }
    await scrollToBottom();
  } catch (e) {
    console.error("Failed to load conversation", e);
  }
}

function startNewConversation() {
  currentConversationId.value = null;
  messages.value = [];
  lastEmotion.value = null;
}

async function sendMessage() {
  const text = inputText.value.trim();
  if (!text || isTyping.value) return;

  inputText.value = "";
  resetTextarea();
  isTyping.value = true;

  const tempUserMsg = {
    id: Date.now(),
    role: "user",
    content: text,
    created_at: new Date().toISOString(),
  };
  messages.value.push(tempUserMsg);
  await scrollToBottom();

  try {
    const res = await api.post("/api/chat/send", {
      conversation_id: currentConversationId.value,
      message: text,
    });

    messages.value = messages.value.filter((m) => m.id !== tempUserMsg.id);
    messages.value.push(res.data.user_message);

    // Add processor_time to assistant message
    const assistantMsg = res.data.assistant_message;
    assistantMsg.processor_time = res.data.processor_time;
    messages.value.push(assistantMsg);

    currentConversationId.value = res.data.conversation_id;
    lastEmotion.value = res.data.user_message.emotion;

    if (res.data.is_crisis) {
      showCrisisAlert.value = true;
    }

    await loadConversations();
    await scrollToBottom();
  } catch (e) {
    messages.value = messages.value.filter((m) => m.id !== tempUserMsg.id);
    messages.value.push({
      id: Date.now(),
      role: "assistant",
      content: "抱歉，我暂时无法回应。请稍后再试。",
      created_at: new Date().toISOString(),
    });
  } finally {
    isTyping.value = false;
  }
}

async function sendQuickMessage(text) {
  inputText.value = text;
  await sendMessage();
}

async function quickCheckIn(mood) {
  try {
    const res = await api.post("/api/emotions/quick-checkin", { mood });
    const supportParts = [
      res.data.micro_support,
      res.data.breathing_guide,
    ].filter(Boolean);
    quickSupport.value = supportParts.join(" ");
    lastEmotion.value = res.data.emotion;
  } catch (e) {
    quickSupport.value = "我在这里陪你。先慢慢呼吸一下，我们再继续。";
  }
}

async function scrollToBottom() {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
}

function autoResize() {
  if (textarea.value) {
    textarea.value.style.height = "auto";
    textarea.value.style.height =
      Math.min(textarea.value.scrollHeight, 120) + "px";
  }
}

function resetTextarea() {
  if (textarea.value) {
    textarea.value.style.height = "auto";
  }
}

function handleLogout() {
  authStore.logout();
  router.push("/login");
}

onMounted(() => {
  loadConversations();
});
</script>

<style scoped>
.chat-layout {
  display: flex;
  height: 100vh;
  background: var(--bg);
  overflow: hidden;
}

.sidebar {
  width: 280px;
  min-width: 280px;
  background: white;
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

@media (max-width: 768px) {
  .chat-layout {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    min-width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--border);
    height: auto;
    max-height: 120px;
    overflow-y: auto;
    flex-wrap: wrap;
    flex-direction: row;
  }
}

.sidebar-header {
  padding: 20px 16px;
  background: linear-gradient(135deg, #6c63ff, #764ba2);
  color: white;
}

@media (max-width: 768px) {
  .sidebar-header {
    padding: 12px 16px;
    min-width: 100%;
  }
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.brand-icon {
  font-size: 24px;
}

.brand-name {
  font-size: 18px;
  font-weight: 700;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
}

.user-sub {
  font-size: 11px;
  opacity: 0.8;
}

.sidebar-actions {
  padding: 12px;
  border-bottom: 1px solid var(--border);
}

@media (max-width: 768px) {
  .sidebar-actions {
    padding: 8px;
    border-bottom: none;
  }
}

.btn-new {
  width: 100%;
  padding: 10px;
  background: linear-gradient(135deg, #6c63ff, #a29bfe);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  transition: opacity 0.2s;
}

@media (max-width: 768px) {
  .btn-new {
    padding: 8px;
    font-size: 12px;
  }
}

.btn-new:hover {
  opacity: 0.9;
}

.nav-links {
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

@media (max-width: 768px) {
  .nav-links {
    padding: 0 8px;
    border-bottom: none;
    flex-direction: row;
    flex: 1;
    gap: 6px;
  }
}

.nav-link {
  padding: 10px 12px;
  border-radius: 10px;
  font-size: 14px;
  color: var(--text-light);
  transition:
    background 0.2s,
    color 0.2s;
}

.nav-link:hover,
.nav-link.router-link-active {
  background: #f0eeff;
  color: var(--primary);
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

@media (max-width: 768px) {
  .conversation-list {
    display: none;
  }
}

.list-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-light);
  text-transform: uppercase;
  padding: 8px 8px 4px;
  letter-spacing: 0.5px;
}

.conv-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 10px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.15s;
  font-size: 13px;
  color: var(--text);
}

.conv-item:hover,
.conv-item.active {
  background: #f0eeff;
  color: var(--primary);
}

.conv-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.no-conv {
  text-align: center;
  color: var(--text-light);
  font-size: 13px;
  padding: 20px;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid var(--border);
}

@media (max-width: 768px) {
  .sidebar-footer {
    padding: 0;
    border-top: none;
    display: none;
  }
}

.btn-logout {
  width: 100%;
  padding: 10px;
  background: none;
  border: 1px solid var(--border);
  border-radius: 10px;
  font-size: 14px;
  color: var(--text-light);
  transition:
    background 0.2s,
    color 0.2s;
}

.btn-logout:hover {
  background: #fff5f5;
  color: var(--danger);
  border-color: var(--danger);
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

@media (max-width: 768px) {
  .chat-header {
    padding: 12px 16px;
  }
}

@media (max-width: 480px) {
  .chat-header {
    padding: 10px 12px;
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-left h2 {
  font-size: 16px;
  font-weight: 600;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #00b894;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}

.status-text {
  font-size: 13px;
  color: var(--text-light);
}

.emotion-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #f0eeff;
  border-radius: 20px;
  font-size: 13px;
  color: var(--primary);
  font-weight: 500;
}

.crisis-alert {
  margin: 12px 16px 0;
  padding: 14px 16px;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 12px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.crisis-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.crisis-content {
  flex: 1;
}

.crisis-title {
  font-weight: 600;
  color: #856404;
  margin-bottom: 4px;
}

.crisis-body {
  font-size: 13px;
  color: #664d03;
  line-height: 1.5;
}

.crisis-close {
  background: none;
  border: none;
  font-size: 16px;
  color: #999;
  padding: 0 4px;
  cursor: pointer;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

@media (max-width: 768px) {
  .messages-container {
    padding: 16px 16px;
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .messages-container {
    padding: 12px 12px;
    gap: 10px;
  }
}

.welcome {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px 20px;
  color: var(--text-light);
}

@media (max-width: 480px) {
  .welcome {
    padding: 20px 16px;
  }
}

.welcome-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

@media (max-width: 480px) {
  .welcome-icon {
    font-size: 36px;
    margin-bottom: 12px;
  }
}

.welcome h3 {
  font-size: 20px;
  color: var(--text);
  margin-bottom: 12px;
}

@media (max-width: 480px) {
  .welcome h3 {
    font-size: 16px;
  }
}

.welcome p {
  font-size: 15px;
  line-height: 1.7;
  max-width: 400px;
  margin-bottom: 24px;
}

@media (max-width: 480px) {
  .welcome p {
    font-size: 13px;
    margin-bottom: 16px;
  }
}

.quick-starts {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.quick-btn {
  padding: 10px 18px;
  background: white;
  border: 1.5px solid var(--primary-light);
  border-radius: 20px;
  font-size: 13px;
  color: var(--primary);
  transition:
    background 0.2s,
    color 0.2s;
}

@media (max-width: 480px) {
  .quick-btn {
    padding: 8px 14px;
    font-size: 12px;
  }
}

.quick-btn:hover {
  background: var(--primary);
  color: white;
}

.message-row {
  display: flex;
  align-items: flex-end;
  gap: 10px;
}

.user-row {
  flex-direction: row-reverse;
}

.avatar-ai {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #6c63ff, #a29bfe);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 15px;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .message-bubble {
    max-width: 80%;
    padding: 10px 14px;
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .message-bubble {
    max-width: 90%;
    padding: 10px 12px;
    font-size: 13px;
  }
}

.user-bubble {
  background: linear-gradient(135deg, #6c63ff, #a29bfe);
  color: white;
  border-bottom-right-radius: 6px;
}

.ai-bubble {
  background: white;
  border: 1px solid var(--border);
  color: var(--text);
  border-bottom-left-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.message-text {
  white-space: pre-wrap;
  word-break: break-word;
}

.message-meta {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 6px;
}

.emotion-tag {
  font-size: 11px;
  opacity: 0.8;
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 6px;
  border-radius: 8px;
}

.ai-bubble .emotion-tag {
  background: var(--bg);
  color: var(--text-light);
}

.message-time {
  font-size: 11px;
  opacity: 0.7;
}

.processor-time {
  font-size: 11px;
  opacity: 0.8;
  color: var(--primary);
  font-weight: 500;
}

.typing-bubble {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 14px 18px;
}

.dot {
  width: 8px;
  height: 8px;
  background: var(--primary-light);
  border-radius: 50%;
  animation: bounce 1.4s infinite;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}
.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-6px);
  }
}

.input-area {
  padding: 16px 24px;
  background: white;
  border-top: 1px solid var(--border);
}

@media (max-width: 768px) {
  .input-area {
    padding: 12px 16px;
  }
}

@media (max-width: 480px) {
  .input-area {
    padding: 10px 12px;
  }
}

.quick-moods {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}

.mood-btn {
  border: 1px solid #e8e4ff;
  border-radius: 16px;
  background: #f8f6ff;
  color: var(--primary);
  padding: 6px 12px;
  font-size: 12px;
}

@media (max-width: 480px) {
  .mood-btn {
    padding: 5px 10px;
    font-size: 11px;
  }
}

.quick-support {
  background: #f6fbff;
  border: 1px solid #d5ebff;
  border-radius: 10px;
  padding: 10px 12px;
  margin-bottom: 10px;
}

@media (max-width: 480px) {
  .quick-support {
    padding: 8px 10px;
    margin-bottom: 8px;
  }
}

.support-title {
  font-size: 12px;
  color: #357ab8;
  margin-bottom: 2px;
}

@media (max-width: 480px) {
  .support-title {
    font-size: 11px;
  }
}

.support-body {
  font-size: 13px;
  color: #2b4c6f;
  line-height: 1.5;
}

@media (max-width: 480px) {
  .support-body {
    font-size: 12px;
  }
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  background: var(--bg);
  border: 2px solid var(--border);
  border-radius: 16px;
  padding: 10px 14px;
  transition: border-color 0.2s;
}

@media (max-width: 480px) {
  .input-wrapper {
    border-radius: 12px;
    padding: 8px 10px;
    gap: 8px;
  }
}

.input-wrapper:focus-within {
  border-color: var(--primary-light);
}

textarea {
  flex: 1;
  border: none;
  background: none;
  font-size: 15px;
  font-family: inherit;
  resize: none;
  outline: none;
  max-height: 120px;
  line-height: 1.5;
  color: var(--text);
  min-height: 40px;
}

@media (max-width: 480px) {
  textarea {
    font-size: 13px;
    min-height: 36px;
  }
}

textarea::placeholder {
  color: #bbb;
}

.send-btn {
  padding: 8px 20px;
  background: linear-gradient(135deg, #6c63ff, #a29bfe);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
  transition: opacity 0.2s;
  min-height: 40px;
  min-width: 50px;
}

@media (max-width: 480px) {
  .send-btn {
    padding: 6px 14px;
    font-size: 12px;
    min-height: 36px;
    min-width: 45px;
  }
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-hint {
  text-align: center;
  font-size: 11px;
  color: #ccc;
  margin-top: 6px;
}
</style>

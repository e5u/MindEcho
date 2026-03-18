<template>
  <div class="chat-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="brand">
          <span class="brand-icon">🌊</span>
          <span class="brand-name">心灵回声</span>
        </div>
        <div class="user-info" v-if="authStore.user">
          <div class="avatar">{{ getInitial(authStore.user.nickname || authStore.user.username) }}</div>
          <div>
            <div class="user-name">{{ authStore.user.nickname || authStore.user.username }}</div>
            <div class="user-sub">大学生用户</div>
          </div>
        </div>
      </div>

      <nav class="nav-links">
        <router-link to="/chat" class="nav-link">
          💬 心理咨询
        </router-link>
        <router-link to="/emotions" class="nav-link">
          📊 情绪记录
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <button class="btn-logout" @click="handleLogout">退出登录</button>
      </div>
    </aside>

    <main class="emotions-main">
      <header class="page-header">
        <h2>📊 我的情绪记录</h2>
        <p>了解你的情绪变化，关注内心的健康</p>
        <div class="date-filter">
          <button
            v-for="d in dateOptions"
            :key="d.value"
            class="filter-btn"
            :class="{ active: selectedDays === d.value }"
            @click="changeDays(d.value)"
          >{{ d.label }}</button>
        </div>
      </header>

      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else class="content">
        <div class="stats-grid">
          <div class="stat-card total">
            <div class="stat-icon">📝</div>
            <div class="stat-value">{{ historyData.total }}</div>
            <div class="stat-label">情绪记录总数</div>
          </div>
          <div
            v-for="stat in historyData.stats.slice(0, 3)"
            :key="stat.emotion"
            class="stat-card"
            :style="{ borderTopColor: emotionColors[stat.emotion] }"
          >
            <div class="stat-icon">{{ emotionEmoji[stat.emotion] }}</div>
            <div class="stat-value">{{ stat.count }}</div>
            <div class="stat-label">{{ emotionLabels[stat.emotion] }}</div>
            <div class="stat-pct">{{ stat.percentage }}%</div>
          </div>
        </div>

        <div class="charts-row">
          <div class="chart-card">
            <h3>情绪分布</h3>
            <div class="pie-chart">
              <div v-if="historyData.stats.length === 0" class="no-data">
                暂无数据，去聊天记录一些心情吧 💙
              </div>
              <div v-else class="emotion-bars">
                <div
                  v-for="stat in historyData.stats"
                  :key="stat.emotion"
                  class="emotion-bar-row"
                >
                  <div class="bar-label">
                    <span>{{ emotionEmoji[stat.emotion] }}</span>
                    <span>{{ emotionLabels[stat.emotion] }}</span>
                  </div>
                  <div class="bar-track">
                    <div
                      class="bar-fill"
                      :style="{
                        width: stat.percentage + '%',
                        background: emotionColors[stat.emotion]
                      }"
                    ></div>
                  </div>
                  <div class="bar-pct">{{ stat.percentage }}%</div>
                </div>
              </div>
            </div>
          </div>

          <div class="chart-card">
            <h3>情绪趋势（近 {{ selectedDays }} 天）</h3>
            <div class="trend-chart" v-if="trendData.length > 0">
              <div class="trend-legend">
                <span v-for="(color, emotion) in emotionColors" :key="emotion" class="legend-item">
                  <span class="legend-dot" :style="{ background: color }"></span>
                  {{ emotionLabels[emotion] }}
                </span>
              </div>
              <div class="trend-bars">
                <div
                  v-for="day in trendData"
                  :key="day.date"
                  class="trend-day"
                >
                  <div class="day-bars">
                    <div
                      v-for="(count, emotion) in day.emotions"
                      :key="emotion"
                      class="day-bar"
                      :style="{
                        height: Math.min(count * 20, 80) + 'px',
                        background: emotionColors[emotion]
                      }"
                      :title="`${emotionLabels[emotion]}: ${count}次`"
                    ></div>
                  </div>
                  <div class="day-label">{{ formatShortDate(day.date) }}</div>
                </div>
              </div>
            </div>
            <div v-else class="no-data">暂无趋势数据</div>
          </div>
        </div>

        <div class="records-card">
          <h3>最近记录</h3>
          <div v-if="historyData.records.length === 0" class="no-data">
            还没有情绪记录，开始和助手聊天吧！
          </div>
          <div class="records-list">
            <div
              v-for="record in historyData.records.slice(0, 20)"
              :key="record.id"
              class="record-item"
            >
              <div class="record-left">
                <span class="record-emoji">{{ emotionEmoji[record.emotion] }}</span>
                <div>
                  <div class="record-emotion" :style="{ color: emotionColors[record.emotion] }">
                    {{ emotionLabels[record.emotion] }}
                  </div>
                  <div class="record-time">{{ formatDateTime(record.created_at) }}</div>
                </div>
              </div>
              <div class="record-score">
                <div class="score-bar">
                  <div
                    class="score-fill"
                    :style="{
                      width: (record.emotion_score * 100) + '%',
                      background: emotionColors[record.emotion]
                    }"
                  ></div>
                </div>
                <span class="score-num">{{ Math.round(record.emotion_score * 100) }}%</span>
              </div>
            </div>
          </div>
        </div>

        <div class="tips-card">
          <h3>💡 心理健康小贴士</h3>
          <div class="tips-grid">
            <div class="tip-item" v-for="tip in mentalHealthTips" :key="tip.title">
              <div class="tip-icon">{{ tip.icon }}</div>
              <div class="tip-title">{{ tip.title }}</div>
              <div class="tip-body">{{ tip.body }}</div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const selectedDays = ref(7)
const historyData = ref({ records: [], stats: [], total: 0 })
const trendData = ref([])

const dateOptions = [
  { label: '7天', value: 7 },
  { label: '30天', value: 30 },
  { label: '90天', value: 90 },
]

const emotionLabels = {
  happy: '开心',
  sad: '悲伤',
  anxious: '焦虑',
  angry: '愤怒',
  neutral: '平静',
  fear: '恐惧',
  lonely: '孤独',
}

const emotionEmoji = {
  happy: '😊',
  sad: '😢',
  anxious: '😰',
  angry: '😤',
  neutral: '😌',
  fear: '😨',
  lonely: '🥺',
}

const emotionColors = {
  happy: '#00b894',
  sad: '#74b9ff',
  anxious: '#fdcb6e',
  angry: '#ff7675',
  neutral: '#a29bfe',
  fear: '#fd79a8',
  lonely: '#636e72',
}

const mentalHealthTips = [
  {
    icon: '🧘',
    title: '正念冥想',
    body: '每天花10分钟进行深呼吸或冥想，有助于缓解焦虑和压力。',
  },
  {
    icon: '🏃',
    title: '适量运动',
    body: '运动能促进内啡肽分泌，改善情绪。每天30分钟的有氧运动效果显著。',
  },
  {
    icon: '😴',
    title: '规律睡眠',
    body: '保持7-8小时的充足睡眠，避免熬夜。睡眠对情绪调节非常重要。',
  },
  {
    icon: '👥',
    title: '社交连接',
    body: '主动与朋友、同学保持联系，孤独感会加重心理负担。',
  },
  {
    icon: '📚',
    title: '寻求专业帮助',
    body: '如果情绪长期低落，请及时联系学校心理咨询中心或专业心理医生。',
  },
  {
    icon: '🎨',
    title: '发展兴趣爱好',
    body: '培养一项让你放松的爱好，如绘画、音乐、写作等，有助于情绪释放。',
  },
]

function getInitial(name) {
  return name ? name[0].toUpperCase() : '?'
}

function formatDateTime(dateStr) {
  const d = new Date(dateStr)
  return d.toLocaleString('zh-CN', {
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatShortDate(dateStr) {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

async function fetchData() {
  loading.value = true
  try {
    const [histRes, trendRes] = await Promise.all([
      api.get(`/api/emotions/history?days=${selectedDays.value}`),
      api.get(`/api/emotions/trend?days=${selectedDays.value}`),
    ])
    historyData.value = histRes.data
    trendData.value = trendRes.data.trend
  } catch (e) {
    console.error('Failed to fetch emotion data', e)
  } finally {
    loading.value = false
  }
}

function changeDays(days) {
  selectedDays.value = days
  fetchData()
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  fetchData()
})
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

.sidebar-header {
  padding: 20px 16px;
  background: linear-gradient(135deg, #6c63ff, #764ba2);
  color: white;
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.brand-icon { font-size: 24px; }
.brand-name { font-size: 18px; font-weight: 700; }

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  width: 36px;
  height: 36px;
  background: rgba(255,255,255,0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
}

.user-name { font-size: 14px; font-weight: 600; }
.user-sub { font-size: 11px; opacity: 0.8; }

.nav-links {
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-link {
  padding: 10px 12px;
  border-radius: 10px;
  font-size: 14px;
  color: var(--text-light);
  transition: background 0.2s, color 0.2s;
}

.nav-link:hover,
.nav-link.router-link-active {
  background: #f0eeff;
  color: var(--primary);
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid var(--border);
  margin-top: auto;
}

.btn-logout {
  width: 100%;
  padding: 10px;
  background: none;
  border: 1px solid var(--border);
  border-radius: 10px;
  font-size: 14px;
  color: var(--text-light);
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.btn-logout:hover {
  background: #fff5f5;
  color: var(--danger);
  border-color: var(--danger);
}

.emotions-main {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  background: white;
  border-radius: var(--radius);
  padding: 24px;
  box-shadow: var(--shadow);
}

.page-header h2 {
  font-size: 22px;
  margin-bottom: 6px;
}

.page-header p {
  color: var(--text-light);
  font-size: 14px;
  margin-bottom: 16px;
}

.date-filter {
  display: flex;
  gap: 8px;
}

.filter-btn {
  padding: 6px 16px;
  border: 1.5px solid var(--border);
  border-radius: 20px;
  font-size: 13px;
  color: var(--text-light);
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn.active,
.filter-btn:hover {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--text-light);
  gap: 12px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.stat-card {
  background: white;
  border-radius: var(--radius);
  padding: 20px;
  text-align: center;
  box-shadow: var(--shadow);
  border-top: 4px solid var(--primary-light);
}

.stat-card.total {
  border-top-color: var(--primary);
}

.stat-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text);
}

.stat-label {
  font-size: 13px;
  color: var(--text-light);
  margin-top: 4px;
}

.stat-pct {
  font-size: 12px;
  color: var(--primary);
  margin-top: 2px;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.chart-card {
  background: white;
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow);
}

.chart-card h3 {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text);
}

.no-data {
  text-align: center;
  color: var(--text-light);
  padding: 30px 0;
  font-size: 14px;
}

.emotion-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.emotion-bar-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.bar-label {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 70px;
  font-size: 13px;
  flex-shrink: 0;
}

.bar-track {
  flex: 1;
  height: 10px;
  background: var(--bg);
  border-radius: 5px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.5s ease;
}

.bar-pct {
  width: 36px;
  font-size: 12px;
  color: var(--text-light);
  text-align: right;
}

.trend-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--text-light);
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.trend-bars {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 100px;
  overflow-x: auto;
}

.trend-day {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 40px;
}

.day-bars {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 80px;
}

.day-bar {
  width: 10px;
  border-radius: 3px 3px 0 0;
  min-height: 4px;
  transition: height 0.3s;
}

.day-label {
  font-size: 10px;
  color: var(--text-light);
  margin-top: 4px;
  white-space: nowrap;
}

.records-card {
  background: white;
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow);
}

.records-card h3 {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 16px;
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.record-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--bg);
  border-radius: 12px;
}

.record-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.record-emoji {
  font-size: 24px;
}

.record-emotion {
  font-size: 14px;
  font-weight: 600;
}

.record-time {
  font-size: 12px;
  color: var(--text-light);
  margin-top: 2px;
}

.record-score {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-bar {
  width: 80px;
  height: 6px;
  background: var(--border);
  border-radius: 3px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  border-radius: 3px;
}

.score-num {
  font-size: 12px;
  color: var(--text-light);
  width: 32px;
}

.tips-card {
  background: white;
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow);
}

.tips-card h3 {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 16px;
}

.tips-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 14px;
}

.tip-item {
  padding: 16px;
  background: linear-gradient(135deg, #f0eeff, #f8f9ff);
  border-radius: 12px;
  border: 1px solid #e8e4ff;
}

.tip-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.tip-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-dark);
  margin-bottom: 6px;
}

.tip-body {
  font-size: 13px;
  color: var(--text-light);
  line-height: 1.5;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
</style>

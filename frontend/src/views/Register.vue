<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="logo">
        <div class="logo-icon">🌊</div>
        <h1 class="logo-title">心灵回声</h1>
        <p class="logo-subtitle">加入 MindEcho，开始你的心理健康之旅</p>
      </div>

      <form @submit.prevent="handleRegister" class="form">
        <div class="form-group">
          <label>用户名</label>
          <input
            v-model="form.username"
            type="text"
            placeholder="请输入用户名（3-20个字符）"
            required
            minlength="3"
            maxlength="20"
          />
        </div>

        <div class="form-group">
          <label>昵称（可选）</label>
          <input
            v-model="form.nickname"
            type="text"
            placeholder="你希望我们怎么称呼你？"
            maxlength="20"
          />
        </div>

        <div class="form-group">
          <label>邮箱</label>
          <input
            v-model="form.email"
            type="email"
            placeholder="请输入邮箱地址"
            required
          />
        </div>

        <div class="form-group">
          <label>密码</label>
          <input
            v-model="form.password"
            type="password"
            placeholder="请设置密码（至少6位）"
            required
            minlength="6"
            autocomplete="new-password"
          />
        </div>

        <div v-if="error" class="error-msg">{{ error }}</div>

        <button type="submit" class="btn-primary" :disabled="loading">
          <span v-if="loading">注册中...</span>
          <span v-else>注 册</span>
        </button>
      </form>

      <p class="switch-link">
        已有账号？
        <router-link to="/login">立即登录</router-link>
      </p>

      <p class="tagline">你的每一次倾诉，都值得被温柔以待 💙</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  nickname: '',
  email: '',
  password: '',
})
const loading = ref(false)
const error = ref('')

async function handleRegister() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.post('/api/auth/register', form.value)
    authStore.setAuth(res.data.access_token, res.data.user)
    router.push('/chat')
  } catch (err) {
    error.value = err.response?.data?.detail || '注册失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.auth-card {
  background: white;
  border-radius: 24px;
  padding: 48px 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.logo {
  text-align: center;
  margin-bottom: 32px;
}

.logo-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

.logo-title {
  font-size: 28px;
  font-weight: 700;
  color: #6c63ff;
  margin-bottom: 6px;
}

.logo-subtitle {
  font-size: 13px;
  color: #999;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #555;
}

.form-group input {
  padding: 12px 16px;
  border: 2px solid #e8e8e8;
  border-radius: 12px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
  font-family: inherit;
}

.form-group input:focus {
  border-color: #6c63ff;
}

.error-msg {
  color: #d63031;
  font-size: 13px;
  padding: 10px 14px;
  background: #fff5f5;
  border-radius: 8px;
  border-left: 3px solid #d63031;
}

.btn-primary {
  padding: 14px;
  background: linear-gradient(135deg, #6c63ff, #a29bfe);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  margin-top: 4px;
  transition: transform 0.15s, box-shadow 0.15s;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(108, 99, 255, 0.4);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.switch-link {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #999;
}

.switch-link a {
  color: #6c63ff;
  font-weight: 500;
}

.tagline {
  text-align: center;
  margin-top: 16px;
  font-size: 12px;
  color: #bbb;
}
</style>

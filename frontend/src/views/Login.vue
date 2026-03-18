<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="logo">
        <div class="logo-icon">🌊</div>
        <h1 class="logo-title">心灵回声</h1>
        <p class="logo-subtitle">MindEcho · 你的心理健康伴侣</p>
      </div>

      <form @submit.prevent="handleLogin" class="form">
        <div class="form-group">
          <label>用户名</label>
          <input
            v-model="form.username"
            type="text"
            placeholder="请输入用户名"
            required
            autocomplete="username"
          />
        </div>

        <div class="form-group">
          <label>密码</label>
          <input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            required
            autocomplete="current-password"
          />
        </div>

        <div v-if="error" class="error-msg">{{ error }}</div>

        <button type="submit" class="btn-primary" :disabled="loading">
          <span v-if="loading">登录中...</span>
          <span v-else>登 录</span>
        </button>
      </form>

      <p class="switch-link">
        还没有账号？
        <router-link to="/register">立即注册</router-link>
      </p>

      <p class="tagline">愿你在这里找到内心的平静与力量 💙</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import api from "../api";

const router = useRouter();
const authStore = useAuthStore();

const form = ref({ username: "", password: "" });
const loading = ref(false);
const error = ref("");

async function handleLogin() {
  loading.value = true;
  error.value = "";
  try {
    const res = await api.post("/api/auth/login", form.value);
    authStore.setAuth(res.data.access_token, res.data.user);
    router.push("/chat");
  } catch (err) {
    error.value = err.response?.data?.detail || "登录失败，请检查用户名和密码";
  } finally {
    loading.value = false;
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

@media (max-width: 480px) {
  .auth-card {
    border-radius: 16px;
    padding: 32px 20px;
    max-width: 100%;
  }
}

.logo {
  text-align: center;
  margin-bottom: 36px;
}

@media (max-width: 480px) {
  .logo {
    margin-bottom: 24px;
  }
}

.logo-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

@media (max-width: 480px) {
  .logo-icon {
    font-size: 36px;
  }
}

.logo-title {
  font-size: 28px;
  font-weight: 700;
  color: #6c63ff;
  margin-bottom: 6px;
}

@media (max-width: 480px) {
  .logo-title {
    font-size: 22px;
  }
}

.logo-subtitle {
  font-size: 14px;
  color: #999;
}

@media (max-width: 480px) {
  .logo-subtitle {
    font-size: 12px;
  }
}

.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

@media (max-width: 480px) {
  .form {
    gap: 16px;
  }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #555;
}

@media (max-width: 480px) {
  .form-group label {
    font-size: 13px;
  }
}

.form-group input {
  padding: 12px 16px;
  border: 2px solid #e8e8e8;
  border-radius: 12px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
  font-family: inherit;
  min-height: 44px;
}

@media (max-width: 480px) {
  .form-group input {
    padding: 10px 12px;
    font-size: 14px;
  }
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

@media (max-width: 480px) {
  .error-msg {
    font-size: 12px;
    padding: 8px 12px;
  }
}

.btn-primary {
  padding: 14px;
  background: linear-gradient(135deg, #6c63ff, #a29bfe);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  margin-top: 8px;
  transition:
    transform 0.15s,
    box-shadow 0.15s;
  min-height: 44px;
}

@media (max-width: 480px) {
  .btn-primary {
    padding: 12px;
    font-size: 14px;
  }
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

@media (max-width: 480px) {
  .switch-link {
    margin-top: 16px;
    font-size: 13px;
  }
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

@media (max-width: 480px) {
  .tagline {
    font-size: 11px;
    margin-top: 12px;
  }
}
</style>

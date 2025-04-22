<template>
  <div class="container">
    <div class="row justify-content-center mt-5">
      <div class="col-md-6 col-lg-4">
        <div class="card shadow-sm">
          <div class="card-header bg-success text-white text-center py-3">
            <h2 class="card-title mb-0">注册</h2>
          </div>
          <div class="card-body p-4">
            <form @submit.prevent="register">
              <!-- Error Alert -->
              <div v-if="userStore.error" class="alert alert-danger">
                {{ userStore.error }}
              </div>
              
              <!-- Success Alert -->
              <div v-if="registrationSuccess" class="alert alert-success">
                注册成功！您可以 <router-link to="/login" class="alert-link">登录</router-link> 了。
              </div>
              
              <!-- Username Field -->
              <div class="mb-3">
                <label for="username" class="form-label">用户名</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-person"></i>
                  </span>
                  <input 
                    type="text" 
                    id="username" 
                    class="form-control" 
                    v-model="userData.username" 
                    placeholder="请输入用户名"
                    required
                  >
                </div>
              </div>
              
              <!-- Email Field -->
              <div class="mb-3">
                <label for="email" class="form-label">邮箱</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-envelope"></i>
                  </span>
                  <input 
                    type="email" 
                    id="email" 
                    class="form-control" 
                    v-model="userData.email" 
                    placeholder="请输入邮箱"
                    required
                  >
                </div>
              </div>
              
              <!-- Password Field -->
              <div class="mb-3">
                <label for="password" class="form-label">密码</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-lock"></i>
                  </span>
                  <input 
                    :type="showPassword ? 'text' : 'password'" 
                    id="password" 
                    class="form-control" 
                    v-model="userData.password" 
                    placeholder="请设置密码"
                    required
                    minlength="6"
                  >
                  <button 
                    class="btn btn-outline-secondary" 
                    type="button"
                    @click="showPassword = !showPassword"
                  >
                    <i class="bi" :class="showPassword ? 'bi-eye-slash' : 'bi-eye'"></i>
                  </button>
                </div>
                <small class="text-muted">密码长度至少6位</small>
              </div>
              
              <!-- Confirm Password Field -->
              <div class="mb-4">
                <label for="confirmPassword" class="form-label">确认密码</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-lock-fill"></i>
                  </span>
                  <input 
                    :type="showPassword ? 'text' : 'password'" 
                    id="confirmPassword" 
                    class="form-control" 
                    v-model="confirmPassword" 
                    placeholder="请再次输入密码"
                    required
                  >
                </div>
                <small v-if="passwordMismatch" class="text-danger">两次密码输入不一致</small>
              </div>
              
              <!-- Register Button -->
              <div class="d-grid">
                <button 
                  type="submit" 
                  class="btn btn-success btn-lg" 
                  :disabled="userStore.loading || passwordMismatch"
                >
                  <span v-if="userStore.loading">
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    注册中...
                  </span>
                  <span v-else>
                    <i class="bi bi-person-plus me-2"></i>注册
                  </span>
                </button>
              </div>
              
              <!-- Login Link -->
              <div class="text-center mt-4">
                <p>已有账号？ 
                  <router-link to="/login" class="text-decoration-none">
                    <strong>立即登录</strong>
                  </router-link>
                </p>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from 'vue';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();

const showPassword = ref(false);
const confirmPassword = ref('');
const registrationSuccess = ref(false);

const userData = reactive({
  username: '',
  email: '',
  password: ''
});

// Check if passwords match
const passwordMismatch = computed(() => {
  return userData.password && confirmPassword.value && userData.password !== confirmPassword.value;
});

// Handle registration
async function register() {
  // Check if passwords match
  if (userData.password !== confirmPassword.value) {
    return;
  }
  
  const success = await userStore.register(userData);
  
  if (success) {
    registrationSuccess.value = true;
    // Clear form
    userData.username = '';
    userData.email = '';
    userData.password = '';
    confirmPassword.value = '';
  }
}
</script>

<style scoped>
.card-header {
  background-color: #198754 !important;
}
</style> 
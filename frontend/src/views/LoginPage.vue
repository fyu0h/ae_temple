<template>
  <div class="container">
    <div class="row justify-content-center mt-5">
      <div class="col-md-6 col-lg-4">
        <div class="card shadow-sm">
          <div class="card-header bg-primary text-white text-center py-3">
            <h2 class="card-title mb-0">登录</h2>
          </div>
          <div class="card-body p-4">
            <form @submit.prevent="login">
              <!-- Error Alert -->
              <div v-if="userStore.error" class="alert alert-danger">
                {{ userStore.error }}
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
                    v-model="credentials.username" 
                    placeholder="请输入用户名"
                    required
                  >
                </div>
              </div>
              
              <!-- Password Field -->
              <div class="mb-4">
                <label for="password" class="form-label">密码</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-lock"></i>
                  </span>
                  <input 
                    :type="showPassword ? 'text' : 'password'" 
                    id="password" 
                    class="form-control" 
                    v-model="credentials.password" 
                    placeholder="请输入密码"
                    required
                  >
                  <button 
                    class="btn btn-outline-secondary" 
                    type="button"
                    @click="showPassword = !showPassword"
                  >
                    <i class="bi" :class="showPassword ? 'bi-eye-slash' : 'bi-eye'"></i>
                  </button>
                </div>
              </div>
              
              <!-- Login Button -->
              <div class="d-grid">
                <button 
                  type="submit" 
                  class="btn btn-primary btn-lg" 
                  :disabled="userStore.loading"
                >
                  <span v-if="userStore.loading">
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    登录中...
                  </span>
                  <span v-else>
                    <i class="bi bi-box-arrow-in-right me-2"></i>登录
                  </span>
                </button>
              </div>
              
              <!-- Register Link -->
              <div class="text-center mt-4">
                <p>还没有账号？ 
                  <router-link to="/register" class="text-decoration-none">
                    <strong>立即注册</strong>
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
import { reactive, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const showPassword = ref(false);
const credentials = reactive({
  username: '',
  password: ''
});

// Handle login
async function login() {
  const success = await userStore.login(credentials);
  
  if (success) {
    // Redirect to the page user was trying to access, or home page
    const redirectPath = route.query.redirect || '/';
    router.push(redirectPath);
  }
}
</script>

<style scoped>
.card-header {
  background-color: #4a6bff !important;
}
</style> 
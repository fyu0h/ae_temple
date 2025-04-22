<template>
  <nav class="navbar navbar-expand-lg navbar-light">
    <div class="container">
      <router-link class="navbar-brand" to="/">
        <i class="bi bi-film me-2"></i>素材管理平台
      </router-link>
      
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" 
              aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <router-link class="nav-link" to="/" active-class="active">首页</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/upload" active-class="active">上传素材</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/materials" active-class="active">素材管理</router-link>
          </li>
          <li class="nav-item" v-if="userStore.isAdmin">
            <router-link class="nav-link" to="/accounts" active-class="active">账号管理</router-link>
          </li>
        </ul>
        
        <div class="d-flex align-items-center" v-if="userStore.isLoggedIn">
          <span class="me-3 user-info">
            <i class="bi bi-person-circle me-1"></i>{{ userStore.user?.username }}
          </span>
          <button @click="logout" class="btn btn-glass">
            <i class="bi bi-box-arrow-right me-1"></i>退出
          </button>
        </div>
        
        <div class="d-flex" v-else>
          <router-link to="/login" class="btn btn-glass me-2">
            <i class="bi bi-box-arrow-in-right me-1"></i>登录
          </router-link>
          <router-link to="/register" class="btn btn-primary">
            <i class="bi bi-person-plus me-1"></i>注册
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useUserStore } from '@/stores/user';
import { useRouter } from 'vue-router';

const userStore = useUserStore();
const router = useRouter();

const logout = async () => {
  await userStore.logout();
  router.push('/login');
};
</script>

<style scoped>
.navbar {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.8rem 0;
}

.navbar-brand {
  font-weight: 600;
  background: linear-gradient(45deg, #2c3e50, #3498db);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 1.3rem;
  transition: all 0.3s ease;
}

.navbar-brand:hover {
  background: linear-gradient(45deg, #3498db, #2c3e50);
  -webkit-background-clip: text;
  background-clip: text;
  transform: translateY(-1px);
}

.nav-link {
  position: relative;
  transition: all 0.3s ease;
  color: #2c3e50;
  font-weight: 500;
  padding: 0.5rem 1rem;
  margin: 0 0.2rem;
}

.nav-link:hover {
  color: #3498db;
  transform: translateY(-2px);
}

.nav-link.active {
  color: #3498db;
  font-weight: 600;
}

.nav-link.active:after {
  content: '';
  position: absolute;
  width: 50%;
  height: 3px;
  background: linear-gradient(45deg, #2c3e50, #3498db);
  bottom: -5px;
  left: 25%;
  border-radius: 3px;
  box-shadow: 0 2px 4px rgba(52, 152, 219, 0.2);
}

.btn-glass {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  border: 1px solid rgba(52, 152, 219, 0.2);
  color: #2c3e50;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.btn-glass:hover {
  background: rgba(52, 152, 219, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(52, 152, 219, 0.15);
  border-color: rgba(52, 152, 219, 0.3);
  color: #3498db;
}

.user-info {
  background: rgba(44, 62, 80, 0.05);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  padding: 0.4rem 0.8rem;
  border-radius: 50px;
  border: 1px solid rgba(52, 152, 219, 0.2);
  color: #2c3e50;
  font-weight: 500;
}
</style> 
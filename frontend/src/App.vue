<template>
  <Navbar />
  <main class="container-fluid mt-4">
    <router-view></router-view>
  </main>
</template>

<script setup>
import Navbar from '@/components/Navbar.vue';
import { onMounted } from 'vue';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();

// 在应用启动时自动获取用户信息，以在页面刷新后恢复登录状态
onMounted(async () => {
  if (userStore.token) {
    await userStore.fetchCurrentUser();
  }
});
</script>

<style>
body {
  min-height: 100vh;
  background: linear-gradient(135deg, #f6f8fc 0%, #e9edf5 100%);
  color: #2c3e50;
}

#app {
  min-height: 100vh;
  background: linear-gradient(165deg, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.7));
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.container {
  position: relative;
  z-index: 1;
}

/* Form Controls */
.form-control,
.form-select {
  border: 1px solid rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  transition: all 0.3s ease;
}

.form-control:focus,
.form-select:focus {
  border-color: rgba(37, 99, 235, 0.5);
  box-shadow: 0 0 0 0.25rem rgba(37, 99, 235, 0.1);
  background: rgba(255, 255, 255, 0.95);
}

/* Card Backgrounds */
.card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

/* Button Styles */
.btn-primary {
  background: linear-gradient(45deg, #2563eb, #3b82f6);
  border: none;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background: linear-gradient(45deg, #1d4ed8, #2563eb);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.25);
}

.btn-outline-primary {
  border: 1px solid #2563eb;
  color: #2563eb;
  background: transparent;
  transition: all 0.3s ease;
}

.btn-outline-primary:hover {
  background: linear-gradient(45deg, #2563eb, #3b82f6);
  border-color: transparent;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.25);
}

/* 全局背景和美化样式 */
body::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('/background.jpg');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  opacity: 0.2;
  z-index: -1;
  animation: subtle-move 120s infinite alternate ease-in-out;
}

@keyframes subtle-move {
  0% {
    background-position: 0% 0%;
  }
  100% {
    background-position: 100% 100%;
  }
}

/* 卡片美化 */
.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
}

/* 表格美化 */
.table-responsive {
  border-radius: 12px;
  overflow: hidden;
}

.table {
  margin-bottom: 0;
}

.table th {
  background-color: rgba(245, 247, 250, 0.8);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  border-top: none;
  font-weight: 600;
  color: #5a5a5a;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.5px;
}

/* 按钮美化 */
.btn {
  border-radius: 10px;
  font-weight: 500;
  transition: all 0.3s ease;
  padding: 8px 16px;
}

.btn-primary i {
  color: #666;
}

.btn-action {
  background: rgba(108, 117, 125, 0.15) !important;
  color: #6c757d !important;
  border: 1px solid rgba(108, 117, 125, 0.2) !important;
  padding: 6px 12px;
  margin: 0 4px;
  border-radius: 8px;
  font-size: 0.9rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.btn-action:hover {
  background: rgba(255, 255, 255, 0.95) !important;
  color: #333 !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: rgba(255, 255, 255, 0.3) !important;
}

.btn-action.btn-edit {
  background: rgba(33, 150, 243, 0.15) !important;
  color: #2196F3 !important;
  border-color: rgba(33, 150, 243, 0.2) !important;
}

.btn-action.btn-edit:hover {
  background: rgba(33, 150, 243, 0.25) !important;
  border-color: rgba(33, 150, 243, 0.3) !important;
}

.btn-action.btn-delete {
  background: rgba(220, 53, 69, 0.15) !important;
  color: #dc3545 !important;
  border-color: rgba(220, 53, 69, 0.2) !important;
}

.btn-action.btn-delete:hover {
  background: rgba(220, 53, 69, 0.25) !important;
  border-color: rgba(220, 53, 69, 0.3) !important;
}

.btn-action i {
  font-size: 1rem;
  vertical-align: middle;
  margin-right: 4px;
}

/* 表格中的操作列样式 */
.table td.actions {
  white-space: nowrap;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
}

/* 美化搜索元素 */
.input-group-text {
  border-radius: 10px 0 0 10px;
  background-color: rgba(240, 242, 245, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

/* 卡片特效 */
.card.bg-dark {
  background: linear-gradient(135deg, rgba(31, 37, 50, 0.8), rgba(42, 50, 70, 0.9)) !important;
}

/* 分页样式统一 */
.pagination {
  margin-top: 1.5rem;
}

.pagination .page-link {
  border: none;
  margin: 0 3px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.8);
  color: #5a5a5a;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.pagination .page-link:hover {
  background: rgba(245, 247, 250, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 1;
}

.pagination .page-item.active .page-link {
  background: linear-gradient(45deg, #4568dc, #b06ab3);
  border-color: transparent;
  color: white;
}

/* 导航栏美化 */
.navbar {
  background: rgba(255, 255, 255, 0.85) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}

/* 操作按钮样式 */
.btn-action {
  background: rgba(108, 117, 125, 0.15) !important;
  color: #6c757d !important;
  border: 1px solid rgba(108, 117, 125, 0.2) !important;
  padding: 6px 12px;
  margin: 0 4px;
  border-radius: 8px;
  font-size: 0.9rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.btn-action:hover {
  background: rgba(255, 255, 255, 0.95) !important;
  color: #333 !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: rgba(255, 255, 255, 0.3) !important;
}

.btn-action.btn-edit {
  background: rgba(33, 150, 243, 0.15) !important;
  color: #2196F3 !important;
  border-color: rgba(33, 150, 243, 0.2) !important;
}

.btn-action.btn-edit:hover {
  background: rgba(33, 150, 243, 0.25) !important;
  border-color: rgba(33, 150, 243, 0.3) !important;
}

.btn-action.btn-delete {
  background: rgba(220, 53, 69, 0.15) !important;
  color: #dc3545 !important;
  border-color: rgba(220, 53, 69, 0.2) !important;
}

.btn-action.btn-delete:hover {
  background: rgba(220, 53, 69, 0.25) !important;
  border-color: rgba(220, 53, 69, 0.3) !important;
}

.btn-action i {
  font-size: 1rem;
  vertical-align: middle;
  margin-right: 4px;
}

/* 表格中的操作列样式 */
.table td.actions {
  white-space: nowrap;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
}
</style>

<style>
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f8f9fa;
}

.material-card {
  height: 100%;
  position: relative;
  overflow: hidden;
}

.material-card img {
  width: 100%;
  height: 180px;
  object-fit: cover;
}

.material-card .card-img-overlay {
  opacity: 0;
  transition: opacity 0.3s ease;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.material-card:hover .card-img-overlay {
  opacity: 1;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.tag {
  background-color: #f0f0f0;
  border-radius: 20px;
  padding: 5px 10px;
  font-size: 0.8rem;
}
</style> 
<template>
  <div class="container">
    <!-- Hero Section -->
    <div class="row mb-5">
      <div class="col-12">
        <div class="hero-section text-center">
          <h1 class="display-4 fw-bold mb-3 hero-title">素材管理平台</h1>
          <p class="lead hero-subtitle">一站式管理你的视频、音乐、AE模板和照片素材</p>
          
          <!-- Search Form -->
          <div class="search-form">
            <div class="row g-3 justify-content-center">
              <div class="col-md-6">
                <div class="search-input-group">
                  <i class="bi bi-search search-icon"></i>
                  <input 
                    type="text" 
                    class="form-control form-control-lg" 
                    placeholder="搜索关键词..." 
                    v-model="searchQuery"
                    @keyup.enter="search"
                  >
                </div>
              </div>
              <div class="col-md-3">
                <div class="select-wrapper">
                  <i class="bi bi-grid-3x3-gap select-icon"></i>
                  <select class="form-select form-select-lg" v-model="categoryFilter">
                    <option value="">全部分类</option>
                    <option value="AE模板">AE模板</option>
                    <option value="视频">视频</option>
                    <option value="音乐">音乐</option>
                    <option value="照片">照片</option>
                  </select>
                </div>
              </div>
              <div class="col-md-2">
                <button class="btn btn-primary btn-lg w-100 search-btn" @click="search">
                  <i class="bi bi-search me-2"></i>搜索
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Category Cards -->
    <div class="row mb-5" v-if="!hasSearched">
      <h2 class="mb-4">素材分类</h2>
      
      <div class="col-md-6 col-lg-3 mb-4">
        <div class="category-card ae-template" @click="filterByCategory('AE模板')">
          <div class="card-body">
            <i class="bi bi-file-earmark-zip"></i>
            <h3 class="card-title">AE模板</h3>
            <p class="card-text">After Effects 模板素材</p>
          </div>
        </div>
      </div>
      
      <div class="col-md-6 col-lg-3 mb-4">
        <div class="category-card video" @click="filterByCategory('视频')">
          <div class="card-body">
            <i class="bi bi-film"></i>
            <h3 class="card-title">视频</h3>
            <p class="card-text">高清视频素材</p>
          </div>
        </div>
      </div>
      
      <div class="col-md-6 col-lg-3 mb-4">
        <div class="category-card music" @click="filterByCategory('音乐')">
          <div class="card-body">
            <i class="bi bi-music-note-beamed"></i>
            <h3 class="card-title">音乐</h3>
            <p class="card-text">背景音乐和音效</p>
          </div>
        </div>
      </div>
      
      <div class="col-md-6 col-lg-3 mb-4">
        <div class="category-card photo" @click="filterByCategory('照片')">
          <div class="card-body">
            <i class="bi bi-image"></i>
            <h3 class="card-title">照片</h3>
            <p class="card-text">高清图片素材</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Search Results -->
    <div v-if="hasSearched">
      <!-- Results Header -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2>搜索结果 <small class="text-muted">({{ materialStore.totalCount }} 个)</small></h2>
        <div class="filter-buttons">
          <div class="btn-group" role="group">
            <button 
              v-for="category in categories" 
              :key="category.value"
              type="button" 
              class="btn" 
              :class="categoryFilter === category.value ? 'btn-primary' : 'btn-outline-primary'"
              @click="filterByCategory(category.value)"
            >
              {{ category.label }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- Loading Spinner -->
      <div v-if="materialStore.loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">加载中...</span>
        </div>
      </div>
      
      <!-- No Results Message -->
      <div v-else-if="materialStore.materials.length === 0" class="text-center py-5">
        <i class="bi bi-search fs-1 text-muted"></i>
        <h3 class="mt-3">未找到结果</h3>
        <p class="text-muted">尝试使用不同的关键词或清除筛选条件</p>
        <button class="btn btn-outline-primary" @click="clearFilters">
          清除筛选条件
        </button>
      </div>
      
      <!-- Material Cards -->
      <div v-else class="row">
        <div v-for="material in materialStore.materials" :key="material.id" class="col-md-6 col-lg-4 col-xl-3 mb-4">
          <MaterialCard :material="material" />
        </div>
        
        <!-- Pagination -->
        <div class="col-12 d-flex justify-content-center mt-4">
          <nav aria-label="Material pagination">
            <ul class="pagination">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)">上一页</a>
              </li>
              <li v-for="page in totalPages" :key="page" class="page-item" :class="{ active: page === currentPage }">
                <a class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
              </li>
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)">下一页</a>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useMaterialStore } from '@/stores/material';
import { useUserStore } from '@/stores/user';
import MaterialCard from '@/components/MaterialCard.vue';

const materialStore = useMaterialStore();
const userStore = useUserStore();

const searchQuery = ref('');
const categoryFilter = ref('');
const hasSearched = ref(false);
const currentPage = ref(1);
const itemsPerPage = 20;

const categories = [
  { label: '全部', value: '' },
  { label: 'AE模板', value: 'AE模板' },
  { label: '视频', value: '视频' },
  { label: '音乐', value: '音乐' },
  { label: '照片', value: '照片' }
];

const totalPages = computed(() => {
  return Math.ceil(materialStore.totalCount / itemsPerPage);
});

// Load materials on mount
onMounted(async () => {
  await fetchMaterials();
});

// Watch for category changes
watch(categoryFilter, async () => {
  if (hasSearched.value) {
    currentPage.value = 1;
    await fetchMaterials();
  }
});

async function search() {
  hasSearched.value = true;
  currentPage.value = 1;
  await fetchMaterials();
}

async function fetchMaterials() {
  const params = {
    query: searchQuery.value,
    category: categoryFilter.value,
    skip: (currentPage.value - 1) * itemsPerPage,
    limit: itemsPerPage
  };
  
  // 如果用户已登录且不是管理员，只显示自己的素材
  if (userStore.isLoggedIn && !userStore.isAdmin) {
    params.uploader_id = userStore.user.id;
  }
  
  await materialStore.fetchMaterials(params);
}

function filterByCategory(category) {
  categoryFilter.value = category;
  hasSearched.value = true;
  search();
}

function clearFilters() {
  searchQuery.value = '';
  categoryFilter.value = '';
  search();
}

function changePage(page) {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  fetchMaterials();
}
</script>

<style scoped>
.hero-section {
  background: linear-gradient(165deg, rgb(249, 249, 249), rgb(198, 198, 198));
  border-radius: 24px;
  padding: 4rem 2rem;
  position: relative;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(198, 198, 198, 0.15);
  color: #333;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(
    circle at center,
    rgba(255, 255, 255, 0.3) 0%,
    rgba(255, 255, 255, 0.15) 25%,
    transparent 50%
  );
  pointer-events: none;
  animation: subtle-rotate 30s linear infinite;
}

@keyframes subtle-rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  color: #333;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin-bottom: 1.5rem;
  position: relative;
  letter-spacing: -0.5px;
}

.hero-subtitle {
  color: #666;
  font-size: 1.25rem;
  font-weight: 400;
  margin-bottom: 2.5rem;
  position: relative;
  letter-spacing: 0.5px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

/* 修改搜索框样式以配合新的设计 */
.search-form {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(198, 198, 198, 0.3);
  border-radius: 16px;
  padding: 2rem;
  position: relative;
  z-index: 1;
}

.search-form .form-control,
.search-form .form-select {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(198, 198, 198, 0.3);
  color: #333;
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
}

.search-form .form-control::placeholder {
  color: rgba(51, 51, 51, 0.6);
}

.search-form .form-control:focus,
.search-form .form-select:focus {
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(198, 198, 198, 0.5);
  box-shadow: 0 0 0 0.25rem rgba(198, 198, 198, 0.1);
}

.search-btn {
  background: rgb(198, 198, 198) !important;
  color: #333 !important;
  border: none !important;
  font-weight: 600 !important;
  padding: 0.75rem 1.5rem !important;
}

.search-btn:hover {
  background: rgb(180, 180, 180) !important;
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.search-input-group {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon,
.select-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
  font-size: 1.2rem;
  z-index: 2;
}

.search-input-group .form-control {
  padding-left: 45px;
  background: rgba(255, 255, 255, 0.8) !important;
  color: #333;
  border: 1px solid rgba(198, 198, 198, 0.3);
}

.search-input-group .form-control::placeholder {
  color: rgba(51, 51, 51, 0.6);
}

.select-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.select-wrapper .form-select {
  padding-left: 45px;
  background: rgba(255, 255, 255, 0.8);
  color: #333;
  border: 1px solid rgba(198, 198, 198, 0.3);
  cursor: pointer;
}

.select-wrapper .form-select option {
  color: #333;
  background: white;
}

.category-card {
  cursor: pointer;
  border-radius: 15px;
  overflow: hidden;
  position: relative;
  height: 200px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  background-size: cover;
  background-position: center;
  color: white;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

.category-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.2), rgba(0, 0, 0, 0.7));
  z-index: 1;
}

.category-card .card-body {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  height: 100%;
  padding: 1.5rem;
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}

.category-card.ae-template {
  background-image: url('/backgrounds/ae.jpg');
}

.category-card.video {
  background-image: url('/backgrounds/video.jpg');
}

.category-card.music {
  background-image: url('/backgrounds/music.jpg');
}

.category-card.photo {
  background-image: url('/backgrounds/photo.jpg');
}

.category-card h5 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.category-card p {
  margin-bottom: 0;
  opacity: 0.9;
}
</style> 
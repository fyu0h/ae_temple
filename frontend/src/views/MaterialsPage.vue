<template>
  <div class="container py-4">
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
          <h1 class="h2 mb-0">{{ userStore.isAdmin ? '所有素材管理' : '我的素材管理' }}</h1>
          
          <router-link to="/upload" class="btn btn-primary">
            <i class="bi bi-plus-lg me-2"></i>上传新素材
          </router-link>
        </div>
      </div>
    </div>
    
    <!-- Filter Controls -->
    <div class="row mb-4">
      <div v-if="!userStore.isAdmin" class="col-md-4 mb-3 mb-md-0">
        <div class="input-group">
          <span class="input-group-text">
            <i class="bi bi-search"></i>
          </span>
          <input 
            type="text" 
            class="form-control" 
            placeholder="搜索我的素材..." 
            v-model="searchQuery"
            @keyup.enter="fetchUserMaterials"
          >
          <button 
            class="btn btn-outline-secondary" 
            type="button"
            @click="fetchUserMaterials"
          >
            搜索
          </button>
        </div>
      </div>
      
      <!-- 管理员可以查看所有用户的素材 -->
      <div v-if="userStore.isAdmin" class="col-md-4 mb-3 mb-md-0">
        <div class="input-group">
          <span class="input-group-text">
            <i class="bi bi-search"></i>
          </span>
          <input 
            type="text" 
            class="form-control" 
            placeholder="搜索所有素材..." 
            v-model="searchQuery"
            @keyup.enter="fetchUserMaterials"
          >
          <button 
            class="btn btn-outline-secondary" 
            type="button"
            @click="fetchUserMaterials"
          >
            搜索
          </button>
        </div>
      </div>
      
      <!-- 用户筛选，仅管理员可见 -->
      <div v-if="userStore.isAdmin" class="col-md-2 mb-3 mb-md-0">
        <select class="form-select" v-model="uploaderFilter" @change="fetchUserMaterials">
          <option :value="null">所有用户</option>
          <option :value="userStore.user?.id">我的素材</option>
          <!-- 显示所有其他用户 -->
          <template v-if="allUsers.length > 0">
            <option disabled>──────────</option>
            <option 
              v-for="user in allUsers.filter(u => u.id !== userStore.user?.id)" 
              :key="user.id" 
              :value="user.id"
            >
              {{ user.username }}
            </option>
          </template>
        </select>
      </div>
      
      <div class="col-md-2 mb-3 mb-md-0">
        <select class="form-select" v-model="categoryFilter" @change="fetchUserMaterials">
          <option value="">所有分类</option>
          <option value="AE模板">AE模板</option>
          <option value="视频">视频</option>
          <option value="音乐">音乐</option>
          <option value="照片">照片</option>
        </select>
      </div>
      
      <div class="col-md-2 mb-3 mb-md-0">
        <select class="form-select" v-model="sortOrder" @change="fetchUserMaterials">
          <option value="newest">最新上传</option>
          <option value="oldest">最早上传</option>
          <option value="az">按名称 A-Z</option>
          <option value="za">按名称 Z-A</option>
        </select>
      </div>
      
      <div class="col-md-2 d-flex justify-content-end">
        <button 
          class="btn btn-outline-secondary w-100" 
          @click="resetFilters"
        >
          <i class="bi bi-arrow-clockwise me-2"></i>重置
        </button>
      </div>
    </div>
    
    <!-- Materials Table -->
    <div class="card shadow-sm">
      <div class="card-body">
        <div v-if="materialStore.loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">加载中...</span>
          </div>
        </div>
        
        <div v-else-if="materialStore.materials.length === 0" class="text-center py-5">
          <i class="bi bi-inbox fs-1 text-muted"></i>
          <h3 class="mt-3">暂无素材</h3>
          <p class="text-muted">您还没有上传任何素材，或没有符合筛选条件的素材</p>
          <router-link to="/upload" class="btn btn-primary mt-2">
            <i class="bi bi-plus-lg me-2"></i>上传素材
          </router-link>
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th>标题</th>
                <th>分类</th>
                <th>上传者</th>
                <th>上传时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="material in materialStore.materials" :key="material.id">
                <!-- Title -->
                <td>
                  <router-link :to="`/materials/${material.id}`" class="text-decoration-none">
                    {{ material.title }}
                  </router-link>
                  <div v-if="material.tags && material.tags.length > 0" class="mt-1">
                    <span v-for="tag in material.tags.slice(0, 2)" :key="tag.id" class="badge bg-light text-dark me-1">
                      {{ tag.name }}
                    </span>
                    <span v-if="material.tags.length > 2" class="badge bg-light text-dark">
                      +{{ material.tags.length - 2 }}
                    </span>
                  </div>
                </td>
                
                <!-- Category -->
                <td>
                  <span class="badge" :class="getCategoryClass(material.category)">
                    <i class="bi me-1" :class="getCategoryIcon(material.category)"></i>
                    {{ material.category }}
                  </span>
                </td>
                
                <!-- Uploader -->
                <td>
                  <small class="d-flex align-items-center">
                    <i class="bi bi-person-circle me-1"></i>
                    {{ material.uploader?.username }}
                    <span v-if="material.uploader?.id === userStore.user?.id" class="badge bg-success ms-1">你</span>
                  </small>
                </td>
                
                <!-- Date -->
                <td>{{ formatDate(material.created_at) }}</td>
                
                <!-- Actions -->
                <td>
                  <div class="btn-group">
                    <router-link :to="`/materials/${material.id}`" class="btn btn-sm btn-action btn-view">
                      <i class="bi bi-eye"></i>
                    </router-link>
                    <button 
                      class="btn btn-sm btn-action btn-delete" 
                      @click="confirmDelete(material)"
                      v-if="userStore.isAdmin || material.uploader?.id === userStore.user?.id"
                      title="删除素材"
                    >
                      <i class="bi bi-trash"></i>
                    </button>
                    <button 
                      v-else
                      class="btn btn-sm btn-action btn-disabled" 
                      disabled
                      title="只能删除自己上传的素材"
                    >
                      <i class="bi bi-lock"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Pagination -->
        <div v-if="materialStore.totalCount > itemsPerPage" class="d-flex justify-content-center mt-4">
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
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useMaterialStore } from '@/stores/material';
import { useUserStore } from '@/stores/user';
import api from '@/services/api';

const router = useRouter();
const materialStore = useMaterialStore();
const userStore = useUserStore();

const searchQuery = ref('');
const categoryFilter = ref('');
const sortOrder = ref('newest');
const currentPage = ref(1);
const itemsPerPage = 10;
const uploaderFilter = ref(null);

const totalPages = computed(() => {
  return Math.ceil(materialStore.totalCount / itemsPerPage);
});

const allUsers = ref([]);

// Fetch user materials on mount
onMounted(async () => {
  if (!userStore.isLoggedIn) {
    router.push('/login?redirect=/materials');
    return;
  }
  
  if (userStore.isAdmin) {
    await fetchAllUsers();
  }
  
  fetchUserMaterials();
});

// Fetch materials with filters
async function fetchUserMaterials() {
  const params = {
    query: searchQuery.value,
    category: categoryFilter.value,
    skip: (currentPage.value - 1) * itemsPerPage,
    limit: itemsPerPage
  };
  
  // 如果是管理员且选择了上传者筛选
  if (userStore.isAdmin && uploaderFilter.value !== null) {
    params.uploader_id = uploaderFilter.value;
  }
  
  await materialStore.fetchMaterials(params);
}

// Reset filters
function resetFilters() {
  searchQuery.value = '';
  categoryFilter.value = '';
  sortOrder.value = 'newest';
  uploaderFilter.value = null;
  currentPage.value = 1;
  fetchUserMaterials();
}

// Change page
function changePage(page) {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  fetchUserMaterials();
}

// Format date
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN');
}

// Get category-specific class
function getCategoryClass(category) {
  switch (category) {
    case 'AE模板': return 'bg-primary';
    case '视频': return 'bg-danger';
    case '音乐': return 'bg-success';
    case '照片': return 'bg-info';
    default: return 'bg-secondary';
  }
}

// Get category-specific icon
function getCategoryIcon(category) {
  switch (category) {
    case 'AE模板': return 'bi-file-earmark-zip';
    case '视频': return 'bi-film';
    case '音乐': return 'bi-music-note-beamed';
    case '照片': return 'bi-image';
    default: return 'bi-file-earmark';
  }
}

// Confirm and delete material
function confirmDelete(material) {
  // 检查权限：只有上传者本人或管理员可以删除
  if (!userStore.isAdmin && material.uploader?.id !== userStore.user?.id) {
    alert('没有权限：您只能删除自己上传的素材');
    return;
  }
  
  if (confirm(`确定要删除素材"${material.title}"吗？此操作不可撤销。`)) {
    deleteMaterial(material.id);
  }
}

// Delete material
async function deleteMaterial(id) {
  try {
    await materialStore.deleteMaterial(id);
    fetchUserMaterials();
  } catch (error) {
    console.error('Delete error:', error);
    alert('删除失败');
  }
}

// 管理员模式下获取所有用户列表
async function fetchAllUsers() {
  if (userStore.isAdmin) {
    try {
      allUsers.value = await api.getAllUsers();
      console.log('已获取所有用户:', allUsers.value.length);
    } catch (error) {
      console.error('获取用户列表失败:', error);
    }
  }
}
</script>

<style scoped>
.material-preview {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 4px;
  background-color: #f8f9fa;
}

.material-preview img {
  width: 60px;
  height: 60px;
  object-fit: cover;
}

.preview-icon {
  font-size: 1.8rem;
}

.badge {
  padding: 6px 10px;
}

.input-group {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  overflow: hidden;
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.input-group-text, 
.input-group .form-control, 
.input-group .btn {
  border: none;
  background: rgba(255, 255, 255, 0.75);
  padding: 12px 15px;
}

.input-group-text {
  background: rgba(240, 242, 245, 0.75);
}

.input-group .form-control:focus {
  box-shadow: none;
  background: rgba(255, 255, 255, 0.9);
}

.input-group .btn-outline-secondary {
  color: #5a5a5a;
  background: linear-gradient(45deg, #f0f2f5, #e2e6ea);
  transition: all 0.3s ease;
}

.input-group .btn-outline-secondary:hover {
  background: #e2e6ea;
  color: #212529;
  transform: translateY(-2px);
}

.form-select {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: none;
  background-color: rgba(255, 255, 255, 0.75);
  padding: 12px 15px;
  border-radius: 10px;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.form-select:focus {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  background-color: rgba(255, 255, 255, 0.9);
  transform: translateY(-2px);
}

.btn-outline-secondary {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: none;
  background: linear-gradient(45deg, #f0f2f5, #e2e6ea);
  transition: all 0.3s ease;
  border-radius: 10px;
  padding: 12px 15px;
}

.btn-outline-secondary:hover {
  background: #e2e6ea;
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

/* 添加标题美化 */
h1.h2 {
  font-weight: 600;
  position: relative;
  display: inline-block;
  margin-bottom: 1rem;
}

h1.h2:after {
  content: "";
  position: absolute;
  left: 0;
  bottom: -8px;
  height: 3px;
  width: 50px;
  background: linear-gradient(45deg, #4568dc, #b06ab3);
  border-radius: 3px;
}

/* 表格容器美化 */
.card.shadow-sm {
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  overflow: hidden;
}

.table {
  margin-bottom: 0;
}

.table th {
  background-color: rgba(245, 247, 250, 0.5);
  border-top: none;
  font-weight: 600;
  color: #5a5a5a;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.5px;
  padding: 15px 10px;
}

.table td {
  vertical-align: middle;
  padding: 15px 10px;
}

.table tr:hover {
  background-color: rgba(240, 242, 245, 0.5);
}

/* 分页美化 */
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
  color: white;
}

.btn-action {
  background: rgba(108, 117, 125, 0.15) !important;
  color: #6c757d !important;
  border: 1px solid rgba(108, 117, 125, 0.2) !important;
  padding: 6px 12px;
  margin: 0 2px;
  border-radius: 6px;
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

.btn-action.btn-view {
  background: rgba(37, 99, 235, 0.15) !important;
  color: #2563eb !important;
  border-color: rgba(37, 99, 235, 0.2) !important;
}

.btn-action.btn-view:hover {
  background: rgba(37, 99, 235, 0.25) !important;
  border-color: rgba(37, 99, 235, 0.3) !important;
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

.btn-action.btn-disabled {
  background: rgba(108, 117, 125, 0.1) !important;
  color: #6c757d !important;
  border-color: rgba(108, 117, 125, 0.15) !important;
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-action i {
  font-size: 1rem;
}
</style> 
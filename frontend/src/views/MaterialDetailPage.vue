<template>
  <div class="container py-4">
    <!-- Loading Spinner -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">加载中...</span>
      </div>
    </div>
    
    <!-- Error Message -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
    </div>
    
    <!-- Debug Info (只在开发环境显示) -->
    <div v-if="isDev && material" class="mb-3 p-3 border rounded bg-light">
      <h6>调试信息</h6>
      <p class="mb-1"><strong>素材ID:</strong> {{ material.id }}</p>
      <p class="mb-1"><strong>类型:</strong> {{ material.category }}</p>
      <p class="mb-1"><strong>文件路径:</strong> {{ material.file_path }}</p>
      <p class="mb-1"><strong>预览路径:</strong> {{ material.preview_path }}</p>
      <p class="mb-1"><strong>预览图片路径:</strong> {{ material.preview_image_path }}</p>
    </div>
    
    <!-- Material Detail -->
    <div v-else-if="material" class="material-detail">
      <div class="row">
        <!-- Breadcrumbs -->
        <div class="col-12 mb-3">
          <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
              <li class="breadcrumb-item"><router-link to="/">首页</router-link></li>
              <li class="breadcrumb-item">
                <router-link :to="`/?category=${material.category}`">
                  {{ material.category }}
                </router-link>
              </li>
              <li class="breadcrumb-item active" aria-current="page">{{ material.title }}</li>
            </ol>
          </nav>
        </div>
        
        <!-- Main Content -->
        <div class="col-md-8">
          <!-- Preview Content -->
          <div class="card mb-4">
            <div class="card-body p-0">
              <!-- AE模板预览 -->
              <template v-if="material.category === 'AE模板'">
                <!-- 如果有预览视频，显示视频播放器 -->
                <video 
                  v-if="material.preview_path" 
                  class="w-100" 
                  controls 
                  :src="getMediaUrl(material.preview_path)"
                ></video>
                
                <!-- 如果没有预览 -->
                <div v-else class="placeholder-preview d-flex align-items-center justify-content-center bg-light p-5">
                  <div class="text-center">
                    <i class="bi bi-file-earmark-zip fs-1 text-primary"></i>
                    <p class="mt-3">AE模板 - 无预览视频</p>
                  </div>
                </div>
              </template>
              
              <!-- 视频预览 -->
              <template v-else-if="material.category === '视频'">
                <div class="video-container position-relative">
                  <!-- 视频预览图 -->
                  <img 
                    v-if="material.preview_path && !isPlaying" 
                    :src="getMediaUrl(material.preview_path)"
                    class="w-100 rounded cursor-pointer" 
                    alt="视频预览" 
                    @click="isPlaying = true"
                  />
                  
                  <!-- 视频播放按钮 -->
                  <div 
                    v-if="!isPlaying && material.preview_path" 
                    class="play-overlay position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center"
                    @click="isPlaying = true"
                  >
                    <div class="play-button bg-primary bg-opacity-75 rounded-circle p-3 text-white">
                      <i class="bi bi-play-fill fs-1"></i>
                    </div>
                  </div>
                  
                  <!-- 视频播放器 -->
                  <video 
                    v-if="isPlaying || !material.preview_path"
                    class="w-100" 
                    controls 
                    :src="getMediaUrl(material.file_path)"
                    autoplay
                  ></video>
                </div>
              </template>
              
              <!-- 音乐预览 -->
              <template v-else-if="material.category === '音乐'">
                <div class="audio-player p-4 bg-light">
                  <div class="text-center mb-3">
                    <img 
                      v-if="material.preview_path" 
                      :src="getMediaUrl(material.preview_path)" 
                      class="img-fluid rounded audio-cover" 
                      alt="音乐封面"
                    >
                    <i v-else class="bi bi-music-note-beamed display-1 text-success"></i>
                  </div>
                  <audio 
                    class="w-100 mt-3" 
                    controls 
                    :src="getMediaUrl(material.file_path)"
                  ></audio>
                </div>
              </template>
              
              <!-- 照片预览 -->
              <template v-else-if="material.category === '照片'">
                <div v-if="!material.file_path && materialStore.thumbnails.length === 0" class="text-center p-5 bg-light">
                  <i class="bi bi-image fs-1 text-info"></i>
                  <p class="mt-3">照片 - 无预览图</p>
                </div>
                <div v-else class="photo-preview">
                  <div class="photo-container">
                    <div 
                      v-for="(thumb, index) in materialStore.thumbnails" 
                      :key="thumb.id"
                      class="photo-item"
                    >
                      <a :href="getMediaUrl(thumb.original_url)" target="_blank">
                        <img 
                          :src="getMediaUrl(thumb.thumb_url)" 
                          class="img-fluid" 
                          alt="缩略图"
                          @error="handleImageError($event, thumb)"
                        >
                      </a>
                    </div>
                  </div>
                </div>
              </template>
              
              <!-- 其他类型预览 -->
              <template v-else>
                <div class="placeholder-preview d-flex align-items-center justify-content-center bg-light p-5">
                  <div class="text-center">
                    <i class="bi bi-file-earmark fs-1 text-secondary"></i>
                    <p class="mt-3">暂无预览</p>
                  </div>
                </div>
              </template>
            </div>
          </div>
          
          <!-- Download & Actions -->
          <div class="card mb-4">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center">
                <h1 class="h3 card-title">{{ material.title }}</h1>
                
                <div class="btn-group" v-if="canEditMaterial">
                  <button class="btn btn-outline-primary" @click="showEditModal = true">
                    <i class="bi bi-pencil-square me-2"></i>编辑
                  </button>
                  <button class="btn btn-outline-danger" @click="confirmDelete">
                    <i class="bi bi-trash me-2"></i>删除
                  </button>
                </div>
              </div>
              
              <hr>
              
              <div v-if="material.original_link" class="mb-3">
                <a :href="material.original_link" target="_blank" class="btn btn-success w-100">
                  <i class="bi bi-download me-2"></i>下载素材
                </a>
              </div>
              
              <div class="mb-3">
                <a :href="getMediaUrl(material.file_path)" target="_blank" class="btn btn-primary w-100">
                  <i class="bi bi-file-earmark-arrow-down me-2"></i>查看原始文件
                </a>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Sidebar -->
        <div class="col-md-4">
          <!-- Material Info -->
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">素材信息</h5>
            </div>
            <div class="card-body">
              <table class="table table-bordered">
                <tbody>
                  <tr>
                    <th>分类</th>
                    <td>
                      <span class="badge" :class="getCategoryClass(material.category)">
                        <i class="bi me-1" :class="getCategoryIcon(material.category)"></i>
                        {{ material.category }}
                      </span>
                    </td>
                  </tr>
                  <tr v-if="material.resolution">
                    <th>分辨率</th>
                    <td>{{ material.resolution }}</td>
                  </tr>
                  <tr>
                    <th>素材源链接</th>
                    <td>
                      <a v-if="material.source_link" :href="material.source_link" target="_blank" 
                         class="btn btn-sm btn-outline-primary">
                        <i class="bi bi-link-45deg me-1"></i>查看源网站
                      </a>
                      <span v-else class="text-muted">无</span>
                    </td>
                  </tr>
                  <tr>
                    <th>上传时间</th>
                    <td>{{ formatDate(material.created_at) }}</td>
                  </tr>
                  <tr>
                    <th>上传者</th>
                    <td>{{ material.uploader.username }}</td>
                  </tr>
                </tbody>
              </table>
              
              <!-- Tags -->
              <div class="mt-3">
                <h6>标签</h6>
                <div class="tags">
                  <span v-for="tag in material.tags" :key="tag.id" class="tag me-2 mb-2">
                    {{ tag.name }}
                  </span>
                  <span v-if="material.tags.length === 0" class="text-muted">暂无标签</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Related Materials -->
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">相关素材</h5>
            </div>
            <div class="card-body">
              <p class="text-muted">
                <i class="bi bi-info-circle me-2"></i>
                更多{{ material.category }}素材
              </p>
              
              <router-link :to="`/?category=${material.category}`" class="btn btn-outline-primary w-100">
                <i class="bi bi-grid me-2"></i>浏览更多{{ material.category }}
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Not Found -->
    <div v-else-if="!isLoading && !error" class="text-center py-5">
      <i class="bi bi-exclamation-triangle fs-1 text-warning"></i>
      <h2 class="mt-3">素材不存在</h2>
      <p class="text-muted">您查找的素材不存在或已被删除</p>
      <router-link to="/" class="btn btn-primary mt-3">
        <i class="bi bi-house me-2"></i>返回首页
      </router-link>
    </div>
    
    <!-- Edit Modal -->
    <div v-if="showEditModal" class="modal fade show" style="display: block;" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">编辑素材</h5>
            <button type="button" class="btn-close" @click="showEditModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateMaterial">
              <div class="mb-3">
                <label for="editTitle" class="form-label">素材名称</label>
                <input type="text" class="form-control" id="editTitle" v-model="editForm.title" required>
              </div>
              
              <div class="mb-3">
                <label for="editTags" class="form-label">标签</label>
                <input type="text" class="form-control" id="editTags" v-model="editForm.tags" placeholder="标签1,标签2,标签3">
                <small class="text-muted">多个标签请用逗号分隔</small>
              </div>
              
              <div class="mb-3">
                <label for="editOriginalLink" class="form-label">外部下载链接</label>
                <input type="url" class="form-control" id="editOriginalLink" v-model="editForm.originalLink">
              </div>
              
              <div class="mb-3">
                <label for="editSourceLink" class="form-label">素材源链接</label>
                <input type="url" class="form-control" id="editSourceLink" v-model="editForm.sourceLink">
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showEditModal = false">取消</button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="updateMaterial"
              :disabled="isUpdating"
            >
              <span v-if="isUpdating">
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                保存中...
              </span>
              <span v-else>保存更改</span>
            </button>
          </div>
        </div>
      </div>
      <div class="modal-backdrop fade show"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useMaterialStore } from '@/stores/material';
import { useUserStore } from '@/stores/user';

const route = useRoute();
const router = useRouter();
const materialStore = useMaterialStore();
const userStore = useUserStore();

const material = ref(null);
const isLoading = ref(true);
const error = ref(null);
const showEditModal = ref(false);
const isPlaying = ref(false);
const isUpdating = ref(false);

const editForm = reactive({
  title: '',
  tags: '',
  originalLink: '',
  sourceLink: ''
});

// 获取媒体文件的完整URL
function getMediaUrl(path) {
  if (!path) return '';
  
  // 如果已经是完整URL，直接返回
  if (path.startsWith('http')) return path;
  
  // 获取基础URL，例如 "http://localhost:5173"
  const baseUrl = window.location.origin;
  
  // 处理照片类型的特殊路径
  if (material.value && material.value.category === '照片') {
    // 检查是否是原始图片URL格式 (例如 /api/v1/materials/{id}/image/{filename})
    if (path.includes('/api/v1/materials/') && path.includes('/image/')) {
      // 这个API路径不需要修改，直接返回完整API URL
      return `${baseUrl}${path}`;
    }
    
    // 其他照片路径处理
    // 确保路径正确处理所有目录层级
    if (path.includes('/')) {
      // 保留完整相对路径
      return `${baseUrl}/media/${path}`;
    } else {
      // 只有文件名的情况
      const filename = path;
      return `${baseUrl}/media/照片/${filename}`;
    }
  }
  
  // 处理路径中的特殊情况
  // 去掉路径中可能存在的 /api/v1 前缀
  if (path.startsWith('/api/v1/')) {
    path = path.substring(8);
  } else if (path.startsWith('/api/v1')) {
    path = path.substring(7);
  }
  
  // 去掉路径中可能存在的 /media/ 前缀
  if (path.startsWith('/media/')) {
    path = path.substring(7);
  } else if (path.startsWith('media/')) {
    path = path.substring(6);
  }
  
  // 去掉路径开头的所有斜杠
  path = path.replace(/^\/+/, '');
  
  // 组合完整URL
  return `${baseUrl}/media/${path}`;
}

// Check if current user can edit this material
const canEditMaterial = computed(() => {
  if (!userStore.isLoggedIn) return false;
  if (!material.value) return false;
  if (userStore.isAdmin) return true;
  
  console.log('权限检查:', {
    '当前用户ID': userStore.user.id,
    '素材上传者ID': material.value.uploader?.id,
    '是否匹配': userStore.user.id === material.value.uploader?.id
  });
  
  return userStore.user.id === material.value.uploader?.id;
});

// Load material on mount and when route changes
watch(() => route.params.id, fetchMaterial, { immediate: true });

async function fetchMaterial() {
  isLoading.value = true;
  error.value = null;
  
  try {
    const materialId = parseInt(route.params.id);
    if (isNaN(materialId)) {
      error.value = "无效的素材ID";
      return;
    }
    
    // 清除上一次的数据
    material.value = null;
    materialStore.thumbnails = [];
    
    // 获取素材详情
    await materialStore.fetchMaterial(materialId);
    
    // 更新本地引用
    material.value = materialStore.currentMaterial;
    
    if (!material.value) {
      error.value = "未找到素材";
      return;
    }
    
    console.log("素材详情:", material.value);
    
    // If it's a photo material, fetch thumbnails
    if (material.value.category === '照片') {
      await materialStore.fetchThumbnails(materialId);
      console.log("照片缩略图:", materialStore.thumbnails);
    }
    
    // Initialize edit form with current values
    if (material.value) {
      editForm.title = material.value.title;
      editForm.tags = material.value.tags.map(tag => tag.name).join(',');
      editForm.originalLink = material.value.original_link || '';
      editForm.sourceLink = material.value.source_link || '';
      
      // 打印权限信息用于调试
      if(userStore.isLoggedIn) {
        console.log('素材详情页权限:', {
          '素材ID': material.value.id,
          '素材标题': material.value.title, 
          '素材类别': material.value.category,
          '素材文件路径': material.value.file_path,
          '素材预览路径': material.value.preview_path,
          '素材上传者ID': material.value.uploader?.id,
          '当前用户ID': userStore.user?.id,
          '是否管理员': userStore.isAdmin,
          '可以编辑': canEditMaterial.value
        });
      }
    }
  } catch (error) {
    console.error("获取素材详情出错:", error);
    error.value = "加载素材详情失败";
  } finally {
    isLoading.value = false;
  }
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

// Update material
async function updateMaterial() {
  if (!editForm.title) {
    alert('素材名称不能为空');
    return;
  }
  
  isUpdating.value = true;
  
  try {
    const updateData = {
      title: editForm.title,
      tags: editForm.tags ? editForm.tags.split(',').map(tag => tag.trim()) : [],
      original_link: editForm.originalLink || undefined,
      source_link: editForm.sourceLink || undefined
    };
    
    await materialStore.updateMaterial(material.value.id, updateData);
    showEditModal.value = false;
  } catch (error) {
    console.error('Update error:', error);
    alert('更新失败');
  } finally {
    isUpdating.value = false;
  }
}

// Confirm and delete material
function confirmDelete() {
  if (confirm(`确定要删除素材"${material.value.title}"吗？此操作不可撤销。`)) {
    deleteMaterial();
  }
}

// Delete material
async function deleteMaterial() {
  try {
    const result = await materialStore.deleteMaterial(material.value.id);
    if (result) {
      router.push('/');
    } else {
      throw new Error(materialStore.error || '删除失败');
    }
  } catch (error) {
    console.error('Delete error:', error);
    alert('删除失败');
  }
}

// Handle image error
function handleImageError(event, thumb) {
  console.error('图片加载失败:', {
    thumb_url: thumb.thumb_url,
    original_url: thumb.original_url,
    processed_thumb_url: getMediaUrl(thumb.thumb_url),
    processed_original_url: getMediaUrl(thumb.original_url)
  });
  
  // 尝试使用原始图片代替缩略图
  event.target.src = getMediaUrl(thumb.original_url);
  
  // 添加错误处理，如果原始图片也加载失败
  event.target.onerror = () => {
    console.error('原始图片也加载失败:', thumb.original_url);
    // 使用默认图片代替
    event.target.src = '/placeholder.jpg';
    event.target.onerror = null; // 防止循环错误
  };
}
</script>

<style scoped>
.audio-cover {
  max-width: 300px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.photo-preview {
  width: 100%;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.photo-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 15px;
}

.photo-item {
  position: relative;
  overflow: hidden;
  border-radius: 4px;
  background-color: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  width: calc(33.333% - 7px);
  margin-bottom: 10px;
}

.photo-item a {
  display: block;
  width: 100%;
  height: 100%;
}

.photo-item img {
  width: 100%;
  height: auto;
  object-fit: contain;
  display: block;
}

@media (max-width: 768px) {
  .photo-item {
    width: calc(50% - 5px);
  }
}

@media (max-width: 576px) {
  .photo-item {
    width: 100%;
  }
}

.badge {
  padding: 6px 10px;
}

.video-container {
  position: relative;
  overflow: hidden;
  background-color: #000;
  border-radius: 8px;
}

.play-overlay {
  cursor: pointer;
  background: rgba(0, 0, 0, 0.3);
  transition: all 0.2s ease;
}

.play-overlay:hover {
  background: rgba(0, 0, 0, 0.5);
}

.play-button {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease;
}

.play-overlay:hover .play-button {
  transform: scale(1.1);
}

.cursor-pointer {
  cursor: pointer;
}
</style> 
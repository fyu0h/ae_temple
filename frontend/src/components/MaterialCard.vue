<template>
  <router-link :to="`/materials/${material.id}`" class="text-decoration-none">
    <div class="card material-card shadow-sm h-100">
      <!-- Preview Image or Video -->
      <div class="card-img-container">
        <!-- AE模板 -->
        <template v-if="material.category === 'AE模板'">
          <div class="video-container" @mouseover="playAEVideo" @mouseleave="pauseAEVideo">
            <img 
              v-if="material.preview_image_path && !isAEVideoPlaying" 
              :src="`/media/${material.preview_image_path}`" 
              class="card-img-top" 
              alt="AE模板预览"
            >
            <video 
              v-if="material.preview_path" 
              class="card-img-top" 
              :src="`/media/${material.preview_path}`" 
              ref="aeVideoEl"
              muted
              :class="{'playing': isAEVideoPlaying}"
            ></video>
            <div v-if="!material.preview_path && !material.preview_image_path" class="placeholder-img bg-light d-flex align-items-center justify-content-center">
              <i class="bi bi-file-earmark-zip fs-1 text-primary"></i>
            </div>
            <div class="video-overlay" v-if="!isAEVideoPlaying && material.preview_path">
              <i class="bi bi-play-circle fs-3"></i>
            </div>
          </div>
        </template>
        
        <!-- 视频 -->
        <template v-else-if="material.category === '视频'">
          <div class="video-container" @mouseover="playVideo" @mouseleave="pauseVideo">
            <img 
              v-if="material.preview_path && !isVideoPlaying" 
              :src="`/media/${material.preview_path}`" 
              class="card-img-top" 
              alt="视频预览"
            >
            <video 
              class="card-img-top" 
              :src="`/media/${material.file_path}`" 
              ref="videoEl"
              muted
              :class="{'playing': isVideoPlaying}"
            ></video>
            <div class="video-overlay" v-if="!isVideoPlaying">
              <i class="bi bi-play-circle fs-3"></i>
            </div>
          </div>
        </template>
        
        <!-- 音乐 -->
        <template v-else-if="material.category === '音乐'">
          <img 
            v-if="material.preview_path" 
            :src="`/media/${material.preview_path}`" 
            class="card-img-top" 
            alt="音乐封面"
          >
          <div v-else class="placeholder-img bg-light d-flex align-items-center justify-content-center">
            <i class="bi bi-music-note-beamed fs-1 text-success"></i>
          </div>
          
          <div class="audio-controls">
            <audio :src="`/media/${material.file_path}`" ref="audioEl"></audio>
            <button class="btn btn-sm btn-light rounded-circle" @click.prevent="toggleAudio">
              <i class="bi" :class="isPlaying ? 'bi-pause-fill' : 'bi-play-fill'"></i>
            </button>
          </div>
        </template>
        
        <!-- 照片 -->
        <template v-else-if="material.category === '照片'">
          <img 
            :src="getMediaUrl(material.file_path)" 
            class="card-img-top" 
            alt="原始图片"
            @error="handleImageError"
          >
          <div v-if="material.thumbnails && material.thumbnails.length > 1" class="thumbnail-counter">
            <i class="bi bi-images me-1"></i>{{ material.thumbnails.length }}
          </div>
        </template>
        
        <!-- Fallback for other categories -->
        <div v-else class="placeholder-img bg-light d-flex align-items-center justify-content-center">
          <i class="bi bi-file-earmark fs-1 text-secondary"></i>
        </div>
        
        <!-- Category Badge -->
        <div class="category-badge" :class="getCategoryClass(material.category)">
          <i class="bi" :class="getCategoryIcon(material.category)"></i>
          {{ material.category }}
        </div>
      </div>
      
      <!-- Card Body -->
      <div class="card-body">
        <h5 class="card-title text-truncate">{{ material.title }}</h5>
        
        <!-- Additional info like resolution -->
        <p v-if="material.resolution" class="card-text small text-muted mb-2">
          <i class="bi bi-aspect-ratio me-1"></i>{{ material.resolution }}
        </p>
        
        <!-- Tags -->
        <div class="tags mt-2" v-if="material.tags && material.tags.length > 0">
          <span v-for="tag in material.tags.slice(0, 3)" :key="tag.id" class="tag">
            {{ tag.name }}
          </span>
          <span v-if="material.tags.length > 3" class="tag">+{{ material.tags.length - 3 }}</span>
        </div>
      </div>
      
      <!-- Card Footer -->
      <div class="card-footer bg-white border-top-0">
        <div class="d-flex justify-content-between align-items-center">
          <small class="text-muted">{{ formatDate(material.created_at) }}</small>
          
          <small class="text-muted">
            <i class="bi bi-person-circle me-1"></i>{{ material.uploader?.username }}
          </small>
        </div>
      </div>
    </div>
  </router-link>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';

const props = defineProps({
  material: {
    type: Object,
    required: true
  }
});

const videoEl = ref(null);
const aeVideoEl = ref(null);
const audioEl = ref(null);
const isPlaying = ref(false);
const isVideoPlaying = ref(false);
const isAEVideoPlaying = ref(false);

// 获取媒体文件的完整URL
function getMediaUrl(path) {
  if (!path) return '';
  
  // 如果已经是完整URL，直接返回
  if (path.startsWith('http')) return path;
  
  // 获取基础URL，例如 "http://localhost:5173"
  const baseUrl = window.location.origin;
  
  // 处理照片类型的特殊路径
  if (props.material && props.material.category === '照片') {
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

// 处理图片加载错误
function handleImageError(event) {
  console.error('照片加载失败:', props.material.file_path);
  // 使用默认图片代替
  event.target.src = '/placeholder.jpg';
}

// Format date
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN');
}

// Play video on hover
function playVideo() {
  if (videoEl.value) {
    videoEl.value.play()
      .then(() => {
        isVideoPlaying.value = true;
      })
      .catch(err => console.error('Video play error:', err));
  }
}

// Pause video when not hovering
function pauseVideo() {
  if (videoEl.value) {
    videoEl.value.pause();
    isVideoPlaying.value = false;
  }
}

// Play AE preview video on hover
function playAEVideo() {
  if (aeVideoEl.value) {
    aeVideoEl.value.play()
      .then(() => {
        isAEVideoPlaying.value = true;
      })
      .catch(err => console.error('AE video play error:', err));
  }
}

// Pause AE preview video when not hovering
function pauseAEVideo() {
  if (aeVideoEl.value) {
    aeVideoEl.value.pause();
    isAEVideoPlaying.value = false;
  }
}

// Toggle audio play/pause
function toggleAudio(event) {
  event.stopPropagation();
  
  if (audioEl.value) {
    if (isPlaying.value) {
      audioEl.value.pause();
      isPlaying.value = false;
    } else {
      // Pause all other audio elements first
      document.querySelectorAll('audio').forEach(audio => {
        if (audio !== audioEl.value) {
          audio.pause();
        }
      });
      
      audioEl.value.play()
        .then(() => {
          isPlaying.value = true;
        })
        .catch(err => console.error('Audio play error:', err));
    }
  }
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

// Pause media when component is unmounted
onBeforeUnmount(() => {
  if (videoEl.value) {
    videoEl.value.pause();
  }
  
  if (aeVideoEl.value) {
    aeVideoEl.value.pause();
  }
  
  if (audioEl.value) {
    audioEl.value.pause();
  }
});
</script>

<style scoped>
.material-card {
  overflow: hidden;
  transition: all 0.3s ease;
}

.card-img-container {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.card-img-top, .placeholder-img {
  width: 100%;
  height: 180px;
  object-fit: cover;
}

video.card-img-top {
  z-index: 1;
}

.video-container {
  position: relative;
  height: 100%;
  overflow: hidden;
}

.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.2);
  z-index: 2;
  color: white;
  transition: all 0.3s ease;
}

.video-overlay i {
  opacity: 0.8;
  font-size: 3rem;
}

.video-container:hover .video-overlay {
  background-color: rgba(0, 0, 0, 0.1);
}

video.playing {
  z-index: 3;
}

.category-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 0.8rem;
  color: white;
  z-index: 3;
}

.audio-controls {
  position: absolute;
  bottom: 10px;
  right: 10px;
  z-index: 3;
}

.thumbnail-counter {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 3px 8px;
  border-radius: 20px;
  font-size: 0.8rem;
  z-index: 3;
}

.tag {
  display: inline-block;
  padding: 2px 8px;
  background-color: #f0f0f0;
  border-radius: 20px;
  font-size: 0.75rem;
  margin-right: 5px;
  color: #555;
}
</style> 
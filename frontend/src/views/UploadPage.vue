<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-lg-8">
        <div class="card shadow">
          <div class="card-header bg-primary text-white">
            <h1 class="h4 mb-0">上传素材</h1>
          </div>
          
          <div class="card-body">
            <form @submit.prevent="uploadMaterial">
              <!-- Common Fields -->
              <div class="mb-3">
                <label for="category" class="form-label">素材分类</label>
                <select 
                  id="category" 
                  class="form-select" 
                  v-model="formData.category" 
                  @change="onCategoryChange"
                >
                  <option value="" disabled>请选择分类</option>
                  <option value="AE模板">AE模板</option>
                  <option value="视频">视频</option>
                  <option value="音乐">音乐</option>
                  <option value="照片">照片</option>
                </select>
              </div>
              
              <div class="mb-3">
                <label for="title" class="form-label">素材名称 <span class="text-danger">*</span></label>
                <input 
                  type="text" 
                  id="title" 
                  class="form-control" 
                  v-model="formData.title" 
                  placeholder="输入素材名称"
                  required
                >
              </div>
              
              <div class="mb-3">
                <label for="tags" class="form-label">标签</label>
                <input 
                  type="text" 
                  id="tags" 
                  class="form-control" 
                  v-model="formData.tags" 
                  placeholder="输入标签，用逗号分隔"
                >
                <small class="text-muted">多个标签请用逗号分隔，如：标签1,标签2,标签3</small>
              </div>
              
              <div class="mb-3">
                <label for="originalLink" class="form-label">外部下载链接</label>
                <input 
                  type="url" 
                  id="originalLink" 
                  class="form-control" 
                  v-model="formData.originalLink" 
                  placeholder="输入素材外部下载链接"
                >
              </div>
              
              <div class="mb-3">
                <label for="sourceLink" class="form-label">素材源链接</label>
                <input 
                  type="url" 
                  id="sourceLink" 
                  class="form-control" 
                  v-model="formData.sourceLink" 
                  placeholder="输入素材的来源链接"
                >
                <small class="text-muted">素材的原始来源地址</small>
              </div>
              
              <hr class="my-4">
              
              <!-- AE模板 -->
              <div v-if="formData.category === 'AE模板'">
                <h5 class="mb-3">AE模板文件</h5>
                
                <div class="mb-3">
                  <label for="aeFile" class="form-label">模板文件</label>
                  <input 
                    type="file" 
                    id="aeFile" 
                    class="form-control" 
                    @change="handleFileChange"
                    accept=".zip,.rar"
                  >
                  <small class="text-muted">只支持 .zip, .rar 格式的压缩文件</small>
                </div>
                
                <div class="mb-3">
                  <label for="previewVideo" class="form-label">预览视频</label>
                  <input 
                    type="file" 
                    id="previewVideo" 
                    class="form-control" 
                    @change="handlePreviewChange"
                    accept="video/*"
                  >
                  <small class="text-muted">上传模板效果预览视频，支持常见视频格式</small>
                </div>
              </div>
              
              <!-- 视频 -->
              <div v-else-if="formData.category === '视频'">
                <h5 class="mb-3">视频文件</h5>
                
                <div class="mb-3">
                  <label for="videoFile" class="form-label">视频文件</label>
                  <input 
                    type="file" 
                    id="videoFile" 
                    class="form-control" 
                    @change="handleFileChange"
                    accept="video/*"
                  >
                  <small class="text-muted">支持 .mp4, .mov, .avi 等常见视频格式</small>
                </div>
                
                <div v-if="videoPreview" class="mb-3">
                  <div class="card">
                    <div class="card-body">
                      <p><strong>预览：</strong></p>
                      <video controls class="img-fluid" :src="videoPreview"></video>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 音乐 -->
              <div v-else-if="formData.category === '音乐'">
                <h5 class="mb-3">音乐文件</h5>
                
                <div class="mb-3">
                  <label for="audioFile" class="form-label">音乐文件</label>
                  <input 
                    type="file" 
                    id="audioFile" 
                    class="form-control" 
                    @change="handleFileChange"
                    accept="audio/*"
                  >
                  <small class="text-muted">支持 .mp3, .wav, .flac 等常见音频格式</small>
                </div>
                
                <div class="mb-3">
                  <label for="audioCover" class="form-label">封面图片</label>
                  <input 
                    type="file" 
                    id="audioCover" 
                    class="form-control" 
                    @change="handlePreviewChange"
                    accept="image/*"
                  >
                  <small class="text-muted">可选上传音乐封面图片</small>
                </div>
                
                <div v-if="audioPreview" class="mb-3">
                  <div class="card">
                    <div class="card-body">
                      <p><strong>预览：</strong></p>
                      <audio controls class="w-100" :src="audioPreview"></audio>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 照片 -->
              <div v-else-if="formData.category === '照片'">
                <h5 class="mb-3">照片文件</h5>
                
                <div class="mb-3">
                  <label for="photoFiles" class="form-label">照片文件</label>
                  <input 
                    type="file" 
                    id="photoFiles" 
                    class="form-control" 
                    @change="handlePhotoFilesChange"
                    accept="image/*"
                    multiple
                  >
                  <small class="text-muted">支持多选上传，最多一次上传200张图片</small>
                </div>
                
                <div v-if="photoFilesPreview.length > 0" class="mb-3">
                  <p><strong>已选择 {{ photoFilesPreview.length }} 张图片：</strong></p>
                  <div class="row">
                    <div 
                      v-for="(preview, index) in photoFilesPreviewDisplay" 
                      :key="index" 
                      class="col-md-3 col-6 mb-2"
                    >
                      <img :src="preview" class="img-thumbnail" alt="Preview">
                    </div>
                    <div v-if="photoFilesPreview.length > 12" class="col-md-3 col-6 mb-2">
                      <div class="img-thumbnail d-flex justify-content-center align-items-center" style="height: 100%;">
                        <span>+{{ photoFilesPreview.length - 12 }} 张</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="mt-4">
                <button 
                  type="submit" 
                  class="btn btn-primary"
                  :disabled="isUploading"
                >
                  <span v-if="isUploading">
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    上传中...
                  </span>
                  <span v-else>
                    <i class="bi bi-cloud-upload me-2"></i>上传素材
                  </span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useMaterialStore } from '@/stores/material';

const router = useRouter();
const materialStore = useMaterialStore();

const formData = reactive({
  category: '',
  title: '',
  tags: '',
  originalLink: '',
  sourceLink: '',
});

const mainFile = ref(null);
const previewFile = ref(null);
const photoFiles = ref([]);
const isUploading = ref(false);

// For file previews
const videoPreview = ref('');
const audioPreview = ref('');
const photoFilesPreview = ref([]);

const photoFilesPreviewDisplay = computed(() => {
  return photoFilesPreview.value.slice(0, 12);
});

// Handle category change
function onCategoryChange() {
  // Reset files
  mainFile.value = null;
  previewFile.value = null;
  photoFiles.value = [];
  
  // Clear previews
  videoPreview.value = '';
  audioPreview.value = '';
  photoFilesPreview.value = [];
}

// Handle main file selection
function handleFileChange(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  mainFile.value = file;
  
  // Create preview for video or audio
  if (formData.category === '视频') {
    videoPreview.value = URL.createObjectURL(file);
  } else if (formData.category === '音乐') {
    audioPreview.value = URL.createObjectURL(file);
  }
}

// Handle preview file selection
function handlePreviewChange(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  previewFile.value = file;
}

// Handle photo files selection
function handlePhotoFilesChange(event) {
  const files = event.target.files;
  if (!files.length) return;
  
  // Check if too many files
  if (files.length > 200) {
    alert('最多一次上传200张图片');
    event.target.value = '';
    return;
  }
  
  photoFiles.value = Array.from(files);
  
  // Create previews for photos
  photoFilesPreview.value = [];
  photoFiles.value.forEach(file => {
    photoFilesPreview.value.push(URL.createObjectURL(file));
  });
}

// Upload material
async function uploadMaterial() {
  // Check if form is valid
  if (!formData.title) {
    alert('请填写素材名称');
    return;
  }
  
  isUploading.value = true;
  
  try {
    // Create form data
    const uploadFormData = new FormData();
    uploadFormData.append('title', formData.title);
    
    if (formData.category) {
      uploadFormData.append('category', formData.category);
    }
    
    if (formData.tags) {
      uploadFormData.append('tags', formData.tags);
    }
    
    if (formData.originalLink) {
      uploadFormData.append('original_link', formData.originalLink);
    }
    
    if (formData.sourceLink) {
      uploadFormData.append('source_link', formData.sourceLink);
    }
    
    // Append appropriate files if provided
    if (formData.category === '照片' && photoFiles.value.length > 0) {
      // For photos - upload the first one as main file
      uploadFormData.append('file', photoFiles.value[0]);
      
      // Store the rest for later thumbnail upload
      for (const file of photoFiles.value) {
        uploadFormData.append('files', file);
      }
    } else if (mainFile.value) {
      // For other categories - upload main file if available
      uploadFormData.append('file', mainFile.value);
      
      // Upload preview file if available
      if (previewFile.value) {
        uploadFormData.append('preview_file', previewFile.value);
      }
    }
    
    // Upload material
    const result = await materialStore.uploadMaterial(uploadFormData);
    
    if (result) {
      // Redirect to material detail page
      router.push(`/materials/${result.id}`);
    } else {
      throw new Error(materialStore.error || '上传失败');
    }
  } catch (error) {
    console.error('Upload error:', error);
    alert('上传失败: ' + (error.message || '未知错误'));
  } finally {
    isUploading.value = false;
  }
}
</script>

<style scoped>
.card-header {
  background-color: #4a6bff !important;
}
</style> 
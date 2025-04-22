<template>
  <div class="container py-4">
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
          <h1 class="h2 mb-0">用户账号管理</h1>
          
          <button class="btn btn-primary" @click="showAddUserModal = true">
            <i class="bi bi-person-plus me-2"></i>添加新用户
          </button>
        </div>
      </div>
    </div>
    
    <!-- 用户列表 -->
    <div class="card shadow-sm">
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">加载中...</span>
          </div>
        </div>
        
        <div v-else-if="users.length === 0" class="text-center py-5">
          <i class="bi bi-people fs-1 text-muted"></i>
          <h3 class="mt-3">暂无用户</h3>
          <p class="text-muted">系统中尚未创建任何用户账号</p>
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th>用户名</th>
                <th>邮箱</th>
                <th>角色</th>
                <th>状态</th>
                <th>创建日期</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.username }}</td>
                <td>{{ user.email }}</td>
                <td>
                  <span class="badge" :class="user.is_admin ? 'bg-danger' : 'bg-info'">
                    {{ user.is_admin ? '管理员' : '普通用户' }}
                  </span>
                </td>
                <td>
                  <span class="badge" :class="user.is_active ? 'bg-success' : 'bg-secondary'">
                    {{ user.is_active ? '已激活' : '已禁用' }}
                  </span>
                </td>
                <td>{{ formatDate(user.created_at) }}</td>
                <td>
                  <div class="btn-group">
                    <button class="btn btn-action btn-edit" @click="editUser(user)">
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button 
                      class="btn btn-action btn-delete" 
                      @click="confirmDelete(user)"
                      :disabled="user.id === currentUser.id"
                    >
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- 添加用户模态框 -->
    <div v-if="showAddUserModal" class="modal fade show" style="display: block;" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">添加新用户</h5>
            <button type="button" class="btn-close" @click="showAddUserModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="createUser">
              <div class="mb-3">
                <label for="newUserEmail" class="form-label">邮箱</label>
                <input type="email" class="form-control" id="newUserEmail" v-model="newUser.email" required>
              </div>
              
              <div class="mb-3">
                <label for="newUserUsername" class="form-label">用户名</label>
                <input type="text" class="form-control" id="newUserUsername" v-model="newUser.username" required>
              </div>
              
              <div class="mb-3">
                <label for="newUserPassword" class="form-label">密码</label>
                <input type="password" class="form-control" id="newUserPassword" v-model="newUser.password" required>
              </div>
              
              <div class="form-check mb-3">
                <input class="form-check-input" type="checkbox" id="newUserIsAdmin" v-model="newUser.is_admin">
                <label class="form-check-label" for="newUserIsAdmin">
                  管理员权限
                </label>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showAddUserModal = false">取消</button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="createUser"
              :disabled="isSubmitting"
            >
              <span v-if="isSubmitting">
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                提交中...
              </span>
              <span v-else>创建用户</span>
            </button>
          </div>
        </div>
      </div>
      <div class="modal-backdrop fade show"></div>
    </div>
    
    <!-- 编辑用户模态框 -->
    <div v-if="showEditModal" class="modal fade show" style="display: block;" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">编辑用户</h5>
            <button type="button" class="btn-close" @click="showEditModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateUser">
              <div class="mb-3">
                <label for="editUserEmail" class="form-label">邮箱</label>
                <input type="email" class="form-control" id="editUserEmail" v-model="editingUser.email" required>
              </div>
              
              <div class="mb-3">
                <label for="editUserUsername" class="form-label">用户名</label>
                <input type="text" class="form-control" id="editUserUsername" v-model="editingUser.username" required>
              </div>
              
              <div class="mb-3">
                <label for="editUserPassword" class="form-label">新密码 (留空则不修改)</label>
                <input type="password" class="form-control" id="editUserPassword" v-model="editingUser.password">
              </div>
              
              <div class="form-check mb-3">
                <input 
                  class="form-check-input" 
                  type="checkbox" 
                  id="editUserIsAdmin" 
                  v-model="editingUser.is_admin"
                  :disabled="editingUser.id === currentUser.id"
                >
                <label class="form-check-label" for="editUserIsAdmin">
                  管理员权限
                </label>
                <small v-if="editingUser.id === currentUser.id" class="form-text text-muted d-block">
                  不能更改自己的管理员状态
                </small>
              </div>
              
              <div class="form-check mb-3">
                <input 
                  class="form-check-input" 
                  type="checkbox" 
                  id="editUserIsActive" 
                  v-model="editingUser.is_active"
                  :disabled="editingUser.id === currentUser.id"
                >
                <label class="form-check-label" for="editUserIsActive">
                  账号已激活
                </label>
                <small v-if="editingUser.id === currentUser.id" class="form-text text-muted d-block">
                  不能禁用自己的账号
                </small>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showEditModal = false">取消</button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="updateUser"
              :disabled="isSubmitting"
            >
              <span v-if="isSubmitting">
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
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import api from '@/services/api';

const router = useRouter();
const userStore = useUserStore();

const users = ref([]);
const loading = ref(true);
const isSubmitting = ref(false);
const showAddUserModal = ref(false);
const showEditModal = ref(false);
const currentUser = ref(null);

const newUser = ref({
  email: '',
  username: '',
  password: '',
  is_admin: false
});

const editingUser = ref({
  id: null,
  email: '',
  username: '',
  password: '',
  is_admin: false,
  is_active: true
});

// 在组件挂载时获取用户列表和当前用户信息
onMounted(async () => {
  if (!userStore.isLoggedIn) {
    router.push('/login?redirect=/accounts');
    return;
  }
  
  if (!userStore.isAdmin) {
    router.push('/');
    return;
  }
  
  currentUser.value = userStore.user;
  await fetchUsers();
});

// 获取所有用户
async function fetchUsers() {
  loading.value = true;
  try {
    const response = await api.getAllUsers();
    users.value = response;
  } catch (error) {
    console.error('获取用户列表失败:', error);
    alert('获取用户列表失败');
  } finally {
    loading.value = false;
  }
}

// 创建新用户
async function createUser() {
  isSubmitting.value = true;
  try {
    await api.createUser(newUser.value);
    showAddUserModal.value = false;
    
    // 重置表单
    newUser.value = {
      email: '',
      username: '',
      password: '',
      is_admin: false
    };
    
    // 刷新用户列表
    await fetchUsers();
  } catch (error) {
    console.error('创建用户失败:', error);
    alert('创建用户失败: ' + (error.response?.data?.detail || '未知错误'));
  } finally {
    isSubmitting.value = false;
  }
}

// 编辑用户
function editUser(user) {
  editingUser.value = {
    id: user.id,
    email: user.email,
    username: user.username,
    password: '',
    is_admin: user.is_admin,
    is_active: user.is_active
  };
  showEditModal.value = true;
}

// 更新用户
async function updateUser() {
  isSubmitting.value = true;
  try {
    // 创建更新对象，只包含已更改的字段
    const updateData = {};
    if (editingUser.value.email) updateData.email = editingUser.value.email;
    if (editingUser.value.username) updateData.username = editingUser.value.username;
    if (editingUser.value.password) updateData.password = editingUser.value.password;
    if (editingUser.value.id !== currentUser.value.id) {
      updateData.is_admin = editingUser.value.is_admin;
      updateData.is_active = editingUser.value.is_active;
    }
    
    await api.updateUser(editingUser.value.id, updateData);
    showEditModal.value = false;
    
    // 如果更新的是当前用户，刷新用户信息
    if (editingUser.value.id === currentUser.value.id) {
      await userStore.getCurrentUser();
    }
    
    // 刷新用户列表
    await fetchUsers();
  } catch (error) {
    console.error('更新用户失败:', error);
    alert('更新用户失败: ' + (error.response?.data?.detail || '未知错误'));
  } finally {
    isSubmitting.value = false;
  }
}

// 确认删除用户
function confirmDelete(user) {
  if (user.id === currentUser.value.id) {
    alert('不能删除自己的账号');
    return;
  }
  
  if (confirm(`确定要删除用户"${user.username}"吗？此操作不可撤销。`)) {
    deleteUser(user.id);
  }
}

// 删除用户
async function deleteUser(userId) {
  try {
    await api.deleteUser(userId);
    await fetchUsers();
  } catch (error) {
    console.error('删除用户失败:', error);
    alert('删除用户失败: ' + (error.response?.data?.detail || '未知错误'));
  }
}

// 格式化日期
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN');
}
</script>

<style scoped>
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
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}
</style> 
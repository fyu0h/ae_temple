import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for API calls
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for API calls
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    // If the error is 401 (Unauthorized) and not already retrying
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      // Clear the token and redirect to login
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

export default {
  // Auth
  async login(credentials) {
    const formData = new FormData()
    formData.append('username', credentials.username || credentials.email)
    formData.append('password', credentials.password)
    
    const response = await apiClient.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },
  
  async register(userData) {
    const response = await apiClient.post('/auth/register', userData)
    return response.data
  },
  
  async getCurrentUser() {
    const response = await apiClient.get('/users/me')
    return response.data
  },
  
  // User Management (Admin Only)
  async getAllUsers() {
    const response = await apiClient.get('/users/')
    return response.data
  },
  
  async getUser(id) {
    const response = await apiClient.get(`/users/${id}`)
    return response.data
  },
  
  async createUser(userData) {
    const response = await apiClient.post('/users/', userData)
    return response.data
  },
  
  async updateUser(id, userData) {
    console.log('更新用户请求:', id, userData);
    try {
      const response = await apiClient.put(`/users/${id}`, userData);
      console.log('更新用户响应:', response.data);
      return response.data;
    } catch (error) {
      console.error('更新用户错误:', error.response ? error.response.data : error.message);
      throw error;
    }
  },
  
  async deleteUser(id) {
    await apiClient.delete(`/users/${id}`)
  },
  
  // Materials
  async searchMaterials(params = {}) {
    const response = await apiClient.get('/materials/search', { params })
    return response.data
  },
  
  async getMaterial(id) {
    const response = await apiClient.get(`/materials/${id}`)
    return response.data
  },
  
  async uploadMaterial(formData) {
    const response = await apiClient.post('/materials/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },
  
  async uploadThumbnails(materialId, formData) {
    const response = await apiClient.post(`/materials/${materialId}/thumbnails`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },
  
  async updateMaterial(id, data) {
    const response = await apiClient.put(`/materials/${id}`, data)
    return response.data
  },
  
  async deleteMaterial(id) {
    await apiClient.delete(`/materials/${id}`)
  },
  
  async getMaterialThumbnails(id) {
    const response = await apiClient.get(`/materials/${id}/thumbs`)
    return response.data
  }
} 
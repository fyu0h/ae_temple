import { defineStore } from 'pinia'
import api from '@/services/api'

export const useUserStore = defineStore('user', {
  state: () => {
    // 尝试从localStorage加载用户数据
    let savedUser = null;
    try {
      const userData = localStorage.getItem('user');
      if (userData) {
        savedUser = JSON.parse(userData);
      }
    } catch (e) {
      console.error('Failed to parse user data from localStorage', e);
    }

    return {
      user: savedUser,
      token: localStorage.getItem('token') || null,
      loading: false,
      error: null
    }
  },
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.user?.is_admin || false
  },
  
  actions: {
    async login(credentials) {
      this.loading = true
      this.error = null
      
      try {
        const data = await api.login(credentials)
        this.token = data.access_token
        localStorage.setItem('token', data.access_token)
        
        // Get user info
        await this.fetchCurrentUser()
        return true
      } catch (error) {
        this.error = error.response?.data?.detail || 'Login failed'
        return false
      } finally {
        this.loading = false
      }
    },
    
    async register(userData) {
      this.loading = true
      this.error = null
      
      try {
        await api.register(userData)
        return true
      } catch (error) {
        this.error = error.response?.data?.detail || 'Registration failed'
        return false
      } finally {
        this.loading = false
      }
    },
    
    async fetchCurrentUser() {
      if (!this.token) return
      
      this.loading = true
      this.error = null
      
      try {
        this.user = await api.getCurrentUser()
        // 将用户信息保存到localStorage
        localStorage.setItem('user', JSON.stringify(this.user))
      } catch (error) {
        this.error = 'Failed to fetch user data'
        this.logout()
      } finally {
        this.loading = false
      }
    },
    
    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
}) 
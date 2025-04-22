import { defineStore } from 'pinia'
import api from '@/services/api'

export const useMaterialStore = defineStore('material', {
  state: () => ({
    materials: [],
    currentMaterial: null,
    thumbnails: [],
    totalCount: 0,
    loading: false,
    error: null
  }),
  
  actions: {
    async fetchMaterials(params = {}) {
      this.loading = true
      this.error = null
      
      try {
        const data = await api.searchMaterials(params)
        this.materials = data.results
        this.totalCount = data.total
      } catch (error) {
        this.error = 'Failed to fetch materials'
        console.error(error)
      } finally {
        this.loading = false
      }
    },
    
    async fetchMaterial(id) {
      this.loading = true
      this.error = null
      
      try {
        this.currentMaterial = await api.getMaterial(id)
      } catch (error) {
        this.error = 'Failed to fetch material details'
        console.error(error)
      } finally {
        this.loading = false
      }
    },
    
    async fetchThumbnails(id) {
      this.loading = true
      
      try {
        this.thumbnails = await api.getMaterialThumbnails(id)
      } catch (error) {
        console.error('Failed to fetch thumbnails', error)
      } finally {
        this.loading = false
      }
    },
    
    async uploadMaterial(formData) {
      this.loading = true
      this.error = null
      
      try {
        const data = await api.uploadMaterial(formData)
        
        // If it's a photo type and has files for thumbnails upload
        if (formData.get('category') === '照片' && formData.getAll('files')?.length > 0) {
          const thumbnailForm = new FormData()
          for (const file of formData.getAll('files')) {
            thumbnailForm.append('files', file)
          }
          
          await api.uploadThumbnails(data.id, thumbnailForm)
        }
        
        return data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to upload material'
        console.error(error)
        return null
      } finally {
        this.loading = false
      }
    },
    
    async updateMaterial(id, data) {
      this.loading = true
      this.error = null
      
      try {
        const updatedMaterial = await api.updateMaterial(id, data)
        
        // Update in materials list if exists
        const index = this.materials.findIndex(m => m.id === id)
        if (index !== -1) {
          this.materials[index] = updatedMaterial
        }
        
        // Update current material if it's the same
        if (this.currentMaterial?.id === id) {
          this.currentMaterial = updatedMaterial
        }
        
        return updatedMaterial
      } catch (error) {
        this.error = 'Failed to update material'
        console.error(error)
        return null
      } finally {
        this.loading = false
      }
    },
    
    async deleteMaterial(id) {
      this.loading = true
      this.error = null
      
      try {
        await api.deleteMaterial(id)
        
        // Remove from materials list
        this.materials = this.materials.filter(m => m.id !== id)
        
        // Clear current material if it's the same
        if (this.currentMaterial?.id === id) {
          this.currentMaterial = null
        }
        
        return true
      } catch (error) {
        this.error = 'Failed to delete material'
        console.error(error)
        return false
      } finally {
        this.loading = false
      }
    }
  }
}) 
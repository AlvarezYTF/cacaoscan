import { defineStore } from 'pinia'
import api from '@/services/api'
import { downloadFileFromResponse } from '@/utils/fileExportUtils'

export const useNotificationsStore = defineStore('notifications', {
  state: () => ({
    notifications: [],
    unreadCount: 0,
    stats: {
      total_notifications: 0,
      unread_count: 0,
      notifications_by_type: {},
      recent_notifications: []
    },
    pagination: {
      currentPage: 1,
      totalPages: 1,
      totalItems: 0,
      itemsPerPage: 20
    },
    loading: false,
    error: null,
    realtimeEnabled: true
  }),

  getters: {
    getNotificationById: (state) => (id) => {
      return state.notifications.find(notification => notification.id === id)
    },

    getUnreadNotifications: (state) => {
      return state.notifications.filter(notification => !notification.leida)
    },

    getNotificationsByType: (state) => (tipo) => {
      return state.notifications.filter(notification => notification.tipo === tipo)
    },

    getRecentNotifications: (state) => (limit = 5) => {
      const sorted = [...state.notifications].sort((a, b) => new Date(b.fecha_creacion) - new Date(a.fecha_creacion))
      return sorted.slice(0, limit)
    },

    getNotificationsByDate: (state) => (date) => {
      const targetDate = new Date(date).toDateString()
      return state.notifications.filter(notification => 
        new Date(notification.fecha_creacion).toDateString() === targetDate
      )
    }
  },

  actions: {
    async fetchNotifications(params = {}) {
      try {
        this.loading = true
        this.error = null

        const response = await api.get('/notifications/', { params })
        
        this.notifications = response.data.results || response.data
        this.pagination = {
          currentPage: response.data.page || 1,
          totalPages: response.data.total_pages || 1,
          totalItems: response.data.count || 0,
          itemsPerPage: response.data.page_size || 20
        }

        // Calcular notificaciones no leídas
        this.unreadCount = this.notifications.filter(n => !n.leida).length

        return response
      } catch (error) {
        this.error = error.response?.data?.detail || 'Error al cargar notificaciones'
        console.error('Error fetching notifications:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchNotificationDetails(id) {
      try {
        const response = await api.get(`/notifications/${id}/`)
        return response
      } catch (error) {
        console.error('Error fetching notification details:', error)
        throw error
      }
    },

    async markAsRead(id) {
      try {
        await api.post(`/notifications/${id}/mark-read/`)
        
        // Actualizar estado local
        const notification = this.getNotificationById(id)
        if (notification && !notification.leida) {
          notification.leida = true
          notification.fecha_lectura = new Date().toISOString()
          this.unreadCount = Math.max(0, this.unreadCount - 1)
        }
        
        return true
      } catch (error) {
        console.error('Error marking notification as read:', error)
        throw error
      }
    },

    async markAllAsRead() {
      try {
        await api.post('/notifications/mark-all-read/')
        
        // Actualizar estado local
        for (const notification of this.notifications) {
          notification.leida = true
          notification.fecha_lectura = new Date().toISOString()
        }
        this.unreadCount = 0
        
        return true
      } catch (error) {
        console.error('Error marking all notifications as read:', error)
        throw error
      }
    },

    async getUnreadCount() {
      try {
        const response = await api.get('/notifications/unread-count/')
        this.unreadCount = response.data.unread_count
        return response.data.unread_count
      } catch (error) {
        console.error('Error getting unread count:', error)
        throw error
      }
    },

    async getNotificationStats() {
      try {
        const response = await api.get('/notifications/stats/')
        this.stats = response.data
        return response.data
      } catch (error) {
        console.error('Error getting notification stats:', error)
        throw error
      }
    },

    async createNotification(notificationData) {
      try {
        const response = await api.post('/notifications/create/', notificationData)
        
        // Agregar a la lista local
        this.notifications.unshift(response.data)
        this.unreadCount++
        
        return response.data
      } catch (error) {
        console.error('Error creating notification:', error)
        throw error
      }
    },

    // Métodos para integración con WebSockets
    addRealtimeNotification(notification) {
      // Verificar si la notificación ya existe
      const existingIndex = this.notifications.findIndex(n => n.id === notification.id)
      
      if (existingIndex >= 0) {
        // Actualizar notificación existente
        this.notifications[existingIndex] = notification
      } else {
        // Agregar nueva notificación al inicio
        this.notifications.unshift(notification)
        
        // Limitar a 100 notificaciones
        if (this.notifications.length > 100) {
          this.notifications = this.notifications.slice(0, 100)
        }
      }
      
      // Actualizar contador de no leídas
      if (!notification.leida) {
        this.unreadCount++
      }
    },

    updateRealtimeNotification(notification) {
      const index = this.notifications.findIndex(n => n.id === notification.id)
      if (index !== -1) {
        const wasUnread = !this.notifications[index].leida
        const isNowRead = notification.leida
        
        this.notifications[index] = notification
        
        // Actualizar contador
        if (wasUnread && isNowRead) {
          this.unreadCount = Math.max(0, this.unreadCount - 1)
        } else if (!wasUnread && !isNowRead) {
          this.unreadCount++
        }
      }
    },

    updateRealtimeStats(stats) {
      this.stats = stats
      this.unreadCount = stats.unread_count
    },

    // Métodos de utilidad
    clearError() {
      this.error = null
    },

    reset() {
      this.notifications = []
      this.unreadCount = 0
      this.stats = {
        total_notifications: 0,
        unread_count: 0,
        notifications_by_type: {},
        recent_notifications: []
      }
      this.pagination = {
        currentPage: 1,
        totalPages: 1,
        totalItems: 0,
        itemsPerPage: 20
      }
      this.loading = false
      this.error = null
    },

    // Métodos para filtros y búsqueda
    async searchNotifications(query) {
      try {
        const response = await api.get('/notifications/', {
          params: { search: query }
        })
        
        this.notifications = response.data.results || response.data
        return response
      } catch (error) {
        console.error('Error searching notifications:', error)
        throw error
      }
    },

    async filterByType(tipo) {
      try {
        const response = await api.get('/notifications/', {
          params: { tipo }
        })
        
        this.notifications = response.data.results || response.data
        return response
      } catch (error) {
        console.error('Error filtering notifications by type:', error)
        throw error
      }
    },

    async filterByReadStatus(leida) {
      try {
        const response = await api.get('/notifications/', {
          params: { leida }
        })
        
        this.notifications = response.data.results || response.data
        return response
      } catch (error) {
        console.error('Error filtering notifications by read status:', error)
        throw error
      }
    },

    // Métodos para paginación
    async goToPage(page) {
      try {
        const response = await this.fetchNotifications({ page })
        return response
      } catch (error) {
        console.error('Error going to page:', error)
        throw error
      }
    },

    async changePageSize(pageSize) {
      try {
        this.pagination.itemsPerPage = pageSize
        const response = await this.fetchNotifications({ 
          page: 1, 
          page_size: pageSize 
        })
        return response
      } catch (error) {
        console.error('Error changing page size:', error)
        throw error
      }
    },

    // Métodos para exportación
    async exportNotifications(format = 'json') {
      try {
        const response = await api.get('/notifications/export/', {
          params: { format },
          responseType: 'blob'
        })

        downloadFileFromResponse(response, 'notificaciones_exportadas.json')

        return true
      } catch (error) {
        console.error('Error exporting notifications:', error)
        throw error
      }
    }
  }
})

// Alias para compatibilidad (singular)
export const useNotificationStore = useNotificationsStore
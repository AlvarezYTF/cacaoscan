/**
 * Composable for recent activity functionality
 * Provides state and methods for displaying recent activity lists
 */
import { ref, computed } from 'vue'

/**
 * Provides recent activity state and methods
 * @param {Object} options - Configuration options
 * @param {number} options.limit - Maximum number of activities to show
 * @param {Function} options.fetchFn - Function to fetch activities
 * @returns {Object} Recent activity composable
 */
export function useRecentActivity(options = {}) {
  const { limit = 10, fetchFn = null } = options

  // State
  const activities = ref([])
  const loading = ref(false)
  const error = ref(null)
  const lastFetch = ref(null)

  // Computed
  const recentActivities = computed(() => {
    return activities.value.slice(0, limit)
  })

  const hasActivities = computed(() => activities.value.length > 0)

  /**
   * Fetches recent activities
   * @param {Object} params - Fetch parameters
   * @returns {Promise<void>}
   */
  const fetchActivities = async (params = {}) => {
    if (!fetchFn || typeof fetchFn !== 'function') {
      throw new Error('fetchFn is required for useRecentActivity')
    }

    loading.value = true
    error.value = null

    try {
      const result = await fetchFn({ ...params, limit })
      activities.value = Array.isArray(result) ? result : (result.data || result.results || [])
      lastFetch.value = new Date()
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Error al cargar actividades recientes'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Adds a new activity to the list
   * @param {Object} activity - Activity object
   * @returns {void}
   */
  const addActivity = (activity) => {
    if (!activity) return

    // Add to beginning of array
    activities.value.unshift(activity)

    // Limit to max items
    if (activities.value.length > limit * 2) {
      activities.value = activities.value.slice(0, limit * 2)
    }
  }

  /**
   * Removes an activity
   * @param {string|number} activityId - Activity ID
   * @returns {void}
   */
  const removeActivity = (activityId) => {
    const index = activities.value.findIndex(a => a.id === activityId)
    if (index !== -1) {
      activities.value.splice(index, 1)
    }
  }

  /**
   * Clears all activities
   * @returns {void}
   */
  const clearActivities = () => {
    activities.value = []
    error.value = null
    lastFetch.value = null
  }

  /**
   * Formats activity for display
   * @param {Object} activity - Activity object
   * @returns {Object} Formatted activity
   */
  const formatActivity = (activity) => {
    if (!activity) return null

    return {
      id: activity.id,
      title: activity.title || activity.action || 'Actividad',
      description: activity.description || activity.message || '',
      timestamp: activity.timestamp || activity.created_at || activity.date,
      type: activity.type || activity.action_type || 'info',
      icon: activity.icon || getDefaultIcon(activity.type || activity.action_type),
      user: activity.user || activity.usuario || null,
      link: activity.link || activity.route || null
    }
  }

  /**
   * Gets default icon for activity type
   * @param {string} type - Activity type
   * @returns {string} Icon name
   */
  const getDefaultIcon = (type) => {
    const iconMap = {
      create: 'plus-circle',
      update: 'pencil',
      delete: 'trash',
      view: 'eye',
      login: 'sign-in',
      logout: 'sign-out',
      upload: 'upload',
      download: 'download',
      analysis: 'chart-bar',
      prediction: 'camera',
      info: 'info-circle',
      success: 'check-circle',
      warning: 'exclamation-triangle',
      error: 'x-circle'
    }
    return iconMap[type] || 'circle'
  }

  /**
   * Groups activities by date
   * @returns {Object} Activities grouped by date
   */
  const groupByDate = () => {
    const groups = {}

    for (const activity of activities.value) {
      const date = new Date(activity.timestamp || activity.created_at || activity.date)
      const dateKey = date.toLocaleDateString('es-CO', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })

      if (!groups[dateKey]) {
        groups[dateKey] = []
      }

      groups[dateKey].push(activity)
    }

    return groups
  }

  return {
    // State
    activities,
    loading,
    error,
    lastFetch,
    recentActivities,
    hasActivities,

    // Methods
    fetchActivities,
    addActivity,
    removeActivity,
    clearActivities,
    formatActivity,
    getDefaultIcon,
    groupByDate
  }
}


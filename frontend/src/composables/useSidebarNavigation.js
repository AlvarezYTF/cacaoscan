/**
 * Composable for sidebar navigation and layout management
 * Centralizes common sidebar patterns across views
 */

import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export function useSidebarNavigation() {
  const router = useRouter()
  const route = useRoute()
  const authStore = useAuthStore()

  // Sidebar collapse state
  const isSidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true')

  // Computed properties
  const userName = computed(() => {
    return authStore.userFullName || 'Usuario'
  })

  const userRole = computed(() => {
    const role = authStore.userRole || 'Usuario'
    // Normalize role for sidebar - Backend returns: 'admin', 'analyst', or 'farmer'
    if (role === 'admin') return 'admin'
    if (role === 'farmer' || role === 'Agricultor') return 'agricultor'
    return 'agricultor' // Default to agricultor
  })

  // Methods
  const handleMenuClick = (item) => {
    if (item.route && item.route !== null) {
      // Navigate to external routes
      const currentPath = route.path
      if (currentPath !== item.route) {
        router.push(item.route)
      }
    } else {
      // For internal sections without routes, navigate to dashboard with query param
      const role = authStore.userRole
      if (role === 'farmer' || role === 'Agricultor') {
        router.push({
          name: 'AgricultorDashboard',
          query: { section: item.id }
        })
      } else {
        router.push({
          name: 'AdminDashboard',
          query: { section: item.id }
        })
      }
    }
  }

  const toggleSidebarCollapse = () => {
    isSidebarCollapsed.value = !isSidebarCollapsed.value
    localStorage.setItem('sidebarCollapsed', isSidebarCollapsed.value)
  }

  const handleLogout = async () => {
    try {
      await authStore.logout()
    } catch (err) {
      console.error('Error durante logout:', err)
      // Continuar con logout aunque haya error
    }
  }

  return {
    isSidebarCollapsed,
    userName,
    userRole,
    handleMenuClick,
    toggleSidebarCollapse,
    handleLogout
  }
}


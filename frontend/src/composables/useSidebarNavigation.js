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

  const normalizeRole = (role) => {
    if (role === 'admin') return 'admin'
    if (role === 'farmer' || role === 'Agricultor') return 'agricultor'
    return 'agricultor'
  }

  const userRole = computed(() => {
    const role = authStore.userRole || 'Usuario'
    return normalizeRole(role)
  })

  const isFarmerRole = (role) => {
    return role === 'farmer' || role === 'Agricultor'
  }

  const getDashboardName = (role) => {
    return isFarmerRole(role) ? 'AgricultorDashboard' : 'AdminDashboard'
  }

  // Methods
  const handleMenuClick = (item) => {
    if (item.route && item.route !== null) {
      const currentPath = route.path
      if (currentPath !== item.route) {
        router.push(item.route)
      }
    } else {
      const role = authStore.userRole
      router.push({
        name: getDashboardName(role),
        query: { section: item.id }
      })
    }
  }

  const toggleSidebarCollapse = () => {
    isSidebarCollapsed.value = !isSidebarCollapsed.value
    localStorage.setItem('sidebarCollapsed', String(isSidebarCollapsed.value))
  }

  const handleLogout = async () => {
    try {
      await authStore.logout()
    } catch (err) {
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


/**
 * Composable for shared AdminSidebar props
 * Used by AuditoriaView, Reportes, and other admin views
 */
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

/**
 * Returns common props for AdminSidebar component
 * @returns {Object} Object with brandName, userName, and userRole
 */
export function useAdminSidebarProps() {
  const authStore = useAuthStore()

  const brandName = computed(() => 'CacaoScan')

  const userName = computed(() => {
    const user = authStore.user
    if (user?.first_name && user?.last_name) {
      return `${user.first_name} ${user.last_name}`
    }
    return user?.username || 'Usuario'
  })

  const userRole = computed(() => {
    return authStore.user?.is_superuser ? 'Administrador' : 'Analista'
  })

  return {
    brandName,
    userName,
    userRole
  }
}


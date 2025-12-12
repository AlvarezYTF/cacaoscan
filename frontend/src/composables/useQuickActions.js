/**
 * Composable for quick actions functionality
 * Provides state and methods for dashboard quick actions
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'

/**
 * Provides quick actions state and methods
 * @returns {Object} Quick actions composable
 */
export function useQuickActions() {
  const router = useRouter()

  // State
  const executingAction = ref(null)
  const actionError = ref(null)

  /**
   * Executes a quick action
   * @param {Object} action - Action object with key, handler, etc.
   * @returns {Promise<void>}
   */
  const executeAction = async (action) => {
    if (!action?.key) {
      throw new Error('Invalid action: action must have a key')
    }

    executingAction.value = action.key
    actionError.value = null

    try {
      // If action has a route, navigate to it
      if (action.route) {
        router.push(action.route)
        return
      }

      // If action has a handler, execute it
      if (action.handler && typeof action.handler === 'function') {
        await action.handler(action)
        return
      }

      // If action has an external URL, open it
      if (action.url) {
        if (action.external) {
          globalThis.open(action.url, '_blank')
        } else {
          globalThis.location.href = action.url
        }
        return
      }

      throw new Error(`Action "${action.key}" has no handler, route, or url`)
    } catch (error) {
      actionError.value = error.message || 'Error al ejecutar la acción'
      throw error
    } finally {
      executingAction.value = null
    }
  }

  /**
   * Checks if an action is currently executing
   * @param {string} actionKey - Action key to check
   * @returns {boolean} True if action is executing
   */
  const isActionExecuting = (actionKey) => {
    return executingAction.value === actionKey
  }

  /**
   * Gets default quick actions for a role
   * @param {string} role - User role (admin, agricultor, analyst)
   * @returns {Array} Array of action objects
   */
  const getDefaultActions = (role) => {
    const actionsByRole = {
      admin: [
        {
          key: 'new-user',
          label: 'Nuevo Usuario',
          icon: 'user-plus',
          route: '/admin/usuarios/nuevo',
          variant: 'primary'
        },
        {
          key: 'new-farmer',
          label: 'Nuevo Agricultor',
          icon: 'user-plus',
          route: '/admin/agricultores/nuevo',
          variant: 'primary'
        },
        {
          key: 'view-reports',
          label: 'Ver Reportes',
          icon: 'chart-bar',
          route: '/reportes',
          variant: 'secondary'
        },
        {
          key: 'view-audit',
          label: 'Auditoría',
          icon: 'shield-check',
          route: '/auditoria',
          variant: 'secondary'
        }
      ],
      agricultor: [
        {
          key: 'new-analysis',
          label: 'Nuevo Análisis',
          icon: 'camera',
          route: '/nuevo-analisis',
          variant: 'primary'
        },
        {
          key: 'new-finca',
          label: 'Nueva Finca',
          icon: 'map',
          route: '/mis-fincas/nueva',
          variant: 'primary'
        },
        {
          key: 'view-history',
          label: 'Mi Historial',
          icon: 'clock',
          route: '/mis-analisis',
          variant: 'secondary'
        },
        {
          key: 'view-fincas',
          label: 'Mis Fincas',
          icon: 'map',
          route: '/mis-fincas',
          variant: 'secondary'
        }
      ],
      analyst: [
        {
          key: 'new-analysis',
          label: 'Nuevo Análisis',
          icon: 'camera',
          route: '/nuevo-analisis',
          variant: 'primary'
        },
        {
          key: 'view-reports',
          label: 'Reportes',
          icon: 'chart-bar',
          route: '/reportes',
          variant: 'primary'
        },
        {
          key: 'view-datasets',
          label: 'Datasets',
          icon: 'database',
          route: '/datasets',
          variant: 'secondary'
        }
      ]
    }

    return actionsByRole[role] || []
  }

  /**
   * Formats action for display
   * @param {Object} action - Action object
   * @returns {Object} Formatted action
   */
  const formatAction = (action) => {
    return {
      ...action,
      disabled: action.disabled || isActionExecuting(action.key),
      loading: isActionExecuting(action.key)
    }
  }

  return {
    // State
    executingAction,
    actionError,

    // Methods
    executeAction,
    isActionExecuting,
    getDefaultActions,
    formatAction
  }
}


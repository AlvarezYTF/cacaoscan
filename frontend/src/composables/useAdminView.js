/**
 * Composable for shared admin view logic (filters, pagination, stats, etc.)
 * Used by AuditoriaView, Reportes, and other admin views
 */
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { usePagination } from '@/composables/usePagination'
import Swal from 'sweetalert2'

/**
 * Creates shared admin view composable
 * @param {Object} options - Configuration options
 * @param {Object} options.store - Pinia store instance
 * @param {Object} options.initialFilters - Initial filter values
 * @param {number} options.initialItemsPerPage - Initial items per page
 * @param {string} options.initialPeriod - Initial period (default: 'week')
 * @param {Function} options.loadData - Function to load data
 * @param {Function} options.loadStats - Function to load stats
 * @param {Function} options.getFilteredData - Function to get filtered data (computed)
 * @returns {Object} Composable return object
 */
export function useAdminView(options) {
  const router = useRouter()
  const {
    store,
    initialFilters = {},
    initialItemsPerPage = 20,
    initialPeriod = 'week',
    loadData,
    loadStats,
    getFilteredData
  } = options

  // State
  const loading = ref(false)
  const showFilters = ref(false)
  const viewMode = ref('table')
  const selectedPeriod = ref(initialPeriod)

  // Filters
  const filters = ref({ ...initialFilters })

  // Stats
  const stats = computed(() => store?.stats || {})

  // Filtered data (if custom function provided)
  const filteredData = computed(() => {
    if (getFilteredData) {
      return getFilteredData(filters.value, store)
    }
    return []
  })

  // Pagination
  const paginationComposable = usePagination({
    initialPage: 1,
    initialItemsPerPage
  })

  // Sync composable with store pagination
  if (store?.pagination) {
    watch(() => store.pagination, (storePagination) => {
      if (storePagination) {
        paginationComposable.updateFromApiResponse({
          page: storePagination.currentPage,
          page_size: storePagination.itemsPerPage,
          count: storePagination.totalItems,
          total_pages: storePagination.totalPages
        })
      }
    }, { immediate: true })
  }

  // Computed pagination for component (backward compatibility)
  const pagination = computed(() => ({
    currentPage: paginationComposable.currentPage.value,
    totalPages: paginationComposable.totalPages.value,
    totalItems: paginationComposable.totalItems.value,
    itemsPerPage: paginationComposable.itemsPerPage.value
  }))

  // Methods
  const handleMenuClick = (menuItem) => {
    if (menuItem.route) {
      router.push(menuItem.route)
    }
  }

  const handleLogout = async () => {
    try {
      const { useAuthStore } = await import('@/stores/auth')
      const authStore = useAuthStore()
      await authStore.logout()
      router.push('/login')
    } catch (error) {
      console.error('Error during logout:', error)
    }
  }

  const handleRefresh = async () => {
    await loadInitialData()
    Swal.fire({
      toast: true,
      position: 'top-end',
      icon: 'success',
      title: 'Datos actualizados',
      showConfirmButton: false,
      timer: 2000
    })
  }

  const loadInitialData = async () => {
    try {
      loading.value = true
      const promises = []
      if (loadStats) promises.push(loadStats())
      if (loadData) promises.push(loadData(filters.value))
      await Promise.all(promises)
    } catch (error) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'No se pudieron cargar los datos'
      })
    } finally {
      loading.value = false
    }
  }

  const applyFilters = async () => {
    try {
      loading.value = true
      if (loadData) {
        await loadData(filters.value)
      }
    } catch (error) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'No se pudieron aplicar los filtros'
      })
    } finally {
      loading.value = false
    }
  }

  const clearFilters = () => {
    filters.value = { ...initialFilters }
    selectedPeriod.value = initialPeriod
    applyFilters()
  }

  const handlePageChange = async (page) => {
    try {
      paginationComposable.goToPage(page)
      if (loadData) {
        await loadData({ ...filters.value, page })
      }
    } catch (error) {
      console.error('Error during page change:', error)
    }
  }

  return {
    // State
    loading,
    showFilters,
    viewMode,
    selectedPeriod,
    filters,
    stats,
    filteredData,
    pagination,
    paginationComposable,

    // Methods
    handleMenuClick,
    handleLogout,
    handleRefresh,
    loadInitialData,
    applyFilters,
    clearFilters,
    handlePageChange
  }
}


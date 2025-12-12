import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { nextTick, ref, reactive } from 'vue'
import Swal from 'sweetalert2'
import Reportes from '../Reportes.vue'

const mockReportsStore = {
  reports: [],
  stats: {
    totalReports: 0,
    reportsChange: 0,
    completedReports: 0,
    completedChange: 0,
    inProgressReports: 0,
    inProgressChange: 0,
    errorReports: 0,
    errorChange: 0
  },
  pagination: {
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    itemsPerPage: 20
  },
  loading: false,
  error: null,
  fetchReports: vi.fn().mockResolvedValue({ data: { results: [] } }),
  fetchStats: vi.fn().mockResolvedValue({
    total_reports: 0,
    reports_change: 0,
    completed_reports: 0,
    completed_change: 0,
    in_progress_reports: 0,
    in_progress_change: 0,
    error_reports: 0,
    error_change: 0
  }),
  fetchUsers: vi.fn().mockResolvedValue({ data: { results: [] } }),
  fetchFincas: vi.fn().mockResolvedValue({ data: { results: [] } }),
  fetchLotesByFinca: vi.fn().mockResolvedValue({ data: { results: [] } }),
  createReport: vi.fn(),
  addReport: vi.fn(),
  downloadReport: vi.fn().mockResolvedValue(undefined),
  deleteReport: vi.fn().mockResolvedValue(undefined),
  exportReports: vi.fn().mockResolvedValue(undefined),
  bulkDeleteReports: vi.fn().mockResolvedValue(undefined)
}

vi.mock('@/stores/reports', () => ({
  useReportsStore: () => mockReportsStore
}))

// Create reactive filters object for watcher to detect changes
const mockFiltersValue = reactive({
  tipo_reporte: '',
  formato: '',
  estado: '',
  usuario_id: '',
  fecha_desde: '',
  fecha_hasta: '',
  finca_id: '',
  lote_id: ''
})

const mockUseAdminView = {
  loading: { value: false },
  showFilters: { value: false },
  viewMode: { value: 'table' },
  selectedPeriod: { value: 'month' },
  filters: ref(mockFiltersValue), // Use ref with reactive object
  stats: { value: {} },
  filteredData: { value: [] },
  pagination: { value: { currentPage: 1, totalPages: 1, totalItems: 0, itemsPerPage: 20 } },
  paginationComposable: {
    goToPage: vi.fn()
  },
  handleMenuClick: vi.fn(),
  handleLogout: vi.fn(),
  applyFilters: vi.fn(),
  clearFilters: vi.fn()
}

vi.mock('@/composables/useAdminView', () => ({
  useAdminView: vi.fn(() => mockUseAdminView)
}))

vi.mock('@/composables/useAdminSidebarProps', () => ({
  useAdminSidebarProps: vi.fn(() => ({
    brandName: 'CacaoScan',
    userName: 'Admin User',
    userRole: 'admin'
  }))
}))

vi.mock('sweetalert2', () => {
  const mockSwal = {
    fire: vi.fn().mockResolvedValue({ isConfirmed: false })
  }
  return {
    default: mockSwal
  }
})

const createWrapper = (options = {}) => {
  return mount(Reportes, {
    global: {
      stubs: {
        'router-link': true,
        'router-view': true,
        'AdminSidebar': true,
        'PeriodSelector': true,
        'StatsCard': true,
        'ReportsTable': true,
        'ReportCard': true,
        'ReportsTimeline': true,
        'Pagination': true,
        'ReportGeneratorModal': true,
        'ReportPreviewModal': true,
        'ConfirmModal': true
      },
      plugins: [createPinia()],
      ...options.global
    },
    ...options
  })
}

describe('Reportes', () => {
  let wrapper

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    mockUseAdminView.loading.value = false
    mockUseAdminView.showFilters.value = false
    mockUseAdminView.viewMode.value = 'table'
    mockUseAdminView.selectedPeriod.value = 'month'
    // Reset filters by updating the reactive object properties
    Object.assign(mockFiltersValue, {
      tipo_reporte: '',
      formato: '',
      estado: '',
      usuario_id: '',
      fecha_desde: '',
      fecha_hasta: '',
      finca_id: '',
      lote_id: ''
    })
    mockUseAdminView.filteredData.value = []
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render reportes view', () => {
    wrapper = createWrapper()
    expect(wrapper.exists()).toBe(true)
  })

  it('should load reports on mount', async () => {
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 100))
    
    expect(mockReportsStore.fetchReports).toHaveBeenCalled()
    expect(mockReportsStore.fetchStats).toHaveBeenCalled()
    expect(mockReportsStore.fetchUsers).toHaveBeenCalled()
    expect(mockReportsStore.fetchFincas).toHaveBeenCalled()
  })

  it('should handle loadInitialData error', async () => {
    mockReportsStore.fetchReports.mockRejectedValueOnce(new Error('Load error'))
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    
    expect(Swal.fire).toHaveBeenCalledWith(
      expect.objectContaining({
        icon: 'error',
        title: 'Error',
        text: 'No se pudieron cargar los datos iniciales'
      })
    )
  })

  it('should handle refresh', async () => {
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    await flushPromises()
    
    vi.clearAllMocks()
    await wrapper.vm.handleRefresh()
    await flushPromises()
    
    expect(Swal.fire).toHaveBeenCalledWith(
      expect.objectContaining({
        toast: true,
        icon: 'success',
        title: 'Datos actualizados'
      })
    )
  })

  it('should handle search', async () => {
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    wrapper.vm.handleSearch('test query')
    await wrapper.vm.$nextTick()
    
    expect(mockUseAdminView.filters.value.search).toBe('test query')
    expect(mockUseAdminView.applyFilters).toHaveBeenCalled()
  })

  it('should load users', async () => {
    const usersData = [{ id: 1, first_name: 'User', last_name: 'One' }]
    mockReportsStore.fetchUsers.mockResolvedValueOnce({ data: { results: usersData } })
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    
    expect(wrapper.vm.users).toEqual(usersData)
  })

  it('should handle loadUsers error', async () => {
    mockReportsStore.fetchUsers.mockRejectedValueOnce(new Error('Users error'))
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    
    expect(consoleErrorSpy).toHaveBeenCalled()
    consoleErrorSpy.mockRestore()
  })

  it('should load fincas', async () => {
    const fincasData = [{ id: 1, nombre: 'Finca Test' }]
    mockReportsStore.fetchFincas.mockResolvedValueOnce({ data: { results: fincasData } })
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    
    expect(wrapper.vm.fincas).toEqual(fincasData)
  })

  it('should handle loadFincas error', async () => {
    mockReportsStore.fetchFincas.mockRejectedValueOnce(new Error('Fincas error'))
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    
    expect(consoleErrorSpy).toHaveBeenCalled()
    consoleErrorSpy.mockRestore()
  })

  it('should load lotes when finca_id changes', async () => {
    const lotesData = [{ id: 1, identificador: 'LOTE-001' }]
    mockReportsStore.fetchLotesByFinca.mockResolvedValueOnce({ data: { results: lotesData } })
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    await flushPromises()
    
    // Change finca_id in the reactive object to trigger the watcher
    mockFiltersValue.finca_id = '1'
    await nextTick() // Wait for watcher to trigger
    await flushPromises() // Wait for loadLotes to complete
    await nextTick() // Wait for reactive updates
    
    expect(mockReportsStore.fetchLotesByFinca).toHaveBeenCalledWith('1')
    expect(wrapper.vm.lotes).toEqual(lotesData)
  })

  it('should clear lotes when finca_id is empty', async () => {
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    await flushPromises()
    
    // First set a finca_id to load lotes
    mockFiltersValue.finca_id = '1'
    await nextTick()
    await flushPromises()
    
    // Set some lotes
    wrapper.vm.lotes = [{ id: 1 }]
    await nextTick()
    
    // Clear finca_id to trigger watcher that should clear lotes
    mockFiltersValue.finca_id = ''
    await nextTick() // Wait for watcher to trigger
    await nextTick() // Wait for reactive updates
    
    expect(wrapper.vm.lotes).toEqual([])
    expect(mockFiltersValue.lote_id).toBe('')
  })

  it('should handle loadLotes error', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    mockReportsStore.fetchLotesByFinca.mockRejectedValueOnce(new Error('Lotes error'))
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    await flushPromises()
    
    // Set finca_id to trigger the watcher
    wrapper.vm.filters.finca_id = ''
    await wrapper.vm.$nextTick()
    wrapper.vm.filters.finca_id = '1'
    await wrapper.vm.$nextTick()
    await flushPromises()
    await new Promise(resolve => setTimeout(resolve, 200))
    
    expect(consoleErrorSpy).toHaveBeenCalled()
    expect(wrapper.vm.lotes).toEqual([])
    consoleErrorSpy.mockRestore()
  })

  it('should handle period change', async () => {
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    await flushPromises()
    
    await wrapper.vm.handlePeriodChange('week')
    await flushPromises()
    
    expect(mockUseAdminView.selectedPeriod.value).toBe('week')
    expect(mockUseAdminView.applyFilters).toHaveBeenCalled()
  })

  it('should clear filters', async () => {
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    // Set initial filter values
    wrapper.vm.filters.tipo_reporte = 'calidad'
    wrapper.vm.selectedPeriod = 'week'
    
    // Verify they are set
    expect(wrapper.vm.filters.tipo_reporte).toBe('calidad')
    expect(wrapper.vm.selectedPeriod).toBe('week')
    
    // Call clearFilters which sets filters.value = { ...initialFilters }
    // This should update both wrapper.vm.filters and mockUseAdminView.filters.value
    wrapper.vm.clearFilters()
    await wrapper.vm.$nextTick()
    
    // After clearFilters, the filters object should be reset to initialFilters
    // The component does: filters.value = { ...initialFilters }
    // Since wrapper.vm.filters is a reference to filters.value from useAdminView,
    // and clearFilters replaces the entire object, we should check the mock directly
    expect(mockUseAdminView.filters.value.tipo_reporte).toBe('')
    expect(mockUseAdminView.selectedPeriod.value).toBe('month')
    expect(mockUseAdminView.clearFilters).toHaveBeenCalled()
  })

  it('should open report generator', async () => {
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.showReportGenerator).toBe(false)
    wrapper.vm.openReportGenerator()
    expect(wrapper.vm.showReportGenerator).toBe(true)
  })

  it('should handle report created', async () => {
    const newReport = { id: 1, titulo: 'New Report' }
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    wrapper.vm.handleReportCreated(newReport)
    await wrapper.vm.$nextTick()
    
    expect(mockReportsStore.addReport).toHaveBeenCalledWith(newReport)
    expect(wrapper.vm.showReportGenerator).toBe(false)
    expect(Swal.fire).toHaveBeenCalledWith(
      expect.objectContaining({
        icon: 'success',
        title: 'Reporte Creado'
      })
    )
  })

  it('should handle view report', async () => {
    const report = { id: 1, titulo: 'Test Report' }
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    wrapper.vm.handleViewReport(report)
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.selectedReport).toEqual(report)
    expect(wrapper.vm.showReportPreview).toBe(true)
  })

  it('should handle download report', async () => {
    const report = { id: 1, titulo: 'Test Report' }
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    await wrapper.vm.handleDownloadReport(report)
    await flushPromises()
    
    expect(mockReportsStore.downloadReport).toHaveBeenCalledWith(1)
    expect(Swal.fire).toHaveBeenCalledWith(
      expect.objectContaining({
        icon: 'success',
        title: 'Descarga Iniciada'
      })
    )
  })

  it('should handle download report error', async () => {
    const report = { id: 1, titulo: 'Test Report' }
    mockReportsStore.downloadReport.mockRejectedValueOnce(new Error('Download error'))
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    await wrapper.vm.handleDownloadReport(report)
    await flushPromises()
    
    expect(Swal.fire).toHaveBeenCalledWith(
      expect.objectContaining({
        icon: 'error',
        title: 'Error',
        text: 'No se pudo descargar el reporte'
      })
    )
    consoleErrorSpy.mockRestore()
  })

  it('should handle delete report', async () => {
    const report = { id: 1, titulo: 'Test Report' }
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    wrapper.vm.handleDeleteReport(report)
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.pendingDeleteId).toBe(1)
    expect(wrapper.vm.deleteConfirmMessage).toContain('Test Report')
    expect(wrapper.vm.showDeleteConfirm).toBe(true)
  })

  it('should confirm delete report', async () => {
    const report = { id: 1, titulo: 'Test Report' }
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    // Use handleDeleteReport to set pendingDeleteId properly
    wrapper.vm.handleDeleteReport(report)
    await wrapper.vm.$nextTick()
    
    // Now confirm the delete
    await wrapper.vm.confirmDelete()
    await flushPromises()
    
    expect(mockReportsStore.deleteReport).toHaveBeenCalledWith(1)
    expect(Swal.fire).toHaveBeenCalledWith(
      expect.objectContaining({
        icon: 'success',
        title: 'Reporte Eliminado'
      })
    )
    expect(wrapper.vm.showDeleteConfirm).toBe(false)
    expect(wrapper.vm.pendingDeleteId).toBe(null)
  })

  it('should handle confirm delete error', async () => {
    mockReportsStore.deleteReport.mockRejectedValueOnce(new Error('Delete error'))
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    wrapper.vm.pendingDeleteId = 1
    await wrapper.vm.confirmDelete()
    await flushPromises()
    
    expect(Swal.fire).toHaveBeenCalledWith(
      expect.objectContaining({
        icon: 'error',
        title: 'Error',
        text: 'No se pudo eliminar el reporte'
      })
    )
    consoleErrorSpy.mockRestore()
  })

  it('should not confirm delete when pendingDeleteId is null', async () => {
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    wrapper.vm.pendingDeleteId = null
    await wrapper.vm.confirmDelete()
    
    expect(mockReportsStore.deleteReport).not.toHaveBeenCalled()
  })

  it('should handle sort', async () => {
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    await wrapper.vm.handleSort({ key: 'titulo', order: 'asc' })
    await flushPromises()
    
    expect(mockReportsStore.fetchReports).toHaveBeenCalledWith({
      sort_by: 'titulo',
      sort_order: 'asc'
    })
  })

  it('should handle sort error', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    await flushPromises()
    
    // Configure mock after initial mount to avoid consuming it in onMounted
    mockReportsStore.fetchReports.mockRejectedValueOnce(new Error('Sort error'))
    
    await wrapper.vm.handleSort({ key: 'titulo', order: 'asc' })
    await flushPromises()
    
    expect(consoleErrorSpy).toHaveBeenCalled()
    consoleErrorSpy.mockRestore()
  })

  it('should handle select report', async () => {
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.selectedReports).toEqual([])
    wrapper.vm.handleSelectReport(1)
    expect(wrapper.vm.selectedReports).toContain(1)
    
    wrapper.vm.handleSelectReport(1)
    expect(wrapper.vm.selectedReports).not.toContain(1)
  })

  it('should handle select all', async () => {
    const reports = [{ id: 1 }, { id: 2 }, { id: 3 }]
    mockUseAdminView.filteredData.value = reports
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    wrapper.vm.handleSelectAll(true)
    expect(wrapper.vm.selectedReports).toEqual([1, 2, 3])
    
    wrapper.vm.handleSelectAll(false)
    expect(wrapper.vm.selectedReports).toEqual([])
  })

  it('should handle page change', async () => {
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    await wrapper.vm.handlePageChange(2)
    await flushPromises()
    
    expect(mockUseAdminView.paginationComposable.goToPage).toHaveBeenCalledWith(2)
    expect(mockReportsStore.fetchReports).toHaveBeenCalled()
  })

  it('should handle page change error', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    await flushPromises()
    
    // Configure mock after initial mount to avoid consuming it in onMounted
    mockReportsStore.fetchReports.mockRejectedValueOnce(new Error('Page error'))
    
    await wrapper.vm.handlePageChange(2)
    await flushPromises()
    
    expect(consoleErrorSpy).toHaveBeenCalled()
    consoleErrorSpy.mockRestore()
  })

  it('should refresh reports', async () => {
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    await flushPromises()
    
    vi.clearAllMocks()
    await wrapper.vm.refreshReports()
    await flushPromises()
    
    expect(mockReportsStore.fetchReports).toHaveBeenCalled()
  })

  it('should export filtered reports', async () => {
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    await wrapper.vm.exportFiltered()
    await flushPromises()
    
    expect(mockReportsStore.exportReports).toHaveBeenCalledWith(
      expect.objectContaining({
        format: 'excel'
      })
    )
    expect(Swal.fire).toHaveBeenCalledWith(
      expect.objectContaining({
        icon: 'success',
        title: 'Exportación Iniciada'
      })
    )
  })

  it('should handle export filtered error', async () => {
    mockReportsStore.exportReports.mockRejectedValueOnce(new Error('Export error'))
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    await wrapper.vm.exportFiltered()
    await flushPromises()
    
    expect(Swal.fire).toHaveBeenCalledWith(
      expect.objectContaining({
        icon: 'error',
        title: 'Error',
        text: 'No se pudo exportar los reportes'
      })
    )
    consoleErrorSpy.mockRestore()
  })

  it('should bulk export reports', async () => {
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    wrapper.vm.selectedReports = [1, 2, 3]
    await wrapper.vm.bulkExport()
    await flushPromises()
    
    expect(mockReportsStore.exportReports).toHaveBeenCalledWith({
      report_ids: [1, 2, 3],
      format: 'zip'
    })
    expect(Swal.fire).toHaveBeenCalledWith(
      expect.objectContaining({
        icon: 'success',
        title: 'Exportación Iniciada'
      })
    )
  })

  it('should not bulk export when no reports selected', async () => {
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    wrapper.vm.selectedReports = []
    await wrapper.vm.bulkExport()
    
    expect(mockReportsStore.exportReports).not.toHaveBeenCalled()
  })

  it('should handle bulk export error', async () => {
    mockReportsStore.exportReports.mockRejectedValueOnce(new Error('Bulk export error'))
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    wrapper.vm.selectedReports = [1, 2]
    await wrapper.vm.bulkExport()
    await flushPromises()
    
    expect(Swal.fire).toHaveBeenCalledWith(
      expect.objectContaining({
        icon: 'error',
        title: 'Error',
        text: 'No se pudo exportar los reportes seleccionados'
      })
    )
    consoleErrorSpy.mockRestore()
  })

  it('should bulk delete reports', async () => {
    vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    wrapper.vm.selectedReports = [1, 2, 3]
    await wrapper.vm.bulkDelete()
    await flushPromises()
    
    expect(Swal.fire).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Confirmar Eliminación',
        text: expect.stringContaining('3 reportes')
      })
    )
    expect(mockReportsStore.bulkDeleteReports).toHaveBeenCalledWith([1, 2, 3])
    expect(wrapper.vm.selectedReports).toEqual([])
    expect(Swal.fire).toHaveBeenCalledWith(
      expect.objectContaining({
        icon: 'success',
        title: 'Reportes Eliminados'
      })
    )
  })

  it('should not bulk delete when no reports selected', async () => {
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    wrapper.vm.selectedReports = []
    await wrapper.vm.bulkDelete()
    
    // bulkDelete should return early if no reports are selected, so Swal.fire should not be called
    expect(Swal.fire).not.toHaveBeenCalled()
  })

  it('should cancel bulk delete', async () => {
    vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: false })
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    wrapper.vm.selectedReports = [1, 2]
    await wrapper.vm.bulkDelete()
    await flushPromises()
    
    expect(mockReportsStore.bulkDeleteReports).not.toHaveBeenCalled()
  })

  it('should handle bulk delete error', async () => {
    vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })
    mockReportsStore.bulkDeleteReports.mockRejectedValueOnce(new Error('Bulk delete error'))
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()
    
    wrapper.vm.selectedReports = [1, 2]
    await wrapper.vm.bulkDelete()
    await flushPromises()
    
    expect(Swal.fire).toHaveBeenCalledWith(
      expect.objectContaining({
        icon: 'error',
        title: 'Error',
        text: 'No se pudieron eliminar los reportes'
      })
    )
    consoleErrorSpy.mockRestore()
  })

  it('should filter reports by tipo_reporte', () => {
    const reports = [
      { id: 1, tipo_reporte: 'calidad' },
      { id: 2, tipo_reporte: 'finca' }
    ]
    mockReportsStore.reports = reports
    mockUseAdminView.filters.value = { tipo_reporte: 'calidad' }
    
    wrapper = createWrapper()
    const filtered = wrapper.vm.getFilteredReports(mockUseAdminView.filters.value, mockReportsStore)
    
    expect(filtered.length).toBe(1)
    expect(filtered[0].tipo_reporte).toBe('calidad')
  })

  it('should filter reports by formato', () => {
    const reports = [
      { id: 1, formato: 'pdf' },
      { id: 2, formato: 'excel' }
    ]
    mockReportsStore.reports = reports
    mockUseAdminView.filters.value = { formato: 'pdf' }
    
    wrapper = createWrapper()
    const filtered = wrapper.vm.getFilteredReports(mockUseAdminView.filters.value, mockReportsStore)
    
    expect(filtered.length).toBe(1)
    expect(filtered[0].formato).toBe('pdf')
  })

  it('should filter reports by estado', () => {
    const reports = [
      { id: 1, estado: 'completado' },
      { id: 2, estado: 'procesando' }
    ]
    mockReportsStore.reports = reports
    mockUseAdminView.filters.value = { estado: 'completado' }
    
    wrapper = createWrapper()
    const filtered = wrapper.vm.getFilteredReports(mockUseAdminView.filters.value, mockReportsStore)
    
    expect(filtered.length).toBe(1)
    expect(filtered[0].estado).toBe('completado')
  })

  it('should filter reports by usuario_id', () => {
    const reports = [
      { id: 1, usuario_id: 1 },
      { id: 2, usuario_id: 2 }
    ]
    mockReportsStore.reports = reports
    mockUseAdminView.filters.value = { usuario_id: '1' }
    
    wrapper = createWrapper()
    const filtered = wrapper.vm.getFilteredReports(mockUseAdminView.filters.value, mockReportsStore)
    
    expect(filtered.length).toBe(1)
    expect(filtered[0].usuario_id).toBe(1)
  })

  it('should filter reports by fecha_desde', async () => {
    const reports = [
      { id: 1, fecha_solicitud: '2024-01-15' },
      { id: 2, fecha_solicitud: '2024-01-10' }
    ]
    mockReportsStore.reports = reports
    mockUseAdminView.filters.value = { fecha_desde: '2024-01-12' }
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick() // Wait for component to be fully mounted
    
    // Verify the method exists
    expect(wrapper.vm.getFilteredReports).toBeDefined()
    expect(typeof wrapper.vm.getFilteredReports).toBe('function')
    
    const filtered = wrapper.vm.getFilteredReports(mockUseAdminView.filters.value, mockReportsStore)
    
    expect(filtered.length).toBe(1)
    expect(filtered[0].id).toBe(1)
  })

  it('should filter reports by fecha_hasta', async () => {
    const reports = [
      { id: 1, fecha_solicitud: '2024-01-15' },
      { id: 2, fecha_solicitud: '2024-01-20' }
    ]
    mockReportsStore.reports = reports
    mockUseAdminView.filters.value = { fecha_hasta: '2024-01-18' }
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick() // Wait for component to be fully mounted
    
    // Verify the method exists
    expect(wrapper.vm.getFilteredReports).toBeDefined()
    expect(typeof wrapper.vm.getFilteredReports).toBe('function')
    
    const filtered = wrapper.vm.getFilteredReports(mockUseAdminView.filters.value, mockReportsStore)
    
    expect(filtered.length).toBe(1)
    expect(filtered[0].id).toBe(1)
  })

  it('should filter reports by finca_id', async () => {
    const reports = [
      { id: 1, parametros: { finca_id: 1 } },
      { id: 2, parametros: { finca_id: 2 } }
    ]
    mockReportsStore.reports = reports
    mockUseAdminView.filters.value = { finca_id: '1' }
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick() // Wait for component to be fully mounted
    
    // Verify the method exists
    expect(wrapper.vm.getFilteredReports).toBeDefined()
    expect(typeof wrapper.vm.getFilteredReports).toBe('function')
    
    const filtered = wrapper.vm.getFilteredReports(mockUseAdminView.filters.value, mockReportsStore)
    
    expect(filtered.length).toBe(1)
    expect(filtered[0].id).toBe(1)
  })

  it('should filter reports by lote_id', async () => {
    const reports = [
      { id: 1, parametros: { lote_id: 1 } },
      { id: 2, parametros: { lote_id: 2 } }
    ]
    mockReportsStore.reports = reports
    mockUseAdminView.filters.value = { lote_id: '1' }
    
    wrapper = createWrapper()
    await wrapper.vm.$nextTick() // Wait for component to be fully mounted
    
    // Verify the method exists
    expect(wrapper.vm.getFilteredReports).toBeDefined()
    expect(typeof wrapper.vm.getFilteredReports).toBe('function')
    
    const filtered = wrapper.vm.getFilteredReports(mockUseAdminView.filters.value, mockReportsStore)
    
    expect(filtered.length).toBe(1)
    expect(filtered[0].id).toBe(1)
  })

  it('should apply multiple filters', () => {
    const reports = [
      { id: 1, tipo_reporte: 'calidad', formato: 'pdf', estado: 'completado' },
      { id: 2, tipo_reporte: 'calidad', formato: 'excel', estado: 'completado' },
      { id: 3, tipo_reporte: 'finca', formato: 'pdf', estado: 'completado' }
    ]
    mockReportsStore.reports = reports
    mockUseAdminView.filters.value = {
      tipo_reporte: 'calidad',
      formato: 'pdf',
      estado: 'completado'
    }
    
    wrapper = createWrapper()
    const filtered = wrapper.vm.getFilteredReports(mockUseAdminView.filters.value, mockReportsStore)
    
    expect(filtered.length).toBe(1)
    expect(filtered[0].id).toBe(1)
  })
})

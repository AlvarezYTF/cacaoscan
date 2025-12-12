import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ReportsTimeline from '../ReportsTimeline.vue'

describe('ReportsTimeline', () => {
  let wrapper

  const mockReports = [
    {
      id: 1,
      titulo: 'Reporte de Calidad',
      tipo_reporte: 'calidad',
      formato: 'pdf',
      estado: 'completado',
      fecha_solicitud: '2024-01-15T10:00:00Z',
      descripcion: 'Reporte de calidad del lote',
      usuario_nombre: 'Usuario Test',
      tamaño_archivo: 1024000,
      tiempo_generacion: 120,
      parametros: {
        finca_id: 1,
        finca_nombre: 'Finca Test',
        lote_id: 1,
        lote_identificador: 'LOTE-001'
      }
    },
    {
      id: 2,
      titulo: 'Reporte de Finca',
      tipo_reporte: 'finca',
      formato: 'excel',
      estado: 'procesando',
      fecha_solicitud: '2024-01-16T10:00:00Z',
      descripcion: null,
      usuario_nombre: 'Usuario Test 2',
      tamaño_archivo: null,
      tiempo_generacion: null,
      parametros: null
    },
    {
      id: 3,
      titulo: 'Reporte de Auditoría',
      tipo_reporte: 'auditoria',
      formato: 'csv',
      estado: 'pendiente',
      fecha_solicitud: '2024-01-17T10:00:00Z'
    },
    {
      id: 4,
      titulo: 'Reporte con Error',
      tipo_reporte: 'personalizado',
      formato: 'json',
      estado: 'error',
      fecha_solicitud: '2024-01-18T10:00:00Z',
      parametros: {
        custom_type: 'Custom Type'
      }
    }
  ]

  const createWrapper = (props = {}) => {
    return mount(ReportsTimeline, {
      props: {
        reports: [],
        loading: false,
        ...props
      }
    })
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render component', () => {
    wrapper = createWrapper()
    expect(wrapper.exists()).toBe(true)
  })

  it('should display loading state', () => {
    wrapper = createWrapper({ loading: true })
    
    expect(wrapper.find('.timeline-loading').exists()).toBe(true)
    expect(wrapper.text()).toContain('Cargando reportes...')
  })

  it('should display empty state when no reports', () => {
    wrapper = createWrapper({ reports: [] })
    
    expect(wrapper.find('.timeline-empty').exists()).toBe(true)
    expect(wrapper.text()).toContain('No hay reportes')
    expect(wrapper.text()).toContain('No se encontraron reportes')
  })

  it('should display reports timeline', () => {
    wrapper = createWrapper({ reports: mockReports })
    
    expect(wrapper.find('.timeline-container').exists()).toBe(true)
    expect(wrapper.find('.timeline-header').exists()).toBe(true)
    expect(wrapper.text()).toContain('Cronología de Reportes')
    expect(wrapper.text()).toContain('4 reportes')
  })

  it('should render all reports', () => {
    wrapper = createWrapper({ reports: mockReports })
    
    const items = wrapper.findAll('.timeline-item')
    expect(items.length).toBe(4)
  })

  it('should mark last item with last class', () => {
    wrapper = createWrapper({ reports: mockReports })
    
    const items = wrapper.findAll('.timeline-item')
    expect(items.at(-1).classes()).toContain('last')
  })

  it('should display report title', () => {
    wrapper = createWrapper({ reports: [mockReports[0]] })
    
    expect(wrapper.text()).toContain('Reporte de Calidad')
  })

  it('should display report type label', () => {
    wrapper = createWrapper({ reports: [mockReports[0]] })
    
    expect(wrapper.text()).toContain('Calidad')
  })

  it('should display report format', () => {
    wrapper = createWrapper({ reports: [mockReports[0]] })
    
    expect(wrapper.text()).toContain('PDF')
  })

  it('should display report date', () => {
    wrapper = createWrapper({ reports: [mockReports[0]] })
    
    const dateText = wrapper.vm.formatDate('2024-01-15T10:00:00Z')
    expect(wrapper.text()).toContain(dateText)
  })

  it('should display status indicator', () => {
    wrapper = createWrapper({ reports: [mockReports[0]] })
    
    const statusIndicator = wrapper.find('.status-indicator')
    expect(statusIndicator.exists()).toBe(true)
    expect(statusIndicator.classes()).toContain('status-completed')
  })

  it('should display description when available', () => {
    wrapper = createWrapper({ reports: [mockReports[0]] })
    
    expect(wrapper.text()).toContain('Reporte de calidad del lote')
  })

  it('should not display description when null', () => {
    wrapper = createWrapper({ reports: [mockReports[1]] })
    
    expect(wrapper.find('.report-description').exists()).toBe(false)
  })

  it('should display report info', () => {
    wrapper = createWrapper({ reports: [mockReports[0]] })
    
    expect(wrapper.text()).toContain('Usuario Test')
    expect(wrapper.find('.info-grid').exists()).toBe(true)
  })

  it('should display file size', () => {
    wrapper = createWrapper({ reports: [mockReports[0]] })
    
    const fileSize = wrapper.vm.formatFileSize(1024000)
    expect(wrapper.text()).toContain(fileSize)
  })

  it('should display duration', () => {
    wrapper = createWrapper({ reports: [mockReports[0]] })
    
    const duration = wrapper.vm.formatDuration(120)
    expect(wrapper.text()).toContain(duration)
  })

  it('should display date time', () => {
    wrapper = createWrapper({ reports: [mockReports[0]] })
    
    const dateTime = wrapper.vm.formatDateTime('2024-01-15T10:00:00Z')
    expect(wrapper.text()).toContain(dateTime)
  })

  it('should display parameters when available', () => {
    wrapper = createWrapper({ reports: [mockReports[0]] })
    
    expect(wrapper.find('.report-parameters').exists()).toBe(true)
    expect(wrapper.text()).toContain('Finca Test')
    expect(wrapper.text()).toContain('LOTE-001')
  })

  it('should display custom type parameter', () => {
    wrapper = createWrapper({ reports: [mockReports[3]] })
    
    expect(wrapper.text()).toContain('Custom Type')
  })

  it('should not display parameters when null', () => {
    wrapper = createWrapper({ reports: [mockReports[1]] })
    
    expect(wrapper.find('.report-parameters').exists()).toBe(false)
  })

  it('should emit view event when view button clicked', async () => {
    wrapper = createWrapper({ reports: [mockReports[0]] })
    
    const viewButton = wrapper.find('button.btn-outline')
    await viewButton.trigger('click')
    
    expect(wrapper.emitted('view')).toBeTruthy()
    expect(wrapper.emitted('view')[0]).toEqual([mockReports[0]])
  })

  it('should emit download event when download button clicked', async () => {
    wrapper = createWrapper({ reports: [mockReports[0]] })
    
    const downloadButton = wrapper.find('button.btn-primary')
    await downloadButton.trigger('click')
    
    expect(wrapper.emitted('download')).toBeTruthy()
    expect(wrapper.emitted('download')[0]).toEqual([mockReports[0]])
  })

  it('should disable buttons when estado is not completado', () => {
    wrapper = createWrapper({ reports: [mockReports[1]] })
    
    const viewButton = wrapper.find('button.btn-outline')
    const downloadButton = wrapper.find('button.btn-primary')
    
    expect(viewButton.attributes('disabled')).toBeDefined()
    expect(downloadButton.attributes('disabled')).toBeDefined()
  })

  it('should enable buttons when estado is completado', () => {
    wrapper = createWrapper({ reports: [mockReports[0]] })
    
    const viewButton = wrapper.find('button.btn-outline')
    const downloadButton = wrapper.find('button.btn-primary')
    
    expect(viewButton.attributes('disabled')).toBeUndefined()
    expect(downloadButton.attributes('disabled')).toBeUndefined()
  })

  describe('getReportTypeLabel', () => {
    it('should return correct label for calidad', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getReportTypeLabel('calidad')).toBe('Calidad')
    })

    it('should return correct label for finca', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getReportTypeLabel('finca')).toBe('Finca')
    })

    it('should return correct label for lote', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getReportTypeLabel('lote')).toBe('Lote')
    })

    it('should return correct label for usuario', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getReportTypeLabel('usuario')).toBe('Usuario')
    })

    it('should return correct label for auditoria', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getReportTypeLabel('auditoria')).toBe('Auditoría')
    })

    it('should return correct label for personalizado', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getReportTypeLabel('personalizado')).toBe('Personalizado')
    })

    it('should return correct label for metricas', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getReportTypeLabel('metricas')).toBe('Métricas')
    })

    it('should return correct label for entrenamiento', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getReportTypeLabel('entrenamiento')).toBe('Entrenamiento')
    })

    it('should return type as fallback for unknown type', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getReportTypeLabel('unknown')).toBe('unknown')
    })
  })

  describe('getStatusLabel', () => {
    it('should return correct label for pendiente', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getStatusLabel('pendiente')).toBe('Pendiente')
    })

    it('should return correct label for procesando', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getStatusLabel('procesando')).toBe('Procesando')
    })

    it('should return correct label for completado', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getStatusLabel('completado')).toBe('Completado')
    })

    it('should return correct label for error', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getStatusLabel('error')).toBe('Error')
    })

    it('should return status as fallback for unknown status', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getStatusLabel('unknown')).toBe('unknown')
    })
  })

  describe('getStatusClass', () => {
    it('should return correct class for pendiente', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getStatusClass('pendiente')).toBe('status-pending')
    })

    it('should return correct class for procesando', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getStatusClass('procesando')).toBe('status-processing')
    })

    it('should return correct class for completado', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getStatusClass('completado')).toBe('status-completed')
    })

    it('should return correct class for error', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getStatusClass('error')).toBe('status-error')
    })

    it('should return status-pending as fallback', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getStatusClass('unknown')).toBe('status-pending')
    })
  })

  describe('getStatusIcon', () => {
    it('should return correct icon for pendiente', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getStatusIcon('pendiente')).toBe('fas fa-clock')
    })

    it('should return correct icon for procesando', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getStatusIcon('procesando')).toBe('fas fa-spinner fa-spin')
    })

    it('should return correct icon for completado', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getStatusIcon('completado')).toBe('fas fa-check-circle')
    })

    it('should return correct icon for error', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getStatusIcon('error')).toBe('fas fa-exclamation-circle')
    })

    it('should return fas fa-clock as fallback', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.getStatusIcon('unknown')).toBe('fas fa-clock')
    })
  })

  describe('formatDate', () => {
    it('should format date correctly', () => {
      wrapper = createWrapper()
      const formatted = wrapper.vm.formatDate('2024-01-15T10:00:00Z')
      expect(formatted).toBeTruthy()
      expect(typeof formatted).toBe('string')
    })

    it('should return N/A for null date', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.formatDate(null)).toBe('N/A')
    })

    it('should return N/A for undefined date', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.formatDate(undefined)).toBe('N/A')
    })
  })

  describe('formatDateTime', () => {
    it('should format date time correctly', () => {
      wrapper = createWrapper()
      const formatted = wrapper.vm.formatDateTime('2024-01-15T10:00:00Z')
      expect(formatted).toBeTruthy()
      expect(typeof formatted).toBe('string')
    })

    it('should return N/A for null date', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.formatDateTime(null)).toBe('N/A')
    })

    it('should return N/A for undefined date', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.formatDateTime(undefined)).toBe('N/A')
    })
  })

  describe('formatFileSize', () => {
    it('should format bytes correctly', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.formatFileSize(1024)).toContain('KB')
    })

    it('should format MB correctly', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.formatFileSize(1048576)).toContain('MB')
    })

    it('should format GB correctly', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.formatFileSize(1073741824)).toContain('GB')
    })

    it('should return N/A for null bytes', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.formatFileSize(null)).toBe('N/A')
    })

    it('should return N/A for undefined bytes', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.formatFileSize(undefined)).toBe('N/A')
    })
  })

  describe('formatDuration', () => {
    it('should format duration correctly', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.formatDuration(120)).toBe('2m 0s')
    })

    it('should format duration with remaining seconds', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.formatDuration(125)).toBe('2m 5s')
    })

    it('should format duration less than a minute', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.formatDuration(30)).toBe('0m 30s')
    })

    it('should return N/A for null duration', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.formatDuration(null)).toBe('N/A')
    })

    it('should return N/A for undefined duration', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.formatDuration(undefined)).toBe('N/A')
    })
  })

  it('should display usuario_nombre or fallback', () => {
    const reportWithUser = { ...mockReports[0], usuario_nombre: 'Test User' }
    wrapper = createWrapper({ reports: [reportWithUser] })
    
    expect(wrapper.text()).toContain('Test User')
  })

  it('should display Usuario as fallback when usuario_nombre is missing', () => {
    const reportWithoutUser = { ...mockReports[0], usuario_nombre: null }
    wrapper = createWrapper({ reports: [reportWithoutUser] })
    
    expect(wrapper.text()).toContain('Usuario')
  })

  it('should display finca_id when finca_nombre is missing', () => {
    const reportWithIdOnly = {
      ...mockReports[0],
      parametros: { finca_id: 1 }
    }
    wrapper = createWrapper({ reports: [reportWithIdOnly] })
    
    expect(wrapper.text()).toContain('1')
  })

  it('should display lote_id when lote_identificador is missing', () => {
    const reportWithIdOnly = {
      ...mockReports[0],
      parametros: { lote_id: 1 }
    }
    wrapper = createWrapper({ reports: [reportWithIdOnly] })
    
    expect(wrapper.text()).toContain('1')
  })
})



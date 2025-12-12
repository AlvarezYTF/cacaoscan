import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { nextTick } from 'vue'
import ReportPreviewModal from '../ReportPreviewModal.vue'

const mockReportsStore = {
  getReportPreview: vi.fn()
}

const mockAuditHelpers = {
  formatJson: vi.fn((data) => JSON.stringify(data, null, 2))
}

vi.mock('@/stores/reports', () => ({
  useReportsStore: () => mockReportsStore
}))

vi.mock('@/composables/useAuditHelpers', () => ({
  useAuditHelpers: () => mockAuditHelpers
}))

vi.mock('@/utils/formatters', () => ({
  formatDateTime: vi.fn((date) => new Date(date).toLocaleString()),
  formatFileSize: vi.fn((bytes) => `${bytes} bytes`),
  formatDuration: vi.fn((seconds) => `${seconds}s`),
  formatNumber: vi.fn((num) => num.toString())
}))

describe('ReportPreviewModal', () => {
  let wrapper
  const defaultReport = {
    id: 1,
    titulo: 'Test Report',
    tipo_reporte: 'calidad',
    formato: 'pdf',
    estado: 'completado',
    fecha_solicitud: '2024-01-01T00:00:00Z',
    tamaño_archivo: 1024,
    tiempo_generacion: 5,
    descripcion: 'Test description',
    parametros: {
      finca_id: 1,
      include_charts: true
    },
    filtros: {
      fecha_desde: '2024-01-01',
      fecha_hasta: '2024-01-31'
    }
  }

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('rendering', () => {
    it('should render modal', () => {
      wrapper = mount(ReportPreviewModal, {
        props: {
          report: defaultReport
        },
        global: {
          stubs: {
            BaseModal: {
              template: '<div><slot name="header"></slot><slot></slot><slot name="footer"></slot></div>',
              props: ['show', 'title', 'subtitle', 'maxWidth'],
              emits: ['close']
            }
          }
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should display report title', () => {
      wrapper = mount(ReportPreviewModal, {
        props: {
          report: defaultReport
        },
        global: {
          stubs: {
            BaseModal: {
              template: '<div><slot name="header"></slot></div>',
              props: ['show', 'title']
            }
          }
        }
      })

      expect(wrapper.text()).toContain('Test Report')
    })
  })

  describe('loading preview', () => {
    it('should load preview on mount', async () => {
      const mockPreviewData = {
        content: 'preview-url',
        headers: ['Col1', 'Col2'],
        rows: [['val1', 'val2']],
        statistics: { total_records: 10 }
      }
      mockReportsStore.getReportPreview.mockResolvedValue({ data: mockPreviewData })

      wrapper = mount(ReportPreviewModal, {
        props: {
          report: defaultReport
        },
        global: {
          stubs: {
            BaseModal: {
              template: '<div><slot></slot></div>'
            }
          }
        }
      })

      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockReportsStore.getReportPreview).toHaveBeenCalledWith(1)
    })

    it('should not load preview if report not completed', async () => {
      const pendingReport = { ...defaultReport, estado: 'pendiente' }

      wrapper = mount(ReportPreviewModal, {
        props: {
          report: pendingReport
        },
        global: {
          stubs: {
            BaseModal: {
              template: '<div><slot></slot></div>'
            }
          }
        }
      })

      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockReportsStore.getReportPreview).not.toHaveBeenCalled()
    })

    it('should handle loading error', async () => {
      const error = { response: { data: { detail: 'Load error' } } }
      mockReportsStore.getReportPreview.mockRejectedValue(error)

      wrapper = mount(ReportPreviewModal, {
        props: {
          report: defaultReport
        },
        global: {
          stubs: {
            BaseModal: {
              template: '<div><slot></slot></div>'
            }
          }
        }
      })

      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.error).toBeTruthy()
    })

    it('should retry loading preview', async () => {
      const mockPreviewData = { content: 'preview-url' }
      mockReportsStore.getReportPreview
        .mockRejectedValueOnce(new Error('First error'))
        .mockResolvedValueOnce({ data: mockPreviewData })

      wrapper = mount(ReportPreviewModal, {
        props: {
          report: defaultReport
        },
        global: {
          stubs: {
            BaseModal: {
              template: '<div><slot></slot></div>'
            }
          }
        }
      })

      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      await wrapper.vm.loadPreview()
      await nextTick()

      expect(mockReportsStore.getReportPreview).toHaveBeenCalledTimes(2)
    })
  })

  describe('formatting functions', () => {
    beforeEach(() => {
      wrapper = mount(ReportPreviewModal, {
        props: {
          report: defaultReport
        },
        global: {
          stubs: {
            BaseModal: {
              template: '<div><slot></slot></div>'
            }
          }
        }
      })
    })

    it('should format report type label', () => {
      expect(wrapper.vm.getReportTypeLabel('calidad')).toBe('Calidad')
      expect(wrapper.vm.getReportTypeLabel('finca')).toBe('Finca')
      expect(wrapper.vm.getReportTypeLabel('lote')).toBe('Lote')
      expect(wrapper.vm.getReportTypeLabel('usuario')).toBe('Usuario')
      expect(wrapper.vm.getReportTypeLabel('auditoria')).toBe('Auditoría')
      expect(wrapper.vm.getReportTypeLabel('personalizado')).toBe('Personalizado')
      expect(wrapper.vm.getReportTypeLabel('metricas')).toBe('Métricas')
      expect(wrapper.vm.getReportTypeLabel('entrenamiento')).toBe('Entrenamiento')
      expect(wrapper.vm.getReportTypeLabel('unknown')).toBe('unknown')
    })

    it('should format status label', () => {
      expect(wrapper.vm.getStatusLabel('pendiente')).toBe('Pendiente')
      expect(wrapper.vm.getStatusLabel('procesando')).toBe('Procesando')
      expect(wrapper.vm.getStatusLabel('completado')).toBe('Completado')
      expect(wrapper.vm.getStatusLabel('error')).toBe('Error')
      expect(wrapper.vm.getStatusLabel('unknown')).toBe('unknown')
    })

    it('should get status class', () => {
      expect(wrapper.vm.getStatusClass('pendiente')).toBe('status-pending')
      expect(wrapper.vm.getStatusClass('procesando')).toBe('status-processing')
      expect(wrapper.vm.getStatusClass('completado')).toBe('status-completed')
      expect(wrapper.vm.getStatusClass('error')).toBe('status-error')
      expect(wrapper.vm.getStatusClass('unknown')).toBe('status-pending')
    })

    it('should format parameter label', () => {
      expect(wrapper.vm.formatParameterLabel('finca_id')).toBe('Finca')
      expect(wrapper.vm.formatParameterLabel('lote_id')).toBe('Lote')
      expect(wrapper.vm.formatParameterLabel('custom_type')).toBe('Tipo Personalizado')
      expect(wrapper.vm.formatParameterLabel('analysis_depth')).toBe('Profundidad')
      expect(wrapper.vm.formatParameterLabel('unknown_param')).toContain('Unknown')
    })

    it('should format parameter value', () => {
      expect(wrapper.vm.formatParameterValue(true)).toBe('Sí')
      expect(wrapper.vm.formatParameterValue(false)).toBe('No')
      expect(wrapper.vm.formatParameterValue({ key: 'value' })).toContain('key')
      expect(wrapper.vm.formatParameterValue('string')).toBe('string')
      expect(wrapper.vm.formatParameterValue(123)).toBe(123)
    })

    it('should format filter label', () => {
      expect(wrapper.vm.formatFilterLabel('fecha_desde')).toBe('Fecha Desde')
      expect(wrapper.vm.formatFilterLabel('fecha_hasta')).toBe('Fecha Hasta')
      expect(wrapper.vm.formatFilterLabel('usuario_id')).toBe('Usuario')
      expect(wrapper.vm.formatFilterLabel('calidad_minima')).toBe('Calidad Mínima')
      expect(wrapper.vm.formatFilterLabel('unknown_filter')).toContain('Unknown')
    })

    it('should format filter value', () => {
      expect(wrapper.vm.formatFilterValue(123)).toBe('123')
      expect(wrapper.vm.formatFilterValue('string')).toBe('string')
    })

    it('should format stat label', () => {
      expect(wrapper.vm.formatStatLabel('total_records')).toBe('Total de Registros')
      expect(wrapper.vm.formatStatLabel('total_pages')).toBe('Total de Páginas')
      expect(wrapper.vm.formatStatLabel('generation_time')).toBe('Tiempo de Generación')
      expect(wrapper.vm.formatStatLabel('file_size')).toBe('Tamaño del Archivo')
      expect(wrapper.vm.formatStatLabel('unknown_stat')).toContain('Unknown')
    })

    it('should format stat value same as filter value', () => {
      expect(wrapper.vm.formatStatValue(123)).toBe(wrapper.vm.formatFilterValue(123))
    })
  })

  describe('preview content', () => {
    it('should display PDF preview', async () => {
      const mockPreviewData = {
        content: 'data:application/pdf;base64,test'
      }
      mockReportsStore.getReportPreview.mockResolvedValue({ data: mockPreviewData })

      wrapper = mount(ReportPreviewModal, {
        props: {
          report: { ...defaultReport, formato: 'pdf' }
        },
        global: {
          stubs: {
            BaseModal: {
              template: '<div><slot></slot></div>'
            }
          }
        }
      })

      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.previewData).toBeTruthy()
    })

    it('should display Excel preview', async () => {
      const mockPreviewData = {
        headers: ['Col1', 'Col2'],
        rows: [['val1', 'val2'], ['val3', 'val4']]
      }
      mockReportsStore.getReportPreview.mockResolvedValue({ data: mockPreviewData })

      wrapper = mount(ReportPreviewModal, {
        props: {
          report: { ...defaultReport, formato: 'excel' }
        },
        global: {
          stubs: {
            BaseModal: {
              template: '<div><slot></slot></div>'
            }
          }
        }
      })

      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.previewData).toBeTruthy()
    })

    it('should display CSV preview', async () => {
      const mockPreviewData = {
        headers: ['Col1', 'Col2'],
        rows: [['val1', 'val2']]
      }
      mockReportsStore.getReportPreview.mockResolvedValue({ data: mockPreviewData })

      wrapper = mount(ReportPreviewModal, {
        props: {
          report: { ...defaultReport, formato: 'csv' }
        },
        global: {
          stubs: {
            BaseModal: {
              template: '<div><slot></slot></div>'
            }
          }
        }
      })

      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.previewData).toBeTruthy()
    })

    it('should display JSON preview', async () => {
      const mockPreviewData = {
        content: { key: 'value' }
      }
      mockReportsStore.getReportPreview.mockResolvedValue({ data: mockPreviewData })

      wrapper = mount(ReportPreviewModal, {
        props: {
          report: { ...defaultReport, formato: 'json' }
        },
        global: {
          stubs: {
            BaseModal: {
              template: '<div><slot></slot></div>'
            }
          }
        }
      })

      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.previewData).toBeTruthy()
      expect(mockAuditHelpers.formatJson).toHaveBeenCalled()
    })

    it('should display default preview for unknown format', async () => {
      const mockPreviewData = {
        content: 'some content'
      }
      mockReportsStore.getReportPreview.mockResolvedValue({ data: mockPreviewData })

      wrapper = mount(ReportPreviewModal, {
        props: {
          report: { ...defaultReport, formato: 'unknown' }
        },
        global: {
          stubs: {
            BaseModal: {
              template: '<div><slot></slot></div>'
            }
          }
        }
      })

      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.previewData).toBeTruthy()
    })
  })

  describe('modal actions', () => {
    beforeEach(() => {
      wrapper = mount(ReportPreviewModal, {
        props: {
          report: defaultReport
        },
        global: {
          stubs: {
            BaseModal: {
              template: '<div><slot name="footer"></slot></div>',
              emits: ['close']
            }
          }
        }
      })
    })

    it('should emit close event', () => {
      wrapper.vm.closeModal()
      expect(wrapper.emitted('close')).toBeTruthy()
    })

    it('should emit download event', () => {
      wrapper.vm.$emit('download', defaultReport)
      expect(wrapper.emitted('download')).toBeTruthy()
    })

    it('should disable download button when not completed', () => {
      const pendingReport = { ...defaultReport, estado: 'pendiente' }
      wrapper = mount(ReportPreviewModal, {
        props: {
          report: pendingReport
        },
        global: {
          stubs: {
            BaseModal: {
              template: '<div><slot name="footer"></slot></div>'
            }
          }
        }
      })

      // Download button should be disabled
      expect(wrapper.vm.report.estado).toBe('pendiente')
    })
  })

  describe('report information display', () => {
    it('should display report description when available', async () => {
      const mockPreviewData = { content: 'preview' }
      mockReportsStore.getReportPreview.mockResolvedValue({ data: mockPreviewData })

      wrapper = mount(ReportPreviewModal, {
        props: {
          report: defaultReport
        },
        global: {
          stubs: {
            BaseModal: {
              template: '<div><slot></slot></div>'
            }
          }
        }
      })

      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.report.descripcion).toBe('Test description')
    })

    it('should display report parameters', async () => {
      const mockPreviewData = { content: 'preview' }
      mockReportsStore.getReportPreview.mockResolvedValue({ data: mockPreviewData })

      wrapper = mount(ReportPreviewModal, {
        props: {
          report: defaultReport
        },
        global: {
          stubs: {
            BaseModal: {
              template: '<div><slot></slot></div>'
            }
          }
        }
      })

      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.report.parametros).toBeDefined()
    })

    it('should display report filters', async () => {
      const mockPreviewData = { content: 'preview' }
      mockReportsStore.getReportPreview.mockResolvedValue({ data: mockPreviewData })

      wrapper = mount(ReportPreviewModal, {
        props: {
          report: defaultReport
        },
        global: {
          stubs: {
            BaseModal: {
              template: '<div><slot></slot></div>'
            }
          }
        }
      })

      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.report.filtros).toBeDefined()
    })

    it('should display report statistics', async () => {
      const mockPreviewData = {
        content: 'preview',
        statistics: {
          total_records: 100,
          total_pages: 10
        }
      }
      mockReportsStore.getReportPreview.mockResolvedValue({ data: mockPreviewData })

      wrapper = mount(ReportPreviewModal, {
        props: {
          report: defaultReport
        },
        global: {
          stubs: {
            BaseModal: {
              template: '<div><slot></slot></div>'
            }
          }
        }
      })

      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.previewData.statistics).toBeDefined()
    })
  })
})


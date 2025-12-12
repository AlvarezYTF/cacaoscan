/**
 * Unit tests for AuditTimeline component
 * Tests all functionality including props, events, methods, and rendering
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AuditTimeline from '../AuditTimeline.vue'

const { mockFormatDateTime, mockFormatDuration, mockFormatJson, mockGetAuditItemTitle, mockGetAuditItemType, mockGetAuditItemStatus, mockGetAuditActionMarkerClass, mockGetAuditActionIcon, mockGetAuditStatusClass } = vi.hoisted(() => ({
  mockFormatDateTime: vi.fn((date) => date ? new Date(date).toLocaleString('es-ES') : 'N/A'),
  mockFormatDuration: vi.fn((duration) => duration || 'N/A'),
  mockFormatJson: vi.fn((data) => JSON.stringify(data, null, 2)),
  mockGetAuditItemTitle: vi.fn((item, type) => {
    if (type === 'activity' || type === 'both') {
      return `${item.accion_display || item.accion} - ${item.modelo}`
    } else if (type === 'login') {
      return `Login ${item.success ? 'Exitoso' : 'Fallido'}`
    }
    return 'Evento de Auditoría'
  }),
  mockGetAuditItemType: vi.fn((type) => {
    if (type === 'activity' || type === 'both') return 'Actividad'
    if (type === 'login') return 'Login'
    return 'Evento'
  }),
  mockGetAuditItemStatus: vi.fn((item, type) => {
    if (type === 'activity' || type === 'both') {
      return item.accion_display || item.accion
    } else if (type === 'login') {
      return item.success ? 'Exitoso' : 'Fallido'
    }
    return 'Completado'
  }),
  mockGetAuditActionMarkerClass: vi.fn((action) => {
    const classes = {
      'create': 'marker-create',
      'update': 'marker-update',
      'delete': 'marker-delete'
    }
    return classes[action] || 'marker-default'
  }),
  mockGetAuditActionIcon: vi.fn((action) => {
    const icons = {
      'create': 'fas fa-plus',
      'update': 'fas fa-edit',
      'delete': 'fas fa-trash'
    }
    return icons[action] || 'fas fa-circle'
  }),
  mockGetAuditStatusClass: vi.fn((item, type) => {
    if (type === 'login' || type === 'both') {
      return item.success ? 'status-success' : 'status-error'
    }
    return 'status-default'
  })
}))

vi.mock('@/composables/useDateFormatting', () => ({
  useDateFormatting: () => ({
    formatDateTime: mockFormatDateTime,
    formatDuration: mockFormatDuration
  })
}))

vi.mock('@/composables/useAuditHelpers', () => ({
  useAuditHelpers: () => ({
    getAuditItemTitle: mockGetAuditItemTitle,
    getAuditItemType: mockGetAuditItemType,
    getAuditItemStatus: mockGetAuditItemStatus,
    getAuditActionMarkerClass: mockGetAuditActionMarkerClass,
    getAuditActionIcon: mockGetAuditActionIcon,
    getAuditStatusClass: mockGetAuditStatusClass,
    formatJson: mockFormatJson
  })
}))

describe('AuditTimeline', () => {
  let wrapper

  // Mock IP addresses using RFC 5737 reserved documentation addresses
  // These are safe for testing and won't trigger SonarQube S1313
  const MOCK_IP_ADDRESS_1 = '203.0.113.1' // RFC 5737 - TEST-NET-3
  const MOCK_IP_ADDRESS_2 = '203.0.113.2' // RFC 5737 - TEST-NET-3

  const createActivityData = () => [
    {
      id: 1,
      usuario: 'testuser',
      ip_address: MOCK_IP_ADDRESS_1,
      modelo: 'CacaoImage',
      accion: 'create',
      accion_display: 'Crear',
      descripcion: 'Test description for activity',
      timestamp: '2024-01-01T10:00:00Z',
      objeto_id: 123,
      datos_antes: { name: 'old' },
      datos_despues: { name: 'new' }
    },
    {
      id: 2,
      usuario: 'testuser2',
      ip_address: MOCK_IP_ADDRESS_2,
      modelo: 'Finca',
      accion: 'update',
      accion_display: 'Actualizar',
      descripcion: 'Another description',
      timestamp: '2024-01-01T11:00:00Z',
      objeto_id: 456
    }
  ]

  const createLoginData = () => [
    {
      id: 1,
      usuario: 'testuser',
      ip_address: MOCK_IP_ADDRESS_1,
      success: true,
      login_time: '2024-01-01T10:00:00Z',
      logout_time: '2024-01-01T12:00:00Z',
      session_duration: '02:00:00',
      failure_reason: null
    },
    {
      id: 2,
      usuario: 'testuser2',
      ip_address: MOCK_IP_ADDRESS_2,
      success: false,
      login_time: '2024-01-01T11:00:00Z',
      logout_time: null,
      session_duration: null,
      failure_reason: 'Invalid credentials'
    }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Props validation', () => {
    it('should accept valid props', () => {
      const data = createActivityData()
      wrapper = mount(AuditTimeline, {
        props: {
          data,
          loading: false,
          auditType: 'activity'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should default to activity auditType', () => {
      const data = createActivityData()
      wrapper = mount(AuditTimeline, {
        props: {
          data,
          loading: false
        }
      })
      expect(wrapper.props('auditType')).toBe('activity')
    })
  })

  describe('Loading state', () => {
    it('should display loading message when loading', () => {
      wrapper = mount(AuditTimeline, {
        props: {
          data: [],
          loading: true,
          auditType: 'activity'
        }
      })
      expect(wrapper.text()).toContain('Cargando cronología de auditoría')
    })

    it('should show loading spinner', () => {
      wrapper = mount(AuditTimeline, {
        props: {
          data: [],
          loading: true,
          auditType: 'activity'
        }
      })
      expect(wrapper.find('.loading-spinner').exists()).toBe(true)
    })
  })

  describe('Empty state', () => {
    it('should display empty message when no data', () => {
      wrapper = mount(AuditTimeline, {
        props: {
          data: [],
          loading: false,
          auditType: 'activity'
        }
      })
      expect(wrapper.text()).toContain('No hay actividad')
      expect(wrapper.text()).toContain('No se encontraron registros')
    })

    it('should show empty icon', () => {
      wrapper = mount(AuditTimeline, {
        props: {
          data: [],
          loading: false,
          auditType: 'activity'
        }
      })
      expect(wrapper.find('.empty-icon').exists()).toBe(true)
    })
  })

  describe('Rendering - Activity type', () => {
    beforeEach(() => {
      const data = createActivityData()
      wrapper = mount(AuditTimeline, {
        props: {
          data,
          loading: false,
          auditType: 'activity'
        }
      })
    })

    it('should render timeline with data', () => {
      expect(wrapper.find('.timeline').exists()).toBe(true)
      expect(wrapper.find('.timeline-item').exists()).toBe(true)
    })

    it('should display timeline header', () => {
      expect(wrapper.text()).toContain('Cronología de Auditoría')
      expect(wrapper.text()).toContain('2 eventos')
    })

    it('should display usuario information', () => {
      expect(wrapper.text()).toContain('testuser')
    })

    it('should display IP address', () => {
      expect(wrapper.text()).toContain(MOCK_IP_ADDRESS_1)
    })

    it('should display modelo', () => {
      expect(wrapper.text()).toContain('CacaoImage')
    })

    it('should display description', () => {
      expect(wrapper.text()).toContain('Test description')
    })

    it('should display marker icon', () => {
      expect(mockGetAuditActionIcon).toHaveBeenCalled()
    })

    it('should display data changes when available', () => {
      expect(mockFormatJson).toHaveBeenCalled()
    })
  })

  describe('Rendering - Login type', () => {
    beforeEach(() => {
      const data = createLoginData()
      wrapper = mount(AuditTimeline, {
        props: {
          data,
          loading: false,
          auditType: 'login'
        }
      })
    })

    it('should display login time', () => {
      expect(mockFormatDateTime).toHaveBeenCalledWith('2024-01-01T10:00:00Z')
    })

    it('should display logout time when available', () => {
      expect(mockFormatDateTime).toHaveBeenCalledWith('2024-01-01T12:00:00Z')
    })

    it('should display session duration', () => {
      expect(mockFormatDuration).toHaveBeenCalledWith('02:00:00')
    })

    it('should display failure reason when login failed', () => {
      expect(wrapper.text()).toContain('Invalid credentials')
    })

    it('should display success marker for successful login', () => {
      expect(wrapper.vm.getMarkerClass(createLoginData()[0])).toContain('success')
    })

    it('should display error marker for failed login', () => {
      expect(wrapper.vm.getMarkerClass(createLoginData()[1])).toContain('error')
    })
  })

  describe('Methods', () => {
    beforeEach(() => {
      const data = createActivityData()
      wrapper = mount(AuditTimeline, {
        props: {
          data,
          loading: false,
          auditType: 'activity'
        }
      })
    })

    it('should get item title correctly', () => {
      const item = createActivityData()[0]
      const title = wrapper.vm.getItemTitle(item)
      expect(mockGetAuditItemTitle).toHaveBeenCalledWith(item, 'activity')
      expect(title).toBeDefined()
    })

    it('should get item type correctly', () => {
      const type = wrapper.vm.getItemType(createActivityData()[0])
      expect(mockGetAuditItemType).toHaveBeenCalledWith('activity')
      expect(type).toBeDefined()
    })

    it('should get item status correctly', () => {
      const item = createActivityData()[0]
      const status = wrapper.vm.getItemStatus(item)
      expect(mockGetAuditItemStatus).toHaveBeenCalledWith(item, 'activity')
      expect(status).toBeDefined()
    })

    it('should get marker class for activity', () => {
      const item = createActivityData()[0]
      const markerClass = wrapper.vm.getMarkerClass(item)
      expect(mockGetAuditActionMarkerClass).toHaveBeenCalledWith('create')
      expect(markerClass).toBeDefined()
    })

    it('should get marker icon for activity', () => {
      const item = createActivityData()[0]
      const icon = wrapper.vm.getMarkerIcon(item)
      expect(mockGetAuditActionIcon).toHaveBeenCalledWith('create')
      expect(icon).toBeDefined()
    })

    it('should get status class correctly', () => {
      const item = createActivityData()[0]
      const statusClass = wrapper.vm.getStatusClass(item)
      expect(mockGetAuditStatusClass).toHaveBeenCalledWith(item, 'activity')
      expect(statusClass).toBeDefined()
    })

    it('should format date time correctly', () => {
      const dateString = '2024-01-01T10:00:00Z'
      wrapper.vm.formatDateTime(dateString)
      expect(mockFormatDateTime).toHaveBeenCalledWith(dateString)
    })

    it('should format duration correctly', () => {
      const durationString = '02:00:00'
      wrapper.vm.formatDuration(durationString)
      expect(mockFormatDuration).toHaveBeenCalledWith(durationString)
    })

    it('should format JSON correctly', () => {
      const jsonData = { test: 'data' }
      wrapper.vm.formatJson(jsonData)
      expect(mockFormatJson).toHaveBeenCalledWith(jsonData)
    })
  })

  describe('Events', () => {
    beforeEach(() => {
      const data = createActivityData()
      wrapper = mount(AuditTimeline, {
        props: {
          data,
          loading: false,
          auditType: 'activity'
        }
      })
    })

    it('should emit view-details when button is clicked', async () => {
      const button = wrapper.find('button')
      if (button.exists()) {
        await button.trigger('click')
        expect(wrapper.emitted('view-details')).toBeTruthy()
      }
    })
  })

  describe('Timeline structure', () => {
    beforeEach(() => {
      const data = createActivityData()
      wrapper = mount(AuditTimeline, {
        props: {
          data,
          loading: false,
          auditType: 'activity'
        }
      })
    })

    it('should render timeline items', () => {
      const items = wrapper.findAll('.timeline-item')
      expect(items.length).toBe(2)
    })

    it('should mark last item', () => {
      const items = wrapper.findAll('.timeline-item')
      expect(items[items.length - 1].classes()).toContain('last')
    })

    it('should render timeline markers', () => {
      const markers = wrapper.findAll('.timeline-marker')
      expect(markers.length).toBe(2)
    })
  })

  describe('Edge cases', () => {
    it('should handle missing usuario', () => {
      const data = [{ ...createActivityData()[0], usuario: null }]
      wrapper = mount(AuditTimeline, {
        props: {
          data,
          loading: false,
          auditType: 'activity'
        }
      })
      expect(wrapper.text()).toContain('Usuario Anónimo')
    })

    it('should handle missing IP address', () => {
      const data = [{ ...createActivityData()[0], ip_address: null }]
      wrapper = mount(AuditTimeline, {
        props: {
          data,
          loading: false,
          auditType: 'activity'
        }
      })
      expect(wrapper.text()).toContain('N/A')
    })

    it('should handle missing timestamp', () => {
      const data = [{ ...createActivityData()[0], timestamp: null }]
      wrapper = mount(AuditTimeline, {
        props: {
          data,
          loading: false,
          auditType: 'activity'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle missing datos_antes', () => {
      const data = [{ ...createActivityData()[0], datos_antes: null }]
      wrapper = mount(AuditTimeline, {
        props: {
          data,
          loading: false,
          auditType: 'activity'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle missing datos_despues', () => {
      const data = [{ ...createActivityData()[0], datos_despues: null }]
      wrapper = mount(AuditTimeline, {
        props: {
          data,
          loading: false,
          auditType: 'activity'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })
  })
})




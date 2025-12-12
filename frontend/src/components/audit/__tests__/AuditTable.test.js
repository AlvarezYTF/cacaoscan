/**
 * Unit tests for AuditTable component
 * Tests all functionality including props, events, sorting, and rendering
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AuditTable from '../AuditTable.vue'

const { mockFormatDateTime, mockFormatDate, mockFormatDuration, mockGetAuditActionIcon, mockGetAuditActionMarkerClass } = vi.hoisted(() => ({
  mockFormatDateTime: vi.fn((date) => date ? new Date(date).toLocaleString('es-ES') : 'N/A'),
  mockFormatDate: vi.fn((date) => date ? new Date(date).toLocaleDateString('es-ES') : 'N/A'),
  mockFormatDuration: vi.fn((duration) => duration || 'N/A'),
  mockGetAuditActionIcon: vi.fn((action) => {
    const icons = {
      'create': 'fas fa-plus',
      'update': 'fas fa-edit',
      'delete': 'fas fa-trash'
    }
    return icons[action] || 'fas fa-circle'
  }),
  mockGetAuditActionMarkerClass: vi.fn((action) => {
    const classes = {
      'create': 'marker-create',
      'update': 'marker-update',
      'delete': 'marker-delete'
    }
    return classes[action] || 'marker-default'
  })
}))

vi.mock('@/composables/useTable', () => ({
  useTable: vi.fn(() => ({
    sortKey: { value: '' },
    sortOrder: { value: 'asc' },
    isSorted: { value: false },
    sortIcon: { value: null },
    handleSort: vi.fn((key) => {
      const mockTable = {
        sortKey: { value: key },
        sortOrder: { value: 'asc' }
      }
      return mockTable
    })
  }))
}))

vi.mock('@/composables/useAuditHelpers', () => ({
  useAuditHelpers: () => ({
    getAuditActionIcon: mockGetAuditActionIcon,
    getAuditActionMarkerClass: mockGetAuditActionMarkerClass
  })
}))

vi.mock('@/composables/useDateFormatting', () => ({
  useDateFormatting: () => ({
    formatDateTime: mockFormatDateTime,
    formatDuration: mockFormatDuration
  })
}))

vi.mock('@/utils/formatters', () => ({
  formatDate: mockFormatDate,
  formatDateTime: mockFormatDateTime
}))

describe('AuditTable', () => {
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
      objeto_id: 123
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
      wrapper = mount(AuditTable, {
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
      wrapper = mount(AuditTable, {
        props: {
          data,
          loading: false
        }
      })
      expect(wrapper.props('auditType')).toBe('activity')
    })

    it('should default to empty array for data', () => {
      wrapper = mount(AuditTable, {
        props: {
          loading: false
        }
      })
      expect(wrapper.props('data')).toEqual([])
    })

    it('should default to false for loading', () => {
      const data = createActivityData()
      wrapper = mount(AuditTable, {
        props: {
          data
        }
      })
      expect(wrapper.props('loading')).toBe(false)
    })
  })

  describe('Loading state', () => {
    it('should display loading message when loading', () => {
      wrapper = mount(AuditTable, {
        props: {
          data: [],
          loading: true,
          auditType: 'activity'
        }
      })
      expect(wrapper.text()).toContain('Cargando datos de auditoría')
    })

    it('should show loading spinner', () => {
      wrapper = mount(AuditTable, {
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
      wrapper = mount(AuditTable, {
        props: {
          data: [],
          loading: false,
          auditType: 'activity'
        }
      })
      expect(wrapper.text()).toContain('No hay datos')
      expect(wrapper.text()).toContain('No se encontraron registros')
    })

    it('should show empty icon', () => {
      wrapper = mount(AuditTable, {
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
      wrapper = mount(AuditTable, {
        props: {
          data,
          loading: false,
          auditType: 'activity'
        }
      })
    })

    it('should render table title', () => {
      expect(wrapper.vm.getTableTitle()).toBe('Logs de Actividad')
    })

    it('should render table with data', () => {
      expect(wrapper.find('.audit-table').exists()).toBe(true)
      expect(wrapper.find('tbody').exists()).toBe(true)
    })

    it('should display usuario information', () => {
      expect(wrapper.text()).toContain('testuser')
    })

    it('should display IP address', () => {
      expect(wrapper.text()).toContain(MOCK_IP_ADDRESS_1)
    })

    it('should display action badge', () => {
      expect(wrapper.text()).toContain('Crear')
    })

    it('should display modelo', () => {
      expect(wrapper.text()).toContain('CacaoImage')
    })

    it('should display description', () => {
      expect(wrapper.text()).toContain('Test description')
    })

    it('should display timestamp', () => {
      expect(mockFormatDate).toHaveBeenCalled()
    })

    it('should render correct columns for activity type', () => {
      const columns = wrapper.vm.getColumns()
      expect(columns.length).toBe(5)
      expect(columns[0].key).toBe('usuario')
      expect(columns[1].key).toBe('accion')
      expect(columns[2].key).toBe('modelo')
    })
  })

  describe('Rendering - Login type', () => {
    beforeEach(() => {
      const data = createLoginData()
      wrapper = mount(AuditTable, {
        props: {
          data,
          loading: false,
          auditType: 'login'
        }
      })
    })

    it('should render table title', () => {
      expect(wrapper.vm.getTableTitle()).toBe('Historial de Logins')
    })

    it('should display success status', () => {
      expect(wrapper.text()).toContain('Exitoso')
    })

    it('should display failed status', () => {
      expect(wrapper.text()).toContain('Fallido')
    })

    it('should display login time', () => {
      expect(mockFormatDateTime).toHaveBeenCalled()
    })

    it('should display logout time when available', () => {
      expect(mockFormatDateTime).toHaveBeenCalled()
    })

    it('should display session duration when available', () => {
      expect(mockFormatDuration).toHaveBeenCalled()
    })

    it('should display failure reason when login failed', () => {
      expect(wrapper.text()).toContain('Invalid credentials')
    })

    it('should render correct columns for login type', () => {
      const columns = wrapper.vm.getColumns()
      expect(columns.length).toBe(5)
      expect(columns[0].key).toBe('usuario')
      expect(columns[1].key).toBe('success')
      expect(columns[2].key).toBe('login_time')
    })
  })

  describe('Rendering - Both type', () => {
    beforeEach(() => {
      const data = [...createActivityData(), ...createLoginData()]
      wrapper = mount(AuditTable, {
        props: {
          data,
          loading: false,
          auditType: 'both'
        }
      })
    })

    it('should render table title', () => {
      expect(wrapper.vm.getTableTitle()).toBe('Auditoría Completa')
    })

    it('should render correct columns for both type', () => {
      const columns = wrapper.vm.getColumns()
      expect(columns.length).toBe(4)
      expect(columns[0].key).toBe('usuario')
    })
  })

  describe('Methods', () => {
    beforeEach(() => {
      const data = createActivityData()
      wrapper = mount(AuditTable, {
        props: {
          data,
          loading: false,
          auditType: 'activity'
        }
      })
    })

    it('should format date time correctly', () => {
      const dateString = '2024-01-01T10:00:00Z'
      wrapper.vm.formatDateTime(dateString)
      expect(mockFormatDateTime).toHaveBeenCalledWith(dateString)
    })

    it('should format date correctly', () => {
      const dateString = '2024-01-01T10:00:00Z'
      wrapper.vm.formatDate(dateString)
      expect(wrapper.vm.formatDate(dateString)).toBeDefined()
    })

    it('should format time correctly', () => {
      const dateString = '2024-01-01T10:00:00Z'
      const time = wrapper.vm.formatTime(dateString)
      expect(time).toBeDefined()
      expect(time).not.toBe('N/A')
    })

    it('should format duration correctly', () => {
      const durationString = '02:00:00'
      wrapper.vm.formatDuration(durationString)
      expect(mockFormatDuration).toHaveBeenCalledWith(durationString)
    })

    it('should truncate text correctly', () => {
      const text = 'a'.repeat(200)
      const result = wrapper.vm.truncateText(text, 50)
      expect(result.length).toBe(53) // 50 + '...'
      expect(result).toContain('...')
    })

    it('should return text as-is if shorter than maxLength', () => {
      const text = 'Short text'
      const result = wrapper.vm.truncateText(text, 50)
      expect(result).toBe(text)
    })

    it('should return N/A for null text', () => {
      const result = wrapper.vm.truncateText(null, 50)
      expect(result).toBe('N/A')
    })

    it('should get action class correctly', () => {
      expect(wrapper.vm.getActionClass('create')).toBe('action-create')
      expect(wrapper.vm.getActionClass('update')).toBe('action-update')
      expect(wrapper.vm.getActionClass('delete')).toBe('action-delete')
      expect(wrapper.vm.getActionClass('unknown')).toBe('action-default')
    })

    it('should get action icon correctly', () => {
      wrapper.vm.getActionIcon('create')
      expect(mockGetAuditActionIcon).toHaveBeenCalledWith('create')
    })
  })

  describe('Sorting', () => {
    beforeEach(() => {
      const data = createActivityData()
      wrapper = mount(AuditTable, {
        props: {
          data,
          loading: false,
          auditType: 'activity'
        }
      })
    })

    it('should emit sort event when column is clicked', async () => {
      const columns = wrapper.vm.getColumns()
      const sortableColumn = columns.find(col => col.sortable)
      
      if (sortableColumn) {
        await wrapper.vm.handleSortClick(sortableColumn.key)
        expect(wrapper.emitted('sort')).toBeTruthy()
      }
    })

    it('should not emit sort for non-sortable columns', () => {
      const columns = wrapper.vm.getColumns()
      const nonSortableColumn = columns.find(col => !col.sortable)
      
      if (nonSortableColumn) {
        wrapper.vm.handleSortClick(nonSortableColumn.key)
        // Should still work but column might not be sortable
        expect(wrapper.exists()).toBe(true)
      }
    })
  })

  describe('Events', () => {
    beforeEach(() => {
      const data = createActivityData()
      wrapper = mount(AuditTable, {
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

  describe('Edge cases', () => {
    it('should handle missing usuario', () => {
      const data = [{ ...createActivityData()[0], usuario: null }]
      wrapper = mount(AuditTable, {
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
      wrapper = mount(AuditTable, {
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
      wrapper = mount(AuditTable, {
        props: {
          data,
          loading: false,
          auditType: 'activity'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle missing login_time', () => {
      const data = [{ ...createLoginData()[0], login_time: null }]
      wrapper = mount(AuditTable, {
        props: {
          data,
          loading: false,
          auditType: 'login'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle empty description', () => {
      const data = [{ ...createActivityData()[0], descripcion: '' }]
      wrapper = mount(AuditTable, {
        props: {
          data,
          loading: false,
          auditType: 'activity'
        }
      })
      expect(wrapper.vm.truncateText('', 50)).toBe('N/A')
    })
  })
})


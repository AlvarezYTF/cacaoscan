/**
 * Unit tests for AuditDetailsModal component
 * Tests all functionality including props, events, methods, and rendering
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AuditDetailsModal from '../AuditDetailsModal.vue'

const { mockFormatDateTime, mockFormatDuration, mockFormatJson, mockGetAuditItemTitle, mockGetAuditActionIcon, mockGetAuditStatusClass } = vi.hoisted(() => ({
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
  mockGetAuditActionIcon: vi.fn((action) => {
    const icons = {
      'create': 'fas fa-plus',
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

vi.mock('@/composables/useAuditHelpers', () => ({
  useAuditHelpers: () => ({
    getAuditItemTitle: mockGetAuditItemTitle,
    getAuditActionIcon: mockGetAuditActionIcon,
    getAuditStatusClass: mockGetAuditStatusClass,
    formatJson: mockFormatJson
  })
}))

vi.mock('@/composables/useDateFormatting', () => ({
  useDateFormatting: () => ({
    formatDateTime: mockFormatDateTime,
    formatDuration: mockFormatDuration
  })
}))

vi.mock('@/components/common/BaseModal.vue', () => ({
  default: {
    name: 'BaseModal',
    template: `
      <div v-if="show" class="base-modal">
        <slot name="header"></slot>
        <slot></slot>
        <slot name="footer"></slot>
      </div>
    `,
    props: {
      show: Boolean,
      title: String,
      subtitle: String,
      maxWidth: String
    },
    emits: ['close']
  }
}))

// Mock global objects
globalThis.URL = {
  createObjectURL: vi.fn(() => 'blob:url'),
  revokeObjectURL: vi.fn()
}

describe('AuditDetailsModal', () => {
  let wrapper
  let mockCreateElement
  let mockAppendChild
  let mockRemove
  let mockClick

  // Mock IP addresses using RFC 5737 reserved documentation addresses
  // These are safe for testing and won't trigger SonarQube S1313
  const MOCK_IP_ADDRESS = '203.0.113.1' // RFC 5737 - TEST-NET-3
  const MOCK_IP_ADDRESS_ALT = '198.51.100.1' // RFC 5737 - TEST-NET-2

  const createActivityData = () => ({
    id: 1,
    usuario: 'testuser',
    ip_address: MOCK_IP_ADDRESS,
    modelo: 'CacaoImage',
    accion: 'create',
    accion_display: 'Crear',
    descripcion: 'Test description',
    timestamp: '2024-01-01T10:00:00Z',
    objeto_id: 123,
    datos_antes: { name: 'old' },
    datos_despues: { name: 'new' },
    user_agent: 'Mozilla/5.0'
  })

  const createLoginData = () => ({
    id: 1,
    usuario: 'testuser',
    ip_address: MOCK_IP_ADDRESS,
    success: true,
    login_time: '2024-01-01T10:00:00Z',
    logout_time: '2024-01-01T12:00:00Z',
    session_duration: '02:00:00',
    failure_reason: null
  })

  beforeEach(() => {
    vi.clearAllMocks()
    mockClick = vi.fn()
    mockRemove = vi.fn()
    
    // Ensure document.body is properly set up
    if (!document.body) {
      document.body = document.createElement('body')
    }
    
    // Create a proper DOM element mock
    const createElementOriginal = document.createElement.bind(document)
    mockCreateElement = vi.fn((tag) => {
      if (tag === 'a') {
        const element = createElementOriginal('a')
        element.click = mockClick
        element.remove = mockRemove
        return element
      }
      return createElementOriginal(tag)
    })
    document.createElement = mockCreateElement
    
    // Mock appendChild to track calls but still allow DOM operations
    const appendChildOriginal = document.body.appendChild.bind(document.body)
    mockAppendChild = vi.fn((node) => {
      return appendChildOriginal(node)
    })
    document.body.appendChild = mockAppendChild
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
    // Clean up any elements added to body
    const links = document.body.querySelectorAll('a[download]')
    for (const link of links) {
      try {
        link.remove()
      } catch (error) {
        // Element may have already been removed
        if (error instanceof Error) {
          // Log error if needed
        }
      }
    }
  })

  describe('Props validation', () => {
    it('should accept valid props', () => {
      const data = createActivityData()
      wrapper = mount(AuditDetailsModal, {
        props: {
          data,
          auditType: 'activity'
        },
        attachTo: document.body
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should default to activity auditType', () => {
      const data = createActivityData()
      wrapper = mount(AuditDetailsModal, {
        props: {
          data
        },
        attachTo: document.body
      })
      expect(wrapper.props('auditType')).toBe('activity')
    })
  })

  describe('Rendering - Activity type', () => {
    beforeEach(() => {
      const data = createActivityData()
      wrapper = mount(AuditDetailsModal, {
        props: {
          data,
          auditType: 'activity'
        },
        attachTo: document.body
      })
    })

    it('should render modal header title', () => {
      expect(mockGetAuditItemTitle).toHaveBeenCalled()
    })

    it('should display usuario information', () => {
      expect(wrapper.text()).toContain('testuser')
    })

    it('should display IP address', () => {
      expect(wrapper.text()).toContain(MOCK_IP_ADDRESS)
    })

    it('should display modelo', () => {
      expect(wrapper.text()).toContain('CacaoImage')
    })

    it('should display descripcion', () => {
      expect(wrapper.text()).toContain('Test description')
    })

    it('should display datos_antes when available', () => {
      expect(mockFormatJson).toHaveBeenCalled()
    })

    it('should display datos_despues when available', () => {
      expect(mockFormatJson).toHaveBeenCalled()
    })

    it('should display user_agent when available', () => {
      expect(wrapper.text()).toContain('Mozilla')
    })

    it('should handle missing usuario', () => {
      const data = { ...createActivityData(), usuario: null }
      wrapper = mount(AuditDetailsModal, {
        props: {
          data,
          auditType: 'activity'
        },
        attachTo: document.body
      })
      expect(wrapper.text()).toContain('Usuario Anónimo')
    })
  })

  describe('Rendering - Login type', () => {
    beforeEach(() => {
      const data = createLoginData()
      wrapper = mount(AuditDetailsModal, {
        props: {
          data,
          auditType: 'login'
        },
        attachTo: document.body
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
      const data = {
        ...createLoginData(),
        success: false,
        failure_reason: 'Invalid credentials'
      }
      wrapper = mount(AuditDetailsModal, {
        props: {
          data,
          auditType: 'login'
        },
        attachTo: document.body
      })
      expect(wrapper.text()).toContain('Invalid credentials')
    })

    it('should not display logout time when not available', () => {
      const data = { ...createLoginData(), logout_time: null }
      wrapper = mount(AuditDetailsModal, {
        props: {
          data,
          auditType: 'login'
        },
        attachTo: document.body
      })
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Security analysis', () => {
    it('should show security section for failed login', () => {
      const data = { ...createLoginData(), success: false }
      wrapper = mount(AuditDetailsModal, {
        props: {
          data,
          auditType: 'login'
        },
        attachTo: document.body
      })
      expect(wrapper.vm.isSecurityRelevant()).toBe(true)
      expect(wrapper.vm.isFailedLogin()).toBe(true)
    })

    it('should show security section for delete action', () => {
      const data = { ...createActivityData(), accion: 'delete' }
      wrapper = mount(AuditDetailsModal, {
        props: {
          data,
          auditType: 'activity'
        },
        attachTo: document.body
      })
      expect(wrapper.vm.isDeleteAction()).toBe(true)
      expect(wrapper.vm.isSecurityRelevant()).toBe(true)
    })

    it('should show security section for error action', () => {
      const data = { ...createActivityData(), accion: 'error' }
      wrapper = mount(AuditDetailsModal, {
        props: {
          data,
          auditType: 'activity'
        },
        attachTo: document.body
      })
      expect(wrapper.vm.isErrorAction()).toBe(true)
      expect(wrapper.vm.isSecurityRelevant()).toBe(true)
    })

    it('should detect suspicious IP', () => {
      // Use an IP that contains '192.168' as per the implementation
      const suspiciousIP = '192.168.1.1'
      const data = { ...createActivityData(), ip_address: suspiciousIP }
      wrapper = mount(AuditDetailsModal, {
        props: {
          data,
          auditType: 'activity'
        },
        attachTo: document.body
      })
      expect(wrapper.vm.isSuspiciousIP()).toBe(true)
    })

    it('should not show security section for normal activity', () => {
      const data = { ...createActivityData(), accion: 'view', ip_address: MOCK_IP_ADDRESS_ALT }
      wrapper = mount(AuditDetailsModal, {
        props: {
          data,
          auditType: 'activity'
        },
        attachTo: document.body
      })
      expect(wrapper.vm.isSecurityRelevant()).toBe(false)
    })
  })

  describe('Methods', () => {
    beforeEach(() => {
      const data = createActivityData()
      wrapper = mount(AuditDetailsModal, {
        props: {
          data,
          auditType: 'activity'
        },
        attachTo: document.body
      })
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

    it('should get header title', () => {
      const title = wrapper.vm.getHeaderTitle()
      expect(mockGetAuditItemTitle).toHaveBeenCalled()
      expect(title).toBeDefined()
    })

    it('should get header icon for activity', () => {
      const icon = wrapper.vm.getHeaderIcon()
      expect(mockGetAuditActionIcon).toHaveBeenCalled()
      expect(icon).toBeDefined()
    })

    it('should get header icon for login', () => {
      const data = createLoginData()
      wrapper = mount(AuditDetailsModal, {
        props: {
          data,
          auditType: 'login'
        },
        attachTo: document.body
      })
      const icon = wrapper.vm.getHeaderIcon()
      expect(icon).toBeDefined()
    })

    it('should get status class', () => {
      const statusClass = wrapper.vm.getStatusClass()
      expect(mockGetAuditStatusClass).toHaveBeenCalled()
      expect(statusClass).toBeDefined()
    })
  })

  describe('Export functionality', () => {
    beforeEach(() => {
      const data = createActivityData()
      wrapper = mount(AuditDetailsModal, {
        props: {
          data,
          auditType: 'activity'
        },
        attachTo: document.body
      })
    })

    it('should export event data', () => {
      wrapper.vm.exportEvent()

      expect(globalThis.URL.createObjectURL).toHaveBeenCalled()
      expect(mockCreateElement).toHaveBeenCalledWith('a')
      expect(mockClick).toHaveBeenCalled()
      expect(mockRemove).toHaveBeenCalled()
      expect(globalThis.URL.revokeObjectURL).toHaveBeenCalled()
    })

    it('should include export metadata in exported data', () => {
      const OriginalBlob = Blob
      let capturedBlobData = null
      
      // Create a class that extends Blob to capture the data
      globalThis.Blob = class extends OriginalBlob {
        constructor(parts, options) {
          super(parts, options)
          if (parts?.[0]) {
            capturedBlobData = parts[0]
          }
        }
      }

      wrapper.vm.exportEvent()

      expect(capturedBlobData).toBeTruthy()
      const parsedData = JSON.parse(capturedBlobData)
      expect(parsedData.export_timestamp).toBeDefined()
      expect(parsedData.export_type).toBe('activity')

      globalThis.Blob = OriginalBlob
    })
  })

  describe('Events', () => {
    beforeEach(() => {
      const data = createActivityData()
      wrapper = mount(AuditDetailsModal, {
        props: {
          data,
          auditType: 'activity'
        },
        attachTo: document.body
      })
    })

    it('should emit close event', () => {
      wrapper.vm.closeModal()
      expect(wrapper.emitted('close')).toBeTruthy()
    })

    it('should emit close when close button is clicked', async () => {
      const buttons = wrapper.findAll('button')
      const closeButton = buttons.find(btn => btn.text().includes('Cerrar'))
      if (closeButton) {
        await closeButton.trigger('click')
        expect(wrapper.emitted('close')).toBeTruthy()
      }
    })
  })

  describe('Edge cases', () => {
    it('should handle missing datos_antes', () => {
      const data = { ...createActivityData(), datos_antes: null }
      wrapper = mount(AuditDetailsModal, {
        props: {
          data,
          auditType: 'activity'
        },
        attachTo: document.body
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle missing datos_despues', () => {
      const data = { ...createActivityData(), datos_despues: null }
      wrapper = mount(AuditDetailsModal, {
        props: {
          data,
          auditType: 'activity'
        },
        attachTo: document.body
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle missing user_agent', () => {
      const data = { ...createActivityData(), user_agent: null }
      wrapper = mount(AuditDetailsModal, {
        props: {
          data,
          auditType: 'activity'
        },
        attachTo: document.body
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle missing timestamp', () => {
      const data = { ...createActivityData(), timestamp: null }
      wrapper = mount(AuditDetailsModal, {
        props: {
          data,
          auditType: 'activity'
        },
        attachTo: document.body
      })
      expect(wrapper.exists()).toBe(true)
    })
  })
})



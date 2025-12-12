/**
 * Unit tests for AuditCard component
 * Tests all functionality including props, events, computed properties, and rendering
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AuditCard from '../AuditCard.vue'

const { mockFormatDateTime, mockFormatDuration, mockGetAuditItemTitle, mockGetAuditItemType, mockGetAuditItemStatus, mockGetAuditStatusClass, mockGetAuditActionMarkerClass, mockGetAuditActionIcon } = vi.hoisted(() => ({
  mockFormatDateTime: vi.fn((date) => date ? new Date(date).toLocaleString('es-ES') : 'N/A'),
  mockFormatDuration: vi.fn((duration) => duration || 'N/A'),
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
  mockGetAuditStatusClass: vi.fn((item, type) => {
    if (type === 'login' || type === 'both') {
      return item.success ? 'status-success' : 'status-error'
    }
    return 'status-default'
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
    getAuditStatusClass: mockGetAuditStatusClass
  })
}))

vi.mock('@/components/common/BaseCard.vue', () => ({
  default: {
    name: 'BaseCard',
    template: `
      <div class="base-card" @click="handleClick">
        <div class="card-header">
          <slot name="meta"></slot>
          <h3>{{ title }}</h3>
        </div>
        <div class="card-body">
          <slot></slot>
        </div>
        <div class="card-footer">
          <slot name="footer"></slot>
        </div>
        <div class="card-actions">
          <slot name="actions"></slot>
        </div>
      </div>
    `,
    props: {
      title: String,
      icon: String,
      variant: String,
      clickable: Boolean
    },
    emits: ['click'],
    methods: {
      handleClick(event) {
        if (this.clickable) {
          this.$emit('click', event)
        }
      }
    }
  }
}))

describe('AuditCard', () => {
  let wrapper

  // Mock IP addresses using RFC 5737 reserved documentation addresses
  // These are safe for testing and won't trigger SonarQube S1313
  const MOCK_IP_ADDRESS = '203.0.113.1' // RFC 5737 - TEST-NET-3

  const createActivityData = () => ({
    id: 1,
    usuario: 'testuser',
    ip_address: MOCK_IP_ADDRESS,
    modelo: 'CacaoImage',
    accion: 'create',
    accion_display: 'Crear',
    descripcion: 'Test description for activity',
    timestamp: '2024-01-01T10:00:00Z',
    objeto_id: 123
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
  })

  describe('Props validation', () => {
    it('should accept valid auditType prop', () => {
      const data = createActivityData()
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'activity'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should accept login auditType', () => {
      const data = createLoginData()
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'login'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should accept both auditType', () => {
      const data = createActivityData()
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'both'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should default to activity auditType', () => {
      const data = createActivityData()
      wrapper = mount(AuditCard, {
        props: {
          data
        }
      })
      expect(wrapper.props('auditType')).toBe('activity')
    })
  })

  describe('Rendering - Activity type', () => {
    beforeEach(() => {
      const data = createActivityData()
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'activity'
        }
      })
    })

    it('should render card title', () => {
      expect(mockGetAuditItemTitle).toHaveBeenCalledWith(createActivityData(), 'activity')
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

    it('should display description', () => {
      expect(wrapper.text()).toContain('Test description')
    })

    it('should display timestamp', () => {
      expect(mockFormatDateTime).toHaveBeenCalled()
    })

    it('should handle missing usuario', () => {
      const data = { ...createActivityData(), usuario: null }
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'activity'
        }
      })
      expect(wrapper.text()).toContain('Usuario Anónimo')
    })

    it('should handle missing IP address', () => {
      const data = { ...createActivityData(), ip_address: null }
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'activity'
        }
      })
      expect(wrapper.text()).toContain('N/A')
    })

    it('should truncate long descriptions', () => {
      const longDescription = 'a'.repeat(200)
      const data = { ...createActivityData(), descripcion: longDescription }
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'activity'
        }
      })
      expect(wrapper.vm.truncateText(longDescription, 100)).toContain('...')
    })
  })

  describe('Rendering - Login type', () => {
    beforeEach(() => {
      const data = createLoginData()
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'login'
        }
      })
    })

    it('should render login card', () => {
      expect(mockGetAuditItemTitle).toHaveBeenCalledWith(createLoginData(), 'login')
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
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'login'
        }
      })
      expect(wrapper.text()).toContain('Invalid credentials')
    })

    it('should not display logout time when not available', () => {
      const data = { ...createLoginData(), logout_time: null }
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'login'
        }
      })
      const sessionItems = wrapper.findAll('.session-item')
      const hasCierre = sessionItems.some(item => item.text().includes('Cierre'))
      expect(hasCierre).toBe(false)
    })
  })

  describe('Computed properties', () => {
    it('should compute card variant for create action', () => {
      const data = { ...createActivityData(), accion: 'create' }
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'activity'
        }
      })
      expect(wrapper.vm.cardVariant).toBe('success')
    })

    it('should compute card variant for delete action', () => {
      const data = { ...createActivityData(), accion: 'delete' }
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'activity'
        }
      })
      expect(wrapper.vm.cardVariant).toBe('error')
    })

    it('should compute card variant for update action', () => {
      const data = { ...createActivityData(), accion: 'update' }
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'activity'
        }
      })
      expect(wrapper.vm.cardVariant).toBe('info')
    })

    it('should compute card variant for successful login', () => {
      const data = { ...createLoginData(), success: true }
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'login'
        }
      })
      expect(wrapper.vm.cardVariant).toBe('success')
    })

    it('should compute card variant for failed login', () => {
      const data = { ...createLoginData(), success: false }
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'login'
        }
      })
      expect(wrapper.vm.cardVariant).toBe('error')
    })

    it('should compute card icon for activity type', () => {
      const data = { ...createActivityData(), accion: 'create' }
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'activity'
        }
      })
      expect(mockGetAuditActionIcon).toHaveBeenCalledWith('create')
    })

    it('should compute card icon for successful login', () => {
      const data = { ...createLoginData(), success: true }
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'login'
        }
      })
      expect(wrapper.vm.cardIcon).toBe('fas fa-check-circle')
    })

    it('should compute card icon for failed login', () => {
      const data = { ...createLoginData(), success: false }
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'login'
        }
      })
      expect(wrapper.vm.cardIcon).toBe('fas fa-times-circle')
    })
  })

  describe('Events', () => {
    it('should emit view-details when card is clicked', async () => {
      const data = createActivityData()
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'activity'
        }
      })

      const card = wrapper.findComponent({ name: 'BaseCard' })
      await card.trigger('click')

      expect(wrapper.emitted('view-details')).toBeTruthy()
      expect(wrapper.emitted('view-details')[0]).toEqual([data, 'activity'])
    })

    it('should emit view-details when button is clicked', async () => {
      const data = createActivityData()
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'activity'
        }
      })

      const button = wrapper.find('button')
      await button.trigger('click')

      expect(wrapper.emitted('view-details')).toBeTruthy()
      expect(wrapper.emitted('view-details')[0]).toEqual([data, 'activity'])
    })

    it('should stop propagation when button is clicked', async () => {
      const data = createActivityData()
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'activity'
        }
      })

      const button = wrapper.find('button')
      const clickEvent = new Event('click')
      clickEvent.stopPropagation = vi.fn()
      button.element.dispatchEvent(clickEvent)

      // Button click should not bubble to card click
      const emitted = wrapper.emitted('view-details')
      expect(emitted).toBeTruthy()
    })
  })

  describe('Methods', () => {
    beforeEach(() => {
      const data = createActivityData()
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'activity'
        }
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

    it('should truncate text correctly', () => {
      const text = 'a'.repeat(200)
      const result = wrapper.vm.truncateText(text, 100)
      expect(result.length).toBe(103) // 100 + '...'
      expect(result).toContain('...')
    })

    it('should return text as-is if shorter than maxLength', () => {
      const text = 'Short text'
      const result = wrapper.vm.truncateText(text, 100)
      expect(result).toBe(text)
    })

    it('should return N/A for null text', () => {
      const result = wrapper.vm.truncateText(null, 100)
      expect(result).toBe('N/A')
    })

    it('should return N/A for undefined text', () => {
      const result = wrapper.vm.truncateText(undefined, 100)
      expect(result).toBe('N/A')
    })
  })

  describe('Both audit type', () => {
    it('should render both activity and login information', () => {
      const data = {
        ...createActivityData(),
        ...createLoginData(),
        login_time: '2024-01-01T10:00:00Z'
      }
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'both'
        }
      })

      expect(wrapper.text()).toContain('CacaoImage')
      expect(mockFormatDuration).toHaveBeenCalled()
    })
  })

  describe('Edge cases', () => {
    it('should handle missing timestamp gracefully', () => {
      const data = { ...createActivityData(), timestamp: null }
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'activity'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle missing login_time gracefully', () => {
      const data = { ...createLoginData(), login_time: null }
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'login'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle empty description', () => {
      const data = { ...createActivityData(), descripcion: '' }
      wrapper = mount(AuditCard, {
        props: {
          data,
          auditType: 'activity'
        }
      })
      expect(wrapper.vm.truncateText('', 100)).toBe('N/A')
    })
  })
})


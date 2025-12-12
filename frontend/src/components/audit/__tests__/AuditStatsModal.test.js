/**
 * Unit tests for AuditStatsModal component
 * Tests all functionality including props, events, methods, and rendering
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AuditStatsModal from '../AuditStatsModal.vue'

vi.mock('@/components/common/BaseModal.vue', () => ({
  default: {
    name: 'BaseModal',
    template: `
      <div v-if="show" class="base-modal">
        <div class="base-modal-header">
          <slot name="header"></slot>
        </div>
        <div class="base-modal-body">
          <slot></slot>
        </div>
        <div class="base-modal-footer">
          <slot name="footer"></slot>
        </div>
      </div>
    `,
    props: {
      show: {
        type: Boolean,
        default: true
      },
      title: String,
      subtitle: String,
      maxWidth: String
    },
    emits: ['close']
  }
}))

globalThis.URL = {
  createObjectURL: vi.fn(() => 'blob:url'),
  revokeObjectURL: vi.fn()
}

describe('AuditStatsModal', () => {
  let wrapper
  let mockCreateElement
  let mockRemove
  let mockClick

  // Mock IP addresses using RFC 5737 reserved documentation addresses
  // These are safe for testing and won't trigger SonarQube S1313
  const MOCK_IP_ADDRESS_1 = '203.0.113.1' // RFC 5737 - TEST-NET-3
  const MOCK_IP_ADDRESS_2 = '203.0.113.2' // RFC 5737 - TEST-NET-3

  const createStatsData = () => ({
    activity_log: {
      total_activities: 100,
      activities_today: 10,
      activities_by_action: {
        create: 30,
        update: 40,
        delete: 20,
        view: 10
      },
      activities_by_model: {
        CacaoImage: 50,
        Finca: 30,
        User: 20
      },
      top_active_users: [
        { usuario__username: 'user1', count: 50 },
        { usuario__username: 'user2', count: 30 }
      ]
    },
    login_history: {
      total_logins: 200,
      successful_logins: 180,
      failed_logins: 20,
      success_rate: 90,
      login_stats_by_day: [
        { date: '2024-01-01', count: 10 },
        { date: '2024-01-02', count: 15 },
        { date: '2024-01-03', count: 12 }
      ],
      top_ips: [
        { ip_address: MOCK_IP_ADDRESS_1, count: 50 },
        { ip_address: MOCK_IP_ADDRESS_2, count: 30 }
      ],
      avg_session_duration_minutes: 45
    },
    generated_at: '2024-01-01T10:00:00Z'
  })

  beforeEach(() => {
    vi.clearAllMocks()
    mockClick = vi.fn()
    mockRemove = vi.fn()
    
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
    
    // Ensure document.body is properly set up
    if (!document.body) {
      document.body = document.createElement('body')
    }
    
    // Mock appendChild to track calls but still allow DOM operations
    const appendChildOriginal = document.body.appendChild.bind(document.body)
    document.body.appendChild = vi.fn((node) => {
      return appendChildOriginal(node)
    })
  })

  describe('Props validation', () => {
    it('should accept valid stats prop', () => {
      const stats = createStatsData()
      wrapper = mount(AuditStatsModal, {
        props: {
          stats
        },
        attachTo: document.body
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle empty stats', () => {
      wrapper = mount(AuditStatsModal, {
        props: {
          stats: {}
        },
        attachTo: document.body
      })
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Rendering', () => {
    beforeEach(() => {
      const stats = createStatsData()
      wrapper = mount(AuditStatsModal, {
        props: {
          stats
        },
        attachTo: document.body
      })
    })

    it('should render summary section', () => {
      expect(wrapper.text()).toContain('Actividades Totales')
      expect(wrapper.text()).toContain('100')
    })

    it('should render activities by action', () => {
      expect(wrapper.text()).toContain('Actividades por Acción')
    })

    it('should render activities by model', () => {
      expect(wrapper.text()).toContain('Actividades por Modelo')
    })

    it('should render top active users', () => {
      expect(wrapper.text()).toContain('Usuarios Más Activos')
      expect(wrapper.text()).toContain('user1')
    })

    it('should render login stats by day', () => {
      expect(wrapper.text()).toContain('Logins por Día')
    })

    it('should render top IPs', () => {
      expect(wrapper.text()).toContain('Direcciones IP Más Frecuentes')
      expect(wrapper.text()).toContain(MOCK_IP_ADDRESS_1)
    })

    it('should render average session duration', () => {
      expect(wrapper.text()).toContain('Duración Promedio de Sesión')
      expect(wrapper.text()).toContain('45')
    })
  })

  describe('Methods', () => {
    beforeEach(() => {
      const stats = createStatsData()
      wrapper = mount(AuditStatsModal, {
        props: {
          stats
        },
        attachTo: document.body
      })
    })

    it('should get action label correctly', () => {
      expect(wrapper.vm.getActionLabel('create')).toBe('Crear')
      expect(wrapper.vm.getActionLabel('update')).toBe('Actualizar')
      expect(wrapper.vm.getActionLabel('delete')).toBe('Eliminar')
      expect(wrapper.vm.getActionLabel('view')).toBe('Ver')
      expect(wrapper.vm.getActionLabel('unknown')).toBe('unknown')
    })

    it('should calculate bar height correctly', () => {
      expect(wrapper.vm.getBarHeight(50, 100)).toBe('50%')
      expect(wrapper.vm.getBarHeight(0, 100)).toBe('0%')
      expect(wrapper.vm.getBarHeight(100, 0)).toBe('0%')
      expect(wrapper.vm.getBarHeight(0, 0)).toBe('0%')
    })

    it('should calculate bar width correctly', () => {
      expect(wrapper.vm.getBarWidth(50, 100)).toBe('50%')
      expect(wrapper.vm.getBarWidth(0, 100)).toBe('0%')
    })

    it('should get max daily logins', () => {
      expect(wrapper.vm.getMaxDailyLogins()).toBe(15)
    })

    it('should handle empty login stats', () => {
      const stats = {
        ...createStatsData(),
        login_history: {
          ...createStatsData().login_history,
          login_stats_by_day: []
        }
      }
      wrapper = mount(AuditStatsModal, {
        props: {
          stats
        },
        attachTo: document.body
      })
      expect(wrapper.vm.getMaxDailyLogins()).toBe(1)
    })

    it('should format date correctly', () => {
      const formatted = wrapper.vm.formatDate('2024-01-01')
      expect(formatted).toBeDefined()
      expect(formatted).not.toBe('N/A')
    })

    it('should handle null date', () => {
      expect(wrapper.vm.formatDate(null)).toBe('N/A')
      expect(wrapper.vm.formatDate(undefined)).toBe('N/A')
    })

    it('should format date time correctly', () => {
      const formatted = wrapper.vm.formatDateTime('2024-01-01T10:00:00Z')
      expect(formatted).toBeDefined()
      expect(formatted).not.toBe('N/A')
    })
  })

  describe('Export functionality', () => {
    beforeEach(() => {
      const stats = createStatsData()
      wrapper = mount(AuditStatsModal, {
        props: {
          stats
        },
        attachTo: document.body
      })
    })

    it('should export stats data', () => {
      wrapper.vm.exportStats()

      expect(globalThis.URL.createObjectURL).toHaveBeenCalled()
      expect(mockCreateElement).toHaveBeenCalledWith('a')
      expect(mockClick).toHaveBeenCalled()
      expect(mockRemove).toHaveBeenCalled()
      expect(globalThis.URL.revokeObjectURL).toHaveBeenCalled()
    })

    it('should include export metadata', () => {
      const blobConstructor = Blob
      let capturedBlobData = null
      globalThis.Blob = vi.fn(function(parts, options) {
        capturedBlobData = parts[0]
        return new blobConstructor(parts, options)
      })

      wrapper.vm.exportStats()

      expect(capturedBlobData).toBeTruthy()
      const parsedData = JSON.parse(capturedBlobData)
      expect(parsedData.export_timestamp).toBeDefined()
      expect(parsedData.export_type).toBe('audit_statistics')

      globalThis.Blob = blobConstructor
    })
  })

  describe('Events', () => {
    beforeEach(() => {
      const stats = createStatsData()
      wrapper = mount(AuditStatsModal, {
        props: {
          stats
        },
        attachTo: document.body
      })
    })

    it('should emit close event', () => {
      wrapper.vm.closeModal()
      expect(wrapper.emitted('close')).toBeTruthy()
    })
  })

  describe('Edge cases', () => {
    it('should handle missing activity_log', () => {
      const stats = {
        login_history: createStatsData().login_history
      }
      wrapper = mount(AuditStatsModal, {
        props: {
          stats
        },
        attachTo: document.body
      })
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.text()).toContain('0')
    })

    it('should handle missing login_history', () => {
      const stats = {
        activity_log: createStatsData().activity_log
      }
      wrapper = mount(AuditStatsModal, {
        props: {
          stats
        },
        attachTo: document.body
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle missing top_active_users', () => {
      const stats = {
        ...createStatsData(),
        activity_log: {
          ...createStatsData().activity_log,
          top_active_users: null
        }
      }
      wrapper = mount(AuditStatsModal, {
        props: {
          stats
        },
        attachTo: document.body
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle missing avg_session_duration', () => {
      const stats = {
        ...createStatsData(),
        login_history: {
          ...createStatsData().login_history,
          avg_session_duration_minutes: null
        }
      }
      wrapper = mount(AuditStatsModal, {
        props: {
          stats
        },
        attachTo: document.body
      })
      expect(wrapper.exists()).toBe(true)
    })
  })
})



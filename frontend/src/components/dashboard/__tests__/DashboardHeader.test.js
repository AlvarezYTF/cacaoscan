import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import DashboardHeader from '../DashboardHeader.vue'

// Mock BaseHeader component
vi.mock('@/components/common/BaseHeader.vue', () => ({
  default: {
    name: 'BaseHeader',
    template: `
      <div class="base-header" :class="headerClass">
        <h2>{{ title }}</h2>
        <p v-if="subtitle">{{ subtitle }}</p>
        <slot name="brand"></slot>
        <slot name="actions"></slot>
      </div>
    `,
    props: {
      title: {
        type: String,
        required: true
      },
      subtitle: {
        type: String,
        default: ''
      },
      headerClass: {
        type: String,
        default: ''
      }
    }
  }
}))

describe('DashboardHeader', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
  })

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = mount(DashboardHeader)

      expect(wrapper.exists()).toBe(true)
    })

    it('should render BaseHeader component', () => {
      wrapper = mount(DashboardHeader)

      const baseHeader = wrapper.findComponent({ name: 'BaseHeader' })
      expect(baseHeader.exists()).toBe(true)
    })

    it('should display welcome message with default farmer name', () => {
      wrapper = mount(DashboardHeader)

      const baseHeader = wrapper.findComponent({ name: 'BaseHeader' })
      expect(baseHeader.props('title')).toContain('Bienvenido')
      expect(baseHeader.props('title')).toContain('Usuario')
    })

    it('should display welcome message with provided farmer name', () => {
      wrapper = mount(DashboardHeader, {
        props: {
          farmerName: 'Juan Pérez'
        }
      })

      const baseHeader = wrapper.findComponent({ name: 'BaseHeader' })
      expect(baseHeader.props('title')).toContain('Bienvenido')
      expect(baseHeader.props('title')).toContain('Juan Pérez')
    })

    it('should display subtitle', () => {
      wrapper = mount(DashboardHeader)

      const baseHeader = wrapper.findComponent({ name: 'BaseHeader' })
      expect(baseHeader.props('subtitle')).toBe('Panel de control para el análisis de tus granos de cacao')
    })

    it('should pass header-class prop to BaseHeader', () => {
      wrapper = mount(DashboardHeader)

      const baseHeader = wrapper.findComponent({ name: 'BaseHeader' })
      expect(baseHeader.props('headerClass')).toBe('dashboard-header mb-8')
    })
  })

  describe('Props', () => {
    it('should use default farmerName when not provided', () => {
      wrapper = mount(DashboardHeader)

      const baseHeader = wrapper.findComponent({ name: 'BaseHeader' })
      const title = baseHeader.props('title')
      expect(title).toContain('Usuario')
    })

    it('should use provided farmerName', () => {
      wrapper = mount(DashboardHeader, {
        props: {
          farmerName: 'María García'
        }
      })

      const baseHeader = wrapper.findComponent({ name: 'BaseHeader' })
      const title = baseHeader.props('title')
      expect(title).toContain('María García')
      expect(title).not.toContain('Usuario')
    })

    it('should handle empty farmerName string', () => {
      wrapper = mount(DashboardHeader, {
        props: {
          farmerName: ''
        }
      })

      const baseHeader = wrapper.findComponent({ name: 'BaseHeader' })
      const title = baseHeader.props('title')
      expect(title).toContain('Bienvenido')
    })

    it('should include emoji in title', () => {
      wrapper = mount(DashboardHeader, {
        props: {
          farmerName: 'Test User'
        }
      })

      const baseHeader = wrapper.findComponent({ name: 'BaseHeader' })
      const title = baseHeader.props('title')
      expect(title).toContain('👨‍🌾')
    })
  })

  describe('Title Formatting', () => {
    it('should format title correctly with farmer name', () => {
      wrapper = mount(DashboardHeader, {
        props: {
          farmerName: 'Carlos Rodríguez'
        }
      })

      const baseHeader = wrapper.findComponent({ name: 'BaseHeader' })
      const title = baseHeader.props('title')
      expect(title).toBe('Bienvenido, Carlos Rodríguez 👨‍🌾')
    })

    it('should format title correctly with default name', () => {
      wrapper = mount(DashboardHeader)

      const baseHeader = wrapper.findComponent({ name: 'BaseHeader' })
      const title = baseHeader.props('title')
      expect(title).toBe('Bienvenido, Usuario 👨‍🌾')
    })
  })
})


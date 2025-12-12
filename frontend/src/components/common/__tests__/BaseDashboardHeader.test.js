/**
 * Unit tests for BaseDashboardHeader component
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseDashboardHeader from '../BaseDashboardHeader.vue'

vi.mock('../BaseHeader.vue', () => ({
  default: {
    name: 'BaseHeader',
    template: `
      <div class="base-header">
        <slot name="brand"></slot>
        <slot name="actions"></slot>
      </div>
    `,
    props: {
      title: String,
      subtitle: String,
      icon: [Object, String],
      headerClass: String,
      showActions: Boolean
    }
  }
}))

// Mock vue-router to avoid $route redefinition errors
const mockRouter = {
  push: vi.fn(),
  replace: vi.fn(),
  currentRoute: {
    value: {
      path: '/',
      name: 'home',
      params: {},
      query: {}
    }
  }
}

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRouter: () => mockRouter,
    useRoute: () => ({
      path: '/',
      name: 'home',
      params: {},
      query: {}
    }),
    RouterLink: {
      name: 'RouterLink',
      template: '<a><slot></slot></a>',
      props: ['to']
    },
    RouterView: {
      name: 'RouterView',
      template: '<div></div>'
    }
  }
})

describe('BaseDashboardHeader', () => {
  let wrapper

  const mountOptions = {
    global: {
      stubs: {
        'router-link': {
          template: '<a><slot></slot></a>',
          props: ['to']
        }
      }
    }
  }

  beforeEach(() => {
    vi.clearAllMocks()
    mockRouter.push.mockClear()
    mockRouter.replace.mockClear()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
  })

  describe('Props validation', () => {
    it('should accept title prop', () => {
      wrapper = mount(BaseDashboardHeader, {
        ...mountOptions,
        props: {
          title: 'Test Title'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should accept breadcrumbs prop', () => {
      wrapper = mount(BaseDashboardHeader, {
        ...mountOptions,
        props: {
          breadcrumbs: [
            { label: 'Home', to: '/' },
            { label: 'Dashboard' }
          ]
        }
      })
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Rendering', () => {
    it('should render title when provided', () => {
      wrapper = mount(BaseDashboardHeader, {
        ...mountOptions,
        props: {
          title: 'Test Title'
        }
      })

      expect(wrapper.text()).toContain('Test Title')
    })

    it('should render subtitle when provided', () => {
      wrapper = mount(BaseDashboardHeader, {
        ...mountOptions,
        props: {
          title: 'Test Title',
          subtitle: 'Test Subtitle'
        }
      })

      expect(wrapper.text()).toContain('Test Subtitle')
    })

    it('should render breadcrumbs when provided', () => {
      wrapper = mount(BaseDashboardHeader, {
        ...mountOptions,
        props: {
          breadcrumbs: [
            { label: 'Home', to: '/' },
            { label: 'Dashboard' }
          ]
        }
      })

      expect(wrapper.text()).toContain('Home')
      expect(wrapper.text()).toContain('Dashboard')
    })
  })

  describe('Slots', () => {
    it('should render brand slot when provided', () => {
      wrapper = mount(BaseDashboardHeader, {
        ...mountOptions,
        slots: {
          brand: '<div>Custom Brand</div>'
        }
      })

      expect(wrapper.text()).toContain('Custom Brand')
    })

    it('should render icon slot when provided', () => {
      wrapper = mount(BaseDashboardHeader, {
        ...mountOptions,
        slots: {
          icon: '<svg>Icon</svg>'
        }
      })

      expect(wrapper.text()).toContain('Icon')
    })

    it('should render actions slot when provided', () => {
      wrapper = mount(BaseDashboardHeader, {
        ...mountOptions,
        slots: {
          actions: '<button>Action</button>'
        }
      })

      expect(wrapper.text()).toContain('Action')
    })
  })
})


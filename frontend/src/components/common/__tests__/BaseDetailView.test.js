/**
 * Unit tests for BaseDetailView component
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseDetailView from '../BaseDetailView.vue'

vi.mock('@/utils/security', () => ({
  escapeHTML: vi.fn((str) => str ? str.replaceAll('<', '&lt;').replaceAll('>', '&gt;') : '')
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

vi.mock('vue-router', () => ({
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
}))

describe('BaseDetailView', () => {
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
      wrapper = mount(BaseDetailView, {
        ...mountOptions,
        props: {
          title: 'Test Title'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should accept breadcrumbs prop', () => {
      wrapper = mount(BaseDetailView, {
        ...mountOptions,
        props: {
          breadcrumbs: [
            { label: 'Home', to: '/' },
            { label: 'Detail' }
          ]
        }
      })
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Rendering', () => {
    it('should render breadcrumbs when provided', () => {
      wrapper = mount(BaseDetailView, {
        ...mountOptions,
        props: {
          breadcrumbs: [
            { label: 'Home', to: '/' },
            { label: 'Detail' }
          ]
        }
      })

      expect(wrapper.text()).toContain('Home')
      expect(wrapper.text()).toContain('Detail')
    })

    it('should show loading state when loading is true', () => {
      wrapper = mount(BaseDetailView, {
        ...mountOptions,
        props: {
          loading: true
        }
      })

      expect(wrapper.text()).toContain('Cargando')
    })

    it('should show error state when error is provided', () => {
      wrapper = mount(BaseDetailView, {
        ...mountOptions,
        props: {
          error: 'Test error'
        }
      })

      expect(wrapper.text()).toContain('Test error')
    })

    it('should render title when provided', () => {
      wrapper = mount(BaseDetailView, {
        ...mountOptions,
        props: {
          title: 'Test Title'
        }
      })

      expect(wrapper.text()).toContain('Test Title')
    })

    it('should render subtitle when provided', () => {
      wrapper = mount(BaseDetailView, {
        ...mountOptions,
        props: {
          title: 'Test Title',
          subtitle: 'Test Subtitle'
        }
      })

      expect(wrapper.text()).toContain('Test Subtitle')
    })

    it('should show edit button when showEditButton is true and canEdit is true', () => {
      wrapper = mount(BaseDetailView, {
        ...mountOptions,
        props: {
          title: 'Test Title',
          showEditButton: true,
          canEdit: true
        }
      })

      expect(wrapper.text()).toContain('Editar')
    })

    it('should not show edit button when canEdit is false', () => {
      wrapper = mount(BaseDetailView, {
        ...mountOptions,
        props: {
          showEditButton: true,
          canEdit: false
        }
      })

      const editButton = wrapper.find('button')
      expect(editButton.exists()).toBe(false)
    })

    it('should render status badge when provided', () => {
      wrapper = mount(BaseDetailView, {
        ...mountOptions,
        props: {
          title: 'Test Title',
          statusBadge: 'activo'
        }
      })

      expect(wrapper.text()).toContain('activo')
    })

    it('should render statistics when provided', () => {
      wrapper = mount(BaseDetailView, {
        ...mountOptions,
        props: {
          statistics: [
            { label: 'Total', value: 100, color: 'primary' },
            { label: 'Active', value: 50, color: 'success' }
          ]
        }
      })

      expect(wrapper.text()).toContain('Total')
      expect(wrapper.text()).toContain('100')
    })
  })

  describe('Events', () => {
    it('should emit edit event when edit button is clicked', async () => {
      wrapper = mount(BaseDetailView, {
        ...mountOptions,
        props: {
          title: 'Test Title',
          showEditButton: true,
          canEdit: true
        }
      })

      const editButton = wrapper.find('button')
      expect(editButton.exists()).toBe(true)
      await editButton.trigger('click')

      expect(wrapper.emitted('edit')).toBeTruthy()
    })

    it('should emit retry event when retry button is clicked', async () => {
      wrapper = mount(BaseDetailView, {
        ...mountOptions,
        props: {
          error: 'Test error',
          showRetryButton: true
        }
      })

      const retryButton = wrapper.find('button')
      await retryButton.trigger('click')

      expect(wrapper.emitted('retry')).toBeTruthy()
    })
  })

  describe('Slots', () => {
    it('should render header slot when provided', () => {
      wrapper = mount(BaseDetailView, {
        ...mountOptions,
        slots: {
          header: '<div>Custom Header</div>'
        }
      })

      expect(wrapper.text()).toContain('Custom Header')
    })

    it('should render main slot when provided', () => {
      wrapper = mount(BaseDetailView, {
        ...mountOptions,
        slots: {
          main: '<div>Main Content</div>'
        }
      })

      expect(wrapper.text()).toContain('Main Content')
    })

    it('should render actions slot when provided', () => {
      wrapper = mount(BaseDetailView, {
        ...mountOptions,
        slots: {
          actions: '<button>Action</button>'
        }
      })

      expect(wrapper.text()).toContain('Action')
    })
  })

  describe('Methods', () => {
    it('should return correct status badge class for activo', () => {
      wrapper = mount(BaseDetailView, {
        ...mountOptions
      })

      const badgeClass = wrapper.vm.getStatusBadgeClass('activo')
      expect(badgeClass).toContain('bg-success')
    })

    it('should return correct status badge class for error', () => {
      wrapper = mount(BaseDetailView, {
        ...mountOptions
      })

      const badgeClass = wrapper.vm.getStatusBadgeClass('error')
      expect(badgeClass).toContain('bg-danger')
    })
  })
})

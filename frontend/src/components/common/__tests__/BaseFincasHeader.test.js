/**
 * Unit tests for BaseFincasHeader component
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseFincasHeader from '../BaseFincasHeader.vue'

describe('BaseFincasHeader', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

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

  describe('Props validation', () => {
    it('should accept title prop', () => {
      wrapper = mount(BaseFincasHeader, {
        ...mountOptions,
        props: {
          title: 'Test Title'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should accept breadcrumbs prop', () => {
      wrapper = mount(BaseFincasHeader, {
        ...mountOptions,
        props: {
          breadcrumbs: [
            { label: 'Home', to: '/' },
            { label: 'Fincas' }
          ]
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should accept actions prop', () => {
      wrapper = mount(BaseFincasHeader, {
        ...mountOptions,
        props: {
          actions: [
            { key: 'add', label: 'Add' }
          ]
        }
      })
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Rendering', () => {
    it('should render title when provided', () => {
      wrapper = mount(BaseFincasHeader, {
        ...mountOptions,
        props: {
          title: 'Test Title'
        }
      })

      expect(wrapper.text()).toContain('Test Title')
    })

    it('should render subtitle when provided', () => {
      wrapper = mount(BaseFincasHeader, {
        ...mountOptions,
        props: {
          title: 'Test Title',
          subtitle: 'Test Subtitle'
        }
      })

      expect(wrapper.text()).toContain('Test Subtitle')
    })

    it('should render breadcrumbs when provided', () => {
      wrapper = mount(BaseFincasHeader, {
        ...mountOptions,
        props: {
          breadcrumbs: [
            { label: 'Home', to: '/' },
            { label: 'Fincas' }
          ]
        }
      })

      expect(wrapper.text()).toContain('Home')
      expect(wrapper.text()).toContain('Fincas')
    })

    it('should render actions when provided', () => {
      wrapper = mount(BaseFincasHeader, {
        ...mountOptions,
        props: {
          actions: [
            { key: 'add', label: 'Add Finca' }
          ]
        }
      })

      expect(wrapper.text()).toContain('Add Finca')
    })
  })

  describe('Events', () => {
    it('should emit action-click event when action is clicked', async () => {
      wrapper = mount(BaseFincasHeader, {
        ...mountOptions,
        props: {
          actions: [
            { key: 'add', label: 'Add' }
          ]
        }
      })

      const actionButton = wrapper.find('button')
      await actionButton.trigger('click')

      expect(wrapper.emitted('action-click')).toBeTruthy()
    })
  })

  describe('Slots', () => {
    it('should render actions slot when provided', () => {
      wrapper = mount(BaseFincasHeader, {
        ...mountOptions,
        slots: {
          actions: '<button>Custom Action</button>'
        }
      })

      expect(wrapper.text()).toContain('Custom Action')
    })
  })
})

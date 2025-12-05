import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import DashboardWidget from '../DashboardWidget.vue'

describe('DashboardWidget', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget'
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should display title', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget'
        }
      })

      expect(wrapper.text()).toContain('Test Widget')
    })

    it('should display icon when provided', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          icon: 'fas fa-chart-bar'
        }
      })

      const icon = wrapper.find('.widget-icon')
      expect(icon.exists()).toBe(true)
      expect(icon.classes()).toContain('fas')
      expect(icon.classes()).toContain('fa-chart-bar')
    })

    it('should not display icon when not provided', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget'
        }
      })

      const icon = wrapper.find('.widget-icon')
      expect(icon.exists()).toBe(false)
    })

    it('should render default slot content', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget'
        },
        slots: {
          default: '<div class="test-content">Widget Content</div>'
        }
      })

      expect(wrapper.find('.test-content').exists()).toBe(true)
      expect(wrapper.text()).toContain('Widget Content')
    })

    it('should render actions slot', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget'
        },
        slots: {
          actions: '<button class="custom-action">Action</button>'
        }
      })

      expect(wrapper.find('.custom-action').exists()).toBe(true)
    })

    it('should render footer slot when footer prop is true', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          footer: true
        },
        slots: {
          footer: '<div class="footer-content">Footer Content</div>'
        }
      })

      expect(wrapper.find('.widget-footer').exists()).toBe(true)
      expect(wrapper.find('.footer-content').exists()).toBe(true)
    })

    it('should not render footer when footer prop is false', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          footer: false
        },
        slots: {
          footer: '<div class="footer-content">Footer Content</div>'
        }
      })

      expect(wrapper.find('.widget-footer').exists()).toBe(false)
    })
  })

  describe('Loading State', () => {
    it('should display loading state when loading is true', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          loading: true
        }
      })

      expect(wrapper.find('.widget-loading').exists()).toBe(true)
      expect(wrapper.find('.loading-spinner').exists()).toBe(true)
    })

    it('should display default loading text', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          loading: true
        }
      })

      expect(wrapper.text()).toContain('Cargando...')
    })

    it('should display custom loading text', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          loading: true,
          loadingText: 'Loading data...'
        }
      })

      expect(wrapper.text()).toContain('Loading data...')
    })

    it('should not display widget body when loading', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          loading: true
        },
        slots: {
          default: '<div class="test-content">Content</div>'
        }
      })

      expect(wrapper.find('.widget-body').exists()).toBe(false)
      expect(wrapper.find('.test-content').exists()).toBe(false)
    })

    it('should disable refresh button when loading', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          loading: true,
          refreshable: true
        }
      })

      const refreshButton = wrapper.find('.refresh-btn')
      expect(refreshButton.attributes('disabled')).toBeDefined()
    })

    it('should add fa-spin class to refresh icon when loading', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          loading: true,
          refreshable: true
        }
      })

      const refreshIcon = wrapper.find('.fa-sync-alt')
      expect(refreshIcon.classes()).toContain('fa-spin')
    })
  })

  describe('Error State', () => {
    it('should display error state when error is provided', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          error: 'Error loading data'
        }
      })

      expect(wrapper.find('.widget-error').exists()).toBe(true)
      expect(wrapper.text()).toContain('Error loading data')
    })

    it('should display retry button when error and retryable is true', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          error: 'Error loading data',
          retryable: true
        }
      })

      expect(wrapper.find('.retry-btn').exists()).toBe(true)
      expect(wrapper.text()).toContain('Reintentar')
    })

    it('should not display retry button when retryable is false', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          error: 'Error loading data',
          retryable: false
        }
      })

      expect(wrapper.find('.retry-btn').exists()).toBe(false)
    })

    it('should not display widget body when error', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          error: 'Error loading data'
        },
        slots: {
          default: '<div class="test-content">Content</div>'
        }
      })

      expect(wrapper.find('.widget-body').exists()).toBe(false)
      expect(wrapper.find('.test-content').exists()).toBe(false)
    })

    it('should not display loading when error is present', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          loading: true,
          error: 'Error loading data'
        }
      })

      const widgetContent = wrapper.find('.widget-content')
      const loadingDiv = widgetContent.find('.widget-loading')
      expect(loadingDiv.exists()).toBe(false)
      expect(wrapper.find('.widget-error').exists()).toBe(true)
    })
  })

  describe('Normal State', () => {
    it('should display widget body when not loading and no error', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          loading: false,
          error: ''
        },
        slots: {
          default: '<div class="test-content">Content</div>'
        }
      })

      expect(wrapper.find('.widget-body').exists()).toBe(true)
      expect(wrapper.find('.test-content').exists()).toBe(true)
    })

    it('should not display loading when not loading', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          loading: false
        }
      })

      expect(wrapper.find('.widget-loading').exists()).toBe(false)
    })

    it('should not display error when no error', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          error: ''
        }
      })

      expect(wrapper.find('.widget-error').exists()).toBe(false)
    })
  })

  describe('Variants', () => {
    it('should apply default variant class', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          variant: 'default'
        }
      })

      expect(wrapper.classes()).toContain('widget-default')
    })

    it('should apply primary variant class', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          variant: 'primary'
        }
      })

      expect(wrapper.classes()).toContain('widget-primary')
    })

    it('should apply success variant class', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          variant: 'success'
        }
      })

      expect(wrapper.classes()).toContain('widget-success')
    })

    it('should apply warning variant class', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          variant: 'warning'
        }
      })

      expect(wrapper.classes()).toContain('widget-warning')
    })

    it('should apply danger variant class', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          variant: 'danger'
        }
      })

      expect(wrapper.classes()).toContain('widget-danger')
    })

    it('should apply info variant class', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          variant: 'info'
        }
      })

      expect(wrapper.classes()).toContain('widget-info')
    })
  })

  describe('Sizes', () => {
    it('should apply small size class', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          size: 'small'
        }
      })

      expect(wrapper.classes()).toContain('widget-small')
    })

    it('should apply medium size class by default', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget'
        }
      })

      expect(wrapper.classes()).toContain('widget-medium')
    })

    it('should apply large size class', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          size: 'large'
        }
      })

      expect(wrapper.classes()).toContain('widget-large')
    })

    it('should apply full size class', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          size: 'full'
        }
      })

      expect(wrapper.classes()).toContain('widget-full')
    })
  })

  describe('Refresh Functionality', () => {
    it('should display refresh button when refreshable is true', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          refreshable: true
        }
      })

      expect(wrapper.find('.refresh-btn').exists()).toBe(true)
    })

    it('should not display refresh button when refreshable is false', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          refreshable: false
        }
      })

      expect(wrapper.find('.refresh-btn').exists()).toBe(false)
    })

    it('should emit refresh event when refresh button is clicked', async () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          refreshable: true,
          loading: false
        }
      })

      const refreshButton = wrapper.find('.refresh-btn')
      await refreshButton.trigger('click')

      expect(wrapper.emitted('refresh')).toBeTruthy()
      expect(wrapper.emitted('refresh')).toHaveLength(1)
    })

    it('should not emit refresh when button is disabled', async () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          refreshable: true,
          loading: true
        }
      })

      const refreshButton = wrapper.find('.refresh-btn')
      await refreshButton.trigger('click')

      expect(wrapper.emitted('refresh')).toBeFalsy()
    })
  })

  describe('Retry Functionality', () => {
    it('should emit retry event when retry button is clicked', async () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          error: 'Error message',
          retryable: true
        }
      })

      const retryButton = wrapper.find('.retry-btn')
      await retryButton.trigger('click')

      expect(wrapper.emitted('retry')).toBeTruthy()
      expect(wrapper.emitted('retry')).toHaveLength(1)
    })
  })

  describe('Clickable State', () => {
    it('should apply clickable class when clickable is true', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          clickable: true
        }
      })

      expect(wrapper.classes()).toContain('widget-clickable')
    })

    it('should not apply clickable class when clickable is false', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          clickable: false
        }
      })

      expect(wrapper.classes()).not.toContain('widget-clickable')
    })

    it('should emit click event when clickable and clicked', async () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          clickable: true
        }
      })

      await wrapper.trigger('click')

      expect(wrapper.emitted('click')).toBeTruthy()
    })
  })

  describe('Computed Classes', () => {
    it('should apply loading class when loading', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          loading: true
        }
      })

      expect(wrapper.classes()).toContain('widget-loading')
    })

    it('should apply error class when error is present', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          error: 'Error message'
        }
      })

      expect(wrapper.classes()).toContain('widget-error')
    })

    it('should apply multiple classes correctly', () => {
      wrapper = mount(DashboardWidget, {
        props: {
          title: 'Test Widget',
          variant: 'primary',
          size: 'large',
          clickable: true,
          loading: true
        }
      })

      expect(wrapper.classes()).toContain('widget-primary')
      expect(wrapper.classes()).toContain('widget-large')
      expect(wrapper.classes()).toContain('widget-clickable')
      expect(wrapper.classes()).toContain('widget-loading')
    })
  })

  describe('Props Validation', () => {
    it('should accept valid variant values', () => {
      const validVariants = ['default', 'primary', 'success', 'warning', 'danger', 'info']
      
      for (const variant of validVariants) {
        wrapper = mount(DashboardWidget, {
          props: {
            title: 'Test Widget',
            variant
          }
        })

        expect(wrapper.exists()).toBe(true)
        expect(wrapper.classes()).toContain(`widget-${variant}`)
        wrapper.unmount()
      }
    })

    it('should accept valid size values', () => {
      const validSizes = ['small', 'medium', 'large', 'full']
      
      for (const size of validSizes) {
        wrapper = mount(DashboardWidget, {
          props: {
            title: 'Test Widget',
            size
          }
        })

        expect(wrapper.exists()).toBe(true)
        expect(wrapper.classes()).toContain(`widget-${size}`)
        wrapper.unmount()
      }
    })
  })
})


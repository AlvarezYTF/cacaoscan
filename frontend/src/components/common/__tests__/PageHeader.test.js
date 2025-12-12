import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import PageHeader from '../PageHeader.vue'

// Mock router-link
const mockRouterLink = {
  name: 'RouterLink',
  template: '<a><slot></slot></a>',
  props: ['to']
}

describe('PageHeader', () => {
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
      wrapper = mount(PageHeader, {
        props: {
          title: 'Test Title'
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should display title', () => {
      wrapper = mount(PageHeader, {
        props: {
          title: 'Test Title'
        }
      })

      expect(wrapper.text()).toContain('Test Title')
    })

    it('should display description when provided', () => {
      wrapper = mount(PageHeader, {
        props: {
          title: 'Test Title',
          description: 'Test Description'
        }
      })

      expect(wrapper.text()).toContain('Test Description')
    })

    it('should display subtitle when provided', () => {
      wrapper = mount(PageHeader, {
        props: {
          title: 'Test Title',
          subtitle: 'Test Subtitle',
          variant: 'simple'
        }
      })

      expect(wrapper.text()).toContain('Test Subtitle')
    })

    it('should display badge text when provided', () => {
      wrapper = mount(PageHeader, {
        props: {
          title: 'Test Title',
          badgeText: 'New'
        }
      })

      expect(wrapper.text()).toContain('New')
    })
  })

  describe('Variants', () => {
    it('should render centered variant by default', () => {
      wrapper = mount(PageHeader, {
        props: {
          title: 'Test Title'
        }
      })

      expect(wrapper.find('.bg-gradient-to-r').exists()).toBe(true)
    })

    it('should render simple variant', () => {
      wrapper = mount(PageHeader, {
        props: {
          title: 'Test Title',
          variant: 'simple'
        }
      })

      expect(wrapper.find('header').exists()).toBe(true)
      expect(wrapper.find('.bg-gradient-to-r').exists()).toBe(false)
    })
  })

  describe('Back Button', () => {
    it('should display back button when showBackButton is true', () => {
      wrapper = mount(PageHeader, {
        props: {
          title: 'Test Title',
          showBackButton: true
        },
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      const backLink = wrapper.findComponent({ name: 'RouterLink' })
      expect(backLink.exists()).toBe(true)
    })

    it('should not display back button when showBackButton is false', () => {
      wrapper = mount(PageHeader, {
        props: {
          title: 'Test Title',
          showBackButton: false
        },
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      const backLinks = wrapper.findAllComponents({ name: 'RouterLink' })
      const backButton = backLinks.find(link => link.text().includes('Volver'))
      expect(backButton).toBeUndefined()
    })

    it('should use default back text', () => {
      wrapper = mount(PageHeader, {
        props: {
          title: 'Test Title',
          showBackButton: true
        },
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('Volver')
    })

    it('should use custom back text', () => {
      wrapper = mount(PageHeader, {
        props: {
          title: 'Test Title',
          showBackButton: true,
          backText: 'Go Back'
        },
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('Go Back')
    })

    it('should use default back route', () => {
      wrapper = mount(PageHeader, {
        props: {
          title: 'Test Title',
          showBackButton: true
        },
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      const backLink = wrapper.findComponent({ name: 'RouterLink' })
      expect(backLink.props('to')).toBe('/')
    })

    it('should use custom back route', () => {
      wrapper = mount(PageHeader, {
        props: {
          title: 'Test Title',
          showBackButton: true,
          backRoute: '/custom'
        },
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      const backLink = wrapper.findComponent({ name: 'RouterLink' })
      expect(backLink.props('to')).toBe('/custom')
    })
  })

  describe('Icon', () => {
    it('should display icon when showIcon is true', () => {
      wrapper = mount(PageHeader, {
        props: {
          title: 'Test Title',
          variant: 'simple',
          showIcon: true
        }
      })

      const icon = wrapper.find('svg')
      expect(icon.exists()).toBe(true)
    })

    it('should not display icon when showIcon is false', () => {
      wrapper = mount(PageHeader, {
        props: {
          title: 'Test Title',
          variant: 'simple',
          showIcon: false
        }
      })

      const svgIcons = wrapper.findAll('svg')
      const headerIcon = svgIcons.find(svg => svg.classes().includes('text-green-600'))
      expect(headerIcon).toBeUndefined()
    })
  })

  describe('Slots', () => {
    it('should render actions slot', () => {
      wrapper = mount(PageHeader, {
        props: {
          title: 'Test Title',
          variant: 'simple'
        },
        slots: {
          actions: '<button class="action-btn">Action</button>'
        }
      })

      expect(wrapper.find('.action-btn').exists()).toBe(true)
    })
  })
})


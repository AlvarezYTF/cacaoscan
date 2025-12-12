import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseHero from '../BaseHero.vue'

const mockRouter = {
  push: vi.fn()
}

vi.mock('vue-router', () => ({
  useRouter: () => mockRouter
}))

describe('BaseHero', () => {
  let wrapper

  beforeEach(() => {
    mockRouter.push.mockClear()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
  })

  describe('Rendering', () => {
    it('should render with title', () => {
      wrapper = mount(BaseHero, {
        props: {
          title: 'Hero Title'
        }
      })

      expect(wrapper.text()).toContain('Hero Title')
    })

    it('should render with subtitle', () => {
      wrapper = mount(BaseHero, {
        props: {
          title: 'Hero Title',
          subtitle: 'Hero Subtitle'
        }
      })

      expect(wrapper.text()).toContain('Hero Title')
      expect(wrapper.text()).toContain('Hero Subtitle')
    })

    it('should render badge when provided', () => {
      wrapper = mount(BaseHero, {
        props: {
          title: 'Hero Title',
          badge: 'New Feature'
        }
      })

      expect(wrapper.text()).toContain('New Feature')
    })
  })

  describe('CTA Button', () => {
    it('should render CTA button when ctaText is provided', () => {
      wrapper = mount(BaseHero, {
        props: {
          title: 'Hero Title',
          ctaText: 'Get Started'
        }
      })

      const button = wrapper.find('button')
      expect(button.exists()).toBe(true)
      expect(button.text()).toContain('Get Started')
    })

    it('should emit cta-click event when CTA button is clicked', async () => {
      wrapper = mount(BaseHero, {
        props: {
          title: 'Hero Title',
          ctaText: 'Get Started'
        }
      })

      const button = wrapper.find('button')
      await button.trigger('click')

      expect(wrapper.emitted('cta-click')).toBeTruthy()
    })

    it('should navigate to ctaLink when button is clicked', async () => {
      wrapper = mount(BaseHero, {
        props: {
          title: 'Hero Title',
          ctaText: 'Get Started',
          ctaLink: '/dashboard'
        }
      })

      const button = wrapper.find('button')
      await button.trigger('click')

      expect(mockRouter.push).toHaveBeenCalledWith('/dashboard')
    })
  })

  describe('Trust Indicators', () => {
    it('should render trust indicators when provided', () => {
      wrapper = mount(BaseHero, {
        props: {
          title: 'Hero Title',
          trustIndicators: ['Indicator 1', 'Indicator 2']
        }
      })

      expect(wrapper.text()).toContain('Indicator 1')
      expect(wrapper.text()).toContain('Indicator 2')
    })

    it('should not render trust indicators when empty array', () => {
      wrapper = mount(BaseHero, {
        props: {
          title: 'Hero Title',
          trustIndicators: []
        }
      })

      const indicatorsContainer = wrapper.find('.flex.flex-wrap')
      expect(indicatorsContainer.exists()).toBe(false)
    })
  })

  describe('Decorations', () => {
    it('should show decorations by default', () => {
      wrapper = mount(BaseHero, {
        props: {
          title: 'Hero Title'
        }
      })

      const decorations = wrapper.find('.absolute.inset-0.opacity-10')
      expect(decorations.exists()).toBe(true)
    })

    it('should hide decorations when showDecorations is false', () => {
      wrapper = mount(BaseHero, {
        props: {
          title: 'Hero Title',
          showDecorations: false
        }
      })

      const decorations = wrapper.find('.absolute.inset-0.opacity-10')
      expect(decorations.exists()).toBe(false)
    })
  })

  describe('Slots', () => {
    it('should render title slot when provided', () => {
      wrapper = mount(BaseHero, {
        props: {
          title: 'Default Title'
        },
        slots: {
          title: '<span class="custom-title">Custom Title</span>'
        }
      })

      expect(wrapper.find('.custom-title').exists()).toBe(true)
      expect(wrapper.text()).not.toContain('Default Title')
    })

    it('should render content slot when provided', () => {
      wrapper = mount(BaseHero, {
        props: {
          title: 'Hero Title'
        },
        slots: {
          content: '<div class="custom-content">Custom Content</div>'
        }
      })

      expect(wrapper.find('.custom-content').exists()).toBe(true)
    })
  })
})


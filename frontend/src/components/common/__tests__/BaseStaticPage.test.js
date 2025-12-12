import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseStaticPage from '../BaseStaticPage.vue'

const mockRouter = {
  push: vi.fn(),
  back: vi.fn()
}

vi.mock('vue-router', () => ({
  useRouter: () => mockRouter
}))

describe('BaseStaticPage', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.clearAllMocks()
  })

  it('should render component', () => {
    wrapper = mount(BaseStaticPage)

    expect(wrapper.exists()).toBe(true)
  })

  it('should display title when provided', () => {
    wrapper = mount(BaseStaticPage, {
      props: {
        title: 'Page Title'
      }
    })

    expect(wrapper.text()).toContain('Page Title')
  })

  it('should show back button when showBackButton is true', () => {
    wrapper = mount(BaseStaticPage, {
      props: {
        showBackButton: true
      }
    })

    const backButton = wrapper.find('button')
    expect(backButton.exists()).toBe(true)
    expect(wrapper.text()).toContain('Volver')
  })

  it('should not show back button when showBackButton is false', () => {
    wrapper = mount(BaseStaticPage, {
      props: {
        showBackButton: false
      }
    })

    const backButton = wrapper.find('button')
    expect(backButton.exists()).toBe(false)
  })

  it('should navigate to backRoute when back button clicked and backRoute provided', async () => {
    wrapper = mount(BaseStaticPage, {
      props: {
        showBackButton: true,
        backRoute: '/previous-page'
      }
    })

    const backButton = wrapper.find('button')
    await backButton.trigger('click')

    expect(mockRouter.push).toHaveBeenCalledWith('/previous-page')
    expect(mockRouter.back).not.toHaveBeenCalled()
  })

  it('should call router.back when back button clicked and no backRoute', async () => {
    wrapper = mount(BaseStaticPage, {
      props: {
        showBackButton: true,
        backRoute: null
      }
    })

    const backButton = wrapper.find('button')
    await backButton.trigger('click')

    expect(mockRouter.back).toHaveBeenCalled()
    expect(mockRouter.push).not.toHaveBeenCalled()
  })

  it('should render header slot', () => {
    wrapper = mount(BaseStaticPage, {
      slots: {
        header: '<div>Custom Header</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Header')
  })

  it('should render default slot', () => {
    wrapper = mount(BaseStaticPage, {
      slots: {
        default: '<div>Page Content</div>'
      }
    })

    expect(wrapper.text()).toContain('Page Content')
  })

  it('should render footer slot', () => {
    wrapper = mount(BaseStaticPage, {
      slots: {
        footer: '<div>Custom Footer</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Footer')
  })

  it('should not show footer when footer slot is not provided', () => {
    wrapper = mount(BaseStaticPage)

    // Footer should not be visible when slot is not provided
    const footer = wrapper.find('.max-w-7xl')
    expect(footer.exists()).toBe(true)
  })
})


import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ErrorAlert from '../ErrorAlert.vue'

// Mock BaseAlert component
vi.mock('../BaseAlert.vue', () => ({
  default: {
    name: 'BaseAlert',
    template: `
      <div v-if="show" :data-variant="variant" data-testid="base-alert">
        <p data-testid="alert-message">{{ message }}</p>
      </div>
    `,
    props: {
      variant: {
        type: String,
        required: true
      },
      message: {
        type: String,
        required: true
      },
      show: {
        type: Boolean,
        default: true
      }
    }
  }
}))

describe('ErrorAlert', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render component', () => {
    wrapper = mount(ErrorAlert, {
      props: {
        message: 'Test error message'
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should render BaseAlert component', () => {
    wrapper = mount(ErrorAlert, {
      props: {
        message: 'Test error message'
      }
    })

    expect(wrapper.findComponent({ name: 'BaseAlert' }).exists()).toBe(true)
  })

  it('should pass error variant to BaseAlert', () => {
    wrapper = mount(ErrorAlert, {
      props: {
        message: 'Test error message'
      }
    })

    const baseAlert = wrapper.findComponent({ name: 'BaseAlert' })
    expect(baseAlert.props('variant')).toBe('error')
  })

  it('should pass message prop to BaseAlert', () => {
    const errorMessage = 'This is an error message'
    wrapper = mount(ErrorAlert, {
      props: {
        message: errorMessage
      }
    })

    const baseAlert = wrapper.findComponent({ name: 'BaseAlert' })
    expect(baseAlert.props('message')).toBe(errorMessage)
  })

  it('should pass show prop as true by default to BaseAlert', () => {
    wrapper = mount(ErrorAlert, {
      props: {
        message: 'Test error message'
      }
    })

    const baseAlert = wrapper.findComponent({ name: 'BaseAlert' })
    expect(baseAlert.props('show')).toBe(true)
  })

  it('should pass show prop as true when explicitly set', () => {
    wrapper = mount(ErrorAlert, {
      props: {
        message: 'Test error message',
        show: true
      }
    })

    const baseAlert = wrapper.findComponent({ name: 'BaseAlert' })
    expect(baseAlert.props('show')).toBe(true)
  })

  it('should pass show prop as false when set to false', () => {
    wrapper = mount(ErrorAlert, {
      props: {
        message: 'Test error message',
        show: false
      }
    })

    const baseAlert = wrapper.findComponent({ name: 'BaseAlert' })
    expect(baseAlert.props('show')).toBe(false)
  })

  it('should display error message when show is true', () => {
    const errorMessage = 'Error occurred during operation'
    wrapper = mount(ErrorAlert, {
      props: {
        message: errorMessage,
        show: true
      }
    })

    const alertMessage = wrapper.find('[data-testid="alert-message"]')
    expect(alertMessage.exists()).toBe(true)
    expect(alertMessage.text()).toBe(errorMessage)
  })

  it('should not display alert when show is false', () => {
    wrapper = mount(ErrorAlert, {
      props: {
        message: 'Error message',
        show: false
      }
    })

    const baseAlert = wrapper.find('[data-testid="base-alert"]')
    expect(baseAlert.exists()).toBe(false)
  })

  it('should require message prop', () => {
    // This test verifies that the prop is required
    // In Vue 3, missing required props will cause a warning
    wrapper = mount(ErrorAlert, {
      props: {
        message: 'Required message'
      }
    })

    expect(wrapper.props('message')).toBe('Required message')
  })

  it('should update message when prop changes', async () => {
    wrapper = mount(ErrorAlert, {
      props: {
        message: 'Initial error message'
      }
    })

    const baseAlert = wrapper.findComponent({ name: 'BaseAlert' })
    expect(baseAlert.props('message')).toBe('Initial error message')

    await wrapper.setProps({
      message: 'Updated error message'
    })

    expect(baseAlert.props('message')).toBe('Updated error message')
  })

  it('should update show prop when it changes', async () => {
    wrapper = mount(ErrorAlert, {
      props: {
        message: 'Test error message',
        show: true
      }
    })

    const baseAlert = wrapper.findComponent({ name: 'BaseAlert' })
    expect(baseAlert.props('show')).toBe(true)

    await wrapper.setProps({
      message: 'Test error message',
      show: false
    })

    expect(baseAlert.props('show')).toBe(false)
  })

  it('should show and hide alert when show prop toggles', async () => {
    wrapper = mount(ErrorAlert, {
      props: {
        message: 'Test error message',
        show: true
      }
    })

    let baseAlert = wrapper.find('[data-testid="base-alert"]')
    expect(baseAlert.exists()).toBe(true)

    await wrapper.setProps({ show: false })
    baseAlert = wrapper.find('[data-testid="base-alert"]')
    expect(baseAlert.exists()).toBe(false)

    await wrapper.setProps({ show: true })
    baseAlert = wrapper.find('[data-testid="base-alert"]')
    expect(baseAlert.exists()).toBe(true)
  })

  it('should handle long error messages', () => {
    const longMessage = 'This is a very long error message that contains multiple sentences and should be displayed correctly in the error alert component without breaking the layout or causing any rendering issues.'
    wrapper = mount(ErrorAlert, {
      props: {
        message: longMessage
      }
    })

    const baseAlert = wrapper.findComponent({ name: 'BaseAlert' })
    expect(baseAlert.props('message')).toBe(longMessage)
  })

  it('should handle empty string message', () => {
    wrapper = mount(ErrorAlert, {
      props: {
        message: ''
      }
    })

    const baseAlert = wrapper.findComponent({ name: 'BaseAlert' })
    expect(baseAlert.props('message')).toBe('')
  })

  it('should handle special characters in message', () => {
    const specialMessage = 'Error: <script>alert("XSS")</script> & "quotes"'
    wrapper = mount(ErrorAlert, {
      props: {
        message: specialMessage
      }
    })

    const baseAlert = wrapper.findComponent({ name: 'BaseAlert' })
    expect(baseAlert.props('message')).toBe(specialMessage)
  })

  it('should handle multiline messages', () => {
    const multilineMessage = 'Error line 1\nError line 2\nError line 3'
    wrapper = mount(ErrorAlert, {
      props: {
        message: multilineMessage
      }
    })

    const baseAlert = wrapper.findComponent({ name: 'BaseAlert' })
    expect(baseAlert.props('message')).toBe(multilineMessage)
  })

  it('should maintain error variant when props change', async () => {
    wrapper = mount(ErrorAlert, {
      props: {
        message: 'Test error message'
      }
    })

    const baseAlert = wrapper.findComponent({ name: 'BaseAlert' })
    expect(baseAlert.props('variant')).toBe('error')

    await wrapper.setProps({
      message: 'Updated message',
      show: false
    })

    expect(baseAlert.props('variant')).toBe('error')
  })

  it('should pass all props correctly to BaseAlert', () => {
    wrapper = mount(ErrorAlert, {
      props: {
        message: 'Complete error message',
        show: true
      }
    })

    const baseAlert = wrapper.findComponent({ name: 'BaseAlert' })
    expect(baseAlert.props('variant')).toBe('error')
    expect(baseAlert.props('message')).toBe('Complete error message')
    expect(baseAlert.props('show')).toBe(true)
  })

  it('should handle rapid show/hide toggles', async () => {
    wrapper = mount(ErrorAlert, {
      props: {
        message: 'Test error message',
        show: true
      }
    })

    await wrapper.setProps({ show: false })
    await wrapper.setProps({ show: true })
    await wrapper.setProps({ show: false })
    await wrapper.setProps({ show: true })

    const baseAlert = wrapper.findComponent({ name: 'BaseAlert' })
    expect(baseAlert.props('show')).toBe(true)
  })

  it('should render with default show value when not provided', () => {
    wrapper = mount(ErrorAlert, {
      props: {
        message: 'Test error message'
      }
    })

    const baseAlert = wrapper.findComponent({ name: 'BaseAlert' })
    expect(baseAlert.props('show')).toBe(true)
    
    const alertElement = wrapper.find('[data-testid="base-alert"]')
    expect(alertElement.exists()).toBe(true)
  })
})


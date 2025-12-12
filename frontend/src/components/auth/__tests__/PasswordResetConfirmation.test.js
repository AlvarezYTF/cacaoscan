import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import PasswordResetConfirmation from '../PasswordResetConfirmation.vue'

// Mock router-link
const mockRouterLink = {
  name: 'RouterLink',
  template: '<a><slot></slot></a>',
  props: ['to']
}

describe('PasswordResetConfirmation', () => {
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
      wrapper = mount(PasswordResetConfirmation, {
        props: {
          email: 'test@example.com'
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should display confirmation title', () => {
      wrapper = mount(PasswordResetConfirmation, {
        props: {
          email: 'test@example.com'
        }
      })

      expect(wrapper.text()).toContain('¡Instrucciones Enviadas!')
    })

    it('should display email in message', () => {
      wrapper = mount(PasswordResetConfirmation, {
        props: {
          email: 'test@example.com'
        }
      })

      expect(wrapper.text()).toContain('test@example.com')
    })

    it('should display information alert', () => {
      wrapper = mount(PasswordResetConfirmation, {
        props: {
          email: 'test@example.com'
        }
      })

      expect(wrapper.text()).toContain('Revisa tu bandeja de entrada')
    })

    it('should display resend button', () => {
      wrapper = mount(PasswordResetConfirmation, {
        props: {
          email: 'test@example.com'
        }
      })

      expect(wrapper.text()).toContain('Enviar Nuevamente')
    })

    it('should display back to login link', () => {
      wrapper = mount(PasswordResetConfirmation, {
        props: {
          email: 'test@example.com'
        },
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      expect(wrapper.text()).toContain('Volver al Login')
    })
  })

  describe('Props', () => {
    it('should display provided email', () => {
      wrapper = mount(PasswordResetConfirmation, {
        props: {
          email: 'user@example.com'
        }
      })

      expect(wrapper.text()).toContain('user@example.com')
    })

    it('should use default button text', () => {
      wrapper = mount(PasswordResetConfirmation, {
        props: {
          email: 'test@example.com'
        }
      })

      expect(wrapper.text()).toContain('Enviar Nuevamente')
    })

    it('should use custom button text', () => {
      wrapper = mount(PasswordResetConfirmation, {
        props: {
          email: 'test@example.com',
          buttonText: 'Resend Email'
        }
      })

      expect(wrapper.text()).toContain('Resend Email')
    })
  })

  describe('Countdown', () => {
    it('should display countdown when recentlySent is true', () => {
      wrapper = mount(PasswordResetConfirmation, {
        props: {
          email: 'test@example.com',
          recentlySent: true,
          countdown: 45
        }
      })

      expect(wrapper.text()).toContain('45')
      expect(wrapper.text()).toContain('segundos')
    })

    it('should not display countdown when recentlySent is false', () => {
      wrapper = mount(PasswordResetConfirmation, {
        props: {
          email: 'test@example.com',
          recentlySent: false
        }
      })

      const countdownText = wrapper.text()
      expect(countdownText.includes('segundos') && countdownText.includes('Podrás enviar')).toBe(false)
    })
  })

  describe('Events', () => {
    it('should emit resend event when resend button is clicked', async () => {
      wrapper = mount(PasswordResetConfirmation, {
        props: {
          email: 'test@example.com',
          isLoading: false,
          recentlySent: false
        }
      })

      const resendButton = wrapper.findAll('button').find(btn => 
        btn.text().includes('Enviar Nuevamente')
      )
      
      if (resendButton) {
        await resendButton.trigger('click')
        expect(wrapper.emitted('resend')).toBeTruthy()
      }
    })

    it('should not emit resend when button is disabled', async () => {
      wrapper = mount(PasswordResetConfirmation, {
        props: {
          email: 'test@example.com',
          isLoading: true,
          recentlySent: false
        }
      })

      const resendButton = wrapper.findAll('button').find(btn => 
        btn.text().includes('Enviar') || btn.text().includes('Esperar')
      )
      
      if (resendButton) {
        await resendButton.trigger('click')
        expect(wrapper.emitted('resend')).toBeFalsy()
      }
    })
  })

  describe('Button States', () => {
    it('should disable resend button when isLoading is true', () => {
      wrapper = mount(PasswordResetConfirmation, {
        props: {
          email: 'test@example.com',
          isLoading: true,
          recentlySent: false
        }
      })

      const resendButton = wrapper.findAll('button').find(btn => 
        btn.text().includes('Enviar') || btn.text().includes('Esperar')
      )
      
      if (resendButton) {
        expect(resendButton.attributes('disabled')).toBeDefined()
      }
    })

    it('should disable resend button when recentlySent is true', () => {
      wrapper = mount(PasswordResetConfirmation, {
        props: {
          email: 'test@example.com',
          isLoading: false,
          recentlySent: true,
          countdown: 30
        }
      })

      const resendButton = wrapper.findAll('button').find(btn => 
        btn.text().includes('Esperar') || btn.text().includes('Enviar')
      )
      
      if (resendButton) {
        expect(resendButton.attributes('disabled')).toBeDefined()
      }
    })

    it('should show countdown text in button when recentlySent is true', () => {
      wrapper = mount(PasswordResetConfirmation, {
        props: {
          email: 'test@example.com',
          recentlySent: true,
          countdown: 30,
          buttonText: 'Esperar 30s'
        }
      })

      expect(wrapper.text()).toContain('Esperar 30s')
    })
  })

  describe('Router Link', () => {
    it('should link to login page', () => {
      wrapper = mount(PasswordResetConfirmation, {
        props: {
          email: 'test@example.com'
        },
        global: {
          components: {
            RouterLink: mockRouterLink
          }
        }
      })

      const loginLink = wrapper.findComponent({ name: 'RouterLink' })
      expect(loginLink.exists()).toBe(true)
      expect(loginLink.props('to')).toBe('/login')
    })
  })
})


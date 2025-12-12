import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import PasswordResetForm from '../PasswordResetForm.vue'

describe('PasswordResetForm', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = mount(PasswordResetForm)

      expect(wrapper.exists()).toBe(true)
    })

    it('should display email input', () => {
      wrapper = mount(PasswordResetForm)

      const emailInput = wrapper.find('#email')
      expect(emailInput.exists()).toBe(true)
    })

    it('should display submit button', () => {
      wrapper = mount(PasswordResetForm)

      const submitButton = wrapper.find('button[type="submit"]')
      expect(submitButton.exists()).toBe(true)
      expect(submitButton.text()).toContain('Enviar Instrucciones')
    })

    it('should display information section', () => {
      wrapper = mount(PasswordResetForm)

      expect(wrapper.text()).toContain('¿Cómo funciona?')
    })
  })

  describe('Form Input', () => {
    it('should bind email input to form', async () => {
      wrapper = mount(PasswordResetForm)

      const emailInput = wrapper.find('#email')
      await emailInput.setValue('test@example.com')
      await nextTick()

      expect(wrapper.vm.form.email).toBe('test@example.com')
    })

    it('should have required attribute on email input', () => {
      wrapper = mount(PasswordResetForm)

      const emailInput = wrapper.find('#email')
      expect(emailInput.attributes('required')).toBeDefined()
    })

    it('should have email type on input', () => {
      wrapper = mount(PasswordResetForm)

      const emailInput = wrapper.find('#email')
      expect(emailInput.attributes('type')).toBe('email')
    })

    it('should disable input when isLoading is true', () => {
      wrapper = mount(PasswordResetForm, {
        props: {
          isLoading: true
        }
      })

      const emailInput = wrapper.find('#email')
      expect(emailInput.attributes('disabled')).toBeDefined()
    })

    it('should enable input when isLoading is false', () => {
      wrapper = mount(PasswordResetForm, {
        props: {
          isLoading: false
        }
      })

      const emailInput = wrapper.find('#email')
      expect(emailInput.attributes('disabled')).toBeUndefined()
    })
  })

  describe('Error Display', () => {
    it('should display error message when error prop is provided', () => {
      wrapper = mount(PasswordResetForm, {
        props: {
          error: 'Email is required'
        }
      })

      expect(wrapper.text()).toContain('Email is required')
    })

    it('should not display error when error prop is empty', () => {
      wrapper = mount(PasswordResetForm, {
        props: {
          error: ''
        }
      })

      const errorElement = wrapper.find('.text-red-600')
      expect(errorElement.exists()).toBe(false)
    })

    it('should apply error styling when error is present', () => {
      wrapper = mount(PasswordResetForm, {
        props: {
          error: 'Error message'
        }
      })

      const emailInput = wrapper.find('#email')
      expect(emailInput.classes()).toContain('border-red-500')
    })
  })

  describe('Initial Email', () => {
    it('should set initial email from prop', async () => {
      wrapper = mount(PasswordResetForm, {
        props: {
          initialEmail: 'initial@example.com'
        }
      })

      await nextTick()
      expect(wrapper.vm.form.email).toBe('initial@example.com')
    })

    it('should update email when initialEmail prop changes', async () => {
      wrapper = mount(PasswordResetForm, {
        props: {
          initialEmail: 'initial@example.com'
        }
      })

      await nextTick()
      expect(wrapper.vm.form.email).toBe('initial@example.com')

      await wrapper.setProps({ initialEmail: 'new@example.com' })
      await nextTick()

      expect(wrapper.vm.form.email).toBe('new@example.com')
    })
  })

  describe('Form Submission', () => {
    it('should emit submit event with email when form is submitted', async () => {
      wrapper = mount(PasswordResetForm)

      const emailInput = wrapper.find('#email')
      await emailInput.setValue('test@example.com')
      await nextTick()

      const form = wrapper.find('form')
      await form.trigger('submit')
      await nextTick()

      expect(wrapper.emitted('submit')).toBeTruthy()
      expect(wrapper.emitted('submit')[0][0]).toBe('test@example.com')
    })

    it('should trim email before emitting', async () => {
      wrapper = mount(PasswordResetForm)

      const emailInput = wrapper.find('#email')
      await emailInput.setValue('  test@example.com  ')
      await nextTick()

      const form = wrapper.find('form')
      await form.trigger('submit')
      await nextTick()

      expect(wrapper.emitted('submit')[0][0]).toBe('test@example.com')
    })

    it('should not emit submit if email is empty', async () => {
      wrapper = mount(PasswordResetForm)

      const form = wrapper.find('form')
      await form.trigger('submit')
      await nextTick()

      // HTML5 validation should prevent submission
      expect(wrapper.emitted('submit')).toBeFalsy()
    })
  })

  describe('Loading State', () => {
    it('should show loading spinner when isLoading is true', () => {
      wrapper = mount(PasswordResetForm, {
        props: {
          isLoading: true
        }
      })

      const spinner = wrapper.find('.animate-spin')
      expect(spinner.exists()).toBe(true)
    })

    it('should show loading text when isLoading is true', () => {
      wrapper = mount(PasswordResetForm, {
        props: {
          isLoading: true
        }
      })

      expect(wrapper.text()).toContain('Enviando...')
    })

    it('should disable submit button when isLoading is true', () => {
      wrapper = mount(PasswordResetForm, {
        props: {
          isLoading: true
        }
      })

      const submitButton = wrapper.find('button[type="submit"]')
      expect(submitButton.attributes('disabled')).toBeDefined()
    })

    it('should show normal button text when isLoading is false', () => {
      wrapper = mount(PasswordResetForm, {
        props: {
          isLoading: false
        }
      })

      expect(wrapper.text()).toContain('Enviar Instrucciones')
    })
  })

  describe('Expose', () => {
    it('should expose form ref', () => {
      wrapper = mount(PasswordResetForm)

      expect(wrapper.vm.form).toBeDefined()
      expect(wrapper.vm.form.email).toBeDefined()
    })
  })
})


import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseConfirmModal from '../BaseConfirmModal.vue'

vi.mock('../BaseModal.vue', () => ({
  default: {
    name: 'BaseModal',
    template: `
      <div v-if="show">
        <slot name="header"></slot>
        <slot></slot>
        <slot name="footer"></slot>
      </div>
    `,
    props: ['show', 'title', 'subtitle', 'maxWidth', 'showCloseButton', 'closeOnOverlay'],
    emits: ['close', 'update:show']
  }
}))

describe('BaseConfirmModal', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
  })

  describe('Rendering', () => {
    it('should render modal when show is true', () => {
      wrapper = mount(BaseConfirmModal, {
        props: {
          show: true,
          message: 'Test message'
        }
      })

      expect(wrapper.text()).toContain('Test message')
    })

    it('should not render when show is false', () => {
      wrapper = mount(BaseConfirmModal, {
        props: {
          show: false,
          message: 'Test message'
        }
      })

      const modalContent = wrapper.find('div')
      expect(modalContent.exists()).toBe(false)
    })

    it('should render with default title', () => {
      wrapper = mount(BaseConfirmModal, {
        props: {
          show: true,
          message: 'Test message'
        }
      })

      expect(wrapper.text()).toContain('Confirmar Acción')
    })

    it('should render with custom title', () => {
      wrapper = mount(BaseConfirmModal, {
        props: {
          show: true,
          message: 'Test message',
          title: 'Custom Title'
        }
      })

      expect(wrapper.text()).toContain('Custom Title')
    })

    it('should render subtitle when provided', () => {
      wrapper = mount(BaseConfirmModal, {
        props: {
          show: true,
          message: 'Test message',
          subtitle: 'Test Subtitle'
        }
      })

      expect(wrapper.text()).toContain('Test Subtitle')
    })

    it('should render details when provided', () => {
      wrapper = mount(BaseConfirmModal, {
        props: {
          show: true,
          message: 'Test message',
          details: ['Detail 1', 'Detail 2']
        }
      })

      expect(wrapper.text()).toContain('Detail 1')
      expect(wrapper.text()).toContain('Detail 2')
    })

    it('should render warning when provided', () => {
      wrapper = mount(BaseConfirmModal, {
        props: {
          show: true,
          message: 'Test message',
          warning: 'Warning message'
        }
      })

      expect(wrapper.text()).toContain('Warning message')
    })
  })

  describe('Variants', () => {
    const variants = ['danger', 'warning', 'info', 'success', 'default']

    for (const variant of variants) {
      it(`should apply correct variant class for ${variant}`, () => {
        wrapper = mount(BaseConfirmModal, {
          props: {
            show: true,
            message: 'Test message',
            variant
          }
        })

        const header = wrapper.find('.confirm-modal-header')
        expect(header.exists()).toBe(true)
        expect(header.classes()).toContain(`variant-${variant}`)
      })
    }
  })

  describe('Buttons', () => {
    it('should render confirm and cancel buttons', () => {
      wrapper = mount(BaseConfirmModal, {
        props: {
          show: true,
          message: 'Test message'
        }
      })

      const buttons = wrapper.findAll('button')
      expect(buttons.length).toBe(2)
      expect(wrapper.text()).toContain('Confirmar')
      expect(wrapper.text()).toContain('Cancelar')
    })

    it('should render custom button text', () => {
      wrapper = mount(BaseConfirmModal, {
        props: {
          show: true,
          message: 'Test message',
          confirmText: 'Delete',
          cancelText: 'Keep'
        }
      })

      expect(wrapper.text()).toContain('Delete')
      expect(wrapper.text()).toContain('Keep')
    })

    it('should disable buttons when loading', () => {
      wrapper = mount(BaseConfirmModal, {
        props: {
          show: true,
          message: 'Test message',
          loading: true
        }
      })

      const buttons = wrapper.findAll('button')
      for (const button of buttons) {
        expect(button.attributes('disabled')).toBeDefined()
      }
    })
  })

  describe('Events', () => {
    it('should emit confirm when confirm button is clicked', async () => {
      wrapper = mount(BaseConfirmModal, {
        props: {
          show: true,
          message: 'Test message'
        }
      })

      const confirmButton = wrapper.findAll('button')[1]
      await confirmButton.trigger('click')

      expect(wrapper.emitted('confirm')).toBeTruthy()
    })

    it('should not emit confirm when loading', async () => {
      wrapper = mount(BaseConfirmModal, {
        props: {
          show: true,
          message: 'Test message',
          loading: true
        }
      })

      const confirmButton = wrapper.findAll('button')[1]
      await confirmButton.trigger('click')

      expect(wrapper.emitted('confirm')).toBeFalsy()
    })

    it('should emit cancel when cancel button is clicked', async () => {
      wrapper = mount(BaseConfirmModal, {
        props: {
          show: true,
          message: 'Test message'
        }
      })

      const cancelButton = wrapper.findAll('button')[0]
      await cancelButton.trigger('click')

      expect(wrapper.emitted('cancel')).toBeTruthy()
      expect(wrapper.emitted('update:show')).toBeTruthy()
      expect(wrapper.emitted('update:show')[0]).toEqual([false])
    })

    it('should not emit cancel when loading', async () => {
      wrapper = mount(BaseConfirmModal, {
        props: {
          show: true,
          message: 'Test message',
          loading: true
        }
      })

      const cancelButton = wrapper.findAll('button')[0]
      await cancelButton.trigger('click')

      expect(wrapper.emitted('cancel')).toBeFalsy()
    })
  })
})


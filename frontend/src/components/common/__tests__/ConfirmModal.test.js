import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ConfirmModal from '../ConfirmModal.vue'

describe('ConfirmModal', () => {
  it('should render with default props', () => {
    const wrapper = mount(ConfirmModal, {
      props: {
        message: 'Test message'
      }
    })

    expect(wrapper.text()).toContain('Test message')
    expect(wrapper.text()).toContain('Confirmar Acción')
    expect(wrapper.text()).toContain('Confirmar')
    expect(wrapper.text()).toContain('Cancelar')
  })

  it('should render custom title and message', () => {
    const wrapper = mount(ConfirmModal, {
      props: {
        title: 'Custom Title',
        message: 'Custom Message'
      }
    })

    expect(wrapper.text()).toContain('Custom Title')
    expect(wrapper.text()).toContain('Custom Message')
  })

  it('should render details when provided', () => {
    const wrapper = mount(ConfirmModal, {
      props: {
        message: 'Test',
        details: ['Detail 1', 'Detail 2']
      }
    })

    expect(wrapper.text()).toContain('Detail 1')
    expect(wrapper.text()).toContain('Detail 2')
  })

  it('should render warning when provided', () => {
    const wrapper = mount(ConfirmModal, {
      props: {
        message: 'Test',
        warning: 'Warning message'
      }
    })

    expect(wrapper.text()).toContain('Warning message')
  })

  it('should emit confirm when confirm button is clicked', async () => {
    const wrapper = mount(ConfirmModal, {
      props: {
        message: 'Test'
      }
    })

    const confirmButton = wrapper.findAll('button').find(btn => btn.text().includes('Confirmar'))
    await confirmButton.trigger('click')

    expect(wrapper.emitted('confirm')).toBeTruthy()
  })

  it('should emit cancel when cancel button is clicked', async () => {
    const wrapper = mount(ConfirmModal, {
      props: {
        message: 'Test'
      }
    })

    const cancelButton = wrapper.findAll('button').find(btn => btn.text().includes('Cancelar'))
    await cancelButton.trigger('click')

    expect(wrapper.emitted('cancel')).toBeTruthy()
  })

  it('should emit cancel when overlay is clicked', async () => {
    const wrapper = mount(ConfirmModal, {
      props: {
        message: 'Test'
      }
    })

    const overlay = wrapper.find('.confirm-modal-overlay')
    await overlay.trigger('click')

    expect(wrapper.emitted('cancel')).toBeTruthy()
  })

  it('should not emit cancel when modal container is clicked', async () => {
    const wrapper = mount(ConfirmModal, {
      props: {
        message: 'Test'
      }
    })

    const container = wrapper.find('.confirm-modal-container')
    await container.trigger('click.stop')

    expect(wrapper.emitted('cancel')).toBeFalsy()
  })

  it('should disable buttons when loading', () => {
    const wrapper = mount(ConfirmModal, {
      props: {
        message: 'Test',
        loading: true
      }
    })

    const buttons = wrapper.findAll('button')
    for (const button of buttons) {
      expect(button.attributes('disabled')).toBeDefined()
    }
  })

  it('should show loading spinner when loading', () => {
    const wrapper = mount(ConfirmModal, {
      props: {
        message: 'Test',
        loading: true
      }
    })

    expect(wrapper.find('.fa-spinner').exists()).toBe(true)
  })

  it('should use custom confirm and cancel text', () => {
    const wrapper = mount(ConfirmModal, {
      props: {
        message: 'Test',
        confirmText: 'Yes',
        cancelText: 'No'
      }
    })

    expect(wrapper.text()).toContain('Yes')
    expect(wrapper.text()).toContain('No')
  })
})


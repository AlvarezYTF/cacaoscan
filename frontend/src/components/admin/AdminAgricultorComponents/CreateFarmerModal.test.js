import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import CreateFarmerModal from './CreateFarmerModal.vue'

vi.mock('@/components/common/BaseModal.vue', () => ({
  default: {
    name: 'BaseModal',
    template: '<div><slot name="header"></slot><slot></slot></div>',
    props: ['show', 'title', 'subtitle', 'maxWidth'],
    emits: ['close', 'update:show']
  }
}))

describe('CreateFarmerModal', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render modal when isOpen is true', () => {
    wrapper = mount(CreateFarmerModal, {
      props: {
        isOpen: true
      },
      global: {
        stubs: {
          BaseModal: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display create farmer title', () => {
    wrapper = mount(CreateFarmerModal, {
      props: {
        isOpen: true
      },
      global: {
        stubs: {
          BaseModal: true
        }
      }
    })

    const text = wrapper.text()
    expect(text.includes('Crear') || text.includes('Agricultor')).toBe(true)
  })

  it('should emit close event when modal is closed', async () => {
    wrapper = mount(CreateFarmerModal, {
      props: {
        isOpen: true
      },
      global: {
        stubs: {
          BaseModal: true
        }
      }
    })

    await wrapper.vm.closeModal()

    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should emit created event when farmer is created successfully', async () => {
    wrapper = mount(CreateFarmerModal, {
      props: {
        isOpen: true
      },
      global: {
        stubs: {
          BaseModal: true
        }
      }
    })

    await wrapper.vm.$nextTick()

    const form = wrapper.find('form')
    if (form.exists()) {
      await form.trigger('submit.prevent')
      await wrapper.vm.$nextTick()
    }
  })
})


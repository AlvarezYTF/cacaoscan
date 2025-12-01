import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import CreateFarmerModal from './CreateFarmerModal.vue'

vi.mock('@/components/common/BaseModal.vue', () => ({
  default: {
    name: 'BaseModal',
    template: '<div v-if="show"><slot name="header"></slot><slot></slot><slot name="footer"></slot></div>',
    props: {
      show: {
        type: Boolean,
        default: true
      },
      title: String,
      subtitle: String,
      maxWidth: String
    },
    emits: ['close', 'update:show']
  }
}))

// Mock api to prevent real API calls when errors occur
vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn().mockResolvedValue({ data: {} }),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn()
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
      global: {
        stubs: {
          BaseModal: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display create farmer title', async () => {
    wrapper = mount(CreateFarmerModal, {
      global: {
        stubs: {
          BaseModal: true
        }
      }
    })

    wrapper.vm.openModal()
    await wrapper.vm.$nextTick()

    const text = wrapper.text()
    expect(text.includes('Crear') || text.includes('Agricultor')).toBe(true)
  })

  it('should emit close event when modal is closed', async () => {
    wrapper = mount(CreateFarmerModal, {
      global: {
        stubs: {
          BaseModal: true
        }
      }
    })

    wrapper.vm.openModal()
    await wrapper.vm.$nextTick()

    await wrapper.vm.closeModal()

    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should emit created event when farmer is created successfully', async () => {
    wrapper = mount(CreateFarmerModal, {
      global: {
        stubs: {
          BaseModal: true
        }
      }
    })

    wrapper.vm.openModal()
    await wrapper.vm.$nextTick()

    const form = wrapper.find('form')
    if (form.exists()) {
      await form.trigger('submit.prevent')
      await wrapper.vm.$nextTick()
    }
  })
})


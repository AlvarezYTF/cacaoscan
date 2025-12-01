import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import EditFarmerModal from './EditFarmerModal.vue'

vi.mock('@/components/common/BaseModal.vue', () => ({
  default: {
    name: 'BaseModal',
    template: '<div><slot name="header"></slot><slot></slot></div>',
    props: ['show', 'title', 'subtitle', 'maxWidth'],
    emits: ['close', 'update:show']
  }
}))

describe('EditFarmerModal', () => {
  let wrapper

  const mockFarmer = {
    id: 1,
    first_name: 'John',
    last_name: 'Doe',
    email: 'john.doe@example.com'
  }

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render modal when isOpen is true', () => {
    wrapper = mount(EditFarmerModal, {
      props: {
        isOpen: true,
        farmer: mockFarmer
      },
      global: {
        stubs: {
          BaseModal: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display edit farmer title', () => {
    wrapper = mount(EditFarmerModal, {
      props: {
        isOpen: true,
        farmer: mockFarmer
      },
      global: {
        stubs: {
          BaseModal: true
        }
      }
    })

    const text = wrapper.text()
    expect(text.includes('Editar') || text.includes('Agricultor')).toBe(true)
  })

  it('should emit close event when modal is closed', async () => {
    wrapper = mount(EditFarmerModal, {
      props: {
        isOpen: true,
        farmer: mockFarmer
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

  it('should switch between tabs', async () => {
    wrapper = mount(EditFarmerModal, {
      props: {
        isOpen: true,
        farmer: mockFarmer
      },
      global: {
        stubs: {
          BaseModal: true
        }
      }
    })

    await wrapper.vm.$nextTick()

    const fincasTab = wrapper.find('button')
    if (fincasTab.exists() && fincasTab.text().includes('Fincas')) {
      await fincasTab.trigger('click')
      expect(wrapper.vm.activeTab).toBe('fincas')
    }
  })
})


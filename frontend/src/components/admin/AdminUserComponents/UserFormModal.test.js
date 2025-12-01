import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import UserFormModal from './UserFormModal.vue'

vi.mock('@/components/common/BaseModal.vue', () => ({
  default: {
    name: 'BaseModal',
    template: '<div><slot name="header"></slot><slot></slot></div>',
    props: ['show', 'title', 'subtitle', 'maxWidth'],
    emits: ['close']
  }
}))

describe('UserFormModal', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render modal in create mode', () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create',
        user: null
      },
      global: {
        stubs: {
          BaseModal: true,
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should render modal in edit mode', () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'edit',
        user: {
          id: 1,
          username: 'testuser',
          email: 'test@example.com'
        }
      },
      global: {
        stubs: {
          BaseModal: true,
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display create user title in create mode', async () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create',
        user: null
      },
      global: {
        stubs: {
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    await wrapper.vm.$nextTick()
    
    const text = wrapper.text()
    // Check for the title in the header slot
    const headerText = wrapper.find('h3')?.text() || ''
    const allText = text + headerText
    
    expect(allText.includes('Crear') || allText.includes('Usuario')).toBe(true)
  })

  it('should emit close event when modal is closed', async () => {
    wrapper = mount(UserFormModal, {
      props: {
        mode: 'create',
        user: null
      },
      global: {
        stubs: {
          BaseModal: true,
          BaseFormField: { template: '<div><slot></slot></div>', props: ['name', 'label', 'required', 'error'] }
        }
      }
    })

    await wrapper.vm.closeModal()

    expect(wrapper.emitted('close')).toBeTruthy()
  })
})


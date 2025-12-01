import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import FincaDetailModal from './FincaDetailModal.vue'

vi.mock('@/components/common/BaseModal.vue', () => ({
  default: {
    name: 'BaseModal',
    template: '<div><slot name="header"></slot><slot></slot></div>',
    props: ['show', 'title', 'subtitle', 'maxWidth']
  }
}))

describe('FincaDetailModal', () => {
  let wrapper

  const mockFinca = {
    id: 1,
    nombre: 'Test Finca',
    municipio: 'Test Municipio',
    departamento: 'Test Departamento',
    activa: true
  }

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render modal when show is true', () => {
    wrapper = mount(FincaDetailModal, {
      props: {
        show: true,
        fincaId: 1
      },
      global: {
        stubs: {
          BaseModal: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should not render modal when show is false', () => {
    wrapper = mount(FincaDetailModal, {
      props: {
        show: false,
        fincaId: 1
      },
      global: {
        stubs: {
          BaseModal: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should emit close event when modal is closed', async () => {
    wrapper = mount(FincaDetailModal, {
      props: {
        show: true,
        fincaId: 1
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
})


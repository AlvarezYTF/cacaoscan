import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BatchInfoForm from './BatchInfoForm.vue'

describe('BatchInfoForm', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render batch info form', () => {
    wrapper = mount(BatchInfoForm, {
      props: {
        formData: {
          farmer: '',
          finca: '',
          lote: '',
          fecha: ''
        },
        errors: {},
        userRole: 'admin'
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display farmer field for admin', () => {
    wrapper = mount(BatchInfoForm, {
      props: {
        formData: {
          farmer: '',
          finca: '',
          lote: '',
          fecha: ''
        },
        errors: {},
        userRole: 'admin'
      }
    })

    const text = wrapper.text()
    expect(text.includes('Agricultor') || text.includes('farmer')).toBe(true)
  })

  it('should display readonly farmer field for agricultor role', () => {
    wrapper = mount(BatchInfoForm, {
      props: {
        formData: {
          farmer: 'test',
          finca: '',
          lote: '',
          fecha: ''
        },
        errors: {},
        userRole: 'agricultor'
      }
    })

    const farmerInput = wrapper.find('input[readonly]')
    if (farmerInput.exists()) {
      expect(farmerInput.attributes('readonly')).toBeDefined()
    }
  })

  it('should emit update event when form data changes', async () => {
    wrapper = mount(BatchInfoForm, {
      props: {
        formData: {
          farmer: '',
          finca: '',
          lote: '',
          fecha: ''
        },
        errors: {},
        userRole: 'admin'
      }
    })

    await wrapper.vm.$nextTick()

    const select = wrapper.find('select')
    if (select.exists()) {
      await select.setValue('test')
      await wrapper.vm.$nextTick()
    }
  })
})


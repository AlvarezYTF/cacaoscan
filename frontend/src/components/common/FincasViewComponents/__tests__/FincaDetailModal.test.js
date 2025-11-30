import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import FincaDetailModal from '../FincaDetailModal.vue'

describe('FincaDetailModal', () => {
  it('should not render when show is false', () => {
    const wrapper = mount(FincaDetailModal, {
      props: {
        show: false
      }
    })

    expect(wrapper.find('.fixed').exists()).toBe(false)
  })

  it('should render when show is true', () => {
    const wrapper = mount(FincaDetailModal, {
      props: {
        show: true,
        fincaId: 1
      }
    })

    expect(wrapper.find('.fixed').exists()).toBe(true)
  })

  it('should show loading state', () => {
    const wrapper = mount(FincaDetailModal, {
      props: {
        show: true,
        fincaId: 1
      }
    })

    wrapper.setData({ loading: true })
    expect(wrapper.text()).toContain('Cargando información')
  })

  it('should emit close when close button is clicked', async () => {
    const wrapper = mount(FincaDetailModal, {
      props: {
        show: true,
        fincaId: 1
      }
    })

    const closeButton = wrapper.find('button[aria-label="Cerrar modal"]')
    await closeButton.trigger('click')

    expect(wrapper.emitted('close')).toBeTruthy()
  })
})


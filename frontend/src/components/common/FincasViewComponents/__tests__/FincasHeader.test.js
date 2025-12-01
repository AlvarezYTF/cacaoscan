import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import FincasHeader from '../FincasHeader.vue'

describe('FincasHeader', () => {
  it('should render header with title', () => {
    const wrapper = mount(FincasHeader)

    expect(wrapper.text()).toContain('Gestión de Fincas')
    expect(wrapper.text()).toContain('Administra las fincas')
  })

  it('should emit create when create button is clicked', async () => {
    const wrapper = mount(FincasHeader)

    const createButton = wrapper.find('button')
    await createButton.trigger('click')

    expect(wrapper.emitted('create')).toBeTruthy()
  })

  it('should display create button', () => {
    const wrapper = mount(FincasHeader)

    expect(wrapper.text()).toContain('Nueva Finca')
  })
})


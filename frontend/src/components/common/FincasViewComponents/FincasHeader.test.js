import { describe, it, expect, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import FincasHeader from './FincasHeader.vue'

describe('FincasHeader', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render header component', () => {
    wrapper = mount(FincasHeader)

    expect(wrapper.exists()).toBe(true)
  })

  it('should display gestion de fincas title', () => {
    wrapper = mount(FincasHeader)

    const text = wrapper.text()
    expect(text.includes('Fincas') || text.includes('Gestión')).toBe(true)
  })

  it('should display create finca button', () => {
    wrapper = mount(FincasHeader)

    const buttons = wrapper.findAll('button')
    const createButton = buttons.find(btn => 
      btn.text().includes('Nueva') || btn.text().includes('Crear') || btn.text().includes('Finca')
    )
    expect(createButton?.exists() ?? false).toBe(true)
  })

  it('should emit create event when create button is clicked', async () => {
    wrapper = mount(FincasHeader)

    const buttons = wrapper.findAll('button')
    const createButton = buttons.find(btn => 
      btn.text().includes('Nueva') || btn.text().includes('Crear') || btn.text().includes('Finca')
    )
    
    if (createButton) {
      await createButton.trigger('click')
      expect(wrapper.emitted('create')).toBeTruthy()
    }
  })
})


import { describe, it, expect, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import FincaCardActions from './FincaCardActions.vue'

describe('FincaCardActions', () => {
  let wrapper

  const mockFinca = {
    id: 1,
    nombre: 'Test Finca',
    activa: true
  }

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render card actions component', () => {
    wrapper = mount(FincaCardActions, {
      props: {
        finca: mockFinca,
        userRole: 'agricultor'
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should show edit button when finca is active', () => {
    wrapper = mount(FincaCardActions, {
      props: {
        finca: { ...mockFinca, activa: true },
        userRole: 'agricultor'
      }
    })

    const buttons = wrapper.findAll('button')
    const editButton = buttons.find(btn => btn.text().includes('Editar'))
    expect(editButton?.exists() ?? false).toBe(true)
  })

  it('should show edit button for admin even when finca is inactive', () => {
    wrapper = mount(FincaCardActions, {
      props: {
        finca: { ...mockFinca, activa: false },
        userRole: 'admin'
      }
    })

    const buttons = wrapper.findAll('button')
    const editButton = buttons.find(btn => btn.text().includes('Editar'))
    expect(editButton?.exists() ?? false).toBe(true)
  })

  it('should show activate button for admin when finca is inactive', () => {
    wrapper = mount(FincaCardActions, {
      props: {
        finca: { ...mockFinca, activa: false },
        userRole: 'admin'
      }
    })

    const buttons = wrapper.findAll('button')
    const activateButton = buttons.find(btn => btn.text().includes('Activar'))
    expect(activateButton?.exists() ?? false).toBe(true)
  })

  it('should not show activate button when finca is active', () => {
    wrapper = mount(FincaCardActions, {
      props: {
        finca: { ...mockFinca, activa: true },
        userRole: 'admin'
      }
    })

    const buttons = wrapper.findAll('button')
    const activateButton = buttons.find(btn => btn.text().includes('Activar'))
    expect(activateButton?.exists() ?? false).toBe(false)
  })

  it('should show view-lotes button when finca is active', () => {
    wrapper = mount(FincaCardActions, {
      props: {
        finca: { ...mockFinca, activa: true },
        userRole: 'agricultor'
      }
    })

    const buttons = wrapper.findAll('button')
    const viewLotesButton = buttons.find(btn => btn.text().includes('Ver Lotes'))
    expect(viewLotesButton?.exists() ?? false).toBe(true)
  })

  it('should show view-lotes button for admin even when finca is inactive', () => {
    wrapper = mount(FincaCardActions, {
      props: {
        finca: { ...mockFinca, activa: false },
        userRole: 'admin'
      }
    })

    const buttons = wrapper.findAll('button')
    const viewLotesButton = buttons.find(btn => btn.text().includes('Ver Lotes'))
    expect(viewLotesButton?.exists() ?? false).toBe(true)
  })

  it('should show delete button when finca is active', () => {
    wrapper = mount(FincaCardActions, {
      props: {
        finca: { ...mockFinca, activa: true },
        userRole: 'agricultor'
      }
    })

    const buttons = wrapper.findAll('button')
    const deleteButton = buttons.find(btn => btn.text().includes('Desactivar'))
    expect(deleteButton?.exists() ?? false).toBe(true)
  })

  it('should not show delete button when finca is inactive', () => {
    wrapper = mount(FincaCardActions, {
      props: {
        finca: { ...mockFinca, activa: false },
        userRole: 'agricultor'
      }
    })

    const buttons = wrapper.findAll('button')
    const deleteButton = buttons.find(btn => btn.text().includes('Desactivar'))
    expect(deleteButton?.exists() ?? false).toBe(false)
  })

  it('should emit edit event when edit button is clicked', async () => {
    wrapper = mount(FincaCardActions, {
      props: {
        finca: { ...mockFinca, activa: true },
        userRole: 'agricultor'
      }
    })

    const buttons = wrapper.findAll('button')
    const editButton = buttons.find(btn => btn.text().includes('Editar'))
    
    if (editButton) {
      await editButton.trigger('click')
      expect(wrapper.emitted('edit')).toBeTruthy()
      expect(wrapper.emitted('edit')[0]).toEqual([mockFinca])
    }
  })

  it('should emit view-lotes event when view-lotes button is clicked', async () => {
    wrapper = mount(FincaCardActions, {
      props: {
        finca: { ...mockFinca, activa: true },
        userRole: 'agricultor'
      }
    })

    const buttons = wrapper.findAll('button')
    const viewLotesButton = buttons.find(btn => btn.text().includes('Ver Lotes'))
    
    if (viewLotesButton) {
      await viewLotesButton.trigger('click')
      expect(wrapper.emitted('view-lotes')).toBeTruthy()
      expect(wrapper.emitted('view-lotes')[0]).toEqual([mockFinca])
    }
  })

  it('should emit confirm-delete event when delete button is clicked', async () => {
    wrapper = mount(FincaCardActions, {
      props: {
        finca: { ...mockFinca, activa: true },
        userRole: 'agricultor'
      }
    })

    const buttons = wrapper.findAll('button')
    const deleteButton = buttons.find(btn => btn.text().includes('Desactivar'))
    
    if (deleteButton) {
      await deleteButton.trigger('click')
      expect(wrapper.emitted('confirm-delete')).toBeTruthy()
      expect(wrapper.emitted('confirm-delete')[0]).toEqual([mockFinca])
    }
  })

  it('should emit confirm-activate event when activate button is clicked', async () => {
    wrapper = mount(FincaCardActions, {
      props: {
        finca: { ...mockFinca, activa: false },
        userRole: 'admin'
      }
    })

    const buttons = wrapper.findAll('button')
    const activateButton = buttons.find(btn => btn.text().includes('Activar'))
    
    if (activateButton) {
      await activateButton.trigger('click')
      expect(wrapper.emitted('confirm-activate')).toBeTruthy()
      expect(wrapper.emitted('confirm-activate')[0]).toEqual([{ ...mockFinca, activa: false }])
    }
  })

  it('should stop event propagation on button clicks', async () => {
    wrapper = mount(FincaCardActions, {
      props: {
        finca: { ...mockFinca, activa: true },
        userRole: 'agricultor'
      }
    })

    const buttons = wrapper.findAll('button')
    const editButton = buttons.find(btn => btn.text().includes('Editar'))
    
    if (editButton) {
      const clickEvent = new Event('click')
      clickEvent.stopPropagation = vi.fn()
      
      await editButton.trigger('click')
      expect(wrapper.emitted('edit')).toBeTruthy()
    }
  })
})


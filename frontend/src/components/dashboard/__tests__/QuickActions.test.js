import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import QuickActions from '../QuickActions.vue'

describe('QuickActions', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = mount(QuickActions)

      expect(wrapper.exists()).toBe(true)
    })

    it('should display section title', () => {
      wrapper = mount(QuickActions)

      expect(wrapper.text()).toContain('Acciones rápidas')
    })

    it('should render all action buttons', () => {
      wrapper = mount(QuickActions)

      const buttons = wrapper.findAll('button')
      expect(buttons.length).toBe(3)
    })

    it('should display upload button', () => {
      wrapper = mount(QuickActions)

      expect(wrapper.text()).toContain('Subir nuevo lote')
    })

    it('should display reports button', () => {
      wrapper = mount(QuickActions)

      expect(wrapper.text()).toContain('Ver reportes')
    })

    it('should display history button', () => {
      wrapper = mount(QuickActions)

      expect(wrapper.text()).toContain('Historial de análisis')
    })
  })

  describe('Events', () => {
    it('should emit upload event when upload button is clicked', async () => {
      wrapper = mount(QuickActions)

      const buttons = wrapper.findAll('button')
      await buttons[0].trigger('click')

      expect(wrapper.emitted('upload')).toBeTruthy()
    })

    it('should not emit events when other buttons are clicked', async () => {
      wrapper = mount(QuickActions)

      const buttons = wrapper.findAll('button')
      await buttons[1].trigger('click')
      await buttons[2].trigger('click')

      expect(wrapper.emitted('upload')).toBeFalsy()
    })
  })

  describe('Button Styles', () => {
    it('should apply primary button class to upload button', () => {
      wrapper = mount(QuickActions)

      const buttons = wrapper.findAll('button')
      const uploadButton = buttons[0]
      
      expect(uploadButton.classes()).toContain('btn-primary')
    })

    it('should apply secondary button class to reports button', () => {
      wrapper = mount(QuickActions)

      const buttons = wrapper.findAll('button')
      const reportsButton = buttons[1]
      
      expect(reportsButton.classes()).toContain('btn-secondary')
    })

    it('should apply secondary button class to history button', () => {
      wrapper = mount(QuickActions)

      const buttons = wrapper.findAll('button')
      const historyButton = buttons[2]
      
      expect(historyButton.classes()).toContain('btn-secondary')
    })
  })

  describe('Structure', () => {
    it('should have correct section structure', () => {
      wrapper = mount(QuickActions)

      const section = wrapper.find('section')
      expect(section.exists()).toBe(true)
      expect(section.classes()).toContain('quick-actions')
    })

    it('should have action buttons container', () => {
      wrapper = mount(QuickActions)

      const buttonsContainer = wrapper.find('.action-buttons')
      expect(buttonsContainer.exists()).toBe(true)
    })

    it('should render icons in buttons', () => {
      wrapper = mount(QuickActions)

      const icons = wrapper.findAll('i')
      expect(icons.length).toBe(3)
    })
  })
})





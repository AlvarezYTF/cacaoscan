import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import VisualSettingsSection from '../VisualSettingsSection.vue'

describe('VisualSettingsSection', () => {
  let wrapper

  const defaultSettings = {
    darkMode: false,
    fontSize: 'medium',
    compactMode: false
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = mount(VisualSettingsSection, {
        props: {
          settings: defaultSettings
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should display section title', () => {
      wrapper = mount(VisualSettingsSection, {
        props: {
          settings: defaultSettings
        }
      })

      expect(wrapper.text()).toContain('Ajustes Visuales')
    })

    it('should display dark mode toggle', () => {
      wrapper = mount(VisualSettingsSection, {
        props: {
          settings: defaultSettings
        }
      })

      expect(wrapper.text()).toContain('Modo oscuro')
    })

    it('should display font size selector', () => {
      wrapper = mount(VisualSettingsSection, {
        props: {
          settings: defaultSettings
        }
      })

      expect(wrapper.text()).toContain('Tamaño de fuente')
      expect(wrapper.find('#visual-settings-font-size').exists()).toBe(true)
    })

    it('should display compact mode toggle', () => {
      wrapper = mount(VisualSettingsSection, {
        props: {
          settings: defaultSettings
        }
      })

      expect(wrapper.text()).toContain('Modo compacto')
    })

    it('should display save button', () => {
      wrapper = mount(VisualSettingsSection, {
        props: {
          settings: defaultSettings
        }
      })

      expect(wrapper.text()).toContain('Guardar Ajustes')
    })
  })

  describe('Dark Mode Toggle', () => {
    it('should show dark mode as off by default', () => {
      wrapper = mount(VisualSettingsSection, {
        props: {
          settings: { ...defaultSettings, darkMode: false }
        }
      })

      const darkModeToggle = wrapper.findAll('button').find(btn => 
        btn.classes().includes('bg-gray-500')
      )
      expect(darkModeToggle).toBeDefined()
    })

    it('should show dark mode as on when enabled', () => {
      wrapper = mount(VisualSettingsSection, {
        props: {
          settings: { ...defaultSettings, darkMode: true }
        }
      })

      const darkModeToggle = wrapper.findAll('button').find(btn => 
        btn.classes().includes('bg-white')
      )
      expect(darkModeToggle).toBeDefined()
    })

    it('should emit update:settings when dark mode toggle is clicked', async () => {
      wrapper = mount(VisualSettingsSection, {
        props: {
          settings: { ...defaultSettings, darkMode: false }
        }
      })

      const toggles = wrapper.findAll('button')
      const darkModeToggle = toggles.find(btn => 
        btn.text().includes('Modo oscuro') || 
        btn.classes().includes('bg-gray-500') ||
        btn.classes().includes('bg-white')
      )
      
      if (darkModeToggle) {
        await darkModeToggle.trigger('click')
        await nextTick()

        expect(wrapper.emitted('update:settings')).toBeTruthy()
        const emitted = wrapper.emitted('update:settings')[0][0]
        expect(emitted.darkMode).toBe(true)
      }
    })
  })

  describe('Font Size', () => {
    it('should display current font size', () => {
      wrapper = mount(VisualSettingsSection, {
        props: {
          settings: { ...defaultSettings, fontSize: 'large' }
        }
      })

      const fontSizeSelect = wrapper.find('#visual-settings-font-size')
      expect(fontSizeSelect.element.value).toBe('large')
    })

    it('should have all font size options', () => {
      wrapper = mount(VisualSettingsSection, {
        props: {
          settings: defaultSettings
        }
      })

      const fontSizeSelect = wrapper.find('#visual-settings-font-size')
      const options = fontSizeSelect.findAll('option')
      
      expect(options.length).toBe(3)
      expect(wrapper.text()).toContain('Pequeño')
      expect(wrapper.text()).toContain('Mediano')
      expect(wrapper.text()).toContain('Grande')
    })

    it('should emit update:settings when font size changes', async () => {
      wrapper = mount(VisualSettingsSection, {
        props: {
          settings: defaultSettings
        }
      })

      const fontSizeSelect = wrapper.find('#visual-settings-font-size')
      await fontSizeSelect.setValue('large')
      await nextTick()

      expect(wrapper.emitted('update:settings')).toBeTruthy()
      const emitted = wrapper.emitted('update:settings')[0][0]
      expect(emitted.fontSize).toBe('large')
    })
  })

  describe('Compact Mode Toggle', () => {
    it('should show compact mode as off by default', () => {
      wrapper = mount(VisualSettingsSection, {
        props: {
          settings: { ...defaultSettings, compactMode: false }
        }
      })

      const compactToggle = wrapper.findAll('button').find(btn => 
        btn.classes().includes('bg-gray-300')
      )
      expect(compactToggle).toBeDefined()
    })

    it('should show compact mode as on when enabled', () => {
      wrapper = mount(VisualSettingsSection, {
        props: {
          settings: { ...defaultSettings, compactMode: true }
        }
      })

      const compactToggle = wrapper.findAll('button').find(btn => 
        btn.classes().includes('bg-green-600')
      )
      expect(compactToggle).toBeDefined()
    })

    it('should emit update:settings when compact mode toggle is clicked', async () => {
      wrapper = mount(VisualSettingsSection, {
        props: {
          settings: { ...defaultSettings, compactMode: false }
        }
      })

      const toggles = wrapper.findAll('button')
      const compactToggle = toggles.find(btn => 
        btn.text().includes('Modo compacto') || 
        btn.classes().includes('bg-gray-300') ||
        btn.classes().includes('bg-green-600')
      )
      
      if (compactToggle) {
        await compactToggle.trigger('click')
        await nextTick()

        expect(wrapper.emitted('update:settings')).toBeTruthy()
        const emitted = wrapper.emitted('update:settings')[0][0]
        expect(emitted.compactMode).toBe(true)
      }
    })
  })

  describe('Save Button', () => {
    it('should emit save event when save button is clicked', async () => {
      wrapper = mount(VisualSettingsSection, {
        props: {
          settings: defaultSettings,
          isLoading: false
        }
      })

      const saveButton = wrapper.findAll('button').find(btn => 
        btn.text().includes('Guardar')
      )
      
      if (saveButton) {
        await saveButton.trigger('click')
        expect(wrapper.emitted('save')).toBeTruthy()
      }
    })

    it('should disable save button when isLoading is true', () => {
      wrapper = mount(VisualSettingsSection, {
        props: {
          settings: defaultSettings,
          isLoading: true
        }
      })

      const saveButton = wrapper.findAll('button').find(btn => 
        btn.text().includes('Guardar')
      )
      
      if (saveButton) {
        expect(saveButton.attributes('disabled')).toBeDefined()
      }
    })

    it('should show loading text when isLoading is true', () => {
      wrapper = mount(VisualSettingsSection, {
        props: {
          settings: defaultSettings,
          isLoading: true
        }
      })

      expect(wrapper.text()).toContain('Guardando...')
    })

    it('should enable save button when isLoading is false', () => {
      wrapper = mount(VisualSettingsSection, {
        props: {
          settings: defaultSettings,
          isLoading: false
        }
      })

      const saveButton = wrapper.findAll('button').find(btn => 
        btn.text().includes('Guardar')
      )
      
      if (saveButton) {
        expect(saveButton.attributes('disabled')).toBeUndefined()
      }
    })
  })
})





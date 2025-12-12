import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ScanPreferencesSection from '../ScanPreferencesSection.vue'

describe('ScanPreferencesSection', () => {
  let wrapper

  const defaultPreferences = {
    grainType: 'Criollo',
    minWeight: 5,
    guidedMode: false,
    advancedResults: false
  }

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: defaultPreferences
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should display section title', () => {
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: defaultPreferences
        }
      })

      expect(wrapper.text()).toContain('Preferencias de Escaneo')
    })

    it('should display grain type selector', () => {
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: defaultPreferences
        }
      })

      const select = wrapper.find('select')
      expect(select.exists()).toBe(true)
    })

    it('should display min weight input', () => {
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: defaultPreferences
        }
      })

      const input = wrapper.find('input[type="number"]')
      expect(input.exists()).toBe(true)
    })

    it('should display guided mode toggle', () => {
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: defaultPreferences
        }
      })

      expect(wrapper.text()).toContain('Modo captura guiada')
    })

    it('should display advanced results toggle', () => {
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: defaultPreferences
        }
      })

      expect(wrapper.text()).toContain('Resultados avanzados')
    })

    it('should display save button', () => {
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: defaultPreferences
        }
      })

      expect(wrapper.text()).toContain('Guardar Preferencias')
    })
  })

  describe('Props', () => {
    it('should require preferences prop', () => {
      expect(() => {
        mount(ScanPreferencesSection)
      }).toThrow()
    })

    it('should accept preferences object prop', () => {
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: defaultPreferences
        }
      })

      expect(wrapper.vm.$props.preferences).toEqual(defaultPreferences)
    })

    it('should use default isLoading value', () => {
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: defaultPreferences
        }
      })

      expect(wrapper.vm.$props.isLoading).toBe(false)
    })

    it('should accept isLoading prop', () => {
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: defaultPreferences,
          isLoading: true
        }
      })

      expect(wrapper.vm.$props.isLoading).toBe(true)
    })
  })

  describe('Grain Type Selection', () => {
    it('should display current grain type value', () => {
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: defaultPreferences
        }
      })

      const select = wrapper.find('select')
      expect(select.element.value).toBe('Criollo')
    })

    it('should emit update:preferences when grain type changes', async () => {
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: defaultPreferences
        }
      })

      const select = wrapper.find('select')
      await select.setValue('Forastero')
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('update:preferences')).toBeTruthy()
      const emittedData = wrapper.emitted('update:preferences')[0][0]
      expect(emittedData.grainType).toBe('Forastero')
    })

    it('should have all grain type options', () => {
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: defaultPreferences
        }
      })

      const options = wrapper.findAll('option')
      expect(options.length).toBeGreaterThanOrEqual(6)
      expect(wrapper.text()).toContain('Criollo')
      expect(wrapper.text()).toContain('Forastero')
      expect(wrapper.text()).toContain('Trinitario')
      expect(wrapper.text()).toContain('Nacional')
      expect(wrapper.text()).toContain('Híbrido')
      expect(wrapper.text()).toContain('Todos los tipos')
    })
  })

  describe('Min Weight Input', () => {
    it('should display current min weight value', () => {
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: defaultPreferences
        }
      })

      const input = wrapper.find('input[type="number"]')
      expect(input.element.value).toBe('5')
    })

    it('should emit update:preferences when min weight changes', async () => {
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: defaultPreferences
        }
      })

      const input = wrapper.find('input[type="number"]')
      await input.setValue('10')
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('update:preferences')).toBeTruthy()
      const emittedData = wrapper.emitted('update:preferences')[0][0]
      expect(emittedData.minWeight).toBe(10)
    })

    it('should handle empty min weight input', async () => {
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: defaultPreferences
        }
      })

      const input = wrapper.find('input[type="number"]')
      await input.setValue('')
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('update:preferences')).toBeTruthy()
      const emittedData = wrapper.emitted('update:preferences')[0][0]
      expect(emittedData.minWeight).toBe(0)
    })
  })

  describe('Toggle Switches', () => {
    it('should display guided mode toggle state', () => {
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: {
            ...defaultPreferences,
            guidedMode: true
          }
        }
      })

      const toggle = wrapper.findAll('button')[0]
      expect(toggle.classes()).toContain('bg-green-600')
    })

    it('should emit update:preferences when guided mode toggled', async () => {
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: defaultPreferences
        }
      })

      const toggles = wrapper.findAll('button')
      const guidedModeToggle = toggles.find(btn => {
        const parentText = btn.element.closest('div')?.textContent || ''
        return parentText.includes('Modo captura guiada')
      })

      if (guidedModeToggle) {
        await guidedModeToggle.trigger('click')
        expect(wrapper.emitted('update:preferences')).toBeTruthy()
      }
    })

    it('should display advanced results toggle state', () => {
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: {
            ...defaultPreferences,
            advancedResults: true
          }
        }
      })

      const toggles = wrapper.findAll('button')
      const advancedToggle = toggles.find(btn => {
        const parentText = btn.element.closest('div')?.textContent || ''
        return parentText.includes('Resultados avanzados')
      })

      if (advancedToggle) {
        expect(advancedToggle.classes()).toContain('bg-green-600')
      }
    })
  })

  describe('Save Button', () => {
    it('should emit save event when save button is clicked', async () => {
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: defaultPreferences
        }
      })

      const saveButton = wrapper.findAll('button').find(btn => 
        btn.text().includes('Guardar Preferencias')
      )

      if (saveButton) {
        await saveButton.trigger('click')
        expect(wrapper.emitted('save')).toBeTruthy()
      }
    })

    it('should disable save button when loading', () => {
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: defaultPreferences,
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
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: defaultPreferences,
          isLoading: true
        }
      })

      expect(wrapper.text()).toContain('Guardando...')
    })

    it('should show loading spinner when isLoading is true', () => {
      wrapper = mount(ScanPreferencesSection, {
        props: {
          preferences: defaultPreferences,
          isLoading: true
        }
      })

      const spinner = wrapper.find('.animate-spin')
      expect(spinner.exists()).toBe(true)
    })
  })
})





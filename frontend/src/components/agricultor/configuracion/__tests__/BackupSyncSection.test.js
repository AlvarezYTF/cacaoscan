import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BackupSyncSection from '../BackupSyncSection.vue'

describe('BackupSyncSection', () => {
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
      wrapper = mount(BackupSyncSection)

      expect(wrapper.exists()).toBe(true)
    })

    it('should display section title', () => {
      wrapper = mount(BackupSyncSection)

      expect(wrapper.text()).toContain('Conectividad y Respaldo')
    })

    it('should display sync section', () => {
      wrapper = mount(BackupSyncSection)

      expect(wrapper.text()).toContain('Sincronizar')
      expect(wrapper.text()).toContain('Última sincronización:')
    })

    it('should display export CSV section', () => {
      wrapper = mount(BackupSyncSection)

      expect(wrapper.text()).toContain('Exportar CSV')
      expect(wrapper.text()).toContain('Descargar reportes en CSV')
    })

    it('should display export PDF section', () => {
      wrapper = mount(BackupSyncSection)

      expect(wrapper.text()).toContain('Exportar PDF')
      expect(wrapper.text()).toContain('Generar reporte en PDF')
    })
  })

  describe('Props', () => {
    it('should display lastSync when provided', () => {
      wrapper = mount(BackupSyncSection, {
        props: {
          lastSync: '2024-01-15 10:30:00'
        }
      })

      expect(wrapper.text()).toContain('2024-01-15 10:30:00')
    })

    it('should display "Nunca" when lastSync is empty', () => {
      wrapper = mount(BackupSyncSection, {
        props: {
          lastSync: ''
        }
      })

      expect(wrapper.text()).toContain('Nunca')
    })

    it('should display "Nunca" when lastSync is not provided', () => {
      wrapper = mount(BackupSyncSection)

      expect(wrapper.text()).toContain('Nunca')
    })

    it('should show sync button as enabled when isLoading is false', () => {
      wrapper = mount(BackupSyncSection, {
        props: {
          isLoading: false
        }
      })

      const syncButton = wrapper.findAll('button')[0]
      expect(syncButton.attributes('disabled')).toBeUndefined()
      expect(syncButton.text()).toBe('Sincronizar Ahora')
    })

    it('should show sync button as disabled when isLoading is true', () => {
      wrapper = mount(BackupSyncSection, {
        props: {
          isLoading: true
        }
      })

      const syncButton = wrapper.findAll('button')[0]
      expect(syncButton.attributes('disabled')).toBeDefined()
      expect(syncButton.text()).toBe('Sincronizando...')
    })

    it('should show sync button text as "Sincronizando..." when isLoading is true', () => {
      wrapper = mount(BackupSyncSection, {
        props: {
          isLoading: true
        }
      })

      const syncButton = wrapper.findAll('button')[0]
      expect(syncButton.text()).toBe('Sincronizando...')
    })
  })

  describe('Events', () => {
    it('should emit sync event when sync button is clicked', async () => {
      wrapper = mount(BackupSyncSection, {
        props: {
          isLoading: false
        }
      })

      const syncButton = wrapper.findAll('button')[0]
      await syncButton.trigger('click')

      expect(wrapper.emitted('sync')).toBeTruthy()
      expect(wrapper.emitted('sync')).toHaveLength(1)
    })

    it('should not emit sync event when sync button is disabled', async () => {
      wrapper = mount(BackupSyncSection, {
        props: {
          isLoading: true
        }
      })

      const syncButton = wrapper.findAll('button')[0]
      await syncButton.trigger('click')

      expect(wrapper.emitted('sync')).toBeFalsy()
    })

    it('should emit export-csv event when CSV export button is clicked', async () => {
      wrapper = mount(BackupSyncSection)

      const csvButton = wrapper.findAll('button')[1]
      await csvButton.trigger('click')

      expect(wrapper.emitted('export-csv')).toBeTruthy()
      expect(wrapper.emitted('export-csv')).toHaveLength(1)
    })

    it('should emit export-pdf event when PDF export button is clicked', async () => {
      wrapper = mount(BackupSyncSection)

      const pdfButton = wrapper.findAll('button')[2]
      await pdfButton.trigger('click')

      expect(wrapper.emitted('export-pdf')).toBeTruthy()
      expect(wrapper.emitted('export-pdf')).toHaveLength(1)
    })

    it('should emit all events correctly', async () => {
      wrapper = mount(BackupSyncSection, {
        props: {
          isLoading: false
        }
      })

      const buttons = wrapper.findAll('button')
      
      await buttons[0].trigger('click')
      await buttons[1].trigger('click')
      await buttons[2].trigger('click')

      expect(wrapper.emitted('sync')).toBeTruthy()
      expect(wrapper.emitted('export-csv')).toBeTruthy()
      expect(wrapper.emitted('export-pdf')).toBeTruthy()
    })
  })

  describe('Button States', () => {
    it('should have three buttons', () => {
      wrapper = mount(BackupSyncSection)

      const buttons = wrapper.findAll('button')
      expect(buttons.length).toBe(3)
    })

    it('should have sync button with correct classes', () => {
      wrapper = mount(BackupSyncSection)

      const syncButton = wrapper.findAll('button')[0]
      expect(syncButton.classes()).toContain('bg-green-600')
    })

    it('should have CSV button with correct classes', () => {
      wrapper = mount(BackupSyncSection)

      const csvButton = wrapper.findAll('button')[1]
      expect(csvButton.classes()).toContain('bg-gray-600')
    })

    it('should have PDF button with correct classes', () => {
      wrapper = mount(BackupSyncSection)

      const pdfButton = wrapper.findAll('button')[2]
      expect(pdfButton.classes()).toContain('bg-red-600')
    })
  })
})


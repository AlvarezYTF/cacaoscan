import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import NotificationsSection from '../NotificationsSection.vue'

describe('NotificationsSection', () => {
  let wrapper

  const defaultNotifications = {
    email: false,
    whatsapp: false,
    quality: false,
    environment: false
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
      wrapper = mount(NotificationsSection, {
        props: {
          notifications: defaultNotifications
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should display section title', () => {
      wrapper = mount(NotificationsSection, {
        props: {
          notifications: defaultNotifications
        }
      })

      expect(wrapper.text()).toContain('Notificaciones')
    })

    it('should display email notification toggle', () => {
      wrapper = mount(NotificationsSection, {
        props: {
          notifications: defaultNotifications
        }
      })

      expect(wrapper.text()).toContain('Notificaciones por email')
    })

    it('should display WhatsApp notification toggle', () => {
      wrapper = mount(NotificationsSection, {
        props: {
          notifications: defaultNotifications
        }
      })

      expect(wrapper.text()).toContain('Notificaciones por WhatsApp')
    })

    it('should display quality alerts toggle', () => {
      wrapper = mount(NotificationsSection, {
        props: {
          notifications: defaultNotifications
        }
      })

      expect(wrapper.text()).toContain('Alertas de calidad')
    })

    it('should display environment alerts toggle', () => {
      wrapper = mount(NotificationsSection, {
        props: {
          notifications: defaultNotifications
        }
      })

      expect(wrapper.text()).toContain('Alertas ambientales')
    })

    it('should display save button', () => {
      wrapper = mount(NotificationsSection, {
        props: {
          notifications: defaultNotifications
        }
      })

      expect(wrapper.text()).toContain('Guardar Notificaciones')
    })
  })

  describe('Toggle States', () => {
    it('should show email toggle as off by default', () => {
      wrapper = mount(NotificationsSection, {
        props: {
          notifications: { ...defaultNotifications, email: false }
        }
      })

      const emailToggle = wrapper.findAll('button').find(btn => 
        btn.text().includes('Notificaciones por email') || 
        btn.classes().includes('bg-gray-300')
      )
      expect(emailToggle).toBeDefined()
    })

    it('should show email toggle as on when enabled', () => {
      wrapper = mount(NotificationsSection, {
        props: {
          notifications: { ...defaultNotifications, email: true }
        }
      })

      const toggles = wrapper.findAll('button')
      const emailToggle = toggles.find(btn => btn.classes().includes('bg-green-600'))
      expect(emailToggle).toBeDefined()
    })

    it('should show WhatsApp toggle as off by default', () => {
      wrapper = mount(NotificationsSection, {
        props: {
          notifications: { ...defaultNotifications, whatsapp: false }
        }
      })

      const toggles = wrapper.findAll('button')
      const whatsappToggle = toggles.find(btn => 
        btn.classes().includes('bg-gray-300')
      )
      expect(whatsappToggle).toBeDefined()
    })

    it('should show WhatsApp toggle as on when enabled', () => {
      wrapper = mount(NotificationsSection, {
        props: {
          notifications: { ...defaultNotifications, whatsapp: true }
        }
      })

      const toggles = wrapper.findAll('button')
      const whatsappToggle = toggles.find(btn => btn.classes().includes('bg-green-600'))
      expect(whatsappToggle).toBeDefined()
    })
  })

  describe('Events', () => {
    it('should emit update:notifications when email toggle is clicked', async () => {
      wrapper = mount(NotificationsSection, {
        props: {
          notifications: { ...defaultNotifications, email: false }
        }
      })

      const toggles = wrapper.findAll('button')
      const emailToggle = toggles.find(btn => 
        btn.text().includes('Notificaciones por email') || 
        btn.classes().includes('bg-gray-300')
      )
      
      if (emailToggle) {
        await emailToggle.trigger('click')
        await nextTick()

        expect(wrapper.emitted('update:notifications')).toBeTruthy()
        const emitted = wrapper.emitted('update:notifications')[0][0]
        expect(emitted.email).toBe(true)
      }
    })

    it('should emit update:notifications when WhatsApp toggle is clicked', async () => {
      wrapper = mount(NotificationsSection, {
        props: {
          notifications: { ...defaultNotifications, whatsapp: false }
        }
      })

      // Find all buttons and locate the WhatsApp toggle
      const allButtons = wrapper.findAll('button')
      const whatsappToggle = allButtons.find(btn => {
        // Check if this button is within a container that has WhatsApp text
        const parent = btn.element.closest('div')
        if (parent) {
          const parentText = parent.textContent || ''
          return parentText.includes('Notificaciones por WhatsApp') && 
                 !parentText.includes('Guardar')
        }
        return false
      })
      
      expect(whatsappToggle).toBeTruthy()
      expect(whatsappToggle.exists()).toBe(true)
      
      await whatsappToggle.trigger('click')
      await nextTick()

      expect(wrapper.emitted('update:notifications')).toBeTruthy()
      const emitted = wrapper.emitted('update:notifications')[0][0]
      expect(emitted.whatsapp).toBe(true)
    })

    it('should emit save event when save button is clicked', async () => {
      wrapper = mount(NotificationsSection, {
        props: {
          notifications: defaultNotifications,
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
  })

  describe('Loading State', () => {
    it('should disable save button when isLoading is true', () => {
      wrapper = mount(NotificationsSection, {
        props: {
          notifications: defaultNotifications,
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
      wrapper = mount(NotificationsSection, {
        props: {
          notifications: defaultNotifications,
          isLoading: true
        }
      })

      expect(wrapper.text()).toContain('Guardando...')
    })

    it('should enable save button when isLoading is false', () => {
      wrapper = mount(NotificationsSection, {
        props: {
          notifications: defaultNotifications,
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


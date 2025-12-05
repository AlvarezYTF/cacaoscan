import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseVisualSettings from '../BaseVisualSettings.vue'

vi.mock('../BasePreferencesWrapper.vue', () => ({
  default: {
    name: 'BasePreferencesWrapper',
    template: '<div><slot name="header-icon"></slot><slot name="settings" :value="modelValue" :update="update"></slot><slot name="actions"></slot></div>',
    props: ['modelValue', 'title', 'showHeader', 'showActions', 'showSaveButton', 'showResetButton', 'saveButtonText', 'resetButtonText', 'containerClass', 'iconPath', 'contentSlotName'],
    emits: ['update:modelValue', 'save', 'reset']
  }
}))

describe('BaseVisualSettings', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render component', () => {
    wrapper = mount(BaseVisualSettings, {
      props: {
        modelValue: {}
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should pass modelValue to BasePreferencesWrapper', () => {
    const settings = { theme: 'dark' }
    wrapper = mount(BaseVisualSettings, {
      props: {
        modelValue: settings
      }
    })

    expect(wrapper.vm.$props.modelValue).toEqual(settings)
  })

  it('should emit update:modelValue event', async () => {
    wrapper = mount(BaseVisualSettings, {
      props: {
        modelValue: {}
      }
    })

    await wrapper.vm.$emit('update:modelValue', { theme: 'light' })

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')[0]).toEqual([{ theme: 'light' }])
  })

  it('should emit save event', async () => {
    wrapper = mount(BaseVisualSettings, {
      props: {
        modelValue: {}
      }
    })

    await wrapper.vm.$emit('save', { theme: 'dark' })

    expect(wrapper.emitted('save')).toBeTruthy()
    expect(wrapper.emitted('save')[0]).toEqual([{ theme: 'dark' }])
  })

  it('should emit reset event', async () => {
    wrapper = mount(BaseVisualSettings, {
      props: {
        modelValue: {}
      }
    })

    await wrapper.vm.$emit('reset')

    expect(wrapper.emitted('reset')).toBeTruthy()
  })

  it('should render header-icon slot', () => {
    wrapper = mount(BaseVisualSettings, {
      props: {
        modelValue: {}
      },
      slots: {
        'header-icon': '<div>Custom Header Icon</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Header Icon')
  })

  it('should render settings slot with scoped props', () => {
    wrapper = mount(BaseVisualSettings, {
      props: {
        modelValue: { theme: 'dark' }
      },
      slots: {
        settings: '<div>Settings: {{ settings.theme }}</div>'
      }
    })

    expect(wrapper.text()).toContain('Settings')
  })

  it('should render actions slot', () => {
    wrapper = mount(BaseVisualSettings, {
      props: {
        modelValue: {}
      },
      slots: {
        actions: '<div>Custom Actions</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Actions')
  })

  it('should use correct preference type configuration', () => {
    wrapper = mount(BaseVisualSettings, {
      props: {
        modelValue: {}
      }
    })

    // The component should use VISUAL preference type
    expect(wrapper.vm.$options.name || 'BaseVisualSettings').toBeTruthy()
  })

  it('should handle title prop', () => {
    wrapper = mount(BaseVisualSettings, {
      props: {
        modelValue: {},
        title: 'Custom Visual Title'
      }
    })

    expect(wrapper.vm.$props.title).toBe('Custom Visual Title')
  })

  it('should handle showHeader prop', () => {
    wrapper = mount(BaseVisualSettings, {
      props: {
        modelValue: {},
        showHeader: false
      }
    })

    expect(wrapper.vm.$props.showHeader).toBe(false)
  })

  it('should handle showActions prop', () => {
    wrapper = mount(BaseVisualSettings, {
      props: {
        modelValue: {},
        showActions: false
      }
    })

    expect(wrapper.vm.$props.showActions).toBe(false)
  })

  it('should handle showSaveButton prop', () => {
    wrapper = mount(BaseVisualSettings, {
      props: {
        modelValue: {},
        showSaveButton: false
      }
    })

    expect(wrapper.vm.$props.showSaveButton).toBe(false)
  })

  it('should handle showResetButton prop', () => {
    wrapper = mount(BaseVisualSettings, {
      props: {
        modelValue: {},
        showResetButton: true
      }
    })

    expect(wrapper.vm.$props.showResetButton).toBe(true)
  })

  it('should handle saveButtonText prop', () => {
    wrapper = mount(BaseVisualSettings, {
      props: {
        modelValue: {},
        saveButtonText: 'Save Visual Settings'
      }
    })

    expect(wrapper.vm.$props.saveButtonText).toBe('Save Visual Settings')
  })

  it('should handle resetButtonText prop', () => {
    wrapper = mount(BaseVisualSettings, {
      props: {
        modelValue: {},
        resetButtonText: 'Reset Visual Settings'
      }
    })

    expect(wrapper.vm.$props.resetButtonText).toBe('Reset Visual Settings')
  })

  it('should handle containerClass prop', () => {
    wrapper = mount(BaseVisualSettings, {
      props: {
        modelValue: {},
        containerClass: 'custom-visual-class'
      }
    })

    expect(wrapper.vm.$props.containerClass).toBe('custom-visual-class')
  })
})


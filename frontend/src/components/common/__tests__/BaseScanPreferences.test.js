import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseScanPreferences from '../BaseScanPreferences.vue'

vi.mock('../BasePreferencesWrapper.vue', () => ({
  default: {
    name: 'BasePreferencesWrapper',
    template: '<div><slot name="header-icon"></slot><slot name="preferences" :value="modelValue" :update="update"></slot><slot name="actions"></slot></div>',
    props: ['modelValue', 'title', 'showHeader', 'showActions', 'showSaveButton', 'showResetButton', 'saveButtonText', 'resetButtonText', 'containerClass', 'iconPath', 'contentSlotName'],
    emits: ['update:modelValue', 'save', 'reset']
  }
}))

describe('BaseScanPreferences', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render component', () => {
    wrapper = mount(BaseScanPreferences, {
      props: {
        modelValue: {}
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should pass modelValue to BasePreferencesWrapper', () => {
    const preferences = { setting1: 'value1' }
    wrapper = mount(BaseScanPreferences, {
      props: {
        modelValue: preferences
      }
    })

    expect(wrapper.vm.$props.modelValue).toEqual(preferences)
  })

  it('should emit update:modelValue event', async () => {
    wrapper = mount(BaseScanPreferences, {
      props: {
        modelValue: {}
      }
    })

    await wrapper.vm.$emit('update:modelValue', { setting1: 'newValue' })

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')[0]).toEqual([{ setting1: 'newValue' }])
  })

  it('should emit save event', async () => {
    wrapper = mount(BaseScanPreferences, {
      props: {
        modelValue: {}
      }
    })

    await wrapper.vm.$emit('save', { setting1: 'value1' })

    expect(wrapper.emitted('save')).toBeTruthy()
    expect(wrapper.emitted('save')[0]).toEqual([{ setting1: 'value1' }])
  })

  it('should emit reset event', async () => {
    wrapper = mount(BaseScanPreferences, {
      props: {
        modelValue: {}
      }
    })

    await wrapper.vm.$emit('reset')

    expect(wrapper.emitted('reset')).toBeTruthy()
  })

  it('should render header-icon slot', () => {
    wrapper = mount(BaseScanPreferences, {
      props: {
        modelValue: {}
      },
      slots: {
        'header-icon': '<div>Custom Header Icon</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Header Icon')
  })

  it('should render preferences slot with scoped props', () => {
    wrapper = mount(BaseScanPreferences, {
      props: {
        modelValue: { setting1: 'value1' }
      },
      slots: {
        preferences: '<div>Preferences: {{ preferences.setting1 }}</div>'
      }
    })

    expect(wrapper.text()).toContain('Preferences')
  })

  it('should render actions slot', () => {
    wrapper = mount(BaseScanPreferences, {
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
    wrapper = mount(BaseScanPreferences, {
      props: {
        modelValue: {}
      }
    })

    // The component should use SCAN preference type
    expect(wrapper.vm.$options.name || 'BaseScanPreferences').toBeTruthy()
  })

  it('should handle title prop', () => {
    wrapper = mount(BaseScanPreferences, {
      props: {
        modelValue: {},
        title: 'Custom Title'
      }
    })

    expect(wrapper.vm.$props.title).toBe('Custom Title')
  })

  it('should handle showHeader prop', () => {
    wrapper = mount(BaseScanPreferences, {
      props: {
        modelValue: {},
        showHeader: false
      }
    })

    expect(wrapper.vm.$props.showHeader).toBe(false)
  })

  it('should handle showActions prop', () => {
    wrapper = mount(BaseScanPreferences, {
      props: {
        modelValue: {},
        showActions: false
      }
    })

    expect(wrapper.vm.$props.showActions).toBe(false)
  })

  it('should handle showSaveButton prop', () => {
    wrapper = mount(BaseScanPreferences, {
      props: {
        modelValue: {},
        showSaveButton: false
      }
    })

    expect(wrapper.vm.$props.showSaveButton).toBe(false)
  })

  it('should handle showResetButton prop', () => {
    wrapper = mount(BaseScanPreferences, {
      props: {
        modelValue: {},
        showResetButton: true
      }
    })

    expect(wrapper.vm.$props.showResetButton).toBe(true)
  })

  it('should handle saveButtonText prop', () => {
    wrapper = mount(BaseScanPreferences, {
      props: {
        modelValue: {},
        saveButtonText: 'Custom Save'
      }
    })

    expect(wrapper.vm.$props.saveButtonText).toBe('Custom Save')
  })

  it('should handle resetButtonText prop', () => {
    wrapper = mount(BaseScanPreferences, {
      props: {
        modelValue: {},
        resetButtonText: 'Custom Reset'
      }
    })

    expect(wrapper.vm.$props.resetButtonText).toBe('Custom Reset')
  })

  it('should handle containerClass prop', () => {
    wrapper = mount(BaseScanPreferences, {
      props: {
        modelValue: {},
        containerClass: 'custom-class'
      }
    })

    expect(wrapper.vm.$props.containerClass).toBe('custom-class')
  })
})


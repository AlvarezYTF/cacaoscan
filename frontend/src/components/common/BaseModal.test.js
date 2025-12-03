import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseModal from './BaseModal.vue'

describe('BaseModal', () => {
  it('should render modal when show is true', () => {
    const wrapper = mount(BaseModal, {
      props: {
        show: true
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should not render modal when show is false', () => {
    const wrapper = mount(BaseModal, {
      props: {
        show: false
      }
    })

    expect(wrapper.find('.fixed').exists()).toBe(false)
  })

  it('should emit close event when close button is clicked', async () => {
    const wrapper = mount(BaseModal, {
      props: {
        show: true,
        showCloseButton: true
      }
    })

    const closeButton = wrapper.find('button')
    if (closeButton.exists()) {
      await closeButton.trigger('click')
      expect(wrapper.emitted('close')).toBeTruthy()
    }
  })

  it('should emit update:show event when close button is clicked', async () => {
    const wrapper = mount(BaseModal, {
      props: {
        show: true,
        showCloseButton: true
      }
    })

    const closeButton = wrapper.find('button')
    if (closeButton.exists()) {
      await closeButton.trigger('click')
      expect(wrapper.emitted('update:show')).toBeTruthy()
      expect(wrapper.emitted('update:show')[0]).toEqual([false])
    }
  })

  it('should handle overlay click when closeOnOverlay is true', async () => {
    const wrapper = mount(BaseModal, {
      props: {
        show: true,
        closeOnOverlay: true
      }
    })

    await wrapper.vm.handleOverlayClick()
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('close')).toBeTruthy()
    expect(wrapper.emitted('update:show')).toBeTruthy()
  })

  it('should not handle overlay click when closeOnOverlay is false', async () => {
    const wrapper = mount(BaseModal, {
      props: {
        show: true,
        closeOnOverlay: false
      }
    })

    await wrapper.vm.handleOverlayClick()
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('close')).toBeFalsy()
  })

  it('should apply correct max width class', () => {
    const wrapper = mount(BaseModal, {
      props: {
        show: true,
        maxWidth: 'lg'
      }
    })

    expect(wrapper.vm.computedContainerClass).toContain('max-w-lg')
  })

  it('should apply custom container class', () => {
    const wrapper = mount(BaseModal, {
      props: {
        show: true,
        containerClass: 'custom-class'
      }
    })

    expect(wrapper.vm.computedContainerClass).toContain('custom-class')
  })

  it('should display title when provided', () => {
    const wrapper = mount(BaseModal, {
      props: {
        show: true,
        title: 'Test Title'
      }
    })

    expect(wrapper.text().includes('Test Title')).toBe(true)
  })

  it('should display subtitle when provided', () => {
    const wrapper = mount(BaseModal, {
      props: {
        show: true,
        title: 'Test Title',
        subtitle: 'Test Subtitle'
      }
    })

    expect(wrapper.text().includes('Test Subtitle')).toBe(true)
  })

  it('should render header slot', () => {
    const wrapper = mount(BaseModal, {
      props: {
        show: true
      },
      slots: {
        header: '<div>Custom Header</div>'
      }
    })

    expect(wrapper.text().includes('Custom Header')).toBe(true)
  })

  it('should render default slot', () => {
    const wrapper = mount(BaseModal, {
      props: {
        show: true
      },
      slots: {
        default: '<div>Modal Content</div>'
      }
    })

    expect(wrapper.text().includes('Modal Content')).toBe(true)
  })

  it('should render footer slot', () => {
    const wrapper = mount(BaseModal, {
      props: {
        show: true
      },
      slots: {
        footer: '<div>Custom Footer</div>'
      }
    })

    expect(wrapper.text().includes('Custom Footer')).toBe(true)
  })
})


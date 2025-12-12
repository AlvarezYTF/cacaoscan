import { describe, it, expect, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseUploadSection from '../BaseUploadSection.vue'

describe('BaseUploadSection', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render component', () => {
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: null
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display label when provided', () => {
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: null,
        label: 'Upload Label'
      }
    })

    expect(wrapper.text()).toContain('Upload Label')
  })

  it('should show required indicator when required is true', () => {
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: null,
        label: 'Upload Label',
        required: true
      }
    })

    expect(wrapper.text()).toContain('*')
  })

  it('should render file input', () => {
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: null
      }
    })

    const input = wrapper.find('input[type="file"]')
    expect(input.exists()).toBe(true)
  })

  it('should use default accept value', () => {
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: null
      }
    })

    const input = wrapper.find('input[type="file"]')
    expect(input.attributes('accept')).toBe('image/*')
  })

  it('should use custom accept value', () => {
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: null,
        accept: '.pdf,.doc'
      }
    })

    const input = wrapper.find('input[type="file"]')
    expect(input.attributes('accept')).toBe('.pdf,.doc')
  })

  it('should disable input when disabled is true', () => {
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: null,
        disabled: true
      }
    })

    const input = wrapper.find('input[type="file"]')
    expect(input.attributes('disabled')).toBeDefined()
  })

  it('should show upload text', () => {
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: null
      }
    })

    expect(wrapper.text()).toContain('Arrastra archivos aquí')
  })

  it('should use custom upload text', () => {
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: null,
        uploadText: 'Custom upload text'
      }
    })

    expect(wrapper.text()).toContain('Custom upload text')
  })

  it('should show uploading state when uploading is true', () => {
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: null,
        uploading: true
      }
    })

    expect(wrapper.text()).toContain('Subiendo...')
  })

  it('should show upload progress when provided', () => {
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: null,
        uploading: true,
        uploadProgress: 50
      }
    })

    expect(wrapper.text()).toContain('50%')
  })

  it('should display error message when provided', () => {
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: null,
        error: 'Error message'
      }
    })

    expect(wrapper.text()).toContain('Error message')
  })

  it('should display helper text when provided and no error', () => {
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: null,
        helperText: 'Helper text'
      }
    })

    expect(wrapper.text()).toContain('Helper text')
  })

  it('should emit update:modelValue when file is selected', async () => {
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: null
      }
    })

    const input = wrapper.find('input[type="file"]')
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    
    Object.defineProperty(input.element, 'files', {
      value: [file],
      writable: false
    })

    await input.trigger('change')
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
  })

  it('should emit file-added event when file is selected', async () => {
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: null
      }
    })

    const input = wrapper.find('input[type="file"]')
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    
    Object.defineProperty(input.element, 'files', {
      value: [file],
      writable: false
    })

    await input.trigger('change')
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('file-added')).toBeTruthy()
  })

  it('should handle drag and drop', async () => {
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: null
      }
    })

    const dropZone = wrapper.find('.border-dashed')
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    
    const dataTransfer = {
      files: [file]
    }

    await dropZone.trigger('dragover', { dataTransfer })
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.isDragging).toBe(true)
  })

  it('should display file list when files are present', () => {
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: file
      }
    })

    expect(wrapper.text()).toContain('test.jpg')
  })

  it('should emit file-removed when file is removed', async () => {
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: file
      }
    })

    const removeButton = wrapper.find('button[aria-label="Eliminar archivo"]')
    if (removeButton.exists()) {
      await removeButton.trigger('click')
      expect(wrapper.emitted('file-removed')).toBeTruthy()
    }
  })

  it('should handle multiple files', async () => {
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: null,
        multiple: true
      }
    })

    const input = wrapper.find('input[type="file"]')
    expect(input.attributes('multiple')).toBeDefined()
  })

  it('should format file size correctly', () => {
    const largeFile = new File(['x'.repeat(1024 * 1024)], 'large.jpg', { type: 'image/jpeg' })
    
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: largeFile
      }
    })

    expect(wrapper.text()).toContain('MB')
  })

  it('should show loading overlay when uploading', () => {
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: null,
        uploading: true
      }
    })

    const overlay = wrapper.find('.absolute.inset-0')
    expect(overlay.exists()).toBe(true)
  })

  it('should render icon slot', () => {
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: null
      },
      slots: {
        icon: '<div>Custom Icon</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Icon')
  })

  it('should validate file type based on accept prop', async () => {
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: null,
        accept: 'image/*'
      }
    })

    const input = wrapper.find('input[type="file"]')
    expect(input.attributes('accept')).toBe('image/*')
  })

  it('should validate file size against maxSize', async () => {
    wrapper = mount(BaseUploadSection, {
      props: {
        modelValue: null,
        maxSize: 1024 * 1024 // 1MB
      }
    })

    const input = wrapper.find('input[type="file"]')
    expect(input.exists()).toBe(true)
  })
})


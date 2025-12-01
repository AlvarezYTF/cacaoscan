import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CameraCapture from '../CameraCapture.vue'

describe('CameraCapture', () => {
  it('should render camera capture component', () => {
    const wrapper = mount(CameraCapture)

    expect(wrapper.find('.camera-capture').exists()).toBe(true)
  })

  it('should show loading state initially', () => {
    const wrapper = mount(CameraCapture)

    expect(wrapper.text()).toContain('Inicializando')
  })
})


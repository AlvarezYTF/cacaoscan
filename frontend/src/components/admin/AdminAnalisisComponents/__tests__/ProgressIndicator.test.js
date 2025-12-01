import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ProgressIndicator from '../ProgressIndicator.vue'

describe('ProgressIndicator', () => {
  it('should render progress indicator', () => {
    const wrapper = mount(ProgressIndicator, {
      props: {
        progress: 50
      }
    })

    expect(wrapper.find('.progress').exists() || wrapper.text().includes('50')).toBe(true)
  })

  it('should display progress percentage', () => {
    const wrapper = mount(ProgressIndicator, {
      props: {
        progress: 75
      }
    })

    expect(wrapper.text()).toContain('75') || expect(wrapper.props('progress')).toBe(75)
  })
})


import { describe, it, expect, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseQuickActions from '../BaseQuickActions.vue'

describe('BaseQuickActions', () => {
  let wrapper

  const mockActions = [
    {
      key: 'action1',
      label: 'Action 1',
      variant: 'primary'
    },
    {
      key: 'action2',
      label: 'Action 2',
      variant: 'secondary'
    }
  ]

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render component', () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: mockActions
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display title when provided', () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: mockActions,
        title: 'Quick Actions'
      }
    })

    expect(wrapper.text()).toContain('Quick Actions')
  })

  it('should display subtitle when provided', () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: mockActions,
        title: 'Quick Actions',
        subtitle: 'Choose an action'
      }
    })

    expect(wrapper.text()).toContain('Choose an action')
  })

  it('should render all actions', () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: mockActions
      }
    })

    const buttons = wrapper.findAll('button')
    expect(buttons.length).toBe(2)
    expect(wrapper.text()).toContain('Action 1')
    expect(wrapper.text()).toContain('Action 2')
  })

  it('should emit action-click event when action is clicked', async () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: mockActions
      }
    })

    const buttons = wrapper.findAll('button')
    await buttons[0].trigger('click')

    expect(wrapper.emitted('action-click')).toBeTruthy()
    expect(wrapper.emitted('action-click')[0]).toEqual([mockActions[0]])
  })

  it('should not emit action-click when action is disabled', async () => {
    const actionsWithDisabled = [
      {
        ...mockActions[0],
        disabled: true
      }
    ]

    wrapper = mount(BaseQuickActions, {
      props: {
        actions: actionsWithDisabled
      }
    })

    const button = wrapper.find('button')
    await button.trigger('click')

    expect(wrapper.emitted('action-click')).toBeFalsy()
  })

  it('should not emit action-click when component is loading', async () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: mockActions,
        loading: true
      }
    })

    const button = wrapper.find('button')
    await button.trigger('click')

    expect(wrapper.emitted('action-click')).toBeFalsy()
  })

  it('should disable actions when loading is true', () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: mockActions,
        loading: true
      }
    })

    const buttons = wrapper.findAll('button')
    for (const button of buttons) {
      expect(button.attributes('disabled')).toBeDefined()
    }
  })

  it('should apply primary variant styles', () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: [
          {
            key: 'action1',
            label: 'Primary Action',
            variant: 'primary'
          }
        ]
      }
    })

    const button = wrapper.find('button')
    expect(button.classes()).toContain('border-green-500')
  })

  it('should apply secondary variant styles', () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: [
          {
            key: 'action1',
            label: 'Secondary Action',
            variant: 'secondary'
          }
        ]
      }
    })

    const button = wrapper.find('button')
    expect(button.classes()).toContain('border-gray-300')
  })

  it('should apply danger variant styles', () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: [
          {
            key: 'action1',
            label: 'Danger Action',
            variant: 'danger'
          }
        ]
      }
    })

    const button = wrapper.find('button')
    expect(button.classes()).toContain('border-red-500')
  })

  it('should apply success variant styles', () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: [
          {
            key: 'action1',
            label: 'Success Action',
            variant: 'success'
          }
        ]
      }
    })

    const button = wrapper.find('button')
    expect(button.classes()).toContain('border-green-500')
  })

  it('should display badge when provided', () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: [
          {
            key: 'action1',
            label: 'Action with Badge',
            badge: 'New'
          }
        ]
      }
    })

    expect(wrapper.text()).toContain('New')
  })

  it('should render icon when provided', () => {
    const TestIcon = { template: '<div class="test-icon">Icon</div>' }
    
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: [
          {
            key: 'action1',
            label: 'Action with Icon',
            icon: TestIcon
          }
        ]
      }
    })

    expect(wrapper.find('.test-icon').exists()).toBe(true)
  })

  it('should render header slot', () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: mockActions
      },
      slots: {
        header: '<div>Custom Header</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Header')
  })

  it('should render footer slot', () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: mockActions
      },
      slots: {
        footer: '<div>Custom Footer</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Footer')
  })

  it('should render icon slot for specific action', () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: mockActions
      },
      slots: {
        'icon-action1': '<div>Custom Icon</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Icon')
  })

  it('should render default slot', () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: mockActions
      },
      slots: {
        default: '<div>Custom Content</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Content')
  })

  it('should use default columns value of 4', () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: mockActions
      }
    })

    const grid = wrapper.find('.grid')
    expect(grid.classes()).toContain('grid-cols-2')
    expect(grid.classes()).toContain('sm:grid-cols-4')
  })

  it('should apply custom columns', () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: mockActions,
        columns: 3
      }
    })

    const grid = wrapper.find('.grid')
    expect(grid.classes()).toContain('grid-cols-3')
  })

  it('should apply compact variant', () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: mockActions,
        variant: 'compact'
      }
    })

    const container = wrapper.find('.bg-white')
    expect(container.classes()).toContain('p-3')
    const grid = wrapper.find('.grid')
    expect(grid.classes()).toContain('gap-2')
  })

  it('should apply spacious variant', () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: mockActions,
        variant: 'spacious'
      }
    })

    const container = wrapper.find('.bg-white')
    expect(container.classes()).toContain('p-8')
    const grid = wrapper.find('.grid')
    expect(grid.classes()).toContain('gap-6')
  })

  it('should apply default variant', () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: mockActions,
        variant: 'default'
      }
    })

    const grid = wrapper.find('.grid')
    expect(grid.classes()).toContain('gap-4')
  })

  it('should use action title as button title attribute', () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: [
          {
            key: 'action1',
            label: 'Action Label',
            title: 'Action Title'
          }
        ]
      }
    })

    const button = wrapper.find('button')
    expect(button.attributes('title')).toBe('Action Title')
  })

  it('should use action label as button title when title not provided', () => {
    wrapper = mount(BaseQuickActions, {
      props: {
        actions: [
          {
            key: 'action1',
            label: 'Action Label'
          }
        ]
      }
    })

    const button = wrapper.find('button')
    expect(button.attributes('title')).toBe('Action Label')
  })

  it('should validate actions prop structure', () => {
    expect(() => {
      mount(BaseQuickActions, {
        props: {
          actions: [
            {
              label: 'Missing key'
            }
          ]
        }
      })
    }).not.toThrow()
  })
})


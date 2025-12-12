import { describe, it, expect, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseTimeline from '../BaseTimeline.vue'

describe('BaseTimeline', () => {
  let wrapper

  const mockItems = [
    { id: 1, title: 'Event 1', description: 'Description 1' },
    { id: 2, title: 'Event 2', description: 'Description 2' },
    { id: 3, title: 'Event 3', description: 'Description 3' }
  ]

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render component', () => {
    wrapper = mount(BaseTimeline, {
      props: {
        items: mockItems
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should show loading state when loading is true', () => {
    wrapper = mount(BaseTimeline, {
      props: {
        items: [],
        loading: true
      }
    })

    expect(wrapper.text()).toContain('Cargando...')
  })

  it('should show empty state when items array is empty', () => {
    wrapper = mount(BaseTimeline, {
      props: {
        items: [],
        loading: false
      }
    })

    expect(wrapper.text()).toContain('No hay elementos')
  })

  it('should render all timeline items', () => {
    wrapper = mount(BaseTimeline, {
      props: {
        items: mockItems,
        loading: false
      }
    })

    expect(wrapper.text()).toContain('Event 1')
    expect(wrapper.text()).toContain('Event 2')
    expect(wrapper.text()).toContain('Event 3')
  })

  it('should display title when provided', () => {
    wrapper = mount(BaseTimeline, {
      props: {
        items: mockItems,
        title: 'Timeline Title'
      }
    })

    expect(wrapper.text()).toContain('Timeline Title')
  })

  it('should show stats when showStats is true', () => {
    wrapper = mount(BaseTimeline, {
      props: {
        items: mockItems,
        showStats: true
      }
    })

    expect(wrapper.text()).toContain('3')
    expect(wrapper.text()).toContain('elementos')
  })

  it('should not show header when showHeader is false', () => {
    wrapper = mount(BaseTimeline, {
      props: {
        items: mockItems,
        showHeader: false
      }
    })

    const header = wrapper.find('.base-timeline-header')
    expect(header.exists()).toBe(false)
  })

  it('should render loading slot when provided', () => {
    wrapper = mount(BaseTimeline, {
      props: {
        items: [],
        loading: true
      },
      slots: {
        loading: '<div>Custom Loading</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Loading')
  })

  it('should render empty slot when provided', () => {
    wrapper = mount(BaseTimeline, {
      props: {
        items: [],
        loading: false
      },
      slots: {
        empty: '<div>Custom Empty State</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Empty State')
  })

  it('should render header slot when provided', () => {
    wrapper = mount(BaseTimeline, {
      props: {
        items: mockItems
      },
      slots: {
        header: '<div>Custom Header</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Header')
  })

  it('should render item slot for each item', () => {
    wrapper = mount(BaseTimeline, {
      props: {
        items: mockItems
      },
      slots: {
        item: '<div>Custom Item: {{ item.title }}</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Item')
  })

  it('should render marker slot for each item', () => {
    wrapper = mount(BaseTimeline, {
      props: {
        items: mockItems
      },
      slots: {
        marker: '<div>Marker</div>'
      }
    })

    const markers = wrapper.findAll('.base-timeline-marker')
    expect(markers.length).toBeGreaterThan(0)
  })

  it('should render item-header slot', () => {
    wrapper = mount(BaseTimeline, {
      props: {
        items: mockItems
      },
      slots: {
        'item-header': '<div>Custom Header: {{ item.title }}</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Header')
  })

  it('should render item-body slot', () => {
    wrapper = mount(BaseTimeline, {
      props: {
        items: mockItems
      },
      slots: {
        'item-body': '<div>Custom Body: {{ item.description }}</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Body')
  })

  it('should render item-footer slot', () => {
    wrapper = mount(BaseTimeline, {
      props: {
        items: mockItems
      },
      slots: {
        'item-footer': '<div>Custom Footer</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Footer')
  })

  it('should use custom itemKey function', () => {
    const customItems = [
      { customId: 1, title: 'Event 1' },
      { customId: 2, title: 'Event 2' }
    ]

    wrapper = mount(BaseTimeline, {
      props: {
        items: customItems,
        itemKey: (item) => item.customId
      }
    })

    expect(wrapper.text()).toContain('Event 1')
    expect(wrapper.text()).toContain('Event 2')
  })

  it('should use custom getItemTitle function', () => {
    const customItems = [
      { name: 'Custom Name 1' },
      { name: 'Custom Name 2' }
    ]

    wrapper = mount(BaseTimeline, {
      props: {
        items: customItems,
        getItemTitle: (item) => item.name
      }
    })

    expect(wrapper.text()).toContain('Custom Name 1')
    expect(wrapper.text()).toContain('Custom Name 2')
  })

  it('should use custom getItemDescription function', () => {
    const customItems = [
      { descripcion: 'Descripción 1' },
      { descripcion: 'Descripción 2' }
    ]

    wrapper = mount(BaseTimeline, {
      props: {
        items: customItems,
        getItemDescription: (item) => item.descripcion
      }
    })

    expect(wrapper.text()).toContain('Descripción 1')
    expect(wrapper.text()).toContain('Descripción 2')
  })

  it('should use custom getMarkerClass function', () => {
    wrapper = mount(BaseTimeline, {
      props: {
        items: mockItems,
        getMarkerClass: () => 'custom-marker-class'
      }
    })

    const markers = wrapper.findAll('.base-timeline-marker-icon')
    expect(markers.length).toBeGreaterThan(0)
  })

  it('should use custom getMarkerIcon function', () => {
    wrapper = mount(BaseTimeline, {
      props: {
        items: mockItems,
        getMarkerIcon: () => 'fas fa-star'
      }
    })

    const markers = wrapper.findAll('.base-timeline-marker-icon')
    expect(markers.length).toBeGreaterThan(0)
  })

  it('should use default empty title', () => {
    wrapper = mount(BaseTimeline, {
      props: {
        items: [],
        loading: false
      }
    })

    expect(wrapper.text()).toContain('No hay elementos')
  })

  it('should use custom empty title', () => {
    wrapper = mount(BaseTimeline, {
      props: {
        items: [],
        loading: false,
        emptyTitle: 'Custom Empty Title'
      }
    })

    expect(wrapper.text()).toContain('Custom Empty Title')
  })

  it('should use custom empty text', () => {
    wrapper = mount(BaseTimeline, {
      props: {
        items: [],
        loading: false,
        emptyText: 'Custom empty text'
      }
    })

    expect(wrapper.text()).toContain('Custom empty text')
  })

  it('should use custom loading text', () => {
    wrapper = mount(BaseTimeline, {
      props: {
        items: [],
        loading: true,
        loadingText: 'Custom loading text'
      }
    })

    expect(wrapper.text()).toContain('Custom loading text')
  })

  it('should use custom items label', () => {
    wrapper = mount(BaseTimeline, {
      props: {
        items: mockItems,
        itemsLabel: 'eventos'
      }
    })

    expect(wrapper.text()).toContain('eventos')
  })
})


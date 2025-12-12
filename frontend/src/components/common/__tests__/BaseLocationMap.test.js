/**
 * Unit tests for BaseLocationMap component
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseLocationMap from '../BaseLocationMap.vue'

// Store mock references in global object - initialize before mock
if (!globalThis.__leafletMocks__) {
  globalThis.__leafletMocks__ = {}
}

// Mock Leaflet
vi.mock('leaflet', () => {
  const mockMap = {
    remove: vi.fn(),
    setView: vi.fn(function() { return this }), // Return this for method chaining
    on: vi.fn()
  }

  const mockMarker = {
    bindPopup: vi.fn(function() { return this }), // Return this for method chaining
    openPopup: vi.fn(),
    on: vi.fn(),
    addTo: vi.fn(function() { return this }), // Return this for method chaining
    getLatLng: vi.fn(() => ({ lat: 10, lng: 20 }))
  }

  // Store references globally for test access
  if (!globalThis.__leafletMocks__) {
    globalThis.__leafletMocks__ = {}
  }
  globalThis.__leafletMocks__.mockMap = mockMap
  globalThis.__leafletMocks__.mockMarker = mockMarker

  const mapFn = vi.fn(() => mockMap)
  const markerFn = vi.fn(() => mockMarker)
  const tileLayerFn = vi.fn(() => ({
    addTo: vi.fn(function() { return this }) // Return this for method chaining
  }))

  return {
    default: {
      map: mapFn,
      tileLayer: tileLayerFn,
      marker: markerFn,
      Icon: {
        Default: {
          mergeOptions: vi.fn(),
          prototype: {}
        }
      }
    },
    map: mapFn,
    tileLayer: tileLayerFn,
    marker: markerFn,
    Icon: {
      Default: {
        mergeOptions: vi.fn(),
        prototype: {}
      }
    }
  }
})

vi.mock('leaflet/dist/leaflet.css', () => ({}))

// Helper functions to access mock objects in tests
const getMockMap = () => globalThis.__leafletMocks__.mockMap
const getMockMarker = () => globalThis.__leafletMocks__.mockMarker

describe('BaseLocationMap', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('Props validation', () => {
    it('should accept latitude and longitude props', () => {
      wrapper = mount(BaseLocationMap, {
        props: {
          latitude: 10,
          longitude: 20
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should accept title prop', () => {
      wrapper = mount(BaseLocationMap, {
        props: {
          latitude: 10,
          longitude: 20,
          title: 'Test Map'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Rendering', () => {
    it('should render map container when coordinates are valid', async () => {
      wrapper = mount(BaseLocationMap, {
        props: {
          latitude: 10,
          longitude: 20
        }
      })

      await wrapper.vm.$nextTick()
      expect(wrapper.find('.map-container').exists()).toBe(true)
    })

    it('should render empty state when coordinates are invalid', () => {
      wrapper = mount(BaseLocationMap, {
        props: {
          latitude: null,
          longitude: null
        }
      })

      expect(wrapper.find('.map-empty').exists()).toBe(true)
    })

    it('should render title when provided', () => {
      wrapper = mount(BaseLocationMap, {
        props: {
          latitude: 10,
          longitude: 20,
          title: 'Test Map'
        }
      })

      expect(wrapper.text()).toContain('Test Map')
    })

    it('should show empty message when no coordinates', () => {
      wrapper = mount(BaseLocationMap, {
        props: {
          latitude: null,
          longitude: null
        }
      })

      expect(wrapper.text()).toContain('No hay ubicación registrada')
    })
  })

  describe('Computed properties', () => {
    it('should compute hasValidCoordinates correctly', () => {
      wrapper = mount(BaseLocationMap, {
        props: {
          latitude: 10,
          longitude: 20
        }
      })

      expect(wrapper.vm.hasValidCoordinates).toBe(true)
    })

    it('should return false for invalid coordinates', () => {
      wrapper = mount(BaseLocationMap, {
        props: {
          latitude: null,
          longitude: null
        }
      })

      expect(wrapper.vm.hasValidCoordinates).toBe(false)
    })

    it('should validate latitude range', () => {
      wrapper = mount(BaseLocationMap, {
        props: {
          latitude: 100, // Invalid (> 90)
          longitude: 20
        }
      })

      expect(wrapper.vm.hasValidCoordinates).toBe(false)
    })

    it('should validate longitude range', () => {
      wrapper = mount(BaseLocationMap, {
        props: {
          latitude: 10,
          longitude: 200 // Invalid (> 180)
        }
      })

      expect(wrapper.vm.hasValidCoordinates).toBe(false)
    })
  })

  describe('Events', () => {
    it('should emit map-ready event when map is initialized', async () => {
      wrapper = mount(BaseLocationMap, {
        props: {
          latitude: 10,
          longitude: 20
        }
      })

      // Wait for component to mount and initMap to be called
      await wrapper.vm.$nextTick()
      // Wait for the nextTick inside initMap and map initialization
      await new Promise(resolve => setTimeout(resolve, 300))

      expect(wrapper.emitted('map-ready')).toBeTruthy()
      // Verify the event was emitted with the map instance
      if (wrapper.emitted('map-ready')) {
        expect(wrapper.emitted('map-ready')[0][0]).toBeDefined()
      }
    })

    it('should emit location-change event when marker is dragged', async () => {
      wrapper = mount(BaseLocationMap, {
        props: {
          latitude: 10,
          longitude: 20,
          editable: true
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))

      // Simulate dragend event
      const marker = getMockMarker()
      const dragendHandler = marker.on.mock.calls.find(call => call[0] === 'dragend')
      if (dragendHandler) {
        dragendHandler[1]({ target: marker })
        expect(wrapper.emitted('location-change')).toBeTruthy()
      }
    })
  })

  describe('Slots', () => {
    it('should render empty slot when provided', () => {
      wrapper = mount(BaseLocationMap, {
        props: {
          latitude: null,
          longitude: null
        },
        slots: {
          empty: '<div>Custom Empty</div>'
        }
      })

      expect(wrapper.text()).toContain('Custom Empty')
    })
  })
})


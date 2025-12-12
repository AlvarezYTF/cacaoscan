import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import FarmersStatsCards from './FarmersStatsCards.vue'

vi.mock('@/components/common/BaseStatsCard.vue', () => ({
  default: {
    name: 'BaseStatsCard',
    template: '<div><slot></slot>{{ label }}: {{ value }}</div>',
    props: ['label', 'value', 'icon', 'color']
  }
}))

describe('FarmersStatsCards', () => {
  const mockFarmers = [
    { id: 1, status: 'Activo' },
    { id: 2, status: 'Activo' },
    { id: 3, status: 'Inactivo' }
  ]

  const mockFincas = [
    { id: 1, hectareas: '10.5' },
    { id: 2, hectareas: '20.3' },
    { id: 3, hectareas: '15.7' }
  ]

  it('should render stats cards', () => {
    const wrapper = mount(FarmersStatsCards, {
      props: {
        totalItems: 3,
        farmers: mockFarmers,
        allFincas: mockFincas
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should calculate total farms correctly', () => {
    const wrapper = mount(FarmersStatsCards, {
      props: {
        totalItems: 3,
        farmers: mockFarmers,
        allFincas: mockFincas
      }
    })

    expect(wrapper.vm.getTotalFarms()).toBe(3)
  })

  it('should calculate active farmers correctly', () => {
    const wrapper = mount(FarmersStatsCards, {
      props: {
        totalItems: 3,
        farmers: mockFarmers,
        allFincas: mockFincas
      }
    })

    expect(wrapper.vm.getActiveFarmers()).toBe(2)
  })

  it('should calculate total area correctly', () => {
    const wrapper = mount(FarmersStatsCards, {
      props: {
        totalItems: 3,
        farmers: mockFarmers,
        allFincas: mockFincas
      }
    })

    const totalArea = wrapper.vm.getTotalArea()
    expect(totalArea).toBe('46.5')
  })

  it('should handle empty fincas array', () => {
    const wrapper = mount(FarmersStatsCards, {
      props: {
        totalItems: 0,
        farmers: [],
        allFincas: []
      }
    })

    expect(wrapper.vm.getTotalFarms()).toBe(0)
    expect(wrapper.vm.getActiveFarmers()).toBe(0)
    expect(wrapper.vm.getTotalArea()).toBe('0.0')
  })

  it('should handle fincas with null hectareas', () => {
    const fincasWithNull = [
      { id: 1, hectareas: null },
      { id: 2, hectareas: '10.5' }
    ]

    const wrapper = mount(FarmersStatsCards, {
      props: {
        totalItems: 2,
        farmers: mockFarmers,
        allFincas: fincasWithNull
      }
    })

    const totalArea = wrapper.vm.getTotalArea()
    expect(totalArea).toBe('10.5')
  })

  it('should handle fincas with undefined hectareas', () => {
    const fincasWithUndefined = [
      { id: 1 },
      { id: 2, hectareas: '10.5' }
    ]

    const wrapper = mount(FarmersStatsCards, {
      props: {
        totalItems: 2,
        farmers: mockFarmers,
        allFincas: fincasWithUndefined
      }
    })

    const totalArea = wrapper.vm.getTotalArea()
    expect(totalArea).toBe('10.5')
  })
})


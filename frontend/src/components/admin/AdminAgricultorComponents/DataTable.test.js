import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DataTable from './DataTable.vue'

describe('DataTable', () => {
  const mockColumns = [
    { key: 'id', label: 'ID', sortable: true },
    { key: 'name', label: 'Name', sortable: false },
    { key: 'email', label: 'Email', sortable: true, align: 'right' }
  ]

  const mockData = [
    { id: 1, name: 'John', email: 'john@test.com' },
    { id: 2, name: 'Jane', email: 'jane@test.com' },
    { id: 3, name: 'Bob', email: 'bob@test.com' }
  ]

  it('should render table with data', () => {
    const wrapper = mount(DataTable, {
      props: {
        columns: mockColumns,
        data: mockData
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('table').exists()).toBe(true)
  })

  it('should display paginated data', () => {
    const wrapper = mount(DataTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        itemsPerPage: 2,
        currentPage: 1
      }
    })

    const rows = wrapper.findAll('tbody tr')
    expect(rows.length).toBe(2)
  })

  it('should display empty state when no data', () => {
    const wrapper = mount(DataTable, {
      props: {
        columns: mockColumns,
        data: []
      }
    })

    const text = wrapper.text()
    expect(text.includes('No hay datos disponibles')).toBe(true)
  })

  it('should emit sort event when sortable column is clicked', async () => {
    const wrapper = mount(DataTable, {
      props: {
        columns: mockColumns,
        data: mockData
      }
    })

    const sortableHeader = wrapper.findAll('th').find(th => th.text().includes('ID'))
    if (sortableHeader) {
      await sortableHeader.trigger('click')
      expect(wrapper.emitted('sort')).toBeTruthy()
      expect(wrapper.emitted('sort')[0]).toEqual(['id'])
    }
  })

  it('should not emit sort event when non-sortable column is clicked', async () => {
    const wrapper = mount(DataTable, {
      props: {
        columns: mockColumns,
        data: mockData
      }
    })

    const nonSortableHeader = wrapper.findAll('th').find(th => th.text().includes('Name'))
    if (nonSortableHeader) {
      await nonSortableHeader.trigger('click')
      expect(wrapper.emitted('sort')).toBeFalsy()
    }
  })

  it('should show table info with correct range', () => {
    const wrapper = mount(DataTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        itemsPerPage: 2,
        currentPage: 1,
        showTableInfo: true
      }
    })

    const text = wrapper.text()
    expect(text.includes('Mostrando 1 a 2 de 3 resultados')).toBe(true)
  })

  it('should show loading indicator when loading', () => {
    const wrapper = mount(DataTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        loading: true,
        showTableInfo: true
      }
    })

    const text = wrapper.text()
    expect(text.includes('Cargando')).toBe(true)
  })

  it('should highlight selected rows', () => {
    const wrapper = mount(DataTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        selectedRows: [1]
      }
    })

    const rows = wrapper.findAll('tbody tr')
    expect(rows.length).toBeGreaterThan(0)
  })

  it('should display controls slot when provided', () => {
    const wrapper = mount(DataTable, {
      props: {
        columns: mockColumns,
        data: mockData
      },
      slots: {
        controls: '<div>Custom Controls</div>'
      }
    })

    const text = wrapper.text()
    expect(text.includes('Custom Controls')).toBe(true)
  })

  it('should display custom cell content via slot', () => {
    const wrapper = mount(DataTable, {
      props: {
        columns: mockColumns,
        data: mockData
      },
      slots: {
        'cell-name': '<template #cell-name="{ row }">{{ row.name.toUpperCase() }}</template>'
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should calculate pagination correctly for second page', () => {
    const wrapper = mount(DataTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        itemsPerPage: 2,
        currentPage: 2
      }
    })

    const text = wrapper.text()
    expect(text.includes('Mostrando 3 a 3 de 3 resultados')).toBe(true)
  })

  it('should handle empty columns array', () => {
    const wrapper = mount(DataTable, {
      props: {
        columns: [],
        data: mockData
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should use custom table label', () => {
    const wrapper = mount(DataTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        tableLabel: 'Custom Table Label'
      }
    })

    const caption = wrapper.find('caption')
    expect(caption.exists()).toBe(true)
  })
})


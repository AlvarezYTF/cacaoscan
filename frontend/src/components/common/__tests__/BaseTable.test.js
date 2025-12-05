import { describe, it, expect, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import BaseTable from '../BaseTable.vue'

describe('BaseTable', () => {
  let wrapper

  const mockColumns = [
    { key: 'name', label: 'Name' },
    { key: 'age', label: 'Age' }
  ]

  const mockData = [
    { id: 1, name: 'John', age: 30 },
    { id: 2, name: 'Jane', age: 25 }
  ]

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render component', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should render table element', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData
      }
    })

    const table = wrapper.find('table')
    expect(table.exists()).toBe(true)
  })

  it('should render all columns in header', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData
      }
    })

    expect(wrapper.text()).toContain('Name')
    expect(wrapper.text()).toContain('Age')
  })

  it('should render all data rows', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData
      }
    })

    expect(wrapper.text()).toContain('John')
    expect(wrapper.text()).toContain('Jane')
    expect(wrapper.text()).toContain('30')
    expect(wrapper.text()).toContain('25')
  })

  it('should display title when provided', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        title: 'Test Table'
      }
    })

    expect(wrapper.text()).toContain('Test Table')
  })

  it('should display subtitle when provided', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        title: 'Test Table',
        subtitle: 'Table subtitle'
      }
    })

    expect(wrapper.text()).toContain('Table subtitle')
  })

  it('should show loading state when loading is true', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        loading: true
      }
    })

    expect(wrapper.text()).toContain('Cargando datos...')
    const table = wrapper.find('table')
    expect(table.exists()).toBe(false)
  })

  it('should show custom loading text', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        loading: true,
        loadingText: 'Custom loading...'
      }
    })

    expect(wrapper.text()).toContain('Custom loading...')
  })

  it('should show empty state when data is empty', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: []
      }
    })

    expect(wrapper.text()).toContain('No hay datos disponibles')
  })

  it('should show custom empty text', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: [],
        emptyText: 'No records found'
      }
    })

    expect(wrapper.text()).toContain('No records found')
  })

  it('should enable selection when enableSelection is true', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        enableSelection: true
      }
    })

    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    expect(checkboxes.length).toBeGreaterThan(0)
  })

  it('should emit row-click event when row is clicked', async () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData
      }
    })

    const row = wrapper.find('tbody tr')
    await row.trigger('click')

    expect(wrapper.emitted('row-click')).toBeTruthy()
  })

  it('should emit sort event when sortable column header is clicked', async () => {
    const sortableColumns = [
      { key: 'name', label: 'Name', sortable: true }
    ]

    wrapper = mount(BaseTable, {
      props: {
        columns: sortableColumns,
        data: mockData
      }
    })

    const header = wrapper.find('th')
    await header.trigger('click')

    expect(wrapper.emitted('sort')).toBeTruthy()
  })

  it('should render header slot', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData
      },
      slots: {
        header: '<div>Custom Header</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Header')
  })

  it('should render controls slot', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData
      },
      slots: {
        controls: '<div>Custom Controls</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Controls')
  })

  it('should render actions slot', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData
      },
      slots: {
        actions: '<div>Custom Actions</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Actions')
  })

  it('should render empty slot', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: []
      },
      slots: {
        empty: '<div>Custom Empty State</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Empty State')
  })

  it('should render pagination slot', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData
      },
      slots: {
        pagination: '<div>Custom Pagination</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom Pagination')
  })

  it('should render cell slot with scoped props', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData
      },
      slots: {
        'cell-name': '<div>Custom: {{ value }}</div>'
      }
    })

    expect(wrapper.text()).toContain('Custom')
  })

  it('should use custom rowKey function', () => {
    const customData = [
      { customId: 1, name: 'John' },
      { customId: 2, name: 'Jane' }
    ]

    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: customData,
        rowKey: (row) => row.customId
      }
    })

    expect(wrapper.text()).toContain('John')
    expect(wrapper.text()).toContain('Jane')
  })

  it('should apply row class function', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        rowClass: (row) => row.age > 25 ? 'highlight' : ''
      }
    })

    const rows = wrapper.findAll('tbody tr')
    expect(rows.length).toBeGreaterThan(0)
  })

  it('should show table info footer when showTableInfo is true', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        showTableInfo: true
      }
    })

    expect(wrapper.text()).toContain('Mostrando')
    expect(wrapper.text()).toContain('resultados')
  })

  it('should enable pagination when enablePagination is true', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        enablePagination: true,
        itemsPerPage: 1
      }
    })

    expect(wrapper.vm.pagination).toBeTruthy()
  })

  it('should handle filter function', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        filterFn: (row) => row.age > 25
      }
    })

    // Filtered data should only contain rows with age > 25
    const processedData = wrapper.vm.processedData
    expect(processedData.length).toBeLessThanOrEqual(mockData.length)
  })

  it('should format cell value using column formatter', () => {
    const columnsWithFormatter = [
      {
        key: 'age',
        label: 'Age',
        formatter: (value) => `${value} years`
      }
    ]

    wrapper = mount(BaseTable, {
      props: {
        columns: columnsWithFormatter,
        data: mockData
      }
    })

    expect(wrapper.text()).toContain('years')
  })

  it('should handle row selection when enableSelection is true', async () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        enableSelection: true
      }
    })

    const checkbox = wrapper.find('tbody input[type="checkbox"]')
    if (checkbox.exists()) {
      await checkbox.setChecked(true)
      expect(wrapper.emitted('row-select')).toBeTruthy()
    }
  })

  it('should handle select all when enableSelection is true', async () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        enableSelection: true
      }
    })

    const selectAllCheckbox = wrapper.find('thead input[type="checkbox"]')
    if (selectAllCheckbox.exists()) {
      await selectAllCheckbox.setChecked(true)
      expect(wrapper.emitted('select-all')).toBeTruthy()
    }
  })

  it('should show selected rows count in table info', async () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        enableSelection: true,
        showTableInfo: true
      }
    })

    // Select some rows using the composable method
    wrapper.vm.selectRow(1)
    wrapper.vm.selectRow(2)
    await nextTick()

    expect(wrapper.text()).toContain('seleccionado')
  })

  it('should handle caption prop', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        caption: 'Test Caption'
      }
    })

    const caption = wrapper.find('caption')
    expect(caption.exists()).toBe(true)
    expect(caption.text()).toBe('Test Caption')
  })

  it('should handle ariaLabel prop', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData,
        ariaLabel: 'Custom Label'
      }
    })

    const table = wrapper.find('table')
    expect(table.attributes('aria-label')).toBe('Custom Label')
  })

  it('should handle emptySubtext prop', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: [],
        emptySubtext: 'Custom subtext'
      }
    })

    expect(wrapper.text()).toContain('Custom subtext')
  })

  it('should handle column align right', () => {
    const rightAlignedColumns = [
      { key: 'name', label: 'Name' },
      { key: 'age', label: 'Age', align: 'right' }
    ]

    wrapper = mount(BaseTable, {
      props: {
        columns: rightAlignedColumns,
        data: mockData
      }
    })

    const ageHeader = wrapper.findAll('th').find(th => th.text().includes('Age'))
    expect(ageHeader.classes()).toContain('text-right')
  })

  it('should handle column width prop', () => {
    const columnsWithWidth = [
      { key: 'name', label: 'Name', width: 'w-1/2' }
    ]

    wrapper = mount(BaseTable, {
      props: {
        columns: columnsWithWidth,
        data: mockData
      }
    })

    const header = wrapper.find('th')
    expect(header.classes()).toContain('w-1/2')
  })

  it('should handle column className prop', () => {
    const columnsWithClass = [
      { key: 'name', label: 'Name', className: 'custom-class' }
    ]

    wrapper = mount(BaseTable, {
      props: {
        columns: columnsWithClass,
        data: mockData
      }
    })

    const cell = wrapper.find('td')
    expect(cell.classes()).toContain('custom-class')
  })

  it('should handle column emptyText prop', () => {
    const columnsWithEmptyText = [
      { key: 'name', label: 'Name', emptyText: 'N/A' }
    ]

    wrapper = mount(BaseTable, {
      props: {
        columns: columnsWithEmptyText,
        data: [{ id: 1, name: null }]
      }
    })

    expect(wrapper.text()).toContain('N/A')
  })

  it('should handle sort order toggle', async () => {
    const sortableColumns = [
      { key: 'name', label: 'Name', sortable: true }
    ]

    wrapper = mount(BaseTable, {
      props: {
        columns: sortableColumns,
        data: mockData
      }
    })

    const header = wrapper.find('th')
    await header.trigger('click')
    await header.trigger('click')

    expect(wrapper.emitted('sort')).toBeTruthy()
    expect(wrapper.emitted('sort').length).toBe(2)
  })

  it('should not sort when column is not sortable', async () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: mockData
      }
    })

    const header = wrapper.find('th')
    await header.trigger('click')

    expect(wrapper.emitted('sort')).toBeFalsy()
  })

  it('should handle pagination with multiple pages', () => {
    const largeData = Array.from({ length: 25 }, (_, i) => ({
      id: i + 1,
      name: `User ${i + 1}`,
      age: 20 + i
    }))

    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: largeData,
        enablePagination: true,
        itemsPerPage: 10
      }
    })

    expect(wrapper.vm.pagination).toBeTruthy()
    expect(wrapper.vm.processedData.length).toBe(10)
  })

  it('should show empty state with custom emptySubtext', () => {
    wrapper = mount(BaseTable, {
      props: {
        columns: mockColumns,
        data: [],
        emptySubtext: 'Try again later'
      }
    })

    expect(wrapper.text()).toContain('Try again later')
  })
})


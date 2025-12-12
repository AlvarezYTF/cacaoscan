/**
 * Unit tests for useTable composable
 */

import { describe, it, expect } from 'vitest'
import { useTable } from '../useTable.js'

describe('useTable', () => {
  describe('initial state', () => {
    it('should have default initial state', () => {
      const table = useTable()
      
      expect(table.sortKey.value).toBe('')
      expect(table.sortOrder.value).toBe('asc')
      expect(table.selectedRows.value).toEqual([])
      expect(table.isSelectAll.value).toBe(false)
    })

    it('should accept custom initial values', () => {
      const table = useTable({
        initialSortKey: 'name',
        initialSortOrder: 'desc',
        enableSelection: true,
        initialSelectedRows: [1, 2]
      })
      
      expect(table.sortKey.value).toBe('name')
      expect(table.sortOrder.value).toBe('desc')
      expect(table.selectedRows.value).toEqual([1, 2])
    })
  })

  describe('sorting', () => {
    it('should handle sort', () => {
      const table = useTable()
      
      table.handleSort('name')
      
      expect(table.sortKey.value).toBe('name')
      expect(table.sortOrder.value).toBe('asc')
    })

    it('should toggle sort order when same key', () => {
      const table = useTable()
      
      table.handleSort('name')
      expect(table.sortOrder.value).toBe('asc')
      
      table.handleSort('name')
      expect(table.sortOrder.value).toBe('desc')
    })

    it('should set sort directly', () => {
      const table = useTable()
      
      table.setSort('name', 'desc')
      
      expect(table.sortKey.value).toBe('name')
      expect(table.sortOrder.value).toBe('desc')
    })

    it('should clear sort', () => {
      const table = useTable()
      
      table.setSort('name', 'desc')
      table.clearSort()
      
      expect(table.sortKey.value).toBe('')
      expect(table.sortOrder.value).toBe('asc')
    })

    it('should compute isSorted correctly', () => {
      const table = useTable()
      
      expect(table.isSorted.value).toBe(false)
      
      table.setSort('name')
      expect(table.isSorted.value).toBe(true)
    })

    it('should compute sortIcon correctly', () => {
      const table = useTable()
      
      expect(table.sortIcon.value).toBe(null)
      
      table.setSort('name', 'asc')
      expect(table.sortIcon.value).toBe('up')
      
      table.setSort('name', 'desc')
      expect(table.sortIcon.value).toBe('down')
    })

    it('should get sort params', () => {
      const table = useTable()
      
      expect(table.getSortParams()).toEqual({})
      
      table.setSort('name', 'desc')
      expect(table.getSortParams()).toEqual({
        sort_by: 'name',
        sort_order: 'desc'
      })
    })
  })

  describe('selection', () => {
    it('should toggle row selection when enabled', () => {
      const table = useTable({ enableSelection: true })
      
      table.toggleRowSelection(1)
      expect(table.selectedRows.value).toContain(1)
      
      table.toggleRowSelection(1)
      expect(table.selectedRows.value).not.toContain(1)
    })

    it('should not toggle selection when disabled', () => {
      const table = useTable({ enableSelection: false })
      
      table.toggleRowSelection(1)
      expect(table.selectedRows.value).not.toContain(1)
    })

    it('should select row', () => {
      const table = useTable({ enableSelection: true })
      
      table.selectRow(1)
      expect(table.selectedRows.value).toContain(1)
      
      table.selectRow(1)
      expect(table.selectedRows.value).toHaveLength(1)
    })

    it('should deselect row', () => {
      const table = useTable({ enableSelection: true })
      
      table.selectRow(1)
      table.deselectRow(1)
      expect(table.selectedRows.value).not.toContain(1)
    })

    it('should select all rows', () => {
      const table = useTable({ enableSelection: true })
      const allRowIds = [1, 2, 3]
      
      table.selectAll(allRowIds)
      expect(table.selectedRows.value).toEqual(allRowIds)
      expect(table.isSelectAll.value).toBe(true)
    })

    it('should clear selection', () => {
      const table = useTable({ enableSelection: true })
      
      table.selectRow(1)
      table.selectRow(2)
      table.clearSelection()
      
      expect(table.selectedRows.value).toEqual([])
      expect(table.isSelectAll.value).toBe(false)
    })

    it('should check if row is selected', () => {
      const table = useTable({ enableSelection: true })
      
      table.selectRow(1)
      expect(table.isRowSelected(1)).toBe(true)
      expect(table.isRowSelected(2)).toBe(false)
    })

    it('should compute selected count', () => {
      const table = useTable({ enableSelection: true })
      
      expect(table.getSelectedCount.value).toBe(0)
      
      table.selectRow(1)
      table.selectRow(2)
      expect(table.getSelectedCount.value).toBe(2)
    })

    it('should compute hasSelection', () => {
      const table = useTable({ enableSelection: true })
      
      expect(table.hasSelection.value).toBe(false)
      
      table.selectRow(1)
      expect(table.hasSelection.value).toBe(true)
    })
  })

  describe('data processing', () => {
    it('should filter data', () => {
      const table = useTable()
      const data = [
        { id: 1, name: 'Test' },
        { id: 2, name: 'Demo' }
      ]
      
      const filtered = table.filterData(data, (item) => item.name === 'Test')
      
      expect(filtered).toHaveLength(1)
      expect(filtered[0].id).toBe(1)
    })

    it('should return original data when no filter function', () => {
      const table = useTable()
      const data = [{ id: 1 }, { id: 2 }]
      
      const result = table.filterData(data)
      
      expect(result).toEqual(data)
    })

    it('should process table data with sorting', () => {
      const table = useTable()
      const data = [
        { id: 1, name: 'Zebra' },
        { id: 2, name: 'Apple' }
      ]
      
      table.setSort('name', 'asc')
      const processed = table.processTableData(data)
      
      expect(processed[0].name).toBe('Apple')
      expect(processed[1].name).toBe('Zebra')
    })

    it('should process table data with filtering and sorting', () => {
      const table = useTable()
      const data = [
        { id: 1, name: 'Zebra', active: true },
        { id: 2, name: 'Apple', active: true },
        { id: 3, name: 'Banana', active: false }
      ]
      
      table.setSort('name', 'asc')
      const processed = table.processTableData(data, {
        filterFn: (item) => item.active
      })
      
      expect(processed).toHaveLength(2)
      expect(processed[0].name).toBe('Apple')
    })
  })

  describe('reset', () => {
    it('should reset to initial values', () => {
      const table = useTable({
        initialSortKey: 'name',
        initialSortOrder: 'asc',
        initialSelectedRows: []
      })
      
      table.setSort('age', 'desc')
      table.selectRow(1)
      table.reset()
      
      expect(table.sortKey.value).toBe('name')
      expect(table.sortOrder.value).toBe('asc')
      expect(table.selectedRows.value).toEqual([])
    })
  })
})


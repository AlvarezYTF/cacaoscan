/**
 * Unit tests for useAuditHelpers composable
 */

import { describe, it, expect } from 'vitest'
import {
  getAuditActionIcon,
  getAuditActionMarkerClass,
  getAuditItemTitle,
  getAuditItemType,
  getAuditItemStatus,
  getAuditStatusClass,
  formatJson
} from '../useAuditHelpers.js'

describe('useAuditHelpers', () => {
  describe('getAuditActionIcon', () => {
    it('should return icon for known actions', () => {
      expect(getAuditActionIcon('login')).toContain('sign-in-alt')
      expect(getAuditActionIcon('logout')).toContain('sign-out-alt')
      expect(getAuditActionIcon('create')).toContain('plus')
      expect(getAuditActionIcon('delete')).toContain('trash')
    })

    it('should return default icon for unknown action', () => {
      expect(getAuditActionIcon('unknown')).toContain('circle')
    })
  })

  describe('getAuditActionMarkerClass', () => {
    it('should return marker class for known actions', () => {
      expect(getAuditActionMarkerClass('login')).toBe('marker-login')
      expect(getAuditActionMarkerClass('create')).toBe('marker-create')
      expect(getAuditActionMarkerClass('delete')).toBe('marker-delete')
    })

    it('should return default marker for unknown action', () => {
      expect(getAuditActionMarkerClass('unknown')).toBe('marker-default')
    })
  })

  describe('getAuditItemTitle', () => {
    it('should return title for activity audit', () => {
      const item = {
        accion: 'create',
        accion_display: 'Crear',
        modelo: 'Finca'
      }
      
      const title = getAuditItemTitle(item, 'activity')
      
      expect(title).toContain('Crear')
      expect(title).toContain('Finca')
    })

    it('should return title for login audit', () => {
      const item = { success: true }
      
      const title = getAuditItemTitle(item, 'login')
      
      expect(title).toContain('Login')
    })
  })

  describe('getAuditItemType', () => {
    it('should return type label', () => {
      expect(getAuditItemType('activity')).toBe('Actividad')
      expect(getAuditItemType('login')).toBe('Login')
      expect(getAuditItemType('both')).toBe('Actividad')
    })
  })

  describe('getAuditItemStatus', () => {
    it('should return status for activity audit', () => {
      const item = {
        accion: 'create',
        accion_display: 'Crear'
      }
      
      expect(getAuditItemStatus(item, 'activity')).toBe('Crear')
    })

    it('should return status for login audit', () => {
      expect(getAuditItemStatus({ success: true }, 'login')).toBe('Exitoso')
      expect(getAuditItemStatus({ success: false }, 'login')).toBe('Fallido')
    })
  })

  describe('getAuditStatusClass', () => {
    it('should return status-success for successful login', () => {
      const item = { success: true }
      
      expect(getAuditStatusClass(item, 'login')).toBe('status-success')
    })

    it('should return status-error for failed login', () => {
      const item = { success: false }
      
      expect(getAuditStatusClass(item, 'login')).toBe('status-error')
    })

    it('should return status-default for activity audit', () => {
      const item = { accion: 'create' }
      
      expect(getAuditStatusClass(item, 'activity')).toBe('status-default')
    })
  })

  describe('formatJson', () => {
    it('should format object to JSON string', () => {
      const data = { key: 'value' }
      const result = formatJson(data)
      
      expect(result).toContain('key')
      expect(result).toContain('value')
    })

    it('should handle null', () => {
      expect(formatJson(null)).toBe('null')
    })

    it('should handle undefined', () => {
      expect(formatJson(undefined)).toBe('undefined')
    })

    it('should handle string', () => {
      expect(formatJson('test')).toBe('test')
    })
  })
})
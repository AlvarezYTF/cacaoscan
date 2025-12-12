/**
 * Unit tests for role utility functions
 * Pure functions with no external dependencies - deterministic tests
 */

import { describe, it, expect } from 'vitest'
import {
  normalizeRole,
  getRedirectPathByRole
} from '../roleUtils.js'

describe('roleUtils', () => {
  describe('normalizeRole', () => {
    it('should normalize admin role variants', () => {
      expect(normalizeRole('admin')).toBe('admin')
      expect(normalizeRole('Admin')).toBe('admin')
      expect(normalizeRole('ADMIN')).toBe('admin')
      expect(normalizeRole('administrador')).toBe('admin')
      expect(normalizeRole('Administrador')).toBe('admin')
      expect(normalizeRole('administrator')).toBe('admin')
      expect(normalizeRole('Administrator')).toBe('admin')
    })

    it('should normalize analyst role variants', () => {
      expect(normalizeRole('analyst')).toBe('analyst')
      expect(normalizeRole('Analyst')).toBe('analyst')
      expect(normalizeRole('ANALYST')).toBe('analyst')
      expect(normalizeRole('analista')).toBe('analyst')
      expect(normalizeRole('Analista')).toBe('analyst')
    })

    it('should normalize farmer role variants', () => {
      expect(normalizeRole('farmer')).toBe('farmer')
      expect(normalizeRole('Farmer')).toBe('farmer')
      expect(normalizeRole('FARMER')).toBe('farmer')
      expect(normalizeRole('agricultor')).toBe('farmer')
      expect(normalizeRole('Agricultor')).toBe('farmer')
    })

    it('should return normalized lowercase for unknown roles', () => {
      expect(normalizeRole('customRole')).toBe('customrole')
      expect(normalizeRole('Custom Role')).toBe('custom role')
    })

    it('should trim whitespace', () => {
      expect(normalizeRole('  admin  ')).toBe('admin')
      expect(normalizeRole('  farmer  ')).toBe('farmer')
    })

    it('should return null for null input', () => {
      expect(normalizeRole(null)).toBe(null)
    })

    it('should return null for undefined input', () => {
      expect(normalizeRole(undefined)).toBe(null)
    })

    it('should return null for empty string', () => {
      expect(normalizeRole('')).toBe(null)
    })

    it('should handle numeric input', () => {
      expect(normalizeRole(123)).toBe('123')
    })
  })

  describe('getRedirectPathByRole', () => {
    it('should return admin dashboard path for admin role', () => {
      expect(getRedirectPathByRole('admin')).toBe('/admin/dashboard')
      expect(getRedirectPathByRole('Admin')).toBe('/admin/dashboard')
      expect(getRedirectPathByRole('administrador')).toBe('/admin/dashboard')
      expect(getRedirectPathByRole('administrator')).toBe('/admin/dashboard')
    })

    it('should return analysis path for analyst role', () => {
      expect(getRedirectPathByRole('analyst')).toBe('/analisis')
      expect(getRedirectPathByRole('Analyst')).toBe('/analisis')
      expect(getRedirectPathByRole('analista')).toBe('/analisis')
    })

    it('should return agricultor dashboard path for farmer role', () => {
      expect(getRedirectPathByRole('farmer')).toBe('/agricultor-dashboard')
      expect(getRedirectPathByRole('Farmer')).toBe('/agricultor-dashboard')
      expect(getRedirectPathByRole('agricultor')).toBe('/agricultor-dashboard')
    })

    it('should return default admin dashboard for unknown roles', () => {
      expect(getRedirectPathByRole('unknown')).toBe('/admin/dashboard')
      expect(getRedirectPathByRole('customRole')).toBe('/admin/dashboard')
    })

    it('should return default path for null role', () => {
      expect(getRedirectPathByRole(null)).toBe('/admin/dashboard')
    })

    it('should return default path for undefined role', () => {
      expect(getRedirectPathByRole(undefined)).toBe('/admin/dashboard')
    })

    it('should return default path for empty string', () => {
      expect(getRedirectPathByRole('')).toBe('/admin/dashboard')
    })

    it('should handle role normalization and return correct path', () => {
      expect(getRedirectPathByRole('ADMINISTRADOR')).toBe('/admin/dashboard')
      expect(getRedirectPathByRole('ANALISTA')).toBe('/analisis')
      expect(getRedirectPathByRole('AGRICULTOR')).toBe('/agricultor-dashboard')
    })
  })
})


/**
 * Unit tests for form field configurations
 */

import { describe, it, expect } from 'vitest'
import {
  COMMON_FIELDS,
  FIELD_GROUPS,
  getFieldConfig,
  getFieldConfigs,
  getFieldGroup
} from '../formFieldConfigs.js'

describe('formFieldConfigs', () => {
  describe('COMMON_FIELDS', () => {
    it('should export COMMON_FIELDS object', () => {
      expect(COMMON_FIELDS).toBeDefined()
      expect(typeof COMMON_FIELDS).toBe('object')
    })

    it('should have firstName field configuration', () => {
      const field = COMMON_FIELDS.firstName
      
      expect(field).toBeDefined()
      expect(field.name).toBe('firstName')
      expect(field.label).toBe('Nombre')
      expect(field.type).toBe('text')
      expect(field.required).toBe(true)
      expect(typeof field.validator).toBe('function')
    })

    it('should have email field configuration', () => {
      const field = COMMON_FIELDS.email
      
      expect(field).toBeDefined()
      expect(field.name).toBe('email')
      expect(field.type).toBe('email')
      expect(field.required).toBe(true)
      expect(typeof field.validator).toBe('function')
    })

    it('should have password field configuration', () => {
      const field = COMMON_FIELDS.password
      
      expect(field).toBeDefined()
      expect(field.name).toBe('password')
      expect(field.type).toBe('password')
      expect(field.required).toBe(true)
    })

    it('should have confirmPassword field configuration', () => {
      const field = COMMON_FIELDS.confirmPassword
      
      expect(field).toBeDefined()
      expect(field.name).toBe('confirmPassword')
      expect(field.type).toBe('password')
      expect(field.required).toBe(true)
    })
  })

  describe('field validators', () => {
    it('should validate firstName correctly', () => {
      const field = COMMON_FIELDS.firstName
      
      expect(field.validator('')).toBeTruthy()
      expect(field.validator('John')).toBe(null)
      expect(field.validator('John123')).toBeTruthy()
    })

    it('should validate lastName correctly', () => {
      const field = COMMON_FIELDS.lastName
      
      expect(field.validator('')).toBeTruthy()
      expect(field.validator('Doe')).toBe(null)
      expect(field.validator('Doe@')).toBeTruthy()
    })

    it('should validate tipoDocumento correctly', () => {
      const field = COMMON_FIELDS.tipoDocumento
      
      expect(field.validator('')).toBeTruthy()
      expect(field.validator('CC')).toBe(null)
    })

    it('should validate numeroDocumento correctly', () => {
      const field = COMMON_FIELDS.numeroDocumento
      const isValidDocument = (val) => /^\d{6,11}$/.test(val)
      
      expect(field.validator('', isValidDocument)).toBeTruthy()
      expect(field.validator('12345', isValidDocument)).toBeTruthy()
      expect(field.validator('1234567890', isValidDocument)).toBe(null)
    })

    it('should validate email with validator function', () => {
      const field = COMMON_FIELDS.email
      // Safe email regex: limits local and domain parts to prevent ReDoS
      // Uses bounded quantifiers and specific character classes
      const isValidEmail = (val) => /^[a-zA-Z0-9._+-]{1,64}@[a-zA-Z0-9.-]{1,255}\.[a-zA-Z]{2,}$/.test(val)
      
      expect(field.validator('', isValidEmail)).toBeTruthy()
      expect(field.validator('invalid', isValidEmail)).toBeTruthy()
      expect(field.validator('test@example.com', isValidEmail)).toBe(null)
    })
  })

  describe('getFieldConfig', () => {
    it('should return field configuration by name', () => {
      const config = getFieldConfig('firstName')
      
      expect(config).toBeDefined()
      expect(config.name).toBe('firstName')
    })

    it('should return null for unknown field', () => {
      expect(getFieldConfig('unknownField')).toBe(null)
    })

    it('should return email field config', () => {
      const config = getFieldConfig('email')
      
      expect(config).toBeDefined()
      expect(config.name).toBe('email')
    })

    it('should return password field config', () => {
      const config = getFieldConfig('password')
      
      expect(config).toBeDefined()
      expect(config.name).toBe('password')
    })
  })

  describe('getFieldConfigs', () => {
    it('should return multiple field configurations', () => {
      const configs = getFieldConfigs(['firstName', 'lastName', 'email'])
      
      expect(configs.firstName).toBeDefined()
      expect(configs.lastName).toBeDefined()
      expect(configs.email).toBeDefined()
    })

    it('should skip unknown field names', () => {
      const configs = getFieldConfigs(['firstName', 'unknownField', 'email'])
      
      expect(configs.firstName).toBeDefined()
      expect(configs.email).toBeDefined()
      expect(configs.unknownField).toBeUndefined()
    })

    it('should return empty object for empty array', () => {
      const configs = getFieldConfigs([])
      
      expect(configs).toEqual({})
    })
  })

  describe('FIELD_GROUPS', () => {
    it('should export FIELD_GROUPS object', () => {
      expect(FIELD_GROUPS).toBeDefined()
      expect(typeof FIELD_GROUPS).toBe('object')
    })

    it('should have personalInfo group', () => {
      expect(FIELD_GROUPS.personalInfo).toBeDefined()
      expect(Array.isArray(FIELD_GROUPS.personalInfo)).toBe(true)
      expect(FIELD_GROUPS.personalInfo).toContain('firstName')
    })

    it('should have documentInfo group', () => {
      expect(FIELD_GROUPS.documentInfo).toBeDefined()
      expect(FIELD_GROUPS.documentInfo).toContain('tipoDocumento')
      expect(FIELD_GROUPS.documentInfo).toContain('numeroDocumento')
    })

    it('should have locationInfo group', () => {
      expect(FIELD_GROUPS.locationInfo).toBeDefined()
      expect(FIELD_GROUPS.locationInfo).toContain('departamento')
      expect(FIELD_GROUPS.locationInfo).toContain('municipio')
    })

    it('should have accountInfo group', () => {
      expect(FIELD_GROUPS.accountInfo).toBeDefined()
      expect(FIELD_GROUPS.accountInfo).toContain('email')
      expect(FIELD_GROUPS.accountInfo).toContain('password')
    })
  })

  describe('getFieldGroup', () => {
    it('should return field configurations for group', () => {
      const group = getFieldGroup('personalInfo')
      
      expect(Array.isArray(group)).toBe(true)
      expect(group.length).toBeGreaterThan(0)
      expect(group[0]).toHaveProperty('name')
    })

    it('should return empty array for unknown group', () => {
      const group = getFieldGroup('unknownGroup')
      
      expect(group).toEqual([])
    })

    it('should return all fields for personalInfo group', () => {
      const group = getFieldGroup('personalInfo')
      const fieldNames = group.map(f => f.name)
      
      expect(fieldNames).toContain('firstName')
      expect(fieldNames).toContain('lastName')
    })

    it('should return all fields for documentInfo group', () => {
      const group = getFieldGroup('documentInfo')
      const fieldNames = group.map(f => f.name)
      
      expect(fieldNames).toContain('tipoDocumento')
      expect(fieldNames).toContain('numeroDocumento')
    })
  })
})


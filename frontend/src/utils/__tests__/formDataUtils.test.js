/**
 * Unit tests for form data utility functions
 * Pure functions with minimal dependencies - deterministic tests
 */

import { describe, it, expect } from 'vitest'
import {
  createFormData,
  formDataToObject,
  serializeFormData,
  validateFormData,
  cleanFormData,
  mergeFormData,
  getFormDataDiff,
  createImageFormData
} from '../formDataUtils.js'

describe('formDataUtils', () => {
  describe('createFormData', () => {
    it('should create FormData from simple object', () => {
      const data = { name: 'Test', value: '123' }
      const formData = createFormData(data)
      
      expect(formData).toBeInstanceOf(FormData)
      expect(formData.get('name')).toBe('Test')
      expect(formData.get('value')).toBe('123')
    })

    it('should exclude null and undefined values', () => {
      const data = { name: 'Test', value: null, empty: undefined }
      const formData = createFormData(data)
      
      expect(formData.get('name')).toBe('Test')
      expect(formData.get('value')).toBeNull()
      expect(formData.has('empty')).toBe(false)
    })

    it('should handle array values', () => {
      const data = { items: ['a', 'b', 'c'] }
      const formData = createFormData(data)
      
      expect(formData.get('items[0]')).toBe('a')
      expect(formData.get('items[1]')).toBe('b')
      expect(formData.get('items[2]')).toBe('c')
    })

    it('should handle object values by stringifying', () => {
      const data = { config: { key: 'value' } }
      const formData = createFormData(data)
      
      const configValue = formData.get('config')
      expect(typeof configValue).toBe('string')
      expect(JSON.parse(configValue)).toEqual({ key: 'value' })
    })

    it('should handle File objects', () => {
      const file = new File(['content'], 'test.txt', { type: 'text/plain' })
      const data = { file }
      const formData = createFormData(data)
      
      expect(formData.get('file')).toBe(file)
    })

    it('should handle Blob objects', () => {
      const blob = new Blob(['content'], { type: 'text/plain' })
      const data = { blob }
      const formData = createFormData(data)
      
      const retrievedBlob = formData.get('blob')
      expect(retrievedBlob).toBeInstanceOf(Blob)
      expect(retrievedBlob.type).toBe(blob.type)
    })

    it('should exclude specified keys', () => {
      const data = { name: 'Test', secret: 'hidden', public: 'visible' }
      const formData = createFormData(data, { exclude: ['secret'] })
      
      expect(formData.get('name')).toBe('Test')
      expect(formData.has('secret')).toBe(false)
      expect(formData.get('public')).toBe('visible')
    })

    it('should apply transform function', () => {
      const data = { value: 'test' }
      const transform = (key, value) => value.toUpperCase()
      const formData = createFormData(data, { transform })
      
      expect(formData.get('value')).toBe('TEST')
    })
  })

  describe('formDataToObject', () => {
    it('should convert FormData to plain object', () => {
      const formData = new FormData()
      formData.append('name', 'Test')
      formData.append('value', '123')
      
      const object = formDataToObject(formData)
      
      expect(object.name).toBe('Test')
      expect(object.value).toBe('123')
    })

    it('should handle array notation', () => {
      const formData = new FormData()
      formData.append('items[0]', 'a')
      formData.append('items[1]', 'b')
      formData.append('items[2]', 'c')
      
      const object = formDataToObject(formData)
      
      expect(Array.isArray(object.items)).toBe(true)
      expect(object.items[0]).toBe('a')
      expect(object.items[1]).toBe('b')
      expect(object.items[2]).toBe('c')
    })

    it('should handle mixed keys', () => {
      const formData = new FormData()
      formData.append('name', 'Test')
      formData.append('items[0]', 'a')
      formData.append('value', '123')
      
      const object = formDataToObject(formData)
      
      expect(object.name).toBe('Test')
      expect(object.value).toBe('123')
      expect(object.items[0]).toBe('a')
    })
  })

  describe('serializeFormData', () => {
    it('should serialize simple object to URL-encoded string', () => {
      const data = { name: 'Test', value: '123' }
      const serialized = serializeFormData(data)
      
      expect(serialized).toContain('name=Test')
      expect(serialized).toContain('value=123')
    })

    it('should exclude null and undefined values', () => {
      const data = { name: 'Test', value: null, empty: undefined }
      const serialized = serializeFormData(data)
      
      expect(serialized).toContain('name=Test')
      expect(serialized).not.toContain('value=null')
      expect(serialized).not.toContain('empty')
    })

    it('should handle array values', () => {
      const data = { items: ['a', 'b', 'c'] }
      const serialized = serializeFormData(data)
      
      expect(serialized).toContain('items=a')
      expect(serialized).toContain('items=b')
      expect(serialized).toContain('items=c')
    })

    it('should stringify object values', () => {
      const data = { config: { key: 'value' } }
      const serialized = serializeFormData(data)
      
      expect(serialized).toContain('config=')
      const configPart = serialized.split('config=')[1]
      const parsed = JSON.parse(decodeURIComponent(configPart))
      expect(parsed).toEqual({ key: 'value' })
    })
  })

  describe('validateFormData', () => {
    it('should validate valid form data', () => {
      const data = { name: 'Test', age: 25 }
      const rules = {
        name: { required: true, type: 'string', minLength: 2 },
        age: { required: true, type: 'number', min: 18 }
      }
      
      const result = validateFormData(data, rules)
      
      expect(result.isValid).toBe(true)
      expect(Object.keys(result.errors).length).toBe(0)
    })

    it('should return errors for invalid data', () => {
      const data = { name: '', age: 15 }
      const rules = {
        name: { required: true },
        age: { required: true, min: 18 }
      }
      
      const result = validateFormData(data, rules)
      
      expect(result.isValid).toBe(false)
      expect(result.errors.name).toBeDefined()
      expect(result.errors.age).toBeDefined()
    })

    it('should validate required fields', () => {
      const data = {}
      const rules = {
        name: { required: true }
      }
      
      const result = validateFormData(data, rules)
      
      expect(result.isValid).toBe(false)
      expect(result.errors.name).toBeDefined()
    })

    it('should validate type', () => {
      const data = { age: 'not a number' }
      const rules = {
        age: { type: 'number' }
      }
      
      const result = validateFormData(data, rules)
      
      expect(result.isValid).toBe(false)
      expect(result.errors.age).toBeDefined()
    })

    it('should validate minLength', () => {
      const data = { name: 'A' }
      const rules = {
        name: { minLength: 3 }
      }
      
      const result = validateFormData(data, rules)
      
      expect(result.isValid).toBe(false)
      expect(result.errors.name).toBeDefined()
    })

    it('should validate maxLength', () => {
      const data = { name: 'Too Long Name' }
      const rules = {
        name: { maxLength: 5 }
      }
      
      const result = validateFormData(data, rules)
      
      expect(result.isValid).toBe(false)
      expect(result.errors.name).toBeDefined()
    })

    it('should validate min value', () => {
      const data = { age: 15 }
      const rules = {
        age: { min: 18 }
      }
      
      const result = validateFormData(data, rules)
      
      expect(result.isValid).toBe(false)
      expect(result.errors.age).toBeDefined()
    })

    it('should validate max value', () => {
      const data = { age: 150 }
      const rules = {
        age: { max: 120 }
      }
      
      const result = validateFormData(data, rules)
      
      expect(result.isValid).toBe(false)
      expect(result.errors.age).toBeDefined()
    })

    it('should validate pattern', () => {
      const data = { email: 'invalid-email' }
      const rules = {
        email: { pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ }
      }
      
      const result = validateFormData(data, rules)
      
      expect(result.isValid).toBe(false)
      expect(result.errors.email).toBeDefined()
    })

    it('should validate with custom validator', () => {
      const data = { password: 'test' }
      const rules = {
        password: {
          validator: (value) => value.length >= 8 || 'Password must be at least 8 characters'
        }
      }
      
      const result = validateFormData(data, rules)
      
      expect(result.isValid).toBe(false)
      expect(result.errors.password).toBeDefined()
    })

    it('should skip validation for optional empty fields', () => {
      const data = { name: '' }
      const rules = {
        name: { required: false, minLength: 3 }
      }
      
      const result = validateFormData(data, rules)
      
      expect(result.isValid).toBe(true)
    })
  })

  describe('cleanFormData', () => {
    it('should remove empty values by default', () => {
      const data = { name: 'Test', empty: '', nullValue: null, undefinedValue: undefined }
      const cleaned = cleanFormData(data)
      
      expect(cleaned.name).toBe('Test')
      expect(cleaned.empty).toBeUndefined()
      expect(cleaned.nullValue).toBeUndefined()
      expect(cleaned.undefinedValue).toBeUndefined()
    })

    it('should trim strings by default', () => {
      const data = { name: '  Test  ', value: '123' }
      const cleaned = cleanFormData(data)
      
      expect(cleaned.name).toBe('Test')
      expect(cleaned.value).toBe('123')
    })

    it('should not remove empty values when removeEmpty is false', () => {
      const data = { name: 'Test', empty: '' }
      const cleaned = cleanFormData(data, { removeEmpty: false })
      
      expect(cleaned.name).toBe('Test')
      expect(cleaned.empty).toBe('')
    })

    it('should not trim strings when trimStrings is false', () => {
      const data = { name: '  Test  ' }
      const cleaned = cleanFormData(data, { trimStrings: false })
      
      expect(cleaned.name).toBe('  Test  ')
    })
  })

  describe('mergeFormData', () => {
    it('should merge data with defaults', () => {
      const data = { name: 'Test' }
      const defaults = { value: 'default', type: 'text' }
      const merged = mergeFormData(data, defaults)
      
      expect(merged.name).toBe('Test')
      expect(merged.value).toBe('default')
      expect(merged.type).toBe('text')
    })

    it('should override defaults with data values', () => {
      const data = { name: 'Override', value: 'new' }
      const defaults = { name: 'Default', value: 'old' }
      const merged = mergeFormData(data, defaults)
      
      expect(merged.name).toBe('Override')
      expect(merged.value).toBe('new')
    })

    it('should handle empty data', () => {
      const data = {}
      const defaults = { value: 'default' }
      const merged = mergeFormData(data, defaults)
      
      expect(merged.value).toBe('default')
    })
  })

  describe('getFormDataDiff', () => {
    it('should detect changed values', () => {
      const original = { name: 'Original', value: '123' }
      const current = { name: 'Updated', value: '123' }
      const diff = getFormDataDiff(original, current)
      
      expect(diff.name).toBeDefined()
      expect(diff.name.old).toBe('Original')
      expect(diff.name.new).toBe('Updated')
      expect(diff.value).toBeUndefined()
    })

    it('should detect removed keys', () => {
      const original = { name: 'Test', value: '123' }
      const current = { name: 'Test' }
      const diff = getFormDataDiff(original, current)
      
      expect(diff.value).toBeDefined()
      expect(diff.value.old).toBe('123')
      expect(diff.value.new).toBeUndefined()
    })

    it('should detect added keys', () => {
      const original = { name: 'Test' }
      const current = { name: 'Test', value: '123' }
      const diff = getFormDataDiff(original, current)
      
      expect(diff.value).toBeDefined()
      expect(diff.value.old).toBeUndefined()
      expect(diff.value.new).toBe('123')
    })

    it('should return empty object for identical data', () => {
      const original = { name: 'Test', value: '123' }
      const current = { name: 'Test', value: '123' }
      const diff = getFormDataDiff(original, current)
      
      expect(Object.keys(diff).length).toBe(0)
    })
  })

  describe('createImageFormData', () => {
    it('should create FormData with image file', () => {
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      const formData = createImageFormData(file)
      
      expect(formData.get('image')).toBe(file)
    })

    it('should add metadata to FormData', () => {
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      const metadata = { title: 'Test Image', description: 'Test' }
      const formData = createImageFormData(file, metadata)
      
      expect(formData.get('image')).toBe(file)
      expect(formData.get('title')).toBe('Test Image')
      expect(formData.get('description')).toBe('Test')
    })

    it('should exclude null and empty metadata values', () => {
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      const metadata = { title: 'Test', empty: '', nullValue: null }
      const formData = createImageFormData(file, metadata)
      
      expect(formData.get('title')).toBe('Test')
      expect(formData.has('empty')).toBe(false)
      expect(formData.has('nullValue')).toBe(false)
    })

    it('should work without metadata', () => {
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      const formData = createImageFormData(file)
      
      expect(formData.get('image')).toBe(file)
    })
  })
})


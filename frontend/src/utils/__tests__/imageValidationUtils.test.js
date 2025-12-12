/**
 * Unit tests for image validation utility functions
 * Pure functions with minimal dependencies - deterministic tests
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import {
  validateImageType,
  validateImageSize,
  validateImageFile,
  getImageValidationError,
  validateImageFileObject,
  validateImageFileSingleError,
  validateImageDimensions,
  validateMultipleImages,
  formatFileSize,
  isImageFile
} from '../imageValidationUtils.js'

describe('imageValidationUtils', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('validateImageType', () => {
    it('should validate JPEG image', () => {
      const file = new File([''], 'test.jpg', { type: 'image/jpeg' })
      expect(validateImageType(file)).toBe(true)
    })

    it('should validate PNG image', () => {
      const file = new File([''], 'test.png', { type: 'image/png' })
      expect(validateImageType(file)).toBe(true)
    })

    it('should validate WebP image', () => {
      const file = new File([''], 'test.webp', { type: 'image/webp' })
      expect(validateImageType(file)).toBe(true)
    })

    it('should reject invalid image type', () => {
      const file = new File([''], 'test.pdf', { type: 'application/pdf' })
      expect(validateImageType(file)).toBe(false)
    })

    it('should return false for null file', () => {
      expect(validateImageType(null)).toBe(false)
    })

    it('should return false for undefined file', () => {
      expect(validateImageType(undefined)).toBe(false)
    })

    it('should accept custom allowed types', () => {
      const file = new File([''], 'test.gif', { type: 'image/gif' })
      expect(validateImageType(file, ['image/gif'])).toBe(true)
      expect(validateImageType(file)).toBe(false)
    })
  })

  describe('validateImageSize', () => {
    it('should validate file within size limits', () => {
      const file = new File(['x'.repeat(1024)], 'test.jpg', { type: 'image/jpeg' })
      expect(validateImageSize(file)).toBe(true)
    })

    it('should reject file too large', () => {
      const file = new File(['x'.repeat(21 * 1024 * 1024)], 'test.jpg', { type: 'image/jpeg' })
      expect(validateImageSize(file)).toBe(false)
    })

    it('should reject file too small', () => {
      const file = new File([''], 'test.jpg', { type: 'image/jpeg' })
      expect(validateImageSize(file)).toBe(false)
    })

    it('should accept custom size limits', () => {
      const file = new File(['x'.repeat(5 * 1024)], 'test.jpg', { type: 'image/jpeg' })
      expect(validateImageSize(file, 10 * 1024, 1024)).toBe(true)
    })

    it('should return false for null file', () => {
      expect(validateImageSize(null)).toBe(false)
    })

    it('should return false for undefined file', () => {
      expect(validateImageSize(undefined)).toBe(false)
    })
  })

  describe('validateImageFile', () => {
    it('should return empty array for valid image', () => {
      const file = new File(['x'.repeat(1024)], 'test.jpg', { type: 'image/jpeg' })
      const errors = validateImageFile(file)
      expect(errors).toEqual([])
    })

    it('should return error for missing file', () => {
      const errors = validateImageFile(null)
      expect(errors).toContain('Archivo requerido')
    })

    it('should return error for invalid type', () => {
      const file = new File([''], 'test.pdf', { type: 'application/pdf' })
      const errors = validateImageFile(file)
      expect(errors.length).toBeGreaterThan(0)
      expect(errors.some(e => e.includes('Formato no válido'))).toBe(true)
    })

    it('should return error for file too large', () => {
      const file = new File(['x'.repeat(21 * 1024 * 1024)], 'test.jpg', { type: 'image/jpeg' })
      const errors = validateImageFile(file)
      expect(errors.some(e => e.includes('demasiado grande'))).toBe(true)
    })

    it('should return error for file too small', () => {
      const file = new File([''], 'test.jpg', { type: 'image/jpeg' })
      const errors = validateImageFile(file)
      expect(errors.some(e => e.includes('demasiado pequeño'))).toBe(true)
    })

    it('should accept custom options', () => {
      const file = new File(['x'.repeat(1024)], 'test.gif', { type: 'image/gif' })
      const errors = validateImageFile(file, { allowedTypes: ['image/gif'] })
      expect(errors).toEqual([])
    })
  })

  describe('getImageValidationError', () => {
    it('should return null for valid image', () => {
      const file = new File(['x'.repeat(1024)], 'test.jpg', { type: 'image/jpeg' })
      expect(getImageValidationError(file)).toBe(null)
    })

    it('should return first error message', () => {
      const file = new File([''], 'test.pdf', { type: 'application/pdf' })
      const error = getImageValidationError(file)
      expect(error).toBeTruthy()
      expect(typeof error).toBe('string')
    })
  })

  describe('validateImageFileObject', () => {
    it('should return valid object for valid image', () => {
      const file = new File(['x'.repeat(1024)], 'test.jpg', { type: 'image/jpeg' })
      const result = validateImageFileObject(file)
      expect(result.isValid).toBe(true)
      expect(result.errors).toEqual([])
    })

    it('should return invalid object with errors', () => {
      const file = new File([''], 'test.pdf', { type: 'application/pdf' })
      const result = validateImageFileObject(file)
      expect(result.isValid).toBe(false)
      expect(result.errors.length).toBeGreaterThan(0)
    })
  })

  describe('validateImageFileSingleError', () => {
    it('should return valid object for valid image', () => {
      const file = new File(['x'.repeat(1024)], 'test.jpg', { type: 'image/jpeg' })
      const result = validateImageFileSingleError(file)
      expect(result.isValid).toBe(true)
      expect(result.error).toBeUndefined()
    })

    it('should return invalid object with single error', () => {
      const file = new File([''], 'test.pdf', { type: 'application/pdf' })
      const result = validateImageFileSingleError(file)
      expect(result.isValid).toBe(false)
      expect(result.error).toBeDefined()
      expect(typeof result.error).toBe('string')
    })
  })

  describe('validateImageDimensions', () => {
    let originalImage
    let originalCreateObjectURL
    let originalRevokeObjectURL

    beforeEach(() => {
      originalImage = globalThis.Image
      originalCreateObjectURL = globalThis.URL.createObjectURL
      originalRevokeObjectURL = globalThis.URL.revokeObjectURL
    })

    afterEach(() => {
      globalThis.Image = originalImage
      globalThis.URL.createObjectURL = originalCreateObjectURL
      globalThis.URL.revokeObjectURL = originalRevokeObjectURL
    })

    it('should validate image dimensions', async () => {
      const mockImage = {
        width: 100,
        height: 100,
        onload: null,
        onerror: null
      }

      globalThis.Image = vi.fn(function() {
        return mockImage
      })

      globalThis.URL.createObjectURL = vi.fn(() => 'blob:mock-url')
      globalThis.URL.revokeObjectURL = vi.fn()

      const file = new File(['test'], 'test.png', { type: 'image/png' })

      const promise = validateImageDimensions(file, {
        minWidth: 50,
        maxWidth: 200,
        minHeight: 50,
        maxHeight: 200
      })

      setTimeout(() => {
        if (mockImage.onload) {
          mockImage.onload()
        }
      }, 0)

      const result = await promise

      expect(result.isValid).toBe(true)
      expect(result.dimensions).toBeDefined()
      expect(result.dimensions.width).toBe(100)
      expect(result.dimensions.height).toBe(100)
    })

    it('should return error for missing file', async () => {
      const result = await validateImageDimensions(null)
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Archivo requerido')
    })

    it('should return error for width too small', async () => {
      const mockImage = {
        width: 50,
        height: 100,
        onload: null,
        onerror: null
      }

      globalThis.Image = vi.fn(function() {
        return mockImage
      })

      globalThis.URL.createObjectURL = vi.fn(() => 'blob:mock-url')
      globalThis.URL.revokeObjectURL = vi.fn()

      const file = new File(['test'], 'test.png', { type: 'image/png' })

      const promise = validateImageDimensions(file, {
        minWidth: 100
      })

      setTimeout(() => {
        if (mockImage.onload) {
          mockImage.onload()
        }
      }, 0)

      const result = await promise

      expect(result.isValid).toBe(false)
      expect(result.errors.some(e => e.includes('Ancho mínimo'))).toBe(true)
    })

    it('should return error for width too large', async () => {
      const mockImage = {
        width: 500,
        height: 100,
        onload: null,
        onerror: null
      }

      globalThis.Image = vi.fn(function() {
        return mockImage
      })

      globalThis.URL.createObjectURL = vi.fn(() => 'blob:mock-url')
      globalThis.URL.revokeObjectURL = vi.fn()

      const file = new File(['test'], 'test.png', { type: 'image/png' })

      const promise = validateImageDimensions(file, {
        maxWidth: 400
      })

      setTimeout(() => {
        if (mockImage.onload) {
          mockImage.onload()
        }
      }, 0)

      const result = await promise

      expect(result.isValid).toBe(false)
      expect(result.errors.some(e => e.includes('Ancho máximo'))).toBe(true)
    })
  })

  describe('validateMultipleImages', () => {
    it('should validate multiple valid images', () => {
      const files = [
        new File(['x'.repeat(1024)], 'test1.jpg', { type: 'image/jpeg' }),
        new File(['x'.repeat(2048)], 'test2.png', { type: 'image/png' })
      ]

      const result = validateMultipleImages(files)
      expect(result.isValid).toBe(true)
      expect(result.errors).toEqual([])
      expect(result.results.length).toBe(2)
      expect(result.results.every(r => r.isValid)).toBe(true)
    })

    it('should validate multiple images with some invalid', () => {
      const files = [
        new File(['x'.repeat(1024)], 'test1.jpg', { type: 'image/jpeg' }),
        new File([''], 'test2.pdf', { type: 'application/pdf' })
      ]

      const result = validateMultipleImages(files)
      expect(result.isValid).toBe(false)
      expect(result.errors.length).toBeGreaterThan(0)
      expect(result.results[0].isValid).toBe(true)
      expect(result.results[1].isValid).toBe(false)
    })

    it('should return error for non-array input', () => {
      const result = validateMultipleImages(null)
      expect(result.isValid).toBe(false)
      expect(result.errors).toContain('Se esperaba un array de archivos')
    })

    it('should handle empty array', () => {
      const result = validateMultipleImages([])
      expect(result.isValid).toBe(true)
      expect(result.results).toEqual([])
    })
  })

  describe('formatFileSize', () => {
    it('should format bytes', () => {
      expect(formatFileSize(0)).toBe('0 Bytes')
      expect(formatFileSize(512)).toContain('Bytes')
    })

    it('should format kilobytes', () => {
      expect(formatFileSize(1024)).toContain('KB')
    })

    it('should format megabytes', () => {
      expect(formatFileSize(1024 * 1024)).toContain('MB')
    })

    it('should format gigabytes', () => {
      expect(formatFileSize(1024 * 1024 * 1024)).toContain('GB')
    })

    it('should handle decimal values', () => {
      const result = formatFileSize(1536)
      // Use a safer validation approach that avoids ReDoS vulnerability
      // Validate structure and content without vulnerable regex patterns
      expect(result).toContain('KB')
      // Split and validate parts separately to avoid regex backtracking
      const parts = result.split(' ')
      expect(parts.length).toBe(2)
      expect(parts[1]).toBe('KB')
      // Validate number format without complex regex
      const numberPart = parts[0]
      expect(numberPart).toContain('.')
      const [integerPart, decimalPart] = numberPart.split('.')
      expect(integerPart.length).toBeGreaterThan(0)
      expect(integerPart.length).toBeLessThanOrEqual(10)
      expect(decimalPart.length).toBeGreaterThan(0)
      expect(decimalPart.length).toBeLessThanOrEqual(10)
      expect(Number.parseFloat(numberPart)).toBeGreaterThan(0)
      expect(Number.parseFloat(numberPart)).toBeLessThan(10)
    })
  })

  describe('isImageFile', () => {
    it('should detect JPEG by extension', () => {
      expect(isImageFile('test.jpg')).toBe(true)
      expect(isImageFile('test.JPG')).toBe(true)
      expect(isImageFile('test.jpeg')).toBe(true)
    })

    it('should detect PNG by extension', () => {
      expect(isImageFile('test.png')).toBe(true)
      expect(isImageFile('test.PNG')).toBe(true)
    })

    it('should detect other image formats', () => {
      expect(isImageFile('test.gif')).toBe(true)
      expect(isImageFile('test.webp')).toBe(true)
      expect(isImageFile('test.bmp')).toBe(true)
      expect(isImageFile('test.svg')).toBe(true)
    })

    it('should reject non-image extensions', () => {
      expect(isImageFile('test.pdf')).toBe(false)
      expect(isImageFile('test.doc')).toBe(false)
      expect(isImageFile('test.txt')).toBe(false)
    })

    it('should return false for null', () => {
      expect(isImageFile(null)).toBe(false)
    })

    it('should return false for undefined', () => {
      expect(isImageFile(undefined)).toBe(false)
    })

    it('should return false for empty string', () => {
      expect(isImageFile('')).toBe(false)
    })

    it('should handle filename with path', () => {
      expect(isImageFile('/path/to/image.jpg')).toBe(true)
      expect(isImageFile(String.raw`C:\path\to\image.png`)).toBe(true)
    })
  })
})


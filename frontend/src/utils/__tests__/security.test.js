/**
 * Unit tests for security utility functions
 * Pure functions with no external dependencies - deterministic tests
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  generateSecureId,
  sanitizeHTML,
  escapeHTML,
  isValidFilename,
  sanitizeFilename
} from '../security.js'

describe('security', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('generateSecureId', () => {
    it('should generate id with default prefix', () => {
      const id = generateSecureId()
      expect(id).toMatch(/^id-/)
      expect(typeof id).toBe('string')
    })

    it('should generate id with custom prefix', () => {
      const id = generateSecureId('test')
      expect(id).toMatch(/^test-/)
    })

    it('should generate unique ids', () => {
      const id1 = generateSecureId()
      const id2 = generateSecureId()
      expect(id1).not.toBe(id2)
    })

    it('should generate ids with correct format', () => {
      const id = generateSecureId('custom')
      expect(id).toMatch(/^custom-[\w-]+$/)
    })

    it('should generate different ids for different prefixes', () => {
      const id1 = generateSecureId('prefix1')
      const id2 = generateSecureId('prefix2')
      expect(id1).not.toBe(id2)
      expect(id1.startsWith('prefix1-')).toBe(true)
      expect(id2.startsWith('prefix2-')).toBe(true)
    })
  })

  describe('sanitizeHTML', () => {
    it('should sanitize HTML string with script tags', () => {
      const html = '<script>alert("xss")</script>Hello'
      const result = sanitizeHTML(html)
      expect(result).not.toContain('<script>')
      expect(result).not.toContain('alert')
    })

    it('should sanitize HTML string with event handlers', () => {
      const html = '<div onclick="alert(\'xss\')">Click me</div>'
      const result = sanitizeHTML(html)
      expect(result).not.toContain('onclick')
    })

    it('should return empty string for null input', () => {
      expect(sanitizeHTML(null)).toBe('')
    })

    it('should return empty string for undefined input', () => {
      expect(sanitizeHTML(undefined)).toBe('')
    })

    it('should return empty string for non-string input', () => {
      expect(sanitizeHTML(123)).toBe('')
      expect(sanitizeHTML({})).toBe('')
    })

    it('should escape HTML special characters', () => {
      const html = '<div>Hello</div>'
      const result = sanitizeHTML(html)
      expect(result).not.toContain('<div>')
    })

    it('should preserve plain text', () => {
      const text = 'Hello World'
      const result = sanitizeHTML(text)
      expect(result).toContain('Hello World')
    })
  })

  describe('escapeHTML', () => {
    it('should escape ampersand', () => {
      expect(escapeHTML('Hello & World')).toBe('Hello &amp; World')
    })

    it('should escape less than', () => {
      expect(escapeHTML('<div>')).toBe('&lt;div&gt;')
    })

    it('should escape greater than', () => {
      expect(escapeHTML('>')).toBe('&gt;')
    })

    it('should escape double quotes', () => {
      expect(escapeHTML('"Hello"')).toBe('&quot;Hello&quot;')
    })

    it('should escape single quotes', () => {
      expect(escapeHTML("'Hello'")).toBe('&#039;Hello&#039;')
    })

    it('should escape all HTML special characters', () => {
      const text = '<div class="test">Hello & World</div>'
      const result = escapeHTML(text)
      expect(result).toBe('&lt;div class=&quot;test&quot;&gt;Hello &amp; World&lt;/div&gt;')
      expect(result).not.toContain('<')
      expect(result).not.toContain('>')
      expect(result).not.toContain('"')
      // Verify that & is only present as part of HTML entities
      const unescapedAmpersands = result.match(/&(?!amp;|lt;|gt;|quot;|#039;)/g)
      expect(unescapedAmpersands).toBeNull()
    })

    it('should return empty string for null input', () => {
      expect(escapeHTML(null)).toBe('')
    })

    it('should return empty string for undefined input', () => {
      expect(escapeHTML(undefined)).toBe('')
    })

    it('should return empty string for non-string input', () => {
      expect(escapeHTML(123)).toBe('')
      expect(escapeHTML({})).toBe('')
    })

    it('should not escape safe text', () => {
      expect(escapeHTML('Hello World')).toBe('Hello World')
    })
  })

  describe('isValidFilename', () => {
    it('should validate safe filename', () => {
      expect(isValidFilename('test.txt')).toBe(true)
      expect(isValidFilename('my-file_123.pdf')).toBe(true)
      expect(isValidFilename('document (1).doc')).toBe(true)
    })

    it('should reject path traversal attempts', () => {
      expect(isValidFilename('../etc/passwd')).toBe(false)
      expect(isValidFilename(String.raw`..\windows\system32`)).toBe(false)
      expect(isValidFilename('../../secret')).toBe(false)
    })

    it('should reject paths with forward slashes', () => {
      expect(isValidFilename('path/to/file.txt')).toBe(false)
      expect(isValidFilename('/etc/passwd')).toBe(false)
    })

    it('should reject paths with backslashes', () => {
      expect(isValidFilename(String.raw`path\to\file.txt`)).toBe(false)
      expect(isValidFilename(String.raw`C:\Windows\file.txt`)).toBe(false)
    })

    it('should reject null bytes', () => {
      expect(isValidFilename(String.raw`test\0file.txt`)).toBe(false)
    })

    it('should reject dangerous characters', () => {
      expect(isValidFilename('file<name>.txt')).toBe(false)
      expect(isValidFilename('file>name.txt')).toBe(false)
      expect(isValidFilename('file:name.txt')).toBe(false)
      expect(isValidFilename('file"name.txt')).toBe(false)
      expect(isValidFilename('file|name.txt')).toBe(false)
      expect(isValidFilename('file?name.txt')).toBe(false)
      expect(isValidFilename('file*name.txt')).toBe(false)
    })

    it('should reject control characters', () => {
      expect(isValidFilename('file\x00name.txt')).toBe(false)
      expect(isValidFilename('file\x1Fname.txt')).toBe(false)
    })

    it('should reject empty filename', () => {
      expect(isValidFilename('')).toBe(false)
      expect(isValidFilename('   ')).toBe(false)
    })

    it('should return false for null input', () => {
      expect(isValidFilename(null)).toBe(false)
    })

    it('should return false for undefined input', () => {
      expect(isValidFilename(undefined)).toBe(false)
    })

    it('should return false for non-string input', () => {
      expect(isValidFilename(123)).toBe(false)
      expect(isValidFilename({})).toBe(false)
    })
  })

  describe('sanitizeFilename', () => {
    it('should sanitize safe filename', () => {
      expect(sanitizeFilename('test.txt')).toBe('test.txt')
    })

    it('should remove path components', () => {
      expect(sanitizeFilename('/path/to/file.txt')).toBe('file.txt')
      expect(sanitizeFilename(String.raw`C:\Windows\file.txt`)).toBe('file.txt')
      expect(sanitizeFilename('../etc/passwd')).toBe('passwd')
    })

    it('should replace dangerous characters with underscore', () => {
      expect(sanitizeFilename('file<name>.txt')).toBe('file_name_.txt')
      expect(sanitizeFilename('file>name.txt')).toBe('file_name.txt')
      expect(sanitizeFilename('file:name.txt')).toBe('file_name.txt')
      expect(sanitizeFilename('file|name.txt')).toBe('file_name.txt')
      expect(sanitizeFilename('file?name.txt')).toBe('file_name.txt')
      expect(sanitizeFilename('file*name.txt')).toBe('file_name.txt')
    })

    it('should remove path traversal attempts', () => {
      expect(sanitizeFilename(String.raw`..\file.txt`)).toBe('file.txt')
      expect(sanitizeFilename('../file.txt')).toBe('file.txt')
    })

    it('should replace control characters with underscore', () => {
      const result = sanitizeFilename('file\x00name.txt')
      expect(result).not.toContain('\x00')
      expect(result).toContain('_')
    })

    it('should trim whitespace', () => {
      expect(sanitizeFilename('  file.txt  ')).toBe('file.txt')
    })

    it('should use default name for empty result', () => {
      expect(sanitizeFilename('')).toBe('file')
      expect(sanitizeFilename('   ')).toBe('file')
      expect(sanitizeFilename('..')).toBe('file')
    })

    it('should limit filename length to 255 characters', () => {
      const longName = 'a'.repeat(300) + '.txt'
      const result = sanitizeFilename(longName)
      expect(result.length).toBeLessThanOrEqual(255)
      expect(result).toContain('.txt')
    })

    it('should preserve extension when truncating', () => {
      const longName = 'a'.repeat(300) + '.pdf'
      const result = sanitizeFilename(longName)
      expect(result).toMatch(/\.pdf$/)
    })

    it('should return default for null input', () => {
      expect(sanitizeFilename(null)).toBe('file')
    })

    it('should return default for undefined input', () => {
      expect(sanitizeFilename(undefined)).toBe('file')
    })

    it('should return default for non-string input', () => {
      expect(sanitizeFilename(123)).toBe('file')
      expect(sanitizeFilename({})).toBe('file')
    })
  })
})


/**
 * Unit tests for file export utility functions
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { downloadBlob, downloadFileFromResponse } from '../fileExportUtils.js'

describe('fileExportUtils', () => {
  let mockCreateObjectURL
  let mockRevokeObjectURL
  let mockAppendChild
  let mockRemove
  let mockClick

  beforeEach(() => {
    mockCreateObjectURL = vi.fn(() => 'blob:mock-url')
    mockRevokeObjectURL = vi.fn()
    mockClick = vi.fn()
    mockRemove = vi.fn()
    mockAppendChild = vi.fn()

    globalThis.URL = {
      createObjectURL: mockCreateObjectURL,
      revokeObjectURL: mockRevokeObjectURL
    }

    const mockLink = {
      href: '',
      download: '',
      click: mockClick,
      remove: mockRemove
    }

    document.createElement = vi.fn(() => mockLink)
    document.body.appendChild = mockAppendChild

    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('downloadBlob', () => {
    it('should download blob with default filename', () => {
      const blob = new Blob(['test content'])
      
      downloadBlob(blob, 'default.pdf')
      
      expect(mockCreateObjectURL).toHaveBeenCalledWith(blob)
      expect(mockAppendChild).toHaveBeenCalled()
      expect(mockClick).toHaveBeenCalled()
      expect(mockRemove).toHaveBeenCalled()
      expect(mockRevokeObjectURL).toHaveBeenCalledWith('blob:mock-url')
    })

    it('should extract filename from content-disposition header', () => {
      const blob = new Blob(['test content'])
      const headers = {
        'content-disposition': 'attachment; filename="custom-file.pdf"'
      }
      
      downloadBlob(blob, 'default.pdf', headers)
      
      expect(mockCreateObjectURL).toHaveBeenCalled()
      const linkElement = document.createElement('a')
      expect(linkElement.download).toBeDefined()
    })

    it('should use default filename when not in headers', () => {
      const blob = new Blob(['test content'])
      const headers = {}
      
      downloadBlob(blob, 'default.pdf', headers)
      
      expect(mockCreateObjectURL).toHaveBeenCalled()
      expect(mockClick).toHaveBeenCalled()
    })

    it('should handle headers without filename', () => {
      const blob = new Blob(['test content'])
      const headers = {
        'content-disposition': 'attachment'
      }
      
      downloadBlob(blob, 'default.pdf', headers)
      
      expect(mockCreateObjectURL).toHaveBeenCalled()
      expect(mockClick).toHaveBeenCalled()
    })

    it('should clean up blob URL after download', () => {
      const blob = new Blob(['test content'])
      
      downloadBlob(blob, 'test.pdf')
      
      expect(mockRevokeObjectURL).toHaveBeenCalledWith('blob:mock-url')
    })
  })

  describe('downloadFileFromResponse', () => {
    it('should download file from axios response', () => {
      const mockResponse = {
        data: new Blob(['test content']),
        headers: {
          'content-disposition': 'attachment; filename="response-file.pdf"'
        }
      }
      
      downloadFileFromResponse(mockResponse, 'default.pdf')
      
      expect(mockCreateObjectURL).toHaveBeenCalled()
      expect(mockClick).toHaveBeenCalled()
    })

    it('should use default filename when not in response headers', () => {
      const mockResponse = {
        data: new Blob(['test content']),
        headers: {}
      }
      
      downloadFileFromResponse(mockResponse, 'default.pdf')
      
      expect(mockCreateObjectURL).toHaveBeenCalled()
      expect(mockClick).toHaveBeenCalled()
    })

    it('should create blob from response data', () => {
      const mockResponse = {
        data: 'test content',
        headers: {}
      }
      
      downloadFileFromResponse(mockResponse, 'default.pdf')
      
      expect(mockCreateObjectURL).toHaveBeenCalled()
      const blobArg = mockCreateObjectURL.mock.calls[0][0]
      expect(blobArg).toBeInstanceOf(Blob)
    })
  })
})

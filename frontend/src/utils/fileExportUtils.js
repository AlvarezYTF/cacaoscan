/**
 * Utility functions for file export operations
 * Provides reusable file download functionality to eliminate code duplication
 */

/**
 * Download a blob file with automatic filename extraction from headers
 * @param {Blob} blob - Blob data to download
 * @param {string} defaultFilename - Default filename if not found in headers
 * @param {Object} headers - Response headers (optional)
 * @returns {void}
 */
export function downloadBlob(blob, defaultFilename, headers = {}) {
  const url = globalThis.URL.createObjectURL(blob)
  
  const link = document.createElement('a')
  link.href = url
  
  let filename = defaultFilename
  
  const contentDisposition = headers['content-disposition']
  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename="(.+)"/)
    if (filenameMatch) {
      filename = filenameMatch[1]
    }
  }
  
  link.download = filename
  document.body.appendChild(link)
  link.click()
  
  link.remove()
  globalThis.URL.revokeObjectURL(url)
}

/**
 * Download file from API response (blob)
 * @param {Object} response - Axios response object with blob data
 * @param {string} defaultFilename - Default filename if not found in headers
 * @returns {void}
 */
export function downloadFileFromResponse(response, defaultFilename) {
  const blob = new Blob([response.data])
  downloadBlob(blob, defaultFilename, response.headers)
}


/**
 * Utility functions for creating FormData objects
 * Provides reusable FormData creation to eliminate code duplication
 */

/**
 * Creates FormData for image upload with metadata
 * @param {File} file - Image file
 * @param {Object} metadata - Additional metadata (optional)
 * @returns {FormData} FormData prepared for upload
 */
export function createImageFormData(file, metadata = {}) {
  const formData = new FormData()
  
  // Add image file
  formData.append('image', file)
  
  // Add metadata if provided
  if (metadata.lote_id) {
    formData.append('lote_id', metadata.lote_id)
  }
  
  if (metadata.finca) {
    formData.append('finca', metadata.finca)
  }
  
  if (metadata.region) {
    formData.append('region', metadata.region)
  }
  
  if (metadata.variedad) {
    formData.append('variedad', metadata.variedad)
  }
  
  if (metadata.fecha_cosecha) {
    formData.append('fecha_cosecha', metadata.fecha_cosecha)
  }
  
  if (metadata.notas) {
    formData.append('notas', metadata.notas)
  }
  
  // Add file technical information
  formData.append('file_name', file.name)
  formData.append('file_size', file.size.toString())
  formData.append('file_type', file.type)
  
  // Timestamp for audit
  formData.append('upload_timestamp', new Date().toISOString())
  
  return formData
}

/**
 * Creates generic FormData from object data
 * @param {Object} data - Data object to convert to FormData
 * @returns {FormData} FormData with all non-null/undefined values
 */
export function createGenericFormData(data) {
  const formData = new FormData()
  
  for (const key of Object.keys(data)) {
    if (data[key] !== null && data[key] !== undefined) {
      formData.append(key, data[key])
    }
  }
  
  return formData
}

/**
 * Alias for createImageFormData for backward compatibility
 * @param {File} file - Image file
 * @param {Object} metadata - Additional metadata (optional)
 * @returns {FormData} FormData prepared for upload
 */
export const createPredictionFormData = createImageFormData


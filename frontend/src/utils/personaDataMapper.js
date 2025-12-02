/**
 * Utility functions for mapping persona API data to form data
 * Reduces duplication in EditFarmerModal and other components
 */

/**
 * Maps persona API response to persona form data
 * @param {Object} personaData - Persona data from API
 * @returns {Object} Mapped persona form data
 */
export function mapPersonaDataToForm(personaData) {
  return {
    primer_nombre: personaData.primer_nombre || '',
    segundo_nombre: personaData.segundo_nombre || '',
    primer_apellido: personaData.primer_apellido || '',
    segundo_apellido: personaData.segundo_apellido || '',
    tipo_documento: personaData.tipo_documento_info?.codigo || '',
    numero_documento: personaData.numero_documento || '',
    genero: personaData.genero_info?.codigo || '',
    fecha_nacimiento: personaData.fecha_nacimiento || '',
    telefono: personaData.telefono || '',
    direccion: personaData.direccion || '',
    departamento: personaData.departamento_info?.id || null,
    municipio: personaData.municipio_info?.id || null
  }
}

/**
 * Maps persona form data to API payload
 * @param {Object} personaForm - Persona form data
 * @returns {Object} Mapped persona API payload
 */
export function mapPersonaFormToPayload(personaForm) {
  return {
    primer_nombre: personaForm.primer_nombre,
    segundo_nombre: personaForm.segundo_nombre || '',
    primer_apellido: personaForm.primer_apellido,
    segundo_apellido: personaForm.segundo_apellido || '',
    tipo_documento: personaForm.tipo_documento,
    numero_documento: personaForm.numero_documento,
    genero: personaForm.genero,
    fecha_nacimiento: personaForm.fecha_nacimiento || null,
    telefono: personaForm.telefono,
    direccion: personaForm.direccion || '',
    departamento: personaForm.departamento || null,
    municipio: personaForm.municipio || null
  }
}

/**
 * Extracts error message with details from API error response
 * @param {Error} error - Error object from API call
 * @param {string} defaultMessage - Default error message
 * @returns {string} Formatted error message with details
 */
export function extractErrorMessageWithDetails(error, defaultMessage = 'Error inesperado') {
  if (!error?.response?.data) {
    return error?.message || defaultMessage
  }

  const data = error.response.data
  // Priority order: detail > error > message > defaultMessage
  let errorMessage
  if (data.detail) {
    errorMessage = data.detail
  } else if (data.error) {
    errorMessage = data.error
  } else if (data.message) {
    errorMessage = data.message
  } else {
    errorMessage = defaultMessage
  }

  // Add details if available
  if (data.details) {
    const details = Object.entries(data.details)
      .map(([key, value]) => `${key}: ${Array.isArray(value) ? value[0] : value}`)
      .join(', ')
    if (details) {
      errorMessage += `\n\nDetalles: ${details}`
    }
  }

  return errorMessage.replaceAll('\n', ' ')
}


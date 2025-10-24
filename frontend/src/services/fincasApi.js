/**
 * Servicio API para gestión de fincas
 * Maneja todas las operaciones CRUD relacionadas con fincas de cacao
 */

import api from './api'

/**
 * Obtener lista de fincas del usuario autenticado
 * @param {Object} params - Parámetros de filtrado y paginación
 * @returns {Promise<Object>} - Lista de fincas con metadatos
 */
export async function getFincas(params = {}) {
  try {
    const response = await api.get('/fincas/', { params })
    return response.data
  } catch (error) {
    console.error('Error obteniendo fincas:', error)
    throw error
  }
}

/**
 * Obtener detalles de una finca específica
 * @param {number} fincaId - ID de la finca
 * @returns {Promise<Object>} - Detalles de la finca
 */
export async function getFincaById(fincaId) {
  try {
    const response = await api.get(`/fincas/${fincaId}/`)
    return response.data
  } catch (error) {
    console.error(`Error obteniendo finca ${fincaId}:`, error)
    throw error
  }
}

/**
 * Crear una nueva finca
 * @param {Object} fincaData - Datos de la finca
 * @returns {Promise<Object>} - Finca creada
 */
export async function createFinca(fincaData) {
  try {
    const response = await api.post('/fincas/', fincaData)
    return response.data
  } catch (error) {
    console.error('Error creando finca:', error)
    throw error
  }
}

/**
 * Actualizar una finca existente
 * @param {number} fincaId - ID de la finca
 * @param {Object} fincaData - Datos actualizados de la finca
 * @returns {Promise<Object>} - Finca actualizada
 */
export async function updateFinca(fincaId, fincaData) {
  try {
    const response = await api.put(`/fincas/${fincaId}/update/`, fincaData)
    return response.data
  } catch (error) {
    console.error(`Error actualizando finca ${fincaId}:`, error)
    throw error
  }
}

/**
 * Eliminar una finca
 * @param {number} fincaId - ID de la finca
 * @returns {Promise<void>}
 */
export async function deleteFinca(fincaId) {
  try {
    await api.delete(`/fincas/${fincaId}/delete/`)
  } catch (error) {
    console.error(`Error eliminando finca ${fincaId}:`, error)
    throw error
  }
}

/**
 * Obtener estadísticas de una finca
 * @param {number} fincaId - ID de la finca
 * @returns {Promise<Object>} - Estadísticas de la finca
 */
export async function getFincaStats(fincaId) {
  try {
    const response = await api.get(`/fincas/${fincaId}/stats/`)
    return response.data
  } catch (error) {
    console.error(`Error obteniendo estadísticas de finca ${fincaId}:`, error)
    throw error
  }
}

/**
 * Obtener lotes de una finca específica
 * @param {number} fincaId - ID de la finca
 * @param {Object} params - Parámetros de filtrado
 * @returns {Promise<Object>} - Lista de lotes de la finca
 */
export async function getLotesByFinca(fincaId, params = {}) {
  try {
    const response = await api.get(`/fincas/${fincaId}/lotes/`, { params })
    return response.data
  } catch (error) {
    console.error(`Error obteniendo lotes de finca ${fincaId}:`, error)
    throw error
  }
}

/**
 * Validar datos de finca antes de envío
 * @param {Object} fincaData - Datos de la finca
 * @returns {Object} - Objeto con isValid y errors
 */
export function validateFincaData(fincaData) {
  const errors = []

  // Validar campos requeridos
  if (!fincaData.nombre || fincaData.nombre.trim().length === 0) {
    errors.push('El nombre de la finca es requerido')
  } else if (fincaData.nombre.length > 200) {
    errors.push('El nombre de la finca no puede exceder 200 caracteres')
  }

  if (!fincaData.ubicacion || fincaData.ubicacion.trim().length === 0) {
    errors.push('La ubicación es requerida')
  } else if (fincaData.ubicacion.length > 300) {
    errors.push('La ubicación no puede exceder 300 caracteres')
  }

  if (!fincaData.municipio || fincaData.municipio.trim().length === 0) {
    errors.push('El municipio es requerido')
  } else if (fincaData.municipio.length > 100) {
    errors.push('El municipio no puede exceder 100 caracteres')
  }

  if (!fincaData.departamento || fincaData.departamento.trim().length === 0) {
    errors.push('El departamento es requerido')
  } else if (fincaData.departamento.length > 100) {
    errors.push('El departamento no puede exceder 100 caracteres')
  }

  // Validar hectáreas
  if (!fincaData.hectareas || fincaData.hectareas <= 0) {
    errors.push('Las hectáreas deben ser un número positivo')
  } else if (fincaData.hectareas > 999999.99) {
    errors.push('Las hectáreas no pueden exceder 999,999.99')
  }

  // Validar coordenadas si se proporcionan
  if (fincaData.coordenadas_lat !== null && fincaData.coordenadas_lat !== undefined) {
    if (fincaData.coordenadas_lat < -90 || fincaData.coordenadas_lat > 90) {
      errors.push('La latitud debe estar entre -90 y 90 grados')
    }
  }

  if (fincaData.coordenadas_lng !== null && fincaData.coordenadas_lng !== undefined) {
    if (fincaData.coordenadas_lng < -180 || fincaData.coordenadas_lng > 180) {
      errors.push('La longitud debe estar entre -180 y 180 grados')
    }
  }

  // Validar descripción si se proporciona
  if (fincaData.descripcion && fincaData.descripcion.length > 1000) {
    errors.push('La descripción no puede exceder 1000 caracteres')
  }

  return {
    isValid: errors.length === 0,
    errors
  }
}

/**
 * Formatear datos de finca para envío
 * @param {Object} fincaData - Datos de la finca
 * @returns {Object} - Datos formateados
 */
export function formatFincaData(fincaData) {
  const formatted = { ...fincaData }

  // Limpiar strings
  if (formatted.nombre) {
    formatted.nombre = formatted.nombre.trim()
  }
  if (formatted.ubicacion) {
    formatted.ubicacion = formatted.ubicacion.trim()
  }
  if (formatted.municipio) {
    formatted.municipio = formatted.municipio.trim()
  }
  if (formatted.departamento) {
    formatted.departamento = formatted.departamento.trim()
  }
  if (formatted.descripcion) {
    formatted.descripcion = formatted.descripcion.trim()
  }

  // Convertir hectáreas a número
  if (formatted.hectareas) {
    formatted.hectareas = parseFloat(formatted.hectareas)
  }

  // Convertir coordenadas a número si se proporcionan
  if (formatted.coordenadas_lat !== null && formatted.coordenadas_lat !== undefined) {
    formatted.coordenadas_lat = parseFloat(formatted.coordenadas_lat)
  }
  if (formatted.coordenadas_lng !== null && formatted.coordenadas_lng !== undefined) {
    formatted.coordenadas_lng = parseFloat(formatted.coordenadas_lng)
  }

  // Establecer activa por defecto
  if (formatted.activa === undefined) {
    formatted.activa = true
  }

  return formatted
}

/**
 * Obtener opciones de departamentos colombianos
 * @returns {Array} - Lista de departamentos
 */
export function getDepartamentosColombia() {
  return [
    'Amazonas', 'Antioquia', 'Arauca', 'Atlántico', 'Bolívar', 'Boyacá',
    'Caldas', 'Caquetá', 'Casanare', 'Cauca', 'Cesar', 'Chocó', 'Córdoba',
    'Cundinamarca', 'Guainía', 'Guaviare', 'Huila', 'La Guajira', 'Magdalena',
    'Meta', 'Nariño', 'Norte de Santander', 'Putumayo', 'Quindío', 'Risaralda',
    'San Andrés y Providencia', 'Santander', 'Sucre', 'Tolima', 'Valle del Cauca',
    'Vaupés', 'Vichada'
  ]
}

/**
 * Obtener opciones de municipios por departamento
 * @param {string} departamento - Departamento seleccionado
 * @returns {Array} - Lista de municipios
 */
export function getMunicipiosByDepartamento(departamento) {
  // Lista básica de municipios por departamento
  const municipiosPorDepartamento = {
    'Antioquia': [
      'Medellín', 'Bello', 'Itagüí', 'Envigado', 'Apartadó', 'Turbo',
      'Rionegro', 'Barbosa', 'Copacabana', 'Girardota', 'La Estrella',
      'Sabaneta', 'Caldas', 'La Ceja', 'Marinilla', 'El Retiro'
    ],
    'Valle del Cauca': [
      'Cali', 'Palmira', 'Buenaventura', 'Tuluá', 'Cartago', 'Buga',
      'Yumbo', 'Ginebra', 'Guacarí', 'El Cerrito', 'Restrepo', 'Vijes'
    ],
    'Cundinamarca': [
      'Bogotá', 'Soacha', 'Girardot', 'Zipaquirá', 'Facatativá', 'Chía',
      'Madrid', 'Mosquera', 'Fusagasugá', 'Cajicá', 'Tabio', 'Tenjo'
    ],
    'Santander': [
      'Bucaramanga', 'Floridablanca', 'Girón', 'Piedecuesta', 'Barrancabermeja',
      'San Gil', 'Socorro', 'Barbosa', 'Málaga', 'Vélez', 'Puerto Wilches'
    ],
    'Tolima': [
      'Ibagué', 'Girardot', 'Espinal', 'Melgar', 'Guamo', 'Purificación',
      'Saldaña', 'Natagaima', 'Coyaima', 'Ortega', 'Chaparral'
    ],
    'Huila': [
      'Neiva', 'Pitalito', 'Garzón', 'La Plata', 'Timaná', 'Aipe',
      'Rivera', 'Palermo', 'Campoalegre', 'Gigante', 'San Agustín'
    ],
    'Cauca': [
      'Popayán', 'Santander de Quilichao', 'Puerto Tejada', 'Patía',
      'Corinto', 'Miranda', 'Caloto', 'Villa Rica', 'Silvia'
    ],
    'Nariño': [
      'Pasto', 'Tumaco', 'Ipiales', 'Túquerres', 'La Unión', 'Sandoná',
      'Consacá', 'Yacuanquer', 'Funes', 'Cumbal'
    ],
    'Meta': [
      'Villavicencio', 'Acacías', 'Granada', 'San Martín', 'El Castillo',
      'El Dorado', 'Cubarral', 'Fuente de Oro', 'Lejanías'
    ],
    'Córdoba': [
      'Montería', 'Cereté', 'Sahagún', 'Lorica', 'Montelíbano', 'Planeta Rica',
      'Tierralta', 'Ayapel', 'Buenavista', 'Ciénaga de Oro'
    ]
  }

  return municipiosPorDepartamento[departamento] || []
}

export default {
  getFincas,
  getFincaById,
  createFinca,
  updateFinca,
  deleteFinca,
  getFincaStats,
  getLotesByFinca,
  validateFincaData,
  formatFincaData,
  getDepartamentosColombia,
  getMunicipiosByDepartamento
}

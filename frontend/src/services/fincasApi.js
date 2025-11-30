/**
 * Servicio API para gestión de fincas
 * Maneja todas las operaciones CRUD relacionadas con fincas de cacao
 * Usa apiClient para reducir duplicación de código
 */

import { apiGet, apiPost, apiPut, apiDelete } from './apiClient'
import { normalizeResponse } from '@/utils/apiResponse'
import api from './api' // Mantener para getAgricultores y getFincasByAgricultor que devuelven respuesta Axios

/**
 * Obtener lista de fincas del usuario autenticado
 * @param {Object} params - Parámetros de filtrado y paginación
 * @returns {Promise<Object>} - Lista de fincas con metadatos
 */
export async function getFincas(params = {}) {
  const data = await apiGet('/fincas/', params)
  return normalizeResponse(data)
}

/**
 * Obtener detalles de una finca específica
 * @param {number} fincaId - ID de la finca
 * @returns {Promise<Object>} - Detalles de la finca
 */
export async function getFincaById(fincaId) {
  return await apiGet(`/fincas/${fincaId}/`)
}

/**
 * Crear una nueva finca
 * @param {Object} fincaData - Datos de la finca
 * @returns {Promise<Object>} - Finca creada
 */
export async function createFinca(fincaData) {
  console.log('📤 [fincasApi] Enviando datos al backend:', fincaData)
  const data = await apiPost('/fincas/', fincaData)
  console.log('✅ [fincasApi] Respuesta del backend:', data)
  return data
}

/**
 * Actualizar una finca existente
 * @param {number} fincaId - ID de la finca
 * @param {Object} fincaData - Datos actualizados de la finca
 * @returns {Promise<Object>} - Finca actualizada
 */
export async function updateFinca(fincaId, fincaData) {
  return await apiPut(`/fincas/${fincaId}/update/`, fincaData)
}

/**
 * Eliminar (desactivar) una finca (soft delete)
 * @param {number} fincaId - ID de la finca
 * @returns {Promise<void>}
 */
export async function deleteFinca(fincaId) {
  await apiDelete(`/fincas/${fincaId}/delete/`)
}

/**
 * Reactivar una finca desactivada (solo admins)
 * @param {number} fincaId - ID de la finca
 * @returns {Promise<Object>} - Finca reactivada
 */
export async function activateFinca(fincaId) {
  return await apiPost(`/fincas/${fincaId}/activate/`)
}

/**
 * Obtener estadísticas de una finca
 * @param {number} fincaId - ID de la finca
 * @returns {Promise<Object>} - Estadísticas de la finca
 */
export async function getFincaStats(fincaId) {
  return await apiGet(`/fincas/${fincaId}/stats/`)
}

/**
 * Obtener lotes de una finca específica
 * @param {number} fincaId - ID de la finca
 * @param {Object} params - Parámetros de filtrado
 * @returns {Promise<Object>} - Lista de lotes de la finca
 */
export async function getLotesByFinca(fincaId, params = {}) {
  const data = await apiGet(`/fincas/${fincaId}/lotes/`, params)
  return normalizeResponse(data)
}

// Nuevas funciones no intrusivas para la administración/agricultor
// Obtener lista de agricultores (usa endpoint existente de usuarios con role=farmer)
// Mantiene api.get para compatibilidad con código que espera respuesta Axios
export const getAgricultores = (params = {}) => {
  const query = { role: 'farmer', page_size: 100, ...params }
  return api.get('/auth/users/', { params: query })
}

// Obtener fincas filtradas por agricultor (devuelve respuesta Axios para compatibilidad)
export const getFincasByAgricultor = (id, params = {}) => {
  const query = { agricultor: id, page_size: 100, ...params }
  return api.get('/fincas/', { params: query })
}

/**
 * Validate required string field with max length
 * @param {string|undefined} value - Field value
 * @param {string} fieldName - Field name for error message
 * @param {number} maxLength - Maximum allowed length
 * @returns {string|null} - Error message or null if valid
 */
function validateRequiredString(value, fieldName, maxLength) {
  if (!value || value.trim().length === 0) {
    return `${fieldName} es requerido`
  }
  if (value.length > maxLength) {
    return `${fieldName} no puede exceder ${maxLength} caracteres`
  }
  return null
}

/**
 * Validate number range
 * @param {number|undefined} value - Number value
 * @param {string} fieldName - Field name for error message
 * @param {number} min - Minimum value (exclusive)
 * @param {number} max - Maximum value (inclusive)
 * @returns {string|null} - Error message or null if valid
 */
function validateNumberRange(value, fieldName, min, max) {
  if (!value || value <= min) {
    return `${fieldName} debe ser un número mayor que ${min}`
  }
  if (value > max) {
    return `${fieldName} no puede exceder ${max}`
  }
  return null
}

/**
 * Validate coordinate value
 * @param {number|null|undefined} value - Coordinate value
 * @param {string} coordinateName - Coordinate name for error message
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 * @returns {string|null} - Error message or null if valid
 */
function validateCoordinate(value, coordinateName, min, max) {
  if (value === null || value === undefined) {
    return null
  }
  if (value < min || value > max) {
    return `${coordinateName} debe estar entre ${min} y ${max} grados`
  }
  return null
}

/**
 * Add error to array if error message exists
 * @param {Array<string>} errors - Errors array
 * @param {string|null} error - Error message or null
 */
function addErrorIfExists(errors, error) {
  if (error) {
    errors.push(error)
  }
}

/**
 * Validar datos de finca antes de envío
 * @param {Object} fincaData - Datos de la finca
 * @returns {Object} - Objeto con isValid y errors
 */
export function validateFincaData(fincaData) {
  const errors = []

  addErrorIfExists(errors, validateRequiredString(fincaData.nombre, 'El nombre de la finca', 200))
  addErrorIfExists(errors, validateRequiredString(fincaData.ubicacion, 'La ubicación', 300))
  addErrorIfExists(errors, validateRequiredString(fincaData.municipio, 'El municipio', 100))
  addErrorIfExists(errors, validateRequiredString(fincaData.departamento, 'El departamento', 100))
  addErrorIfExists(errors, validateNumberRange(fincaData.hectareas, 'Las hectáreas', 0, 999999.99))
  addErrorIfExists(errors, validateCoordinate(fincaData.coordenadas_lat, 'La latitud', -90, 90))
  addErrorIfExists(errors, validateCoordinate(fincaData.coordenadas_lng, 'La longitud', -180, 180))

  if (fincaData.descripcion && fincaData.descripcion.length > 1000) {
    errors.push('La descripción no puede exceder 1000 caracteres')
  }

  return {
    isValid: errors.length === 0,
    errors
  }
}

/**
 * Trim string value if it exists
 * @param {string|undefined} value - String value to trim
 * @returns {string|undefined} - Trimmed string or undefined
 */
function trimString(value) {
  return value ? value.trim() : value
}

/**
 * Convert coordinate value to number or null
 * @param {string|number|null|undefined} value - Coordinate value
 * @returns {number|null} - Parsed number or null
 */
function parseCoordinate(value) {
  if (value === null || value === undefined || value === '') {
    return null
  }
  const parsed = Number.parseFloat(value)
  if (Number.isNaN(parsed)) {
    return null
  }
  return parsed
}

/**
 * Convert hectares to number if valid
 * @param {string|number|null|undefined} value - Hectares value
 * @returns {number|undefined} - Parsed number or undefined
 */
function parseHectareas(value) {
  if (value === '' || value === null || value === undefined) {
    return value
  }
  return Number.parseFloat(value)
}

/**
 * Remove fields that don't exist in the model
 * @param {Object} data - Data object
 */
function removeInvalidFields(data) {
  const invalidFields = ['id', 'created_at', 'updated_at', 'total_lotes', 'total_analisis', 'calidad_promedio']
  for (const field of invalidFields) {
    delete data[field]
  }
}

/**
 * Clean string fields in finca data
 * @param {Object} formatted - Formatted data object
 */
function cleanStringFields(formatted) {
  formatted.nombre = trimString(formatted.nombre)
  formatted.ubicacion = trimString(formatted.ubicacion)
  formatted.municipio = trimString(formatted.municipio)
  formatted.departamento = trimString(formatted.departamento)
  formatted.descripcion = trimString(formatted.descripcion)
}

/**
 * Format coordinate fields in finca data
 * @param {Object} formatted - Formatted data object
 */
function formatCoordinateFields(formatted) {
  formatted.coordenadas_lat = parseCoordinate(formatted.coordenadas_lat)
  formatted.coordenadas_lng = parseCoordinate(formatted.coordenadas_lng)
}

/**
 * Formatear datos de finca para envío
 * @param {Object} fincaData - Datos de la finca
 * @returns {Object} - Datos formateados
 */
export function formatFincaData(fincaData) {
  const formatted = { ...fincaData }

  cleanStringFields(formatted)
  formatted.hectareas = parseHectareas(formatted.hectareas)
  formatCoordinateFields(formatted)

  if (formatted.activa === undefined) {
    formatted.activa = true
  }

  removeInvalidFields(formatted)

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
  // Lista completa de municipios por departamento
  const municipiosPorDepartamento = {
    'Amazonas': [
      'Leticia', 'El Encanto', 'La Chorrera', 'La Pedrera', 'La Victoria',
      'Mirití-Paraná', 'Puerto Alegría', 'Puerto Arica', 'Puerto Nariño', 'Puerto Santander', 'Tarapacá'
    ],
    'Antioquia': [
      'Medellín', 'Bello', 'Itagüí', 'Envigado', 'Apartadó', 'Turbo',
      'Rionegro', 'Barbosa', 'Copacabana', 'Girardota', 'La Estrella',
      'Sabaneta', 'Caldas', 'La Ceja', 'Marinilla', 'El Retiro'
    ],
    'Arauca': [
      'Arauca', 'Arauquita', 'Cravo Norte', 'Fortul', 'Puerto Rondón',
      'Saravena', 'Tame'
    ],
    'Atlántico': [
      'Barranquilla', 'Soledad', 'Malambo', 'Sabanagrande', 'Puerto Colombia',
      'Galapa', 'Sabanalarga', 'Usiacurí', 'Tubará', 'Baranoa'
    ],
    'Bolívar': [
      'Cartagena', 'Magangué', 'Turbaco', 'Arjona', 'Mahates',
      'Morales', 'Norosí', 'Pinillos', 'Regidor', 'Río Viejo', 'San Pablo de Borbur'
    ],
    'Boyacá': [
      'Tunja', 'Duitama', 'Sogamoso', 'Chiquinquirá', 'Paipa',
      'Villa de Leyva', 'Monguí', 'Tópaga', 'Nobsa', 'Toca', 'Ramiriquí'
    ],
    'Caldas': [
      'Manizales', 'Pensilvania', 'Aguadas', 'Anserma', 'Aranzazu',
      'Belalcázar', 'Chinchiná', 'Filadelfia', 'La Dorada', 'La Merced'
    ],
    'Caquetá': [
      'Florencia', 'Albania', 'Belén de los Andaquíes', 'Cartagena del Chairá',
      'Curillo', 'El Doncello', 'El Paujil', 'La Montañita', 'Milán', 'Morelia'
    ],
    'Casanare': [
      'Yopal', 'Aguazul', 'Chameza', 'Hato Corozal', 'La Salina',
      'Maní', 'Monterrey', 'Nunchía', 'Orocué', 'Paz de Ariporo'
    ],
    'Cauca': [
      'Popayán', 'Santander de Quilichao', 'Puerto Tejada', 'Patía',
      'Corinto', 'Miranda', 'Caloto', 'Villa Rica', 'Silvia'
    ],
    'Cesar': [
      'Valledupar', 'Aguachica', 'Bosconia', 'Chiriguaná', 'Curumaní',
      'El Copey', 'El Paso', 'La Gloria', 'La Jagua de Ibirico', 'Manaure'
    ],
    'Chocó': [
      'Quibdó', 'Acandí', 'Alto Baudó', 'Bagadó', 'Bahía Solano',
      'Bajo Baudó', 'Bojayá', 'Cértegui', 'Condoto', 'El Cantón del San Pablo'
    ],
    'Córdoba': [
      'Montería', 'Cereté', 'Sahagún', 'Lorica', 'Montelíbano', 'Planeta Rica',
      'Tierralta', 'Ayapel', 'Buenavista', 'Ciénaga de Oro'
    ],
    'Cundinamarca': [
      'Bogotá', 'Soacha', 'Girardot', 'Zipaquirá', 'Facatativá', 'Chía',
      'Madrid', 'Mosquera', 'Fusagasugá', 'Cajicá', 'Tabio', 'Tenjo'
    ],
    'Guainía': [
      'Inírida', 'Barranco Minas', 'Mapiripana', 'San Felipe', 'Puerto Colombia',
      'La Guadalupe', 'Cacahual', 'Pana Pana', 'Morichal'
    ],
    'Guaviare': [
      'San José del Guaviare', 'Calamar', 'El Retorno', 'Miraflores'
    ],
    'Huila': [
      'Neiva', 'Pitalito', 'Garzón', 'La Plata', 'Timaná', 'Aipe',
      'Rivera', 'Palermo', 'Campoalegre', 'Gigante', 'San Agustín'
    ],
    'La Guajira': [
      'Riohacha', 'Albania', 'Barrancas', 'Dibulla', 'Distracción',
      'El Molino', 'Fonseca', 'Hatonuevo', 'La Jagua del Pilar', 'Maicao'
    ],
    'Magdalena': [
      'Santa Marta', 'Aracataca', 'Ariguaní', 'Cerro San Antonio', 'Chivolo',
      'Ciénaga', 'Concordia', 'El Banco', 'El Piñón', 'El Retén'
    ],
    'Meta': [
      'Villavicencio', 'Acacías', 'Granada', 'San Martín', 'El Castillo',
      'El Dorado', 'Cubarral', 'Fuente de Oro', 'Lejanías'
    ],
    'Nariño': [
      'Pasto', 'Tumaco', 'Ipiales', 'Túquerres', 'La Unión', 'Sandoná',
      'Consacá', 'Yacuanquer', 'Funes', 'Cumbal'
    ],
    'Norte de Santander': [
      'Cúcuta', 'Ábrego', 'Arboledas', 'Bochalema', 'Bucarasica',
      'Cáchira', 'Cácota', 'Chinácota', 'Chitagá', 'Convención'
    ],
    'Putumayo': [
      'Mocoa', 'Colón', 'Leguízamo', 'Orito', 'Puerto Asís',
      'Puerto Caicedo', 'Puerto Guzmán', 'San Francisco', 'San Miguel', 'Santiago'
    ],
    'Quindío': [
      'Armenia', 'Calarcá', 'Circasia', 'Córdoba', 'Filandia',
      'Génova', 'La Tebaida', 'Montenegro', 'Pijao', 'Quimbaya'
    ],
    'Risaralda': [
      'Pereira', 'Apía', 'Balboa', 'Belén de Umbría', 'Dosquebradas',
      'Guática', 'La Celia', 'La Virginia', 'Marsella', 'Mistrató'
    ],
    'San Andrés y Providencia': [
      'San Andrés', 'Providencia'
    ],
    'Santander': [
      'Bucaramanga', 'Floridablanca', 'Girón', 'Piedecuesta', 'Barrancabermeja',
      'San Gil', 'Socorro', 'Barbosa', 'Málaga', 'Vélez', 'Puerto Wilches'
    ],
    'Sucre': [
      'Sincelejo', 'Buenavista', 'Caimito', 'Chalán', 'Colosó',
      'Coveñas', 'El Roble', 'Galeras', 'Guaranda', 'La Unión'
    ],
    'Tolima': [
      'Ibagué', 'Girardot', 'Espinal', 'Melgar', 'Guamo', 'Purificación',
      'Saldaña', 'Natagaima', 'Coyaima', 'Ortega', 'Chaparral'
    ],
    'Valle del Cauca': [
      'Cali', 'Palmira', 'Buenaventura', 'Tuluá', 'Cartago', 'Buga',
      'Yumbo', 'Ginebra', 'Guacarí', 'El Cerrito', 'Restrepo', 'Vijes'
    ],
    'Vaupés': [
      'Mitú', 'Carurú', 'Pacoa', 'Taraira', 'Yavaraté'
    ],
    'Vichada': [
      'Puerto Carreño', 'Cumaribo', 'La Primavera', 'Santa Rosalía'
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
  activateFinca,
  getFincaStats,
  getLotesByFinca,
  validateFincaData,
  formatFincaData,
  getDepartamentosColombia,
  getMunicipiosByDepartamento
}

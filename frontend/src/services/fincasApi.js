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
    console.log('📤 [fincasApi] Enviando datos al backend:', fincaData)
    const response = await api.post('/fincas/', fincaData)
    console.log('✅ [fincasApi] Respuesta del backend:', response.data)
    return response.data
  } catch (error) {
    console.error('❌ [fincasApi] Error creando finca:', error)
    console.error('❌ [fincasApi] Error response:', error.response?.data)
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
 * Eliminar (desactivar) una finca (soft delete)
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
 * Reactivar una finca desactivada (solo admins)
 * @param {number} fincaId - ID de la finca
 * @returns {Promise<Object>} - Finca reactivada
 */
export async function activateFinca(fincaId) {
  try {
    const response = await api.post(`/fincas/${fincaId}/activate/`)
    return response.data
  } catch (error) {
    console.error(`Error reactivando finca ${fincaId}:`, error)
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
  if (formatted.hectareas !== '' && formatted.hectareas !== null && formatted.hectareas !== undefined) {
    formatted.hectareas = parseFloat(formatted.hectareas)
  }

  // Convertir coordenadas a número si se proporcionan (no vacías)
  if (formatted.coordenadas_lat !== '' && formatted.coordenadas_lat !== null && formatted.coordenadas_lat !== undefined) {
    const lat = parseFloat(formatted.coordenadas_lat)
    if (!isNaN(lat)) {
      formatted.coordenadas_lat = lat
    } else {
      formatted.coordenadas_lat = null
    }
  } else {
    formatted.coordenadas_lat = null
  }
  
  if (formatted.coordenadas_lng !== '' && formatted.coordenadas_lng !== null && formatted.coordenadas_lng !== undefined) {
    const lng = parseFloat(formatted.coordenadas_lng)
    if (!isNaN(lng)) {
      formatted.coordenadas_lng = lng
    } else {
      formatted.coordenadas_lng = null
    }
  } else {
    formatted.coordenadas_lng = null
  }

  // Establecer activa por defecto
  if (formatted.activa === undefined) {
    formatted.activa = true
  }

  // Eliminar campos que no existen en el modelo
  delete formatted.id
  delete formatted.created_at
  delete formatted.updated_at
  delete formatted.total_lotes
  delete formatted.total_analisis
  delete formatted.calidad_promedio

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

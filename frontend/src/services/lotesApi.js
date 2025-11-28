/**
 * Servicio API para gestión de lotes
 */

import api from './api'
import { normalizeResponse } from '@/utils/apiResponse'

export async function getLotes(params = {}) {
  try {
    const response = await api.get('/lotes/', { params })
    return normalizeResponse(response.data)
  } catch (error) {
    console.error('Error obteniendo lotes:', error)
    throw error
  }
}

export async function getLoteById(loteId) {
  try {
    const response = await api.get(`/lotes/${loteId}/`)
    return response.data
  } catch (error) {
    console.error(`Error obteniendo lote ${loteId}:`, error)
    throw error
  }
}

export async function createLote(loteData) {
  try {
    const response = await api.post('/lotes/', loteData)
    return response.data
  } catch (error) {
    console.error('Error creando lote:', error)
    throw error
  }
}

export async function updateLote(loteId, loteData) {
  try {
    const response = await api.put(`/lotes/${loteId}/update/`, loteData)
    return response.data
  } catch (error) {
    console.error(`Error actualizando lote ${loteId}:`, error)
    throw error
  }
}

export async function deleteLote(loteId) {
  try {
    await api.delete(`/lotes/${loteId}/delete/`)
  } catch (error) {
    console.error(`Error eliminando lote ${loteId}:`, error)
    throw error
  }
}

export async function getLoteStats(loteId) {
  try {
    const response = await api.get(`/lotes/${loteId}/stats/`)
    return response.data
  } catch (error) {
    console.error(`Error obteniendo estadísticas de lote ${loteId}:`, error)
    throw error
  }
}

export function validateLoteData(loteData) {
  const errors = []

  if (!loteData.finca || !loteData.finca.id) {
    errors.push('La finca es requerida')
  }

  if (!loteData.identificador || loteData.identificador.trim().length === 0) {
    errors.push('El identificador del lote es requerido')
  } else if (loteData.identificador.length > 50) {
    errors.push('El identificador no puede exceder 50 caracteres')
  }

  if (!loteData.variedad || loteData.variedad.trim().length === 0) {
    errors.push('La variedad es requerida')
  } else if (loteData.variedad.length > 100) {
    errors.push('La variedad no puede exceder 100 caracteres')
  }

  if (!loteData.fecha_plantacion) {
    errors.push('La fecha de plantación es requerida')
  }

  if (!loteData.area_hectareas || loteData.area_hectareas <= 0) {
    errors.push('El área en hectáreas debe ser un número positivo')
  }

  if (loteData.fecha_cosecha && loteData.fecha_plantacion) {
    if (new Date(loteData.fecha_cosecha) < new Date(loteData.fecha_plantacion)) {
      errors.push('La fecha de cosecha no puede ser anterior a la fecha de plantación')
    }
  }

  return {
    isValid: errors.length === 0,
    errors
  }
}

export function formatLoteData(loteData) {
  const formatted = { ...loteData }

  if (formatted.identificador) {
    formatted.identificador = formatted.identificador.trim()
  }
  if (formatted.variedad) {
    formatted.variedad = formatted.variedad.trim()
  }
  if (formatted.descripcion) {
    formatted.descripcion = formatted.descripcion.trim()
  }

  if (formatted.area_hectareas) {
    formatted.area_hectareas = Number.parseFloat(formatted.area_hectareas)
  }

  if (formatted.activa === undefined) {
    formatted.activa = true
  }

  return formatted
}

export function getVariedadesCacao() {
  return [
    'Criollo', 'Forastero', 'Trinitario', 'Nacional', 'CCN-51', 'ICS-1',
    'ICS-6', 'ICS-39', 'ICS-60', 'ICS-95', 'UF-613', 'UF-668', 'UF-712',
    'UF-273', 'UF-613', 'UF-668', 'UF-712', 'UF-273', 'EET-400', 'EET-96',
    'EET-103', 'EET-8', 'EET-62', 'EET-400', 'EET-96', 'EET-103', 'EET-8',
    'EET-62', 'TSH-565', 'TSH-1188', 'TSH-919', 'TSH-565', 'TSH-1188',
    'TSH-919', 'PA-150', 'PA-169', 'PA-150', 'PA-169', 'IMC-67', 'IMC-67'
  ]
}

export function getEstadosLote() {
  return [
    { value: 'activo', label: 'Activo' },
    { value: 'inactivo', label: 'Inactivo' },
    { value: 'cosechado', label: 'Cosechado' },
    { value: 'renovado', label: 'Renovado' }
  ]
}

export default {
  getLotes,
  getLoteById,
  createLote,
  updateLote,
  deleteLote,
  getLoteStats,
  validateLoteData,
  formatLoteData,
  getVariedadesCacao,
  getEstadosLote
}

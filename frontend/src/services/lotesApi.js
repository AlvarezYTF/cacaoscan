/**
 * Servicio API para gestión de lotes
 * Usa apiClient para reducir duplicación de código
 */

import { apiGet, apiPost, apiPut, apiDelete } from './apiClient'
import { normalizeResponse } from '@/utils/apiResponse'

export async function getLotes(params = {}) {
  const data = await apiGet('/lotes/', params)
  return normalizeResponse(data)
}

export async function getLoteById(loteId) {
  return await apiGet(`/lotes/${loteId}/`)
}

export async function createLote(loteData) {
  return await apiPost('/lotes/', loteData)
}

export async function updateLote(loteId, loteData) {
  return await apiPut(`/lotes/${loteId}/update/`, loteData)
}

export async function deleteLote(loteId) {
  await apiDelete(`/lotes/${loteId}/delete/`)
}

export async function getLoteStats(loteId) {
  return await apiGet(`/lotes/${loteId}/stats/`)
}

export function validateLoteData(loteData) {
  const errors = []

  // Aceptar tanto finca como número o como objeto con id
  const fincaId = loteData.finca?.id || loteData.finca
  if (!fincaId) {
    errors.push('La finca es requerida')
  }

  // Validar identificador (requerido)
  if (!loteData.identificador || (typeof loteData.identificador === 'string' && loteData.identificador.trim().length === 0)) {
    errors.push('El identificador del lote es requerido')
  } else if (typeof loteData.identificador === 'string') {
    if (loteData.identificador.trim().length < 2) {
      errors.push('El identificador debe tener al menos 2 caracteres')
    } else if (loteData.identificador.length > 50) {
      errors.push('El identificador no puede exceder 50 caracteres')
    }
  }

  // Validar variedad (requerida)
  if (!loteData.variedad || (typeof loteData.variedad === 'string' && loteData.variedad.trim().length === 0)) {
    errors.push('La variedad es requerida')
  }

  // Validar peso_kg (opcional, pero si se proporciona debe ser válido)
  if (loteData.peso_kg !== undefined && loteData.peso_kg !== null && loteData.peso_kg.toString().trim().length > 0) {
    const pesoKg = parseFloat(loteData.peso_kg)
    if (isNaN(pesoKg)) {
      errors.push('El peso debe ser un número válido')
    } else if (pesoKg <= 0) {
      errors.push('El peso debe ser mayor a 0')
    } else if (pesoKg > 100000) {
      errors.push('El peso no puede exceder 100,000 kg')
    }
  }

  // Validar fecha_recepcion (opcional, pero si se proporciona debe ser válida)
  // No es requerida en la validación básica

  // Validar fecha_procesamiento (opcional, pero si se proporciona debe ser >= fecha_recepcion)
  if (loteData.fecha_procesamiento && loteData.fecha_recepcion) {
    if (new Date(loteData.fecha_procesamiento) < new Date(loteData.fecha_recepcion)) {
      errors.push('La fecha de procesamiento no puede ser anterior a la fecha de recepción')
    }
  }

  // Validar fecha_cosecha (opcional, pero si se proporciona debe ser >= fecha_plantacion)
  if (loteData.fecha_cosecha && loteData.fecha_plantacion) {
    if (new Date(loteData.fecha_cosecha) < new Date(loteData.fecha_plantacion)) {
      errors.push('La fecha de cosecha no puede ser anterior a la fecha de plantación')
    }
  }

  // Validar area_hectareas (opcional, pero si se proporciona debe ser válido)
  if (loteData.area_hectareas !== undefined && loteData.area_hectareas !== null && loteData.area_hectareas !== '') {
    const areaHectareas = parseFloat(loteData.area_hectareas)
    if (isNaN(areaHectareas)) {
      errors.push('El área en hectáreas debe ser un número válido')
    } else if (areaHectareas <= 0) {
      errors.push('El área en hectáreas debe ser un número positivo')
    } else if (areaHectareas > 999999.99) {
      errors.push('El área en hectáreas no puede exceder 999,999.99')
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
    formatted.identificador = formatted.identificador.trim() || null
  }

  if (formatted.nombre) {
    formatted.nombre = formatted.nombre.trim()
  }

  if (formatted.descripcion) {
    formatted.descripcion = formatted.descripcion.trim() || null
  }

  // Formatear variedad: puede ser un número (ID), un objeto con id, o un string (legacy)
  if (formatted.variedad !== undefined && formatted.variedad !== null) {
    if (typeof formatted.variedad === 'object' && formatted.variedad !== null) {
      // Si es un objeto, extraer el ID
      formatted.variedad = formatted.variedad.id || formatted.variedad
    } else if (typeof formatted.variedad === 'string') {
      // Si es un string, intentar convertirlo a número primero
      const variedadNum = Number.parseInt(formatted.variedad, 10)
      if (!Number.isNaN(variedadNum)) {
        formatted.variedad = variedadNum
      } else {
        // Si no es un número válido, mantener como string (legacy)
        formatted.variedad = formatted.variedad.trim()
      }
    }
    // Si ya es un número, mantenerlo (no necesita conversión)
  }

  // Formatear estado: puede ser un número (ID), un objeto con id, o un string (legacy)
  if (formatted.estado !== undefined && formatted.estado !== null) {
    if (typeof formatted.estado === 'object' && formatted.estado !== null) {
      // Si es un objeto, extraer el ID
      formatted.estado = formatted.estado.id || formatted.estado
    } else if (typeof formatted.estado === 'string') {
      // Si es un string, intentar convertirlo a número primero
      const estadoNum = Number.parseInt(formatted.estado, 10)
      if (!Number.isNaN(estadoNum)) {
        formatted.estado = estadoNum
      } else {
        // Si no es un número válido, mantener como string (legacy)
        formatted.estado = formatted.estado.trim()
      }
    }
    // Si ya es un número, mantenerlo (no necesita conversión)
  }

  // Formatear finca: puede ser un número (ID) o un objeto con id
  if (formatted.finca !== undefined && formatted.finca !== null) {
    if (typeof formatted.finca === 'object' && formatted.finca !== null) {
      // Si es un objeto, extraer el ID
      formatted.finca = formatted.finca.id || formatted.finca
    } else if (typeof formatted.finca === 'string') {
      // Si es un string, intentar convertirlo a número
      const fincaNum = Number.parseInt(formatted.finca, 10)
      if (!Number.isNaN(fincaNum)) {
        formatted.finca = fincaNum
      }
    }
    // Si ya es un número, mantenerlo (no necesita conversión)
  }

  // Formatear peso_kg
  if (formatted.peso_kg !== undefined && formatted.peso_kg !== null) {
    formatted.peso_kg = Number.parseFloat(formatted.peso_kg)
  }

  // Formatear area_hectareas
  if (formatted.area_hectareas !== undefined && formatted.area_hectareas !== null && formatted.area_hectareas !== '') {
    formatted.area_hectareas = Number.parseFloat(formatted.area_hectareas)
  }

  // Formatear campos opcionales
  if (formatted.fecha_procesamiento === '' || formatted.fecha_procesamiento === null) {
    formatted.fecha_procesamiento = null
  }
  if (formatted.fecha_plantacion === '' || formatted.fecha_plantacion === null) {
    formatted.fecha_plantacion = null
  }
  if (formatted.fecha_cosecha === '' || formatted.fecha_cosecha === null) {
    formatted.fecha_cosecha = null
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

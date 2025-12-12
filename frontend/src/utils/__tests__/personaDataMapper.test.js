/**
 * Unit tests for persona data mapper utility functions
 */

import { describe, it, expect } from 'vitest'
import {
  mapPersonaDataToForm,
  mapPersonaFormToPayload,
  extractErrorMessageWithDetails
} from '../personaDataMapper.js'

describe('personaDataMapper', () => {
  describe('mapPersonaDataToForm', () => {
    it('should map persona data to form format', () => {
      const personaData = {
        primer_nombre: 'Juan',
        segundo_nombre: 'Carlos',
        primer_apellido: 'Pérez',
        segundo_apellido: 'González',
        tipo_documento_info: { codigo: 'CC' },
        numero_documento: '1234567890',
        genero_info: { codigo: 'M' },
        fecha_nacimiento: '1990-01-01',
        telefono: '3001234567',
        direccion: 'Calle 123',
        departamento_info: { id: 1 },
        municipio_info: { id: 2 }
      }

      const result = mapPersonaDataToForm(personaData)

      expect(result.primer_nombre).toBe('Juan')
      expect(result.segundo_nombre).toBe('Carlos')
      expect(result.primer_apellido).toBe('Pérez')
      expect(result.segundo_apellido).toBe('González')
      expect(result.tipo_documento).toBe('CC')
      expect(result.numero_documento).toBe('1234567890')
      expect(result.genero).toBe('M')
      expect(result.fecha_nacimiento).toBe('1990-01-01')
      expect(result.telefono).toBe('3001234567')
      expect(result.direccion).toBe('Calle 123')
      expect(result.departamento).toBe(1)
      expect(result.municipio).toBe(2)
    })

    it('should handle missing nested objects', () => {
      const personaData = {
        primer_nombre: 'Juan'
      }

      const result = mapPersonaDataToForm(personaData)

      expect(result.primer_nombre).toBe('Juan')
      expect(result.tipo_documento).toBe('')
      expect(result.genero).toBe('')
      expect(result.departamento).toBe(null)
      expect(result.municipio).toBe(null)
    })

    it('should use empty strings for missing values', () => {
      const personaData = {}

      const result = mapPersonaDataToForm(personaData)

      expect(result.primer_nombre).toBe('')
      expect(result.segundo_nombre).toBe('')
      expect(result.numero_documento).toBe('')
    })
  })

  describe('mapPersonaFormToPayload', () => {
    it('should map form data to API payload format', () => {
      const personaForm = {
        primer_nombre: 'Juan',
        segundo_nombre: 'Carlos',
        primer_apellido: 'Pérez',
        segundo_apellido: 'González',
        tipo_documento: 'CC',
        numero_documento: '1234567890',
        genero: 'M',
        fecha_nacimiento: '1990-01-01',
        telefono: '3001234567',
        direccion: 'Calle 123',
        departamento: 1,
        municipio: 2
      }

      const result = mapPersonaFormToPayload(personaForm)

      expect(result.primer_nombre).toBe('Juan')
      expect(result.segundo_nombre).toBe('Carlos')
      expect(result.primer_apellido).toBe('Pérez')
      expect(result.segundo_apellido).toBe('González')
      expect(result.tipo_documento).toBe('CC')
      expect(result.numero_documento).toBe('1234567890')
      expect(result.genero).toBe('M')
      expect(result.fecha_nacimiento).toBe('1990-01-01')
      expect(result.telefono).toBe('3001234567')
      expect(result.direccion).toBe('Calle 123')
      expect(result.departamento).toBe(1)
      expect(result.municipio).toBe(2)
    })

    it('should handle optional fields with defaults', () => {
      const personaForm = {
        primer_nombre: 'Juan',
        primer_apellido: 'Pérez',
        tipo_documento: 'CC',
        numero_documento: '1234567890',
        genero: 'M',
        telefono: '3001234567'
      }

      const result = mapPersonaFormToPayload(personaForm)

      expect(result.segundo_nombre).toBe('')
      expect(result.segundo_apellido).toBe('')
      expect(result.fecha_nacimiento).toBe(null)
      expect(result.direccion).toBe('')
      expect(result.departamento).toBe(null)
      expect(result.municipio).toBe(null)
    })
  })

  describe('extractErrorMessageWithDetails', () => {
    it('should extract error message from response data', () => {
      const error = {
        response: {
          data: {
            message: 'Error message'
          }
        }
      }

      const result = extractErrorMessageWithDetails(error)

      expect(result).toBe('Error message')
    })

    it('should prioritize error field over message', () => {
      const error = {
        response: {
          data: {
            error: 'Error field',
            message: 'Message field'
          }
        }
      }

      const result = extractErrorMessageWithDetails(error)

      expect(result).toBe('Error field')
    })

    it('should prioritize detail field', () => {
      const error = {
        response: {
          data: {
            detail: 'Detail message',
            error: 'Error field',
            message: 'Message field'
          }
        }
      }

      const result = extractErrorMessageWithDetails(error)

      expect(result).toBe('Detail message')
    })

    it('should include details if available', () => {
      const error = {
        response: {
          data: {
            message: 'Error message',
            details: {
              field1: 'Error 1',
              field2: ['Error 2']
            }
          }
        }
      }

      const result = extractErrorMessageWithDetails(error)

      expect(result).toContain('Error message')
      expect(result).toContain('field1')
      expect(result).toContain('Error 1')
    })

    it('should use default message when no error data', () => {
      const error = {}

      const result = extractErrorMessageWithDetails(error, 'Default error')

      expect(result).toBe('Default error')
    })

    it('should use error message when available', () => {
      const error = {
        message: 'Network error'
      }

      const result = extractErrorMessageWithDetails(error, 'Default error')

      expect(result).toBe('Network error')
    })

    it('should replace newlines with spaces', () => {
      const error = {
        response: {
          data: {
            message: 'Error\nmessage\nwith\nnewlines'
          }
        }
      }

      const result = extractErrorMessageWithDetails(error)

      expect(result).not.toContain('\n')
      expect(result).toContain('Error message with newlines')
    })
  })
})


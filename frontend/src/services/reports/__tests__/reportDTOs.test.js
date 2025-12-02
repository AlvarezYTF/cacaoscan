/**
 * Unit tests for reportDTOs
 * Tests report data normalization functions
 */

import { describe, it, expect } from 'vitest'
import {
  normalizeReportDTO,
  normalizeReportListResponse,
  normalizeReportStatsResponse,
  buildReportRequestPayload
} from '../reportDTOs.js'

describe('reportDTOs', () => {
  describe('normalizeReportDTO', () => {
    it('should normalize report DTO', () => {
      const apiReport = {
        id: 1,
        tipo_reporte: 'calidad',
        formato: 'pdf',
        estado: 'completado',
        fecha_solicitud: '2024-01-01',
        usuario: { id: 1, username: 'testuser' }
      }
      
      const normalized = normalizeReportDTO(apiReport)
      
      expect(normalized.id).toBe(1)
      expect(normalized.tipo_reporte).toBe('calidad')
      expect(normalized.formato).toBe('pdf')
      expect(normalized.usuario_id).toBe(1)
    })

    it('should return null for null input', () => {
      expect(normalizeReportDTO(null)).toBe(null)
    })

    it('should handle missing fields with defaults', () => {
      const apiReport = { id: 1 }
      
      const normalized = normalizeReportDTO(apiReport)
      
      expect(normalized.estado).toBe('pendiente')
      expect(normalized.tipo_reporte).toBe('')
    })

    it('should handle alternative field names', () => {
      const apiReport = {
        id: 1,
        fecha_inicio: '2024-01-01',
        fecha_fin: '2024-01-02',
        usuario: { nombre: 'Test User' }
      }
      
      const normalized = normalizeReportDTO(apiReport)
      
      expect(normalized.fecha_solicitud).toBe('2024-01-01')
      expect(normalized.fecha_generacion).toBe('2024-01-02')
    })
  })

  describe('normalizeReportListResponse', () => {
    it('should normalize report list response', () => {
      const apiResponse = {
        results: [
          { id: 1, tipo_reporte: 'calidad' },
          { id: 2, tipo_reporte: 'finca' }
        ],
        count: 2,
        page: 1,
        total_pages: 1
      }
      
      const normalized = normalizeReportListResponse(apiResponse)
      
      expect(normalized.reports).toHaveLength(2)
      expect(normalized.pagination.totalItems).toBe(2)
      expect(normalized.pagination.currentPage).toBe(1)
    })

    it('should handle empty response', () => {
      const normalized = normalizeReportListResponse(null)
      
      expect(normalized.reports).toEqual([])
      expect(normalized.pagination.totalItems).toBe(0)
    })
  })

  describe('normalizeReportStatsResponse', () => {
    it('should normalize report stats response', () => {
      const apiResponse = {
        total_reportes: 100,
        reportes_completados: 80,
        reportes_generando: 15,
        reportes_fallidos: 5
      }
      
      const normalized = normalizeReportStatsResponse(apiResponse)
      
      expect(normalized.totalReports).toBe(100)
      expect(normalized.completedReports).toBe(80)
      expect(normalized.inProgressReports).toBe(15)
      expect(normalized.errorReports).toBe(5)
    })

    it('should handle empty stats response', () => {
      const normalized = normalizeReportStatsResponse(null)
      
      expect(normalized.totalReports).toBe(0)
      expect(normalized.reportsByType).toEqual({})
    })
  })

  describe('buildReportRequestPayload', () => {
    it('should build report request payload', () => {
      const formData = {
        tipo_reporte: 'calidad',
        formato: 'pdf',
        titulo: 'Reporte de Calidad',
        parametros: { finca_id: 1 },
        filtros: { fecha_desde: '2024-01-01' }
      }
      
      const payload = buildReportRequestPayload(formData)
      
      expect(payload.tipo_reporte).toBe('calidad')
      expect(payload.formato).toBe('pdf')
      expect(payload.parametros).toEqual({ finca_id: 1 })
    })

    it('should handle empty form data', () => {
      const payload = buildReportRequestPayload({})
      
      expect(payload.tipo_reporte).toBe('')
      expect(payload.parametros).toEqual({})
    })
  })
})


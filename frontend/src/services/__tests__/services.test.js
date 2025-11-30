/**
 * Tests unitarios para servicios de CacaoScan Frontend.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import axios from 'axios'

// Mock de axios
vi.mock('axios')
const mockedAxios = axios

// Importar servicios
import api from '../services/api.js'
import authApi from '../services/authApi.js'
import predictionApi from '../services/predictionApi.js'
import fincasApi from '../services/fincasApi.js'
import lotesApi from '../services/lotesApi.js'
import adminApi from '../services/adminApi.js'

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('configura axios correctamente', () => {
    expect(mockedAxios.create).toHaveBeenCalled()
  })

  it('maneja respuestas exitosas', async () => {
    const mockResponse = {
      data: { success: true, message: 'Success' },
      status: 200
    }
    
    mockedAxios.get.mockResolvedValue(mockResponse)
    
    const response = await api.get('/test')
    
    expect(response).toEqual(mockResponse.data)
  })

  it('maneja errores de red', async () => {
    const mockError = {
      response: {
        status: 500,
        data: { error: 'Internal Server Error' }
      }
    }
    
    mockedAxios.get.mockRejectedValue(mockError)
    
    await expect(api.get('/test')).rejects.toThrow()
  })

  it('maneja errores de autenticación', async () => {
    const mockError = {
      response: {
        status: 401,
        data: { error: 'Unauthorized' }
      }
    }
    
    mockedAxios.get.mockRejectedValue(mockError)
    
    await expect(api.get('/test')).rejects.toThrow()
  })

  it('intercepta requests para agregar token', () => {
    // Verificar que se configuró el interceptor
    expect(mockedAxios.interceptors.request.use).toHaveBeenCalled()
  })

  it('intercepta responses para manejar errores', () => {
    // Verificar que se configuró el interceptor
    expect(mockedAxios.interceptors.response.use).toHaveBeenCalled()
  })
})

describe('Auth API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('realiza login correctamente', async () => {
    const loginData = {
      email: 'test@example.com',
      password: 'password123'
    }
    
    const mockResponse = {
      data: {
        success: true,
        access: 'access_token',
        refresh: 'refresh_token',
        user: { id: 1, email: 'test@example.com' }
      }
    }
    
    mockedAxios.post.mockResolvedValue(mockResponse)
    
    const response = await authApi.login(loginData)
    
    expect(mockedAxios.post).toHaveBeenCalledWith('/api/auth/login/', loginData)
    expect(response).toEqual(mockResponse.data)
  })

  it('maneja errores de login', async () => {
    const loginData = {
      email: 'test@example.com',
      password: 'wrongpassword'
    }
    
    const mockError = {
      response: {
        status: 401,
        data: { error: 'Invalid credentials' }
      }
    }
    
    mockedAxios.post.mockRejectedValue(mockError)
    
    await expect(authApi.login(loginData)).rejects.toThrow()
  })

  it('realiza registro correctamente', async () => {
    const registerData = {
      username: 'testuser',
      email: 'test@example.com',
      password: 'password123',
      password_confirm: 'password123'
    }
    
    const mockResponse = {
      data: {
        success: true,
        access: 'access_token',
        refresh: 'refresh_token',
        user: { id: 1, email: 'test@example.com' }
      }
    }
    
    mockedAxios.post.mockResolvedValue(mockResponse)
    
    const response = await authApi.register(registerData)
    
    expect(mockedAxios.post).toHaveBeenCalledWith('/api/auth/register/', registerData)
    expect(response).toEqual(mockResponse.data)
  })

  it('valida datos de registro', async () => {
    const invalidData = {
      username: '',
      email: 'invalid-email',
      password: 'weak',
      password_confirm: 'different'
    }
    
    const mockError = {
      response: {
        status: 400,
        data: { 
          error: 'Validation failed',
          details: {
            username: ['This field is required'],
            email: ['Enter a valid email address'],
            password: ['Password too weak'],
            password_confirm: ['Passwords do not match']
          }
        }
      }
    }
    
    mockedAxios.post.mockRejectedValue(mockError)
    
    await expect(authApi.register(invalidData)).rejects.toThrow()
  })

  it('obtiene perfil de usuario', async () => {
    const mockResponse = {
      data: {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        first_name: 'Test',
        last_name: 'User'
      }
    }
    
    mockedAxios.get.mockResolvedValue(mockResponse)
    
    const response = await authApi.getProfile()
    
    expect(mockedAxios.get).toHaveBeenCalledWith('/api/auth/profile/')
    expect(response).toEqual(mockResponse.data)
  })

  it('actualiza perfil de usuario', async () => {
    const profileData = {
      first_name: 'Updated',
      last_name: 'Name'
    }
    
    const mockResponse = {
      data: {
        success: true,
        user: { ...profileData }
      }
    }
    
    mockedAxios.put.mockResolvedValue(mockResponse)
    
    const response = await authApi.updateProfile(profileData)
    
    expect(mockedAxios.put).toHaveBeenCalledWith('/api/auth/profile/', profileData)
    expect(response).toEqual(mockResponse.data)
  })

  it('realiza logout correctamente', async () => {
    const mockResponse = {
      data: { success: true, message: 'Logged out successfully' }
    }
    
    mockedAxios.post.mockResolvedValue(mockResponse)
    
    const response = await authApi.logout()
    
    expect(mockedAxios.post).toHaveBeenCalledWith('/api/auth/logout/')
    expect(response).toEqual(mockResponse.data)
  })

  it('refresca token correctamente', async () => {
    const refreshToken = 'refresh_token'
    
    const mockResponse = {
      data: {
        access: 'new_access_token',
        refresh: 'new_refresh_token'
      }
    }
    
    mockedAxios.post.mockResolvedValue(mockResponse)
    
    const response = await authApi.refreshToken(refreshToken)
    
    expect(mockedAxios.post).toHaveBeenCalledWith('/api/auth/refresh/', {
      refresh: refreshToken
    })
    expect(response).toEqual(mockResponse.data)
  })
})

describe('Prediction API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('sube imagen correctamente', async () => {
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    const formData = new FormData()
    formData.append('file', file)
    
    const mockResponse = {
      data: {
        success: true,
        image: {
          id: 1,
          filename: 'test.jpg',
          upload_status: 'completed'
        }
      }
    }
    
    mockedAxios.post.mockResolvedValue(mockResponse)
    
    const response = await predictionApi.uploadImage(file)
    
    expect(mockedAxios.post).toHaveBeenCalledWith('/api/images/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    expect(response).toEqual(mockResponse.data)
  })

  it('analiza imagen correctamente', async () => {
    const imageId = 1
    
    const mockResponse = {
      data: {
        success: true,
        prediction: {
          id: 1,
          quality_score: 85.5,
          maturity_percentage: 75.0,
          defects_count: 2,
          analysis_status: 'completed'
        }
      }
    }
    
    mockedAxios.post.mockResolvedValue(mockResponse)
    
    const response = await predictionApi.analyzeImage(imageId)
    
    expect(mockedAxios.post).toHaveBeenCalledWith(`/api/images/${imageId}/analyze/`)
    expect(response).toEqual(mockResponse.data)
  })

  it('obtiene historial de análisis', async () => {
    const mockResponse = {
      data: {
        success: true,
        analyses: [
          {
            id: 1,
            filename: 'test1.jpg',
            quality_score: 85.5,
            created_at: '2024-01-01T10:00:00Z'
          },
          {
            id: 2,
            filename: 'test2.jpg',
            quality_score: 92.0,
            created_at: '2024-01-02T10:00:00Z'
          }
        ]
      }
    }
    
    mockedAxios.get.mockResolvedValue(mockResponse)
    
    const response = await predictionApi.getAnalysisHistory()
    
    expect(mockedAxios.get).toHaveBeenCalledWith('/api/images/')
    expect(response).toEqual(mockResponse.data)
  })

  it('obtiene estadísticas de análisis', async () => {
    const mockResponse = {
      data: {
        success: true,
        stats: {
          total_analyses: 100,
          average_quality: 85.5,
          success_rate: 95.0
        }
      }
    }
    
    mockedAxios.get.mockResolvedValue(mockResponse)
    
    const response = await predictionApi.getAnalysisStats()
    
    expect(mockedAxios.get).toHaveBeenCalledWith('/api/images/stats/')
    expect(response).toEqual(mockResponse.data)
  })

  it('obtiene detalle de análisis', async () => {
    const analysisId = 1
    
    const mockResponse = {
      data: {
        success: true,
        analysis: {
          id: 1,
          filename: 'test.jpg',
          quality_score: 85.5,
          maturity_percentage: 75.0,
          defects_count: 2,
          recommendations: ['Cosecha recomendada']
        }
      }
    }
    
    mockedAxios.get.mockResolvedValue(mockResponse)
    
    const response = await predictionApi.getAnalysisDetail(analysisId)
    
    expect(mockedAxios.get).toHaveBeenCalledWith(`/api/images/${analysisId}/`)
    expect(response).toEqual(mockResponse.data)
  })

  it('elimina análisis correctamente', async () => {
    const analysisId = 1
    
    const mockResponse = {
      data: {
        success: true,
        message: 'Analysis deleted successfully'
      }
    }
    
    mockedAxios.delete.mockResolvedValue(mockResponse)
    
    const response = await predictionApi.deleteAnalysis(analysisId)
    
    expect(mockedAxios.delete).toHaveBeenCalledWith(`/api/images/${analysisId}/delete/`)
    expect(response).toEqual(mockResponse.data)
  })
})

describe('Fincas API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('obtiene lista de fincas', async () => {
    const mockResponse = {
      data: {
        success: true,
        fincas: [
          {
            id: 1,
            nombre: 'Finca 1',
            ubicacion: 'Location 1',
            area_total: '10.5'
          },
          {
            id: 2,
            nombre: 'Finca 2',
            ubicacion: 'Location 2',
            area_total: '15.0'
          }
        ]
      }
    }
    
    mockedAxios.get.mockResolvedValue(mockResponse)
    
    const response = await fincasApi.getFincas()
    
    expect(mockedAxios.get).toHaveBeenCalledWith('/api/fincas/')
    expect(response).toEqual(mockResponse.data)
  })

  it('crea finca correctamente', async () => {
    const fincaData = {
      nombre: 'Nueva Finca',
      ubicacion: 'Nueva Ubicación',
      area_total: '20.0',
      descripcion: 'Descripción de la finca'
    }
    
    const mockResponse = {
      data: {
        success: true,
        finca: {
          id: 1,
          ...fincaData
        }
      }
    }
    
    mockedAxios.post.mockResolvedValue(mockResponse)
    
    const response = await fincasApi.createFinca(fincaData)
    
    expect(mockedAxios.post).toHaveBeenCalledWith('/api/fincas/', fincaData)
    expect(response).toEqual(mockResponse.data)
  })

  it('actualiza finca correctamente', async () => {
    const fincaId = 1
    const updateData = {
      nombre: 'Finca Actualizada',
      area_total: '25.0'
    }
    
    const mockResponse = {
      data: {
        success: true,
        finca: {
          id: fincaId,
          ...updateData
        }
      }
    }
    
    mockedAxios.put.mockResolvedValue(mockResponse)
    
    const response = await fincasApi.updateFinca(fincaId, updateData)
    
    expect(mockedAxios.put).toHaveBeenCalledWith(`/api/fincas/${fincaId}/`, updateData)
    expect(response).toEqual(mockResponse.data)
  })

  it('elimina finca correctamente', async () => {
    const fincaId = 1
    
    const mockResponse = {
      data: {
        success: true,
        message: 'Finca deleted successfully'
      }
    }
    
    mockedAxios.delete.mockResolvedValue(mockResponse)
    
    const response = await fincasApi.deleteFinca(fincaId)
    
    expect(mockedAxios.delete).toHaveBeenCalledWith(`/api/fincas/${fincaId}/`)
    expect(response).toEqual(mockResponse.data)
  })

  it('obtiene estadísticas de fincas', async () => {
    const mockResponse = {
      data: {
        success: true,
        stats: {
          total_fincas: 5,
          total_area: 100.5,
          average_area: 20.1
        }
      }
    }
    
    mockedAxios.get.mockResolvedValue(mockResponse)
    
    const response = await fincasApi.getFincaStats()
    
    expect(mockedAxios.get).toHaveBeenCalledWith('/api/fincas/stats/')
    expect(response).toEqual(mockResponse.data)
  })
})

describe('Lotes API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('obtiene lista de lotes', async () => {
    const mockResponse = {
      data: {
        success: true,
        lotes: [
          {
            id: 1,
            nombre: 'Lote 1',
            area: '5.0',
            variedad: 'CCN-51'
          },
          {
            id: 2,
            nombre: 'Lote 2',
            area: '8.0',
            variedad: 'Nacional'
          }
        ]
      }
    }
    
    mockedAxios.get.mockResolvedValue(mockResponse)
    
    const response = await lotesApi.getLotes()
    
    expect(mockedAxios.get).toHaveBeenCalledWith('/api/lotes/')
    expect(response).toEqual(mockResponse.data)
  })

  it('obtiene lotes por finca', async () => {
    const fincaId = 1
    
    const mockResponse = {
      data: {
        success: true,
        lotes: [
          {
            id: 1,
            nombre: 'Lote 1',
            area: '5.0',
            variedad: 'CCN-51',
            finca: fincaId
          }
        ]
      }
    }
    
    mockedAxios.get.mockResolvedValue(mockResponse)
    
    const response = await lotesApi.getLotesByFinca(fincaId)
    
    expect(mockedAxios.get).toHaveBeenCalledWith(`/api/lotes/finca/${fincaId}/`)
    expect(response).toEqual(mockResponse.data)
  })

  it('crea lote correctamente', async () => {
    const loteData = {
      finca: 1,
      nombre: 'Nuevo Lote',
      area: '10.0',
      variedad: 'CCN-51',
      edad_plantas: 5
    }
    
    const mockResponse = {
      data: {
        success: true,
        lote: {
          id: 1,
          ...loteData
        }
      }
    }
    
    mockedAxios.post.mockResolvedValue(mockResponse)
    
    const response = await lotesApi.createLote(loteData)
    
    expect(mockedAxios.post).toHaveBeenCalledWith('/api/lotes/', loteData)
    expect(response).toEqual(mockResponse.data)
  })

  it('actualiza lote correctamente', async () => {
    const loteId = 1
    const updateData = {
      nombre: 'Lote Actualizado',
      area: '12.0'
    }
    
    const mockResponse = {
      data: {
        success: true,
        lote: {
          id: loteId,
          ...updateData
        }
      }
    }
    
    mockedAxios.put.mockResolvedValue(mockResponse)
    
    const response = await lotesApi.updateLote(loteId, updateData)
    
    expect(mockedAxios.put).toHaveBeenCalledWith(`/api/lotes/${loteId}/`, updateData)
    expect(response).toEqual(mockResponse.data)
  })

  it('elimina lote correctamente', async () => {
    const loteId = 1
    
    const mockResponse = {
      data: {
        success: true,
        message: 'Lote deleted successfully'
      }
    }
    
    mockedAxios.delete.mockResolvedValue(mockResponse)
    
    const response = await lotesApi.deleteLote(loteId)
    
    expect(mockedAxios.delete).toHaveBeenCalledWith(`/api/lotes/${loteId}/`)
    expect(response).toEqual(mockResponse.data)
  })
})

describe('Admin API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('obtiene lista de usuarios', async () => {
    const mockResponse = {
      data: {
        success: true,
        users: [
          {
            id: 1,
            username: 'user1',
            email: 'user1@example.com',
            role: 'farmer'
          },
          {
            id: 2,
            username: 'user2',
            email: 'user2@example.com',
            role: 'analyst'
          }
        ]
      }
    }
    
    mockedAxios.get.mockResolvedValue(mockResponse)
    
    const response = await adminApi.getUsers()
    
    expect(mockedAxios.get).toHaveBeenCalledWith('/api/admin/users/')
    expect(response).toEqual(mockResponse.data)
  })

  it('crea usuario correctamente', async () => {
    const userData = {
      username: 'newuser',
      email: 'newuser@example.com',
      password: 'password123',
      role: 'farmer'
    }
    
    const mockResponse = {
      data: {
        success: true,
        user: {
          id: 1,
          ...userData
        }
      }
    }
    
    mockedAxios.post.mockResolvedValue(mockResponse)
    
    const response = await adminApi.createUser(userData)
    
    expect(mockedAxios.post).toHaveBeenCalledWith('/api/admin/users/', userData)
    expect(response).toEqual(mockResponse.data)
  })

  it('actualiza usuario correctamente', async () => {
    const userId = 1
    const updateData = {
      role: 'analyst',
      is_active: true
    }
    
    const mockResponse = {
      data: {
        success: true,
        user: {
          id: userId,
          ...updateData
        }
      }
    }
    
    mockedAxios.put.mockResolvedValue(mockResponse)
    
    const response = await adminApi.updateUser(userId, updateData)
    
    expect(mockedAxios.put).toHaveBeenCalledWith(`/api/admin/users/${userId}/`, updateData)
    expect(response).toEqual(mockResponse.data)
  })

  it('elimina usuario correctamente', async () => {
    const userId = 1
    
    const mockResponse = {
      data: {
        success: true,
        message: 'User deleted successfully'
      }
    }
    
    mockedAxios.delete.mockResolvedValue(mockResponse)
    
    const response = await adminApi.deleteUser(userId)
    
    expect(mockedAxios.delete).toHaveBeenCalledWith(`/api/admin/users/${userId}/`)
    expect(response).toEqual(mockResponse.data)
  })

  it('obtiene estadísticas del sistema', async () => {
    const mockResponse = {
      data: {
        success: true,
        stats: {
          total_users: 100,
          total_analyses: 500,
          total_fincas: 50,
          system_uptime: '7 days'
        }
      }
    }
    
    mockedAxios.get.mockResolvedValue(mockResponse)
    
    const response = await adminApi.getSystemStats()
    
    expect(mockedAxios.get).toHaveBeenCalledWith('/api/admin/stats/')
    expect(response).toEqual(mockResponse.data)
  })

  it('obtiene logs de auditoría', async () => {
    const mockResponse = {
      data: {
        success: true,
        logs: [
          {
            id: 1,
            user: 'testuser',
            action: 'login',
            timestamp: '2024-01-01T10:00:00Z'
          },
          {
            id: 2,
            user: 'testuser',
            action: 'upload_image',
            timestamp: '2024-01-01T10:05:00Z'
          }
        ]
      }
    }
    
    mockedAxios.get.mockResolvedValue(mockResponse)
    
    const response = await adminApi.getAuditLogs()
    
    expect(mockedAxios.get).toHaveBeenCalledWith('/api/admin/audit-logs/')
    expect(response).toEqual(mockResponse.data)
  })
})

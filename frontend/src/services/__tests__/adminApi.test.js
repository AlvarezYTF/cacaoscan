/**
 * Unit tests for adminApi service
 * Tests advanced administrative API functions
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  startAdvancedTraining,
  startMLTraining,
  getTrainingHistory,
  getMultipleJobStatus,
  cancelTrainingJob,
  getModelMetrics,
  compareModels,
  createExperiment,
  getExperiments,
  validateTrainingConfig,
  estimateTrainingTime,
  formatAdvancedTrainingMetrics,
  TRAINING_PRESETS,
  DATA_FILTERS,
  ADMIN_TRAINING_CONFIG
} from '../adminApi.js'
import { fetchGet, fetchPost } from '../apiClient.js'
import {
  trainRegressionModel as baseTrainRegression,
  trainVisionModel as baseTrainVision,
  getTrainingJobStatus as baseGetJobStatus,
  getTrainingJobs as baseGetJobs
} from '../datasetApi.js'

// Mock dependencies
vi.mock('../apiClient.js', () => ({
  fetchGet: vi.fn(),
  fetchPost: vi.fn()
}))

vi.mock('../datasetApi.js', () => ({
  trainRegressionModel: vi.fn(),
  trainVisionModel: vi.fn(),
  getTrainingJobStatus: vi.fn(),
  getTrainingJobs: vi.fn(),
  formatNumber: vi.fn((value, decimals = 2) => {
    if (value === null || value === undefined || Number.isNaN(value)) return 'N/A'
    return Number.parseFloat(value).toFixed(decimals)
  })
}))

describe('adminApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('TRAINING_PRESETS', () => {
    it('should export training presets', () => {
      expect(TRAINING_PRESETS).toBeDefined()
      expect(TRAINING_PRESETS.FAST).toBeDefined()
      expect(TRAINING_PRESETS.STANDARD).toBeDefined()
      expect(TRAINING_PRESETS.PRODUCTION).toBeDefined()
    })

    it('should have FAST preset configuration', () => {
      expect(TRAINING_PRESETS.FAST.regression).toBeDefined()
      expect(TRAINING_PRESETS.FAST.vision).toBeDefined()
    })
  })

  describe('DATA_FILTERS', () => {
    it('should export data filters', () => {
      expect(DATA_FILTERS).toBeDefined()
      expect(DATA_FILTERS.QUALITY_LEVELS).toBeDefined()
      expect(DATA_FILTERS.DATA_TYPES).toBeDefined()
      expect(DATA_FILTERS.TIME_RANGES).toBeDefined()
    })
  })

  describe('ADMIN_TRAINING_CONFIG', () => {
    it('should export admin training config', () => {
      expect(ADMIN_TRAINING_CONFIG).toBeDefined()
      expect(ADMIN_TRAINING_CONFIG.STATUS_REFRESH_INTERVAL).toBeDefined()
      expect(ADMIN_TRAINING_CONFIG.MAX_CONCURRENT_JOBS).toBeDefined()
    })
  })

  describe('startMLTraining', () => {
    it('should start ML training with default config', async () => {
      const mockResponse = { id: 1, status: 'pending' }
      fetchPost.mockResolvedValue(mockResponse)

      const result = await startMLTraining()

      expect(fetchPost).toHaveBeenCalledWith('/ml/train/', expect.objectContaining({
        job_type: 'regression',
        epochs: 150
      }))
      expect(result).toEqual(mockResponse)
    })

    it('should accept custom config', async () => {
      const mockResponse = { id: 1 }
      fetchPost.mockResolvedValue(mockResponse)
      const customConfig = {
        epochs: 200,
        batch_size: 32
      }

      await startMLTraining(customConfig)

      expect(fetchPost).toHaveBeenCalledWith('/ml/train/', expect.objectContaining({
        epochs: 200,
        batch_size: 32
      }))
    })
  })

  describe('getTrainingHistory', () => {
    it('should get training history', async () => {
      const mockHistory = [{ id: 1, status: 'completed' }]
      fetchGet.mockResolvedValue(mockHistory)

      const result = await getTrainingHistory()

      expect(fetchGet).toHaveBeenCalled()
      expect(result).toEqual(mockHistory)
    })
  })

  describe('getMultipleJobStatus', () => {
    it('should get multiple job statuses', async () => {
      const mockStatuses = {
        1: { status: 'completed' },
        2: { status: 'running' }
      }
      fetchPost.mockResolvedValue(mockStatuses)

      const result = await getMultipleJobStatus([1, 2])

      expect(fetchPost).toHaveBeenCalled()
      expect(result).toEqual(mockStatuses)
    })
  })

  describe('cancelTrainingJob', () => {
    it('should cancel training job', async () => {
      const mockResponse = { success: true }
      fetchPost.mockResolvedValue(mockResponse)

      const result = await cancelTrainingJob('job-123')

      expect(fetchPost).toHaveBeenCalledWith('/train/jobs/job-123/cancel/')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('getModelMetrics', () => {
    it('should get model metrics', async () => {
      const mockMetrics = {
        accuracy: 0.95,
        loss: 0.05
      }
      fetchGet.mockResolvedValue(mockMetrics)

      const result = await getModelMetrics('job-123')

      expect(fetchGet).toHaveBeenCalled()
      expect(result).toEqual(mockMetrics)
    })
  })

  describe('compareModels', () => {
    it('should compare multiple models', async () => {
      const mockComparison = {
        best_model: 1,
        comparisons: []
      }
      fetchPost.mockResolvedValue(mockComparison)

      const result = await compareModels(['job-1', 'job-2'])

      expect(fetchPost).toHaveBeenCalledWith('/train/jobs/compare/', {
        job_ids: ['job-1', 'job-2']
      })
      expect(result).toEqual(mockComparison)
    })
  })

  describe('validateTrainingConfig', () => {
    it('should validate valid config', () => {
      const validConfig = {
        epochs: 50,
        learning_rate: 0.001,
        batch_size: 32
      }

      const result = validateTrainingConfig('regression', validConfig)

      expect(result.errors).toEqual([])
      expect(result.isValid).toBe(true)
    })

    it('should reject invalid epochs', () => {
      const invalidConfig = {
        epochs: 0,
        learning_rate: 0.001,
        batch_size: 32
      }

      const result = validateTrainingConfig('regression', invalidConfig)

      expect(result.isValid).toBe(false)
      expect(result.errors.length).toBeGreaterThan(0)
    })
  })

  describe('estimateTrainingTime', () => {
    it('should estimate training time', () => {
      const result = estimateTrainingTime(
        'regression',
        {
          epochs: 50,
          batch_size: 32
        },
        1000
      )

      expect(result.totalSeconds).toBeGreaterThan(0)
      expect(result.formatted).toBeDefined()
      expect(result.estimatedCompletion).toBeInstanceOf(Date)
    })
  })

  describe('formatAdvancedTrainingMetrics', () => {
    it('should format training metrics', () => {
      const metrics = {
        final_loss: 0.05,
        final_accuracy: 0.95,
        r2_score: 0.92,
        total_epochs: 50
      }

      const formatted = formatAdvancedTrainingMetrics(metrics)

      expect(formatted.loss).toBeDefined()
      expect(formatted.accuracy).toBeDefined()
      expect(formatted.total_epochs).toBe(50)
    })
  })
})


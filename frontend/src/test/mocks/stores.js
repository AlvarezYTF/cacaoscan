/**
 * Shared mocks for stores
 * Centralizes store mocks to reduce duplication across test files
 */

import { vi } from 'vitest'

/**
 * Creates a mock auth store
 * @param {Object} overrides - Properties to override
 * @returns {Object} Mock auth store
 */
export function createMockAuthStore(overrides = {}) {
  return {
    isAuthenticated: false,
    isAdmin: false,
    accessToken: null,
    user: null,
    userRole: null,
    userFullName: null,
    getCurrentUser: vi.fn(),
    clearAll: vi.fn(),
    updateLastActivity: vi.fn(),
    checkSessionTimeout: vi.fn(() => false),
    logout: vi.fn(),
    ...overrides
  }
}

/**
 * Creates a mock admin store
 * @param {Object} overrides - Properties to override
 * @returns {Object} Mock admin store
 */
export function createMockAdminStore(overrides = {}) {
  return {
    stats: {
      users: { total: 0, this_week: 0, this_month: 0 },
      fincas: { total: 0, this_week: 0, this_month: 0 },
      images: { total: 0, this_week: 0, this_month: 0 },
      predictions: { average_confidence: 0 },
      activity_by_day: { labels: [], data: [] },
      quality_distribution: { excelente: 0, buena: 0, regular: 0, baja: 0 }
    },
    users: [],
    activities: [],
    reports: [],
    alerts: [],
    loading: false,
    error: null,
    getGeneralStats: vi.fn().mockResolvedValue({ data: {} }),
    getRecentUsers: vi.fn().mockResolvedValue({ data: { results: [] } }),
    getRecentActivities: vi.fn().mockResolvedValue({ data: { results: [] } }),
    getSystemAlerts: vi.fn().mockResolvedValue({ data: { results: [] } }),
    getReportStats: vi.fn().mockResolvedValue({ data: {} }),
    getActivityData: vi.fn().mockResolvedValue({ data: { labels: [], data: [] } }),
    getQualityDistribution: vi.fn().mockResolvedValue({ data: {} }),
    ...overrides
  }
}

/**
 * Creates a mock config store
 * @param {Object} overrides - Properties to override
 * @returns {Object} Mock config store
 */
export function createMockConfigStore(overrides = {}) {
  return {
    brandName: 'CacaoScan',
    getConfig: vi.fn(),
    ...overrides
  }
}


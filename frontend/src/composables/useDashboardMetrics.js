/**
 * Composable for dashboard metrics
 * Consolidates metric calculation, formatting, and display logic
 */
// No Vue imports needed - this composable only provides utility functions
import { useDateFormatting } from './useDateFormatting'

/**
 * Main useDashboardMetrics composable
 * @param {Object} options - Configuration options
 * @returns {Object} Dashboard metrics composable methods and state
 */
export function useDashboardMetrics(options = {}) {
  const { formatDate, formatNumber } = useDateFormatting()
  
  /**
   * Format metric value for display
   * @param {number|string} value - Value to format
   * @param {Object} options - Formatting options
   * @returns {string} Formatted value
   */
  const formatMetricValue = (value, options = {}) => {
    if (value === null || value === undefined) return 'N/A'
    
    const { decimals = 0, suffix = '', prefix = '' } = options
    
    if (typeof value === 'number') {
      // Handle large numbers with abbreviations
      if (value >= 1000000) {
        return `${prefix}${(value / 1000000).toFixed(1)}M${suffix}`
      } else if (value >= 1000) {
        return `${prefix}${(value / 1000).toFixed(1)}K${suffix}`
      }
      
      // Format with decimals and locale
      return `${prefix}${value.toLocaleString('es-ES', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
      })}${suffix}`
    }
    
    return `${prefix}${value}${suffix}`
  }
  
  /**
   * Format percentage change
   * @param {number} change - Percentage change value
   * @returns {string} Formatted change
   */
  const formatPercentageChange = (change) => {
    if (change === null || change === undefined) return ''
    if (typeof change !== 'number') return String(change)
    
    const sign = change >= 0 ? '+' : ''
    return `${sign}${change.toFixed(1)}%`
  }
  
  /**
   * Get change indicator class
   * @param {number} change - Change value
   * @returns {string} CSS class
   */
  const getChangeClass = (change) => {
    if (change === null || change === undefined) return 'neutral'
    if (typeof change !== 'number') return 'neutral'
    
    if (change > 0) return 'positive'
    if (change < 0) return 'negative'
    return 'neutral'
  }
  
  /**
   * Get change icon class
   * @param {number} change - Change value
   * @returns {string} Icon class
   */
  const getChangeIcon = (change) => {
    if (change === null || change === undefined) return 'fas fa-minus'
    if (typeof change !== 'number') return 'fas fa-minus'
    
    if (change > 0) return 'fas fa-arrow-up'
    if (change < 0) return 'fas fa-arrow-down'
    return 'fas fa-minus'
  }
  
  /**
   * Calculate percentage change between two values
   * @param {number} current - Current value
   * @param {number} previous - Previous value
   * @returns {number} Percentage change
   */
  const calculatePercentageChange = (current, previous) => {
    if (!previous || previous === 0) {
      return current > 0 ? 100 : 0
    }
    return ((current - previous) / previous) * 100
  }
  
  /**
   * Build stat card configuration from raw data
   * @param {Object} config - Stat configuration
   * @param {string} config.id - Stat ID
   * @param {number} config.value - Current value
   * @param {number} config.previousValue - Previous value for comparison
   * @param {string} config.label - Stat label
   * @param {string} config.icon - Icon class
   * @param {string} config.variant - Color variant
   * @param {string} config.suffix - Value suffix
   * @param {string} config.description - Description text
   * @param {Array} config.trendData - Trend data array
   * @param {string} config.changePeriod - Change period label
   * @param {boolean} config.clickable - Whether stat is clickable
   * @returns {Object} Formatted stat object
   */
  const buildStatCard = (config) => {
    const {
      id,
      value = 0,
      previousValue = null,
      label,
      icon,
      variant = 'default',
      suffix = '',
      prefix = '',
      description,
      trendData = [],
      changePeriod = 'vs período anterior',
      clickable = false
    } = config
    
    const change = previousValue !== null && previousValue !== undefined
      ? calculatePercentageChange(value, previousValue)
      : null
    
    return {
      id,
      value: formatMetricValue(value, { suffix, prefix }),
      rawValue: value,
      label,
      icon,
      variant,
      suffix,
      prefix,
      description,
      change: change === null ? undefined : formatPercentageChange(change),
      rawChange: change,
      changePeriod,
      clickable,
      trend: trendData.length > 0 ? {
        data: trendData,
        color: getVariantColor(variant)
      } : null
    }
  }
  
  /**
   * Get color for variant
   * @param {string} variant - Variant name
   * @returns {string} Color hex code
   */
  const getVariantColor = (variant) => {
    const colors = {
      'primary': '#3b82f6',
      'success': '#10b981',
      'warning': '#f59e0b',
      'danger': '#ef4444',
      'info': '#06b6d4',
      'default': '#6b7280'
    }
    return colors[variant] || colors.default
  }
  
  /**
   * Build multiple stat cards from array of configurations
   * @param {Array<Object>} configs - Array of stat configurations
   * @returns {Array<Object>} Array of formatted stat objects
   */
  const buildStatCards = (configs) => {
    return configs.map(config => buildStatCard(config))
  }
  
  /**
   * Normalize stats data from API response
   * @param {Object} apiData - Raw API response data
   * @param {Object} mapping - Field mapping configuration
   * @returns {Object} Normalized stats object
   */
  const normalizeStatsData = (apiData, mapping = {}) => {
    const defaultMapping = {
      totalUsers: 'total_users',
      totalFincas: 'total_fincas',
      totalAnalyses: 'total_analyses',
      avgQuality: 'avg_quality',
      usersChange: 'users_change',
      fincasChange: 'fincas_change',
      analysesChange: 'analyses_change',
      qualityChange: 'quality_change'
    }
    
    const finalMapping = { ...defaultMapping, ...mapping }
    const normalized = {}
    
    for (const [key, apiKey] of Object.entries(finalMapping)) {
      if (apiData.hasOwnProperty(apiKey)) {
        normalized[key] = apiData[apiKey]
      }
    }
    
    return normalized
  }
  
  return {
    // Formatting methods
    formatMetricValue,
    formatPercentageChange,
    
    // Calculation methods
    calculatePercentageChange,
    
    // Display helpers
    getChangeClass,
    getChangeIcon,
    getVariantColor,
    
    // Stat building
    buildStatCard,
    buildStatCards,
    normalizeStatsData,
    
    // Utilities
    formatDate,
    formatNumber
  }
}


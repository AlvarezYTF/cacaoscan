/**
 * Composable for date period calculations
 * Provides reusable functions to calculate date ranges for different periods
 */
import { ref } from 'vue'

/**
 * Calculate date range for a given period
 * @param {string} period - Period type: 'today', 'week', 'month', 'quarter', 'year', 'custom'
 * @param {Date} referenceDate - Reference date (defaults to now)
 * @returns {Object} Object with fecha_desde and fecha_hasta in ISO format (YYYY-MM-DD)
 */
export function calculatePeriodDates(period, referenceDate = null) {
  const now = referenceDate || new Date()
  let fecha_desde = ''
  const fecha_hasta = now.toISOString().split('T')[0]

  switch (period) {
    case 'today':
      fecha_desde = fecha_hasta
      break
    case 'week':
      fecha_desde = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
      break
    case 'month':
      fecha_desde = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
      break
    case 'quarter':
      fecha_desde = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
      break
    case 'year':
      fecha_desde = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
      break
    case 'custom':
      // Return empty strings for custom period (user will set dates manually)
      return { fecha_desde: '', fecha_hasta: fecha_hasta }
    default:
      // fecha_desde already initialized as empty string, no need to reassign
      break
  }

  return { fecha_desde, fecha_hasta }
}

/**
 * Composable for managing period-based date filters
 * @param {Object} options - Options
 * @param {string} options.initialPeriod - Initial period (default: 'week')
 * @param {Function} options.onPeriodChange - Callback when period changes
 * @returns {Object} Period state and methods
 */
export function usePeriodDates(options = {}) {
  const {
    initialPeriod = 'week',
    onPeriodChange = null
  } = options

  const selectedPeriod = ref(initialPeriod)
  const fecha_desde = ref('')
  const fecha_hasta = ref('')

  /**
   * Update period and calculate dates
   * @param {string} period - Period type
   */
  const setPeriod = (period) => {
    selectedPeriod.value = period
    
    if (period === 'custom') {
      // Don't change dates for custom period
      if (onPeriodChange) {
        onPeriodChange(period, fecha_desde.value, fecha_hasta.value)
      }
      return
    }

    const dates = calculatePeriodDates(period)
    fecha_desde.value = dates.fecha_desde
    fecha_hasta.value = dates.fecha_hasta

    if (onPeriodChange) {
      onPeriodChange(period, dates.fecha_desde, dates.fecha_hasta)
    }
  }

  /**
   * Set custom date range
   * @param {string} desde - Start date (ISO format)
   * @param {string} hasta - End date (ISO format)
   */
  const setCustomDates = (desde, hasta) => {
    fecha_desde.value = desde
    fecha_hasta.value = hasta
    selectedPeriod.value = 'custom'
    
    if (onPeriodChange) {
      onPeriodChange('custom', desde, hasta)
    }
  }

  /**
   * Reset to initial period
   */
  const resetPeriod = () => {
    setPeriod(initialPeriod)
  }

  // Initialize with default period
  setPeriod(initialPeriod)

  return {
    selectedPeriod,
    fecha_desde,
    fecha_hasta,
    setPeriod,
    setCustomDates,
    resetPeriod,
    calculatePeriodDates
  }
}


/**
 * Composable for chart event handling
 * Centralizes chart event handlers to reduce duplication
 */

/**
 * Creates chart event handlers
 * @param {Function} emit - Vue emit function
 * @returns {Object} Chart event handlers
 */
export function useChartEvents(emit) {
  /**
   * Handles chart click event
   * @param {Object} data - Click event data
   */
  const handleChartClick = (data) => {
    emit('chart-click', data)
  }

  /**
   * Handles chart hover event
   * @param {Object} data - Hover event data
   */
  const handleChartHover = (data) => {
    emit('chart-hover', data)
  }

  /**
   * Handles chart loaded event
   * @param {Object} instance - Chart instance
   */
  const handleChartLoaded = (instance) => {
    emit('chart-loaded', instance)
  }

  return {
    handleChartClick,
    handleChartHover,
    handleChartLoaded
  }
}


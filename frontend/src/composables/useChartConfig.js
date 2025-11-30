/**
 * Composable for Chart.js configuration
 * Provides centralized chart configuration and theme management
 */
import { computed } from 'vue'

/**
 * Default chart colors
 */
export const DEFAULT_CHART_COLORS = [
  '#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6',
  '#1abc9c', '#34495e', '#e67e22', '#95a5a6', '#f1c40f'
]

/**
 * Chart themes configuration
 */
export const CHART_THEMES = {
  light: {
    textColor: '#333333',
    gridColor: 'rgba(0, 0, 0, 0.1)',
    backgroundColor: 'rgba(255, 255, 255, 1)',
    tooltipBackground: 'rgba(0, 0, 0, 0.8)',
    tooltipBorder: 'rgba(255, 255, 255, 0.2)'
  },
  dark: {
    textColor: '#ffffff',
    gridColor: 'rgba(255, 255, 255, 0.1)',
    backgroundColor: 'rgba(31, 41, 55, 1)',
    tooltipBackground: 'rgba(0, 0, 0, 0.9)',
    tooltipBorder: 'rgba(255, 255, 255, 0.2)'
  }
}

/**
 * Create chart configuration composable
 * @param {Object} options - Chart options
 * @param {string} options.theme - Theme name ('light' | 'dark')
 * @param {string} options.type - Chart type
 * @param {boolean} options.responsive - Responsive chart
 * @param {boolean} options.maintainAspectRatio - Maintain aspect ratio
 * @param {boolean} options.animation - Enable animation
 * @param {number} options.animationDuration - Animation duration
 * @param {boolean} options.showLegend - Show legend
 * @param {string} options.legendPosition - Legend position
 * @param {Array} options.colors - Color palette
 * @returns {Object} Chart configuration
 */
export function useChartConfig(options = {}) {
  const {
    theme = 'light',
    type = 'line',
    responsive = true,
    maintainAspectRatio = false,
    animation = true,
    animationDuration = 1000,
    showLegend = true,
    legendPosition = 'top',
    colors = DEFAULT_CHART_COLORS
  } = options

  // Get theme colors
  const themeColors = computed(() => {
    return CHART_THEMES[theme] || CHART_THEMES.light
  })

  /**
   * Get default chart options
   * @returns {Object} Chart.js options
   */
  const getDefaultOptions = computed(() => {
    const textColor = themeColors.value.textColor
    const gridColor = themeColors.value.gridColor

    return {
      responsive,
      maintainAspectRatio,
      animation: animation ? {
        duration: animationDuration,
        easing: 'easeInOutQuart'
      } : false,
      plugins: {
        legend: {
          display: showLegend,
          position: legendPosition,
          labels: {
            color: textColor,
            usePointStyle: true,
            boxWidth: 12,
            padding: 15,
            font: {
              size: 12,
              family: "'Inter', sans-serif"
            }
          }
        },
        tooltip: {
          enabled: true,
          mode: 'index',
          intersect: false,
          backgroundColor: themeColors.value.tooltipBackground,
          titleColor: '#ffffff',
          bodyColor: '#ffffff',
          borderColor: themeColors.value.tooltipBorder,
          borderWidth: 1,
          cornerRadius: 8,
          displayColors: true,
          callbacks: {
            title: (context) => {
              return context[0]?.label || ''
            },
            label: (context) => {
              const label = context.dataset.label || ''
              const value = context.parsed.y || context.parsed || context.raw
              const formattedValue = typeof value === 'number' ? value.toLocaleString() : value
              return `${label}: ${formattedValue}`
            }
          }
        }
      },
      scales: type !== 'pie' && type !== 'doughnut' ? {
        x: {
          grid: {
            display: true,
            color: gridColor,
            drawBorder: false
          },
          ticks: {
            color: textColor,
            font: {
              size: 11,
              family: "'Inter', sans-serif"
            },
            padding: 8,
            maxRotation: 45,
            minRotation: 0
          }
        },
        y: {
          beginAtZero: true,
          grid: {
            display: true,
            color: gridColor,
            drawBorder: false
          },
          ticks: {
            color: textColor,
            font: {
              size: 11,
              family: "'Inter', sans-serif"
            },
            padding: 8,
            callback: (value) => {
              return typeof value === 'number' ? value.toLocaleString() : value
            }
          }
        }
      } : {},
      interaction: {
        mode: 'nearest',
        axis: 'x',
        intersect: false
      }
    }
  })

  /**
   * Process chart data with colors
   * @param {Object} chartData - Chart data
   * @param {boolean} gradient - Use gradient colors
   * @param {Function} createGradient - Gradient creation function
   * @returns {Object} Processed chart data
   */
  const processChartData = (chartData, gradient = false, createGradient = null) => {
    if (!chartData?.datasets) {
      return chartData
    }

    const data = { ...chartData }
    data.datasets = data.datasets.map((dataset, index) => {
      const processedDataset = { ...dataset }

      // Apply colors if not defined
      if (!processedDataset.backgroundColor) {
        if (type === 'pie' || type === 'doughnut') {
          processedDataset.backgroundColor = colors.slice(0, data.labels?.length || 10)
        } else {
          processedDataset.backgroundColor = gradient && createGradient
            ? createGradient(colors[index % colors.length])
            : colors[index % colors.length]
        }
      }

      if (!processedDataset.borderColor && type !== 'pie' && type !== 'doughnut') {
        processedDataset.borderColor = colors[index % colors.length]
      }

      // Default configuration for different chart types
      if (type === 'line') {
        processedDataset.fill = false
        processedDataset.tension = 0.4
        processedDataset.borderWidth = 2
        processedDataset.pointRadius = 4
        processedDataset.pointHoverRadius = 6
      } else if (type === 'bar') {
        processedDataset.borderWidth = 1
        processedDataset.borderRadius = 4
        processedDataset.borderSkipped = false
      }

      return processedDataset
    })

    return data
  }

  /**
   * Create gradient for chart
   * @param {CanvasRenderingContext2D} ctx - Canvas context
   * @param {string} color - Base color
   * @param {number} height - Gradient height
   * @returns {CanvasGradient} Gradient object
   */
  const createGradient = (ctx, color, height = 400) => {
    const gradient = ctx.createLinearGradient(0, 0, 0, height)
    gradient.addColorStop(0, color + '80')
    gradient.addColorStop(1, color + '20')
    return gradient
  }

  return {
    // Configuration
    getDefaultOptions,
    themeColors,
    colors,

    // Methods
    processChartData,
    createGradient
  }
}


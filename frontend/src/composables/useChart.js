/**
 * Composable for Chart.js lifecycle management
 * Provides unified chart instance management, lifecycle hooks, and update handling
 */
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'

// Register Chart.js plugins once
Chart.register(...registerables)

/**
 * Chart lifecycle management composable
 * @param {Object} config - Chart configuration
 * @param {Object} config.chartData - Chart data object
 * @param {Object} config.options - Chart.js options
 * @param {string} config.type - Chart type ('line', 'bar', 'pie', etc.)
 * @param {Function} config.onClick - Click handler
 * @param {Function} config.onHover - Hover handler
 * @param {Function} config.onLoaded - Loaded handler
 * @param {boolean} config.enableResizeObserver - Enable ResizeObserver
 * @returns {Object} Chart management utilities
 */
export function useChart(config) {
  const {
    chartRef: externalChartRef = null,
    chartData,
    options = {},
    type = 'line',
    onClick = null,
    onHover = null,
    onLoaded = null,
    enableResizeObserver = true
  } = config

  const chartRef = externalChartRef || ref(null)
  let chartInstance = null
  let resizeObserver = null

  /**
   * Create or update chart instance
   * @param {Object} data - Chart data
   * @param {Object} opts - Chart options
   */
  const createChart = async (data = chartData, opts = options) => {
    if (chartInstance) {
      chartInstance.destroy()
      chartInstance = null
    }

    if (!chartRef.value || !data) {
      return
    }

    await nextTick()

    const ctx = chartRef.value.getContext('2d')
    if (!ctx) {
      return
    }

    const chartOptions = {
      ...opts,
      onClick: (event, elements) => {
        if (onClick && elements.length > 0) {
          onClick({
            event,
            elements,
            element: elements[0],
            datasetIndex: elements[0]?.datasetIndex,
            index: elements[0]?.index,
            value: elements[0]?.element?.$context?.parsed
          })
        }
      },
      onHover: (event, elements) => {
        if (onHover) {
          onHover({
            event,
            elements,
            element: elements[0],
            datasetIndex: elements[0]?.datasetIndex,
            index: elements[0]?.index
          })
        }
      }
    }

    // Get current type value (handle both ref/computed and plain values)
    const currentType = typeof type === 'function' || type?.value !== undefined
      ? type.value
      : type

    chartInstance = new Chart(ctx, {
      type: currentType,
      data,
      options: chartOptions
    })

    if (onLoaded) {
      onLoaded(chartInstance)
    }
  }

  /**
   * Update chart data
   * @param {Object} newData - New chart data
   */
  const updateChart = (newData) => {
    if (chartInstance && newData) {
      chartInstance.data = newData
      chartInstance.update()
    }
  }

  /**
   * Update chart options
   * @param {Object} newOptions - New chart options
   */
  const updateOptions = (newOptions) => {
    if (chartInstance && newOptions) {
      Object.assign(chartInstance.options, newOptions)
      chartInstance.update()
    }
  }

  /**
   * Add data point to chart
   * @param {*} data - Data point value(s)
   * @param {string} label - Label for the data point
   */
  const addData = (data, label) => {
    if (chartInstance) {
      if (label && chartInstance.data.labels) {
        chartInstance.data.labels.push(label)
      }
      if (Array.isArray(data)) {
        for (let index = 0; index < chartInstance.data.datasets.length; index++) {
          const dataset = chartInstance.data.datasets[index]
          dataset.data.push(data[index] || 0)
        }
      } else {
        for (const dataset of chartInstance.data.datasets) {
          dataset.data.push(data)
        }
      }
      chartInstance.update()
    }
  }

  /**
   * Remove data point from chart
   * @param {number} index - Index to remove
   */
  const removeData = (index) => {
    if (chartInstance) {
      if (chartInstance.data.labels && chartInstance.data.labels.length > index) {
        chartInstance.data.labels.splice(index, 1)
      }
      for (const dataset of chartInstance.data.datasets) {
        if (dataset.data.length > index) {
          dataset.data.splice(index, 1)
        }
      }
      chartInstance.update()
    }
  }

  /**
   * Resize chart
   */
  const resizeChart = () => {
    if (chartInstance) {
      chartInstance.resize()
    }
  }

  /**
   * Export chart as image
   * @param {string} format - Image format ('png' | 'jpeg')
   * @returns {string|null} Base64 image string
   */
  const exportChart = (format = 'png') => {
    if (chartInstance) {
      return chartInstance.toBase64Image(format)
    }
    return null
  }

  /**
   * Destroy chart instance
   */
  const destroyChart = () => {
    if (chartInstance) {
      chartInstance.destroy()
      chartInstance = null
    }
  }

  /**
   * Handle window resize
   */
  const handleResize = () => {
    resizeChart()
  }

  // Setup resize observer
  const setupResizeObserver = () => {
    if (!enableResizeObserver || !globalThis.ResizeObserver) {
      return
    }

    if (chartRef.value) {
      resizeObserver = new ResizeObserver(() => {
        handleResize()
      })
      resizeObserver.observe(chartRef.value)
    }
  }

  // Setup window event listeners
  const setupEventListeners = () => {
    if (globalThis.addEventListener) {
      globalThis.addEventListener('orientationchange', handleResize)
      globalThis.addEventListener('resize', handleResize)
    }
  }

  // Remove event listeners
  const removeEventListeners = () => {
    if (globalThis.removeEventListener) {
      globalThis.removeEventListener('orientationchange', handleResize)
      globalThis.removeEventListener('resize', handleResize)
    }
  }

  // Lifecycle hooks
  onMounted(async () => {
    await createChart()
    setupResizeObserver()
    setupEventListeners()
  })

  onUnmounted(() => {
    destroyChart()
    if (resizeObserver) {
      resizeObserver.disconnect()
      resizeObserver = null
    }
    removeEventListeners()
  })

  // Watch for data changes
  if (chartData) {
    watch(() => chartData, (newData) => {
      if (newData) {
        createChart(newData, options)
      }
    }, { deep: true })
  }

  // Watch for options changes
  if (options) {
    watch(() => options, (newOptions) => {
      if (newOptions) {
        updateOptions(newOptions)
      }
    }, { deep: true })
  }

  // Watch for type changes - requires recreating chart (only if type is reactive)
  if (typeof type === 'function' || type?.value !== undefined) {
    watch(type, () => {
      createChart(chartData, options)
    })
  }

  return {
    chartRef,
    chartInstance: () => chartInstance,
    createChart,
    updateChart,
    updateOptions,
    addData,
    removeData,
    resizeChart,
    exportChart,
    destroyChart
  }
}


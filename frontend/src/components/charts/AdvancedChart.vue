<template>
  <div class="chart-container" :style="containerStyle">
    <div v-if="title" class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div v-if="showControls" class="chart-controls">
        <slot name="controls"></slot>
      </div>
    </div>
    <div class="chart-body">
      <canvas ref="chart"></canvas>
    </div>
    <div v-if="showLegend && legendPosition === 'bottom'" class="chart-legend">
      <slot name="legend"></slot>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed, onUnmounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

export default {
  name: 'AdvancedChart',
  props: {
    chartData: {
      type: Object,
      required: true
    },
    options: {
      type: Object,
      default: () => ({})
    },
    type: {
      type: String,
      default: 'line',
      validator: (value) => ['line', 'bar', 'pie', 'doughnut', 'radar', 'polarArea', 'scatter', 'bubble'].includes(value)
    },
    title: {
      type: String,
      default: ''
    },
    height: {
      type: [String, Number],
      default: '300px'
    },
    responsive: {
      type: Boolean,
      default: true
    },
    maintainAspectRatio: {
      type: Boolean,
      default: false
    },
    showControls: {
      type: Boolean,
      default: false
    },
    showLegend: {
      type: Boolean,
      default: true
    },
    legendPosition: {
      type: String,
      default: 'top',
      validator: (value) => ['top', 'bottom', 'left', 'right'].includes(value)
    },
    animation: {
      type: Boolean,
      default: true
    },
    animationDuration: {
      type: Number,
      default: 1000
    },
    colors: {
      type: Array,
      default: () => [
        '#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6',
        '#1abc9c', '#34495e', '#e67e22', '#95a5a6', '#f1c40f'
      ]
    },
    gradient: {
      type: Boolean,
      default: false
    },
    theme: {
      type: String,
      default: 'light',
      validator: (value) => ['light', 'dark'].includes(value)
    }
  },
  emits: ['chart-click', 'chart-hover', 'chart-loaded'],
  setup(props, { emit, attrs }) {
    const chart = ref(null)
    let chartInstance = null
    let resizeObserver = null

    // Estilos del contenedor
    const containerStyle = computed(() => {
      const hasHeightClass = Object.keys(attrs).some(key => String(attrs[key]).includes('h-'))
      return hasHeightClass ? {} : { height: props.height }
    })

    // Configuración por defecto del tema
    const defaultOptions = computed(() => {
      const isDark = props.theme === 'dark'
      const textColor = isDark ? '#ffffff' : '#333333'
      const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'

      return {
        responsive: props.responsive,
        maintainAspectRatio: props.maintainAspectRatio,
        animation: props.animation ? {
          duration: props.animationDuration,
          easing: 'easeInOutQuart'
        } : false,
        plugins: {
          legend: {
            display: props.showLegend,
            position: props.legendPosition,
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
            backgroundColor: isDark ? 'rgba(0, 0, 0, 0.9)' : 'rgba(0, 0, 0, 0.8)',
            titleColor: '#ffffff',
            bodyColor: '#ffffff',
            borderColor: 'rgba(255, 255, 255, 0.2)',
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
        scales: props.type !== 'pie' && props.type !== 'doughnut' ? {
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
        },
        onClick: (event, elements) => {
          if (elements.length > 0) {
            emit('chart-click', {
              element: elements[0],
              datasetIndex: elements[0].datasetIndex,
              index: elements[0].index,
              value: elements[0].element.$context.parsed
            })
          }
        },
        onHover: (event, elements) => {
          emit('chart-hover', {
            element: elements[0],
            datasetIndex: elements[0]?.datasetIndex,
            index: elements[0]?.index
          })
        }
      }
    })

    // Aplicar colores a los datasets
    const processedChartData = computed(() => {
      if (!props.chartData || !props.chartData.datasets) {
        return props.chartData
      }

      const data = { ...props.chartData }
      data.datasets = data.datasets.map((dataset, index) => {
        const processedDataset = { ...dataset }
        
        // Aplicar colores si no están definidos
        if (!processedDataset.backgroundColor) {
          if (props.type === 'pie' || props.type === 'doughnut') {
            processedDataset.backgroundColor = props.colors.slice(0, data.labels?.length || 10)
          } else {
            processedDataset.backgroundColor = props.gradient 
              ? createGradient(props.colors[index % props.colors.length])
              : props.colors[index % props.colors.length]
          }
        }

        if (!processedDataset.borderColor && props.type !== 'pie' && props.type !== 'doughnut') {
          processedDataset.borderColor = props.colors[index % props.colors.length]
        }

        // Configuración por defecto para diferentes tipos de gráfico
        if (props.type === 'line') {
          processedDataset.fill = false
          processedDataset.tension = 0.4
          processedDataset.borderWidth = 2
          processedDataset.pointRadius = 4
          processedDataset.pointHoverRadius = 6
        } else if (props.type === 'bar') {
          processedDataset.borderWidth = 1
          processedDataset.borderRadius = 4
          processedDataset.borderSkipped = false
        }

        return processedDataset
      })

      return data
    })

    // Crear gradiente
    const createGradient = (color) => {
      if (!chart.value) return color
      
      const ctx = chart.value.getContext('2d')
      const gradient = ctx.createLinearGradient(0, 0, 0, 400)
      gradient.addColorStop(0, color + '80')
      gradient.addColorStop(1, color + '20')
      return gradient
    }

    // Renderizar gráfico
    const renderChart = async () => {
      if (chartInstance) {
        chartInstance.destroy()
      }

      if (chart.value && processedChartData.value) {
        await nextTick()
        
        const ctx = chart.value.getContext('2d')
        chartInstance = new Chart(ctx, {
          type: props.type,
          data: processedChartData.value,
          options: {
            ...defaultOptions.value,
            ...props.options
          }
        })

        emit('chart-loaded', chartInstance)
      }
    }

    // Manejar redimensionamiento
    const handleResize = () => {
      if (chartInstance) {
        chartInstance.resize()
      }
    }

    // Lifecycle
    onMounted(async () => {
      await renderChart()
      
      // Observador de cambios de tamaño
      if (globalThis.ResizeObserver) {
        resizeObserver = new ResizeObserver(() => {
          handleResize()
        })
        if (chart.value) {
          resizeObserver.observe(chart.value)
        }
      }

      // Listeners para cambios de orientación
      globalThis.addEventListener('orientationchange', handleResize)
      globalThis.addEventListener('resize', handleResize)
    })

    onUnmounted(() => {
      if (chartInstance) {
        chartInstance.destroy()
      }
      if (resizeObserver) {
        resizeObserver.disconnect()
      }
      globalThis.removeEventListener('orientationchange', handleResize)
      globalThis.removeEventListener('resize', handleResize)
    })

    // Watchers
    watch(() => props.chartData, () => {
      renderChart()
    }, { deep: true })

    watch(() => props.options, () => {
      renderChart()
    }, { deep: true })

    watch(() => props.type, () => {
      renderChart()
    })

    watch(() => props.theme, () => {
      renderChart()
    })

    // Métodos públicos
    const updateChart = (newData) => {
      if (chartInstance) {
        chartInstance.data = newData
        chartInstance.update()
      }
    }

    const addData = (data, label) => {
      if (chartInstance) {
        chartInstance.data.labels.push(label)
        for (const [index, dataset] of chartInstance.data.datasets.entries()) {
          dataset.data.push(data[index] || 0)
        }
        chartInstance.update()
      }
    }

    const removeData = (index) => {
      if (chartInstance) {
        chartInstance.data.labels.splice(index, 1)
        for (const dataset of chartInstance.data.datasets) {
          dataset.data.splice(index, 1)
        }
        chartInstance.update()
      }
    }

    const exportChart = (format = 'png') => {
      if (chartInstance) {
        return chartInstance.toBase64Image(format)
      }
      return null
    }

    return {
      chart,
      containerStyle,
      updateChart,
      addData,
      removeData,
      exportChart
    }
  }
}
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
  min-height: 200px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  transition: all 0.3s ease;
}

.chart-header {
  padding: 20px 20px 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  font-family: "Inter", sans-serif;
}

.chart-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.chart-body {
  padding: 20px;
  position: relative;
}

.chart-legend {
  padding: 0 20px 20px 20px;
}

/* Tema oscuro */
.chart-container.dark {
  background: #1f2937;
}

.chart-container.dark .chart-title {
  color: #f9fafb;
}

/* Responsive */
@media (max-width: 768px) {
  .chart-container {
    min-height: 250px;
  }
  
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .chart-controls {
    width: 100%;
    justify-content: flex-end;
  }
}

@media (max-width: 480px) {
  .chart-container {
    min-height: 300px;
  }
  
  .chart-body {
    padding: 15px;
  }
}

.chart-container:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
}
</style>

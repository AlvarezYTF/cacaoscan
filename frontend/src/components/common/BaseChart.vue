<template>
  <div class="w-full" :class="containerClass">
    <!-- Chart container -->
    <div ref="chartContainer" class="relative" :style="{ height: height }">
      <canvas ref="chartCanvas" :class="canvasClass"></canvas>
      
      <!-- Loading overlay -->
      <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 z-10">
        <div class="w-8 h-8 border-4 border-gray-300 border-t-green-600 rounded-full animate-spin"></div>
      </div>

      <!-- Error state -->
      <div v-if="error && !loading" class="absolute inset-0 flex items-center justify-center bg-red-50 border border-red-200 rounded-lg">
        <div class="text-center p-4">
          <svg class="w-8 h-8 text-red-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <p class="text-sm text-red-600">{{ error }}</p>
        </div>
      </div>

      <!-- Empty state -->
      <div v-if="!loading && !error && (!data || data.length === 0)" class="absolute inset-0 flex items-center justify-center bg-gray-50 border border-gray-200 rounded-lg">
        <div class="text-center p-4">
          <svg class="w-8 h-8 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
          <p class="text-sm text-gray-500">{{ emptyMessage || 'No hay datos para mostrar' }}</p>
        </div>
      </div>
    </div>

    <!-- Legend (if enabled) -->
    <div v-if="showLegend && legendData && legendData.length > 0" class="mt-4 flex flex-wrap justify-center gap-4">
      <div
        v-for="(item, index) in legendData"
        :key="index"
        class="flex items-center space-x-2"
      >
        <div
          class="w-4 h-4 rounded"
          :style="{ backgroundColor: item.color || getColor(index) }"
        ></div>
        <span class="text-sm text-gray-600">{{ item.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'

const props = defineProps({
  type: {
    type: String,
    required: true,
    validator: (value) => ['line', 'bar', 'pie', 'doughnut', 'radar', 'polarArea', 'trend'].includes(value)
  },
  data: {
    type: Array,
    default: () => []
  },
  labels: {
    type: Array,
    default: () => []
  },
  datasets: {
    type: Array,
    default: () => []
  },
  options: {
    type: Object,
    default: () => ({})
  },
  height: {
    type: String,
    default: '300px'
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  },
  emptyMessage: {
    type: String,
    default: null
  },
  showLegend: {
    type: Boolean,
    default: true
  },
  colors: {
    type: Array,
    default: () => [
      '#10b981', // green
      '#3b82f6', // blue
      '#f59e0b', // yellow
      '#ef4444', // red
      '#8b5cf6', // purple
      '#ec4899', // pink
      '#06b6d4', // cyan
      '#84cc16'  // lime
    ]
  },
  responsive: {
    type: Boolean,
    default: true
  },
  maintainAspectRatio: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click', 'hover', 'legend-click'])

const chartContainer = ref(null)
const chartCanvas = ref(null)
let chartInstance = null

const containerClass = computed(() => {
  return props.responsive ? 'w-full' : ''
})

const canvasClass = computed(() => {
  return 'w-full h-full'
})

const legendData = computed(() => {
  if (props.datasets && props.datasets.length > 0) {
    return props.datasets.map((dataset, index) => ({
      label: dataset.label || `Dataset ${index + 1}`,
      color: dataset.backgroundColor || getColor(index)
    }))
  }
  return []
})

const getColor = (index) => {
  return props.colors[index % props.colors.length]
}

const buildChartData = () => {
  if (props.datasets && props.datasets.length > 0) {
    return {
      labels: props.labels,
      datasets: props.datasets.map((dataset, index) => ({
        ...dataset,
        backgroundColor: dataset.backgroundColor || (props.type === 'pie' || props.type === 'doughnut' ? props.colors : getColor(index)),
        borderColor: dataset.borderColor || getColor(index),
        borderWidth: dataset.borderWidth || 2
      }))
    }
  }

  // Fallback: build from simple data array
  if (props.data && props.data.length > 0) {
    const isNumeric = props.data.every(item => typeof item === 'number')
    
    if (isNumeric) {
      return {
        labels: props.labels || props.data.map((_, i) => `Item ${i + 1}`),
        datasets: [{
          label: 'Data',
          data: props.data,
          backgroundColor: props.type === 'pie' || props.type === 'doughnut' 
            ? props.colors.slice(0, props.data.length)
            : getColor(0),
          borderColor: getColor(0),
          borderWidth: 2
        }]
      }
    }
  }

  return {
    labels: props.labels || [],
    datasets: []
  }
}

const buildChartOptions = () => {
  const defaultOptions = {
    responsive: props.responsive,
    maintainAspectRatio: props.maintainAspectRatio,
    plugins: {
      legend: {
        display: false // We handle legend manually
      },
      tooltip: {
        enabled: true
      }
    },
    onClick: (event, elements) => {
      if (elements.length > 0) {
        emit('click', { event, elements, chart: chartInstance })
      }
    },
    onHover: (event, elements) => {
      emit('hover', { event, elements, chart: chartInstance })
    }
  }

  // Type-specific options
  if (props.type === 'line' || props.type === 'trend') {
    defaultOptions.scales = {
      y: {
        beginAtZero: true,
        ...props.options.scales?.y
      },
      x: {
        ...props.options.scales?.x
      }
    }
  } else if (props.type === 'bar') {
    defaultOptions.scales = {
      y: {
        beginAtZero: true,
        ...props.options.scales?.y
      },
      x: {
        ...props.options.scales?.x
      }
    }
  }

  return {
    ...defaultOptions,
    ...props.options
  }
}

const initChart = async () => {
  if (!chartCanvas.value) return

  // Dynamic import of Chart.js
  const { Chart, registerables } = await import('chart.js')
  Chart.register(...registerables)

  const chartData = buildChartData()
  const chartOptions = buildChartOptions()

  // Destroy existing chart
  if (chartInstance) {
    chartInstance.destroy()
  }

  // Create new chart
  chartInstance = new Chart(chartCanvas.value, {
    type: props.type === 'trend' ? 'line' : props.type,
    data: chartData,
    options: chartOptions
  })
}

const updateChart = () => {
  if (!chartInstance) return

  const chartData = buildChartData()
  chartInstance.data = chartData
  chartInstance.update()
}

watch([() => props.data, () => props.labels, () => props.datasets, () => props.type], () => {
  if (chartInstance) {
    updateChart()
  } else {
    nextTick(() => {
      initChart()
    })
  }
}, { deep: true })

watch(() => props.loading, (newVal) => {
  if (!newVal && chartInstance) {
    updateChart()
  }
})

onMounted(() => {
  if (!props.loading && !props.error) {
    nextTick(() => {
      initChart()
    })
  }
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
})
</script>

<style scoped>
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>


<template>
  <div :class="['base-chart', containerClass]">
    <h3 v-if="title" class="text-lg font-semibold text-gray-800 mb-4">{{ title }}</h3>
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps({
  type: {
    type: String,
    default: 'line',
    validator: (value) => ['line', 'bar', 'pie', 'doughnut', 'radar'].includes(value)
  },
  data: {
    type: Object,
    required: true,
    default: () => ({ datasets: [] })
  },
  options: {
    type: Object,
    default: () => ({})
  },
  title: {
    type: String,
    default: ''
  },
  height: {
    type: [String, Number],
    default: 400
  },
  containerClass: {
    type: String,
    default: 'bg-white p-6 rounded-lg shadow-sm border border-gray-200'
  }
})

const chartCanvas = ref(null)
let chartInstance = null

const defaultOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
      labels: {
        usePointStyle: true,
        boxWidth: 10,
        padding: 20
      }
    },
    tooltip: {
      mode: 'index',
      intersect: false
    }
  },
  scales: props.type === 'pie' || props.type === 'doughnut' ? undefined : {
    x: {
      grid: {
        display: false
      }
    },
    y: {
      beginAtZero: true
    }
  }
}

const createChart = () => {
  if (!chartCanvas.value) return

  if (chartInstance) {
    chartInstance.destroy()
  }

  const mergedOptions = {
    ...defaultOptions,
    ...props.options
  }

  chartInstance = new Chart(chartCanvas.value, {
    type: props.type,
    data: props.data,
    options: mergedOptions
  })
}

const updateChart = () => {
  if (!chartInstance) {
    createChart()
    return
  }

  chartInstance.data = props.data
  chartInstance.update()
}

onMounted(() => {
  createChart()
})

watch(() => props.data, () => {
  updateChart()
}, { deep: true })

watch(() => props.type, () => {
  createChart()
})

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy()
  }
})
</script>

<style scoped>
.base-chart {
  @apply relative;
}

.base-chart canvas {
  max-height: v-bind(typeof height === 'number' ? `${height}px` : height);
}
</style>

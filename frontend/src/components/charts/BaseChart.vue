<template>
  <div class="base-chart" :style="containerStyle">
    <div v-if="title" class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div v-if="showControls" class="chart-controls">
        <slot name="controls"></slot>
      </div>
    </div>
    <div class="chart-body">
      <canvas ref="chartRef"></canvas>
    </div>
    <div v-if="showLegend && legendPosition === 'bottom'" class="chart-legend">
      <slot name="legend"></slot>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, useAttrs } from 'vue'
import { useChart } from '@/composables/useChart'
import { useChartConfig } from '@/composables/useChartConfig'

const props = defineProps({
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
  },
  enableResizeObserver: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['chart-click', 'chart-hover', 'chart-loaded'])

const attrs = useAttrs()

// Use chart config composable
const chartConfig = useChartConfig({
  theme: props.theme,
  type: props.type,
  responsive: props.responsive,
  maintainAspectRatio: props.maintainAspectRatio,
  animation: props.animation,
  animationDuration: props.animationDuration,
  showLegend: props.showLegend,
  legendPosition: props.legendPosition,
  colors: props.colors
})

// Container style
const containerStyle = computed(() => {
  const hasHeightClass = Object.keys(attrs).some(key => String(attrs[key]).includes('h-'))
  return hasHeightClass ? {} : { height: props.height }
})

// Chart ref for template
const chartRef = ref(null)

// Process chart data with colors and gradients
const processedChartData = computed(() => {
  if (!props.chartData || !props.chartData.datasets) {
    return props.chartData
  }

  const createGradientFn = (color) => {
    if (!chartRef.value) return color
    const ctx = chartRef.value.getContext('2d')
    if (!ctx) return color
    return chartConfig.createGradient(ctx, color, typeof props.height === 'number' ? props.height : 400)
  }

  return chartConfig.processChartData(
    props.chartData,
    props.gradient,
    createGradientFn
  )
})

// Get default options from composable
const defaultOptions = computed(() => {
  const baseOptions = chartConfig.getDefaultOptions.value
  return {
    ...baseOptions,
    ...props.options
  }
})

// Use chart lifecycle composable
const { createChart, updateChart, updateOptions, addData, removeData, resizeChart, exportChart } = useChart({
  chartRef,
  chartData: processedChartData,
  options: defaultOptions,
  type: props.type,
  onClick: (data) => {
    emit('chart-click', data)
  },
  onHover: (data) => {
    emit('chart-hover', data)
  },
  onLoaded: (instance) => {
    emit('chart-loaded', instance)
  },
  enableResizeObserver: props.enableResizeObserver
})

// Watch for type changes and recreate chart
watch(() => props.type, () => {
  createChart(processedChartData.value, defaultOptions.value)
})

// Expose methods for parent components
defineExpose({
  createChart,
  updateChart,
  updateOptions,
  addData,
  removeData,
  resizeChart,
  exportChart
})
</script>

<style scoped>
.base-chart {
  position: relative;
  width: 100%;
  min-height: 200px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  transition: all 0.3s ease;
}

.base-chart:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
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

/* Dark theme */
.base-chart.dark {
  background: #1f2937;
}

.base-chart.dark .chart-title {
  color: #f9fafb;
}

/* Responsive */
@media (max-width: 768px) {
  .base-chart {
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
  .base-chart {
    min-height: 300px;
  }
  
  .chart-body {
    padding: 15px;
  }
}
</style>


<template>
  <BaseChart
    :chart-data="chartData"
    :options="mergedOptions"
    :type="type"
    :title="title"
    :height="height"
    :responsive="responsive"
    :maintain-aspect-ratio="maintainAspectRatio"
    :show-controls="showControls"
    :show-legend="showLegend"
    :legend-position="legendPosition"
    :animation="animation"
    :animation-duration="animationDuration"
    :colors="colors"
    :gradient="gradient"
    :theme="theme"
    :enable-resize-observer="true"
    @chart-click="handleChartClick"
    @chart-hover="handleChartHover"
    @chart-loaded="handleChartLoaded"
  >
    <template v-if="showControls" #controls>
      <slot name="controls"></slot>
    </template>
    <template v-if="showLegend && legendPosition === 'bottom'" #legend>
      <slot name="legend"></slot>
    </template>
  </BaseChart>
</template>

<script setup>
import { computed } from 'vue'
import BaseChart from './BaseChart.vue'

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
  }
})

const emit = defineEmits(['chart-click', 'chart-hover', 'chart-loaded'])

// Merge custom options with default options from BaseChart
const mergedOptions = computed(() => {
  return {
    ...props.options
  }
})

// Event handlers
const handleChartClick = (data) => {
  emit('chart-click', data)
}

const handleChartHover = (data) => {
  emit('chart-hover', data)
}

const handleChartLoaded = (instance) => {
  emit('chart-loaded', instance)
}
</script>

<style scoped>
/* Styles are handled by BaseChart */
</style>

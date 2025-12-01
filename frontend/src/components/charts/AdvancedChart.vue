<template>
  <BaseChart
    v-bind="$attrs"
    :chart-data="chartData"
    :options="options"
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
import BaseChart from './BaseChart.vue'
import { useChartEvents } from '@/composables/useChartEvents'

const props = defineProps({
  chartData: {
    type: Object,
    required: true
  },
  options: {
    type: Object,
    default: () => ({})
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
    default: 'top'
  }
})

const emit = defineEmits(['chart-click', 'chart-hover', 'chart-loaded'])

// Use composable for event handlers
const { handleChartClick, handleChartHover, handleChartLoaded } = useChartEvents(emit)
</script>

<style scoped>
/* Styles are handled by BaseChart */
</style>

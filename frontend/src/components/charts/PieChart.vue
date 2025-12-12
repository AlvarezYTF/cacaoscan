<template>
  <BaseChart
    :data="chartData"
    :options="mergedOptions"
    type="pie"
    :title="title"
    :height="height"
    :container-class="containerClass"
  />
</template>

<script setup>
import { computed, watch } from 'vue'
import BaseChart from '@/components/common/BaseChart.vue'

const props = defineProps({
  chartData: {
    type: Object,
    required: true
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

watch(() => props.chartData, (value) => {
  if (!value) {
    throw new Error('PieChart: chartData prop is required')
  }
}, { immediate: true })

const defaultPieOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'right'
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          const label = context.label || ''
          const value = context.raw || 0
          const total = context.dataset.data.reduce((a, b) => a + b, 0)
          const percentage = Math.round((value / total) * 100)
          return `${label}: ${value} (${percentage}%)`
        }
      }
    }
  }
}

const mergedOptions = computed(() => {
  return {
    ...defaultPieOptions,
    ...props.options
  }
})
</script>
  
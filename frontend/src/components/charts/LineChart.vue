<template>
  <BaseChart
    type="line"
    :data="chartData"
    :options="mergedOptions"
    :title="title"
  />
</template>

<script setup>
import { computed } from 'vue'
import BaseChart from '@/components/common/BaseChart.vue'

const props = defineProps({
  chartData: {
    type: Object,
    required: true,
    default: () => ({ datasets: [] })
  },
  chartOptions: {
    type: Object,
    default: () => ({})
  },
  title: {
    type: String,
    default: 'Evolución de análisis por tipo de defecto'
  }
})

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
  scales: {
    x: {
      grid: {
        display: false
      }
    },
    y: {
      beginAtZero: true,
      ticks: {
        stepSize: 2
      }
    }
  }
}

const mergedOptions = computed(() => {
  return {
    ...defaultOptions,
    ...props.chartOptions
  }
})
</script>
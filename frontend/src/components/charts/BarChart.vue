<template>
  <BaseChart
    :data="chartData"
    :options="mergedOptions"
    type="bar"
    :title="title"
    :height="height"
    :container-class="containerClass"
  />
</template>

<script setup>
import { computed } from 'vue'
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

const defaultBarOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'top',
      labels: {
        boxWidth: 12,
        padding: 15,
        font: {
          size: 12
        }
      }
    },
    tooltip: {
      enabled: true,
      mode: 'index',
      intersect: false,
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: 'white',
      bodyColor: 'white',
      borderColor: 'rgba(255, 255, 255, 0.2)',
      borderWidth: 1
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        display: true,
        color: 'rgba(0, 0, 0, 0.05)'
      },
      ticks: {
        font: {
          size: 11
        },
        padding: 8
      }
    },
    x: {
      grid: {
        display: false
      },
      ticks: {
        font: {
          size: 11
        },
        padding: 8,
        maxRotation: 45,
        minRotation: 0
      }
    }
  },
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false
  }
}

const mergedOptions = computed(() => {
  return {
    ...defaultBarOptions,
    ...props.options
  }
})
</script>
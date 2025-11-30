<template>
  <BaseChart
    :chart-data="chartData"
    :options="chartOptions"
    type="line"
    :height="height"
    :show-legend="false"
    :enable-resize-observer="false"
  />
</template>

<script setup>
import { computed } from 'vue'
import BaseChart from './BaseChart.vue'

const props = defineProps({
  data: {
    type: Array,
    required: true,
    validator: (data) => Array.isArray(data) && data.length > 0
  },
  color: {
    type: String,
    default: '#3498db'
  },
  height: {
    type: Number,
    default: 40
  },
  width: {
    type: Number,
    default: 60
  },
  showPoints: {
    type: Boolean,
    default: false
  },
  smooth: {
    type: Boolean,
    default: true
  },
  fill: {
    type: Boolean,
    default: true
  }
})

// Transform data to BaseChart format
const chartData = computed(() => {
  return {
    labels: props.data.map((_, index) => index),
    datasets: [{
      data: props.data,
      borderColor: props.color,
      backgroundColor: props.color,
      borderWidth: 2,
      pointRadius: props.showPoints ? 2 : 0,
      pointHoverRadius: props.showPoints ? 4 : 0,
      pointBackgroundColor: props.color,
      pointBorderColor: props.color,
      fill: props.fill,
      tension: props.smooth ? 0.4 : 0,
      spanGaps: true
    }]
  }
})

// Chart options
const chartOptions = computed(() => {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        enabled: false
      }
    },
    scales: {
      x: {
        display: false
      },
      y: {
        display: false
      }
    },
    interaction: {
      intersect: false
    },
    elements: {
      point: {
        hoverBackgroundColor: props.color,
        hoverBorderColor: props.color
      }
    }
  }
})
</script>

<style scoped>
/* Styles are handled by BaseChart */
</style>

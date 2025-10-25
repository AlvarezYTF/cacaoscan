<template>
  <div class="trend-chart" :style="{ height: height + 'px' }">
    <canvas ref="chart"></canvas>
  </div>
</template>

<script>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

export default {
  name: 'TrendChart',
  props: {
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
  },
  setup(props) {
    const chart = ref(null)
    let chartInstance = null

    const createChart = () => {
      if (chartInstance) {
        chartInstance.destroy()
      }

      if (chart.value && props.data.length > 0) {
        const ctx = chart.value.getContext('2d')
        
        // Crear gradiente si fill está habilitado
        let backgroundColor = props.color
        if (props.fill) {
          const gradient = ctx.createLinearGradient(0, 0, 0, props.height)
          gradient.addColorStop(0, props.color + '40')
          gradient.addColorStop(1, props.color + '10')
          backgroundColor = gradient
        }

        chartInstance = new Chart(ctx, {
          type: 'line',
          data: {
            labels: props.data.map((_, index) => index),
            datasets: [{
              data: props.data,
              borderColor: props.color,
              backgroundColor: backgroundColor,
              borderWidth: 2,
              pointRadius: props.showPoints ? 2 : 0,
              pointHoverRadius: props.showPoints ? 4 : 0,
              pointBackgroundColor: props.color,
              pointBorderColor: props.color,
              fill: props.fill,
              tension: props.smooth ? 0.4 : 0,
              spanGaps: true
            }]
          },
          options: {
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
      }
    }

    onMounted(() => {
      createChart()
    })

    onUnmounted(() => {
      if (chartInstance) {
        chartInstance.destroy()
      }
    })

    watch(() => props.data, () => {
      createChart()
    }, { deep: true })

    watch(() => props.color, () => {
      createChart()
    })

    return {
      chart
    }
  }
}
</script>

<style scoped>
.trend-chart {
  position: relative;
  width: 100%;
}

.trend-chart canvas {
  max-width: 100%;
  height: auto;
}
</style>

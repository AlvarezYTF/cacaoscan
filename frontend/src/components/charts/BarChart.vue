<template>
  <div class="chart-container" :style="containerStyle">
    <canvas ref="chart"></canvas>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

export default {
  name: 'BarChart',
  props: {
    chartData: {
      type: Object,
      required: true
    },
    options: {
      type: Object,
      default: () => ({
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top',
          },
          tooltip: {
            enabled: true,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              display: true,
              color: 'rgba(0, 0, 0, 0.05)'
            }
          },
          x: {
            grid: {
              display: false
            }
          }
        }
      })
    },
    type: {
      type: String,
      default: 'bar'
    }
  },
  setup(props, { attrs }) {
    const chart = ref(null);
    let chartInstance = null;

    // Detecta si se pasa una clase de altura, si no, usa 16rem
    const containerStyle = computed(() => {
      const hasHeightClass = Object.keys(attrs).some(key => String(attrs[key]).includes('h-'));
      return hasHeightClass ? {} : { height: '16rem' };
    });

    const renderChart = () => {
      if (chartInstance) {
        chartInstance.destroy();
      }

      if (chart.value) {
        const ctx = chart.value.getContext('2d');
        chartInstance = new Chart(ctx, {
          type: props.type,
          data: props.chartData,
          options: props.options
        });
      }
    };

    onMounted(() => {
      renderChart();
    });

    watch(() => props.chartData, () => {
      renderChart();
    }, { deep: true });

    return {
      chart,
      containerStyle
    };
  }
};
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
  /* height: 100%;  <-- Elimina esta línea para que la altura sea controlada por el style o la clase */
}
</style>

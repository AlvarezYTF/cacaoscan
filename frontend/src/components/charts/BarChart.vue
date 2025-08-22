l<template>
  <div class="chart-container" :style="containerStyle">
    <canvas ref="chart"></canvas>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed, onUnmounted } from 'vue';
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
          },
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
    let resizeObserver = null;

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
          options: {
            ...props.options,
            responsive: true,
            maintainAspectRatio: false
          }
        });
      }
    };

    const handleResize = () => {
      if (chartInstance) {
        chartInstance.resize();
      }
    };

    onMounted(() => {
      renderChart();
      
      // Observador de cambios de tamaño para mejor responsividad
      if (window.ResizeObserver) {
        resizeObserver = new ResizeObserver(() => {
          handleResize();
        });
        if (chart.value) {
          resizeObserver.observe(chart.value);
        }
      }

      // Listener para cambios de orientación en dispositivos móviles
      window.addEventListener('orientationchange', handleResize);
      window.addEventListener('resize', handleResize);
    });

    onUnmounted(() => {
      if (chartInstance) {
        chartInstance.destroy();
      }
      if (resizeObserver) {
        resizeObserver.disconnect();
      }
      window.removeEventListener('orientationchange', handleResize);
      window.removeEventListener('resize', handleResize);
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
  min-height: 200px;
}

/* Media queries para mejor responsividad en dispositivos móviles */
@media (max-width: 768px) {
  .chart-container {
    min-height: 250px;
  }
}

@media (max-width: 480px) {
  .chart-container {
    min-height: 300px;
  }
}

/* Asegura que el canvas se ajuste al contenedor */
.chart-container canvas {
  max-width: 100%;
  height: auto;
}
</style>
<template>
    <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">Evolución de análisis por tipo de defecto</h3>
      <canvas ref="lineChart"></canvas>
    </div>
  </template>
  
  <script>
  import { ref, onMounted, watch } from 'vue';
  import { Chart, registerables } from 'chart.js';
  
  Chart.register(...registerables);
  
  export default {
    name: 'LineChart',
    props: {
      chartData: {
        type: Object,
        required: true,
        default: () => ({ datasets: [] })
      },
      chartOptions: {
        type: Object,
        default: () => ({
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
              labels: {
                usePointStyle: true,
                boxWidth: 10,
                padding: 20,
              },
            },
            tooltip: {
              mode: 'index',
              intersect: false,
            },
          },
          scales: {
            x: {
              grid: {
                display: false,
              },
            },
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 2,
              },
            },
          },
        })
      }
    },
    setup(props) {
      const lineChart = ref(null);
      let chartInstance = null;
  
      const createChart = () => {
        if (chartInstance) {
          chartInstance.destroy();
        }
        chartInstance = new Chart(lineChart.value, {
          type: 'line',
          data: props.chartData,
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'top',
              },
              title: {
                display: false,
                text: 'Evolución de análisis por tipo de defecto'
              }
            },
            scales: {
              y: {
                beginAtZero: true
              }
            },
            ...props.chartOptions
          }
        });
      };
  
      onMounted(() => {
        createChart();
      });
  
      watch(() => props.chartData, () => {
        createChart();
      }, { deep: true });
  
      watch(() => props.chartOptions, () => {
        createChart();
      }, { deep: true });
  
      return {
        lineChart
      };
    }
  };
  </script>
  
  <style scoped>
  /* Add any specific styles for the chart here */
  </style>
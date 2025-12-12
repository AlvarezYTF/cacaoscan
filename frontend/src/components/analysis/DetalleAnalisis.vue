<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto">
      <!-- Header con botón de regreso -->
      <div class="mb-8">
        <router-link 
          to="/nuevo-analisis"
          class="inline-flex items-center text-sm font-medium text-green-600 hover:text-green-500"
        >
          <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Volver a Nuevo Análisis
        </router-link>
      </div>

      <!-- Título principal -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Detalle del Análisis de Cacao</h1>
        <p class="mt-2 text-gray-600">Resultados completos del análisis de calidad</p>
      </div>

      <!-- Grid principal -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- Columna izquierda - Información General y Técnica -->
        <div class="lg:col-span-1 space-y-6">
          
          <!-- Información General -->
          <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <svg class="mr-2 h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Información General
            </h2>
            <div class="space-y-3">
              <div class="flex justify-between">
                <span class="text-gray-600">ID del Lote:</span>
                <span class="font-medium text-gray-900">Lote-2025-01</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Fecha y Hora:</span>
                <span class="font-medium text-gray-900">2025-08-20 14:35</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Ubicación:</span>
                <span class="font-medium text-gray-900">Finca El Paraíso - Huila</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Responsable:</span>
                <span class="font-medium text-gray-900">Juan Pérez</span>
              </div>
            </div>
          </div>

          <!-- Resultados Técnicos -->
          <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <svg class="mr-2 h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              Resultados Técnicos
            </h2>
            <div class="space-y-3">
              <div class="flex justify-between">
                <span class="text-gray-600">Peso promedio:</span>
                <span class="font-medium text-gray-900">1.2 g</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Tamaño promedio:</span>
                <span class="font-medium text-gray-900">25 mm</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Color predominante:</span>
                <span class="font-medium text-gray-900">Marrón</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Humedad estimada:</span>
                <span class="font-medium text-gray-900">7%</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Total de granos:</span>
                <span class="font-medium text-gray-900">150</span>
              </div>
            </div>
          </div>

          <!-- Indicador y Recomendación -->
          <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <svg class="mr-2 h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Clasificación y Recomendación
            </h2>
            <div class="space-y-4">
              <div class="text-center">
                <div class="text-3xl font-bold text-green-600 mb-2">82%</div>
                <div class="text-sm text-gray-600">Puntaje Total</div>
              </div>
              <div class="bg-green-50 border border-green-200 rounded-lg p-3">
                <div class="text-sm font-medium text-green-800 mb-1">Clasificación:</div>
                <div class="text-lg font-semibold text-green-900">Fino de Aroma</div>
              </div>
              <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <div class="text-sm font-medium text-blue-800 mb-1">Recomendación:</div>
                <div class="text-sm text-blue-900">El lote es apto para exportación. Mantener las prácticas actuales de fermentación.</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Columna derecha - Gráficos y Tabla -->
        <div class="lg:col-span-2 space-y-6">
          
          <!-- Clasificación de Calidad - Tabla -->
          <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <svg class="mr-2 h-6 w-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8 4s8 1.79 8 4" />
              </svg>
              Clasificación de Calidad
            </h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Tabla -->
              <div class="overflow-hidden">
                <table class="min-w-full divide-y divide-gray-200" aria-label="Tabla de detalles del análisis">
                  <caption class="sr-only">Tabla mostrando categoría, porcentaje y cantidad de granos de cacao</caption>
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Categoría</th>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Porcentaje</th>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cantidad</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr>
                      <td class="px-3 py-2 whitespace-nowrap text-sm font-medium text-gray-900">Bien Fermentados</td>
                      <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-900">65%</td>
                      <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-900">98</td>
                    </tr>
                    <tr>
                      <td class="px-3 py-2 whitespace-nowrap text-sm font-medium text-gray-900">Pizarrosos</td>
                      <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-900">15%</td>
                      <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-900">23</td>
                    </tr>
                    <tr>
                      <td class="px-3 py-2 whitespace-nowrap text-sm font-medium text-gray-900">Violetas</td>
                      <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-900">10%</td>
                      <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-900">15</td>
                    </tr>
                    <tr>
                      <td class="px-3 py-2 whitespace-nowrap text-sm font-medium text-gray-900">Dañados/Germinados</td>
                      <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-900">10%</td>
                      <td class="px-3 py-2 whitespace-nowrap text-sm text-gray-900">14</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Gráfico de Pastel -->
              <div class="flex items-center justify-center">
                <canvas ref="pieChart" width="200" height="200"></canvas>
              </div>
            </div>
          </div>

          <!-- Comparación con Análisis Anteriores -->
          <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <svg class="mr-2 h-6 w-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
              </svg>
              Comparación con Análisis Anteriores
            </h2>
            <div class="h-64">
              <canvas ref="barChart"></canvas>
            </div>
          </div>

          <!-- Acciones -->
          <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4">Acciones</h2>
            <div class="flex flex-wrap gap-3">
              <button class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
                <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Descargar PDF
              </button>
              <button class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                </svg>
                Compartir
              </button>
              <button class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
                <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Editar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import Chart from 'chart.js/auto';

export default {
  name: 'DetalleAnalisis',
  
  setup() {
    const pieChart = ref(null);
    const barChart = ref(null);
    let pieChartInstance = null;
    let barChartInstance = null;
    

    // Datos para el gráfico de pastel
    const pieData = [
      { name: 'Bien Fermentados', value: 65, color: '#10B981' },
      { name: 'Pizarrosos', value: 15, color: '#F59E0B' },
      { name: 'Violetas', value: 10, color: '#8B5CF6' },
      { name: 'Dañados/Germinados', value: 10, color: '#EF4444' }
    ];

    // Datos para el gráfico de barras
    const barData = [
      { name: 'Análisis 1', puntaje: 75 },
      { name: 'Análisis 2', puntaje: 80 },
      { name: 'Actual', puntaje: 82 }
    ];

    const createPieChart = () => {
      if (pieChart.value) {
        const ctx = pieChart.value.getContext('2d');
        if (pieChartInstance) {
          pieChartInstance.destroy();
        }
        pieChartInstance = new Chart(ctx, {
          type: 'pie',
          data: {
            labels: pieData.map(item => item.name),
            datasets: [{
              data: pieData.map(item => item.value),
              backgroundColor: pieData.map(item => item.color),
              borderWidth: 2,
              borderColor: '#ffffff'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'bottom',
                labels: {
                  padding: 20,
                  usePointStyle: true
                }
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    return `${context.label}: ${context.parsed}%`;
                  }
                }
              }
            }
          }
        });
      }
    };

    const createBarChart = () => {
      if (barChart.value) {
        const ctx = barChart.value.getContext('2d');
        if (barChartInstance) {
          barChartInstance.destroy();
        }
        barChartInstance = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: barData.map(item => item.name),
            datasets: [{
              label: 'Puntaje (%)',
              data: barData.map(item => item.puntaje),
              backgroundColor: '#10B981',
              borderColor: '#059669',
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                max: 100,
                ticks: {
                  callback: function(value) {
                    return value + '%';
                  }
                }
              }
            },
            plugins: {
              legend: {
                display: false
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    return `Puntaje: ${context.parsed.y}%`;
                  }
                }
              }
            }
          }
        });
      }
    };

    onMounted(async () => {
      await nextTick();
      createPieChart();
      createBarChart();
    });

    onUnmounted(() => {
      if (pieChartInstance) {
        pieChartInstance.destroy();
        pieChartInstance = null;
      }
      if (barChartInstance) {
        barChartInstance.destroy();
        barChartInstance = null;
      }
    });

    return {
      pieChart,
      barChart,
      createPieChart,
      createBarChart
    };
  }
};
</script>

<style scoped>
/* Estilos personalizados si son necesarios */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-gradient-to-r from-green-700 to-green-500 shadow">
      <div class="max-w-7xl mx-auto px-4 py-6">
        <h1 class="text-3xl font-extrabold text-white tracking-tight">Panel de Administración</h1>
      </div>
    </header>

    <!-- Main Content -->
    <main class="p-4 max-w-7xl mx-auto">
      <!-- Summary Cards -->
      <div class="grid grid-cols-1 gap-4 md:grid-cols-3 mb-8">
        <SummaryCard 
          title="Agricultores registrados" 
          :value="'221,324'" 
          icon="👨‍🌾"
          color="green"
        />
        <SummaryCard 
          title="Lotes analizados" 
          :value="'2,324'"
          icon="🌱"
          color="emerald"
        />
        <SummaryCard 
          title="Total de análisis" 
          :value="'16,703'"
          icon="📊"
          color="lime"
        />
      </div>

      <!-- Charts and Table -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <!-- Gráfico de líneas -->
        <div class="col-span-2 bg-white p-6 rounded-xl shadow-lg border border-green-100">
          <h2 class="text-lg font-semibold mb-4 text-green-800">
            Evolución de análisis 
          </h2>
          <BarChart 
            :chart-data="lineChartData"
            :chart-options="lineChartOptions"
            type="line"
            class="h-64"
          />
        </div>
        <!-- Gráfico de dona -->
        <div class="bg-white p-6 rounded-xl shadow-lg border border-green-100 flex flex-col items-center justify-center">
          <h2 class="text-lg font-semibold mb-4 text-green-800 text-center">
            Distribución por tipo de cacao
          </h2>
          <PieChart 
            :chart-data="doughnutChartData"
            :chart-options="doughnutChartOptions"
            class="h-64 w-full"
          />
        </div>
      </div>

      <!-- Últimos análisis realizados -->
      <div class="bg-white p-6 rounded-xl shadow-lg border border-green-100 mb-8">
        <h2 class="text-lg font-semibold mb-4 text-green-800">Últimos análisis realizados</h2>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-green-100">
            <thead>
              <tr>
                <th class="px-4 py-2 text-left text-xs font-bold text-green-700 uppercase">Agricultor</th>
                <th class="px-4 py-2 text-left text-xs font-bold text-green-700 uppercase">Lote</th>
                <th class="px-4 py-2 text-left text-xs font-bold text-green-700 uppercase">Resultado</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-green-50">
              <tr v-for="(item, idx) in paginatedAnalyses" :key="idx" class="hover:bg-green-50 transition">
                <td class="px-4 py-2 whitespace-nowrap text-black">{{ item.agricultor }}</td>
                <td class="px-4 py-2 whitespace-nowrap text-black">{{ item.lote }}</td>
                <td class="px-4 py-2 whitespace-nowrap text-black">{{ item.resultado }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <!-- Paginación simple -->
        <div class="flex justify-end mt-4 space-x-2">
          <button v-for="page in totalPages" :key="page" @click="currentPage = page" :class="['px-3 py-1 rounded font-semibold', currentPage === page ? 'bg-green-600 text-white' : 'bg-green-100 text-green-800 hover:bg-green-200']">
            {{ page }}
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import SummaryCard from '@/components/dashboard/SummaryCard.vue';
import BarChart from '@/components/charts/BarChart.vue';
import PieChart from '@/components/charts/PieChart.vue';

export default {
  name: 'AdminDashboard',
  components: { SummaryCard, BarChart, PieChart },
  setup() {
    // Datos de prueba para el gráfico de líneas (evolución por tipo de defecto)
    const lineChartData = ref({
      labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May'],
      datasets: [
        {
          label: 'Hongos',
          data: [12, 19, 3, 5, 2],
          borderColor: '#10B981',
          backgroundColor: 'rgba(16,185,129,0.2)',
          tension: 0.4,
        },
        {
          label: 'Fermentación',
          data: [7, 11, 5, 8, 13],
          borderColor: '#EF4444',
          backgroundColor: 'rgba(239,68,68,0.2)',
          tension: 0.4,
        },
        {
          label: 'Planos',
          data: [9, 7, 10, 15, 8],
          borderColor: '#3B82F6',
          backgroundColor: 'rgba(59,130,246,0.2)',
          tension: 0.4,
        },
        {
          label: 'Insectos',
          data: [5, 6, 7, 9, 10],
          borderColor: '#F59E0B',
          backgroundColor: 'rgba(245,158,11,0.2)',
          tension: 0.4,
        },
      ],
    });
    const lineChartOptions = ref({
      responsive: true,
      plugins: {
        legend: { position: 'top' },
      },
    });

    // Datos de prueba para el gráfico de dona (tipo de cacao)
    const doughnutChartData = ref({
      labels: ['Fino aroma', 'Común', 'Híbrido'],
      datasets: [
        {
          data: [40, 30, 30],
          backgroundColor: ['#F59E0B', '#2563EB', '#10B981'],
          borderWidth: 2,
        },
      ],
    });
    const doughnutChartOptions = ref({
      responsive: true,
      cutout: '70%',
      plugins: {
        legend: { position: 'bottom' },
      },
    });

    // Datos de prueba para la tabla de últimos análisisxx
    const analyses = ref([
      { agricultor: 'Camilo Hernandez', lote: 101, resultado: 'Aceptado' },
      { agricultor: 'Jeferson Alvarez', lote: 102, resultado: 'Condicional' },
      { agricultor: 'Cristian Camacho', lote: 103, resultado: 'Rechazado' },
      { agricultor: 'Juan Pablo Pérez', lote: 104, resultado: 'Aceptado' },
      { agricultor: 'Carlos Pérez', lote: 105, resultado: 'Aceptado' },
      { agricultor: 'María Gómez', lote: 106, resultado: 'Condicional' },
      { agricultor: 'Juan Torres', lote: 107, resultado: 'Rechazado' },
      { agricultor: 'Ana Ruiz', lote: 108, resultado: 'Aceptado' },
    ]);
    const currentPage = ref(1);
    const pageSize = 4;
    const totalPages = computed(() => Math.ceil(analyses.value.length / pageSize));
    const paginatedAnalyses = computed(() => {
      const start = (currentPage.value - 1) * pageSize;
      return analyses.value.slice(start, start + pageSize);
    });

    return {
      lineChartData,
      lineChartOptions,
      doughnutChartData,
      doughnutChartOptions,
      analyses,
      currentPage,
      totalPages,
      paginatedAnalyses,
    };
  },
};
</script>

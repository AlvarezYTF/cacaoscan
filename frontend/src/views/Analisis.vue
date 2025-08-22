<template>
  <div class="min-h-screen bg-gray-50 flex pb-8">
    <!-- Sidebar -->
    <AdminSidebar 
      user-initials="AD"
      user-name="Admin"
      user-role="Ver perfil"
    />
  
    <!-- Main Content -->
    <main class="flex-1 ml-16 md:ml-64">
      <!-- Header -->
      <PageHeader 
        title="Análisis"
        subtitle="Gestión de análisis de calidad de cacao"
      />
  
      <!-- Contenido principal -->
      <div class="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8 py-4 md:py-8">
        <!-- Barra de acciones -->
        <div class="mb-4 md:mb-6">
          <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center space-y-3 sm:space-y-0">
            <div>
              <h2 class="text-lg md:text-xl font-semibold text-gray-800">Análisis de Calidad</h2>
              <p class="text-xs md:text-sm text-gray-500">Gestiona los análisis de calidad de granos de cacao</p>
            </div>
            <div class="flex flex-col sm:flex-row items-stretch sm:items-center space-y-2 sm:space-y-0 sm:space-x-3">
              <SearchBar 
                v-model="searchQuery"
                placeholder="Buscar análisis..."
              />
              <ActionButton 
                label="Nuevo Análisis"
                short-label="+ Nuevo"
                variant="primary"
                icon="PlusIcon"
                @click="handleNewAnalysis"
              />
            </div>
          </div>
        </div>
  
        <!-- Filtros -->
        <div class="mb-4 md:mb-6 bg-white p-3 md:p-4 rounded-lg shadow-sm border border-gray-200">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
            <FilterSelect 
              id="agricultor"
              label="Agricultor"
              v-model="filters.agricultor"
              :options="farmerOptions"
            />
            <FilterSelect 
              id="resultado"
              label="Resultado"
              v-model="filters.resultado"
              :options="resultOptions"
            />
            <DateInput 
              id="fecha"
              label="Fecha"
              v-model="filters.fecha"
            />
            <div class="sm:col-span-2 lg:col-span-1 flex items-end">
              <ActionButton 
                label="Aplicar Filtros"
                variant="secondary"
                @click="applyFilters"
              />
            </div>
          </div>
        </div>
  
        <!-- Tarjetas de resumen -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-4 md:mb-6">
          <StatsCard 
            title="Análisis Aceptados"
            :value="stats.aceptados"
            :change="stats.aceptadosChange"
            icon="CheckIcon"
            variant="success"
          />
          <StatsCard 
            title="Análisis Condicionales"
            :value="stats.condicionales"
            :change="stats.condicionalesChange"
            icon="ExclamationIcon"
            variant="warning"
          />
          <StatsCard 
            title="Análisis Rechazados"
            :value="stats.rechazados"
            :change="stats.rechazadosChange"
            icon="XIcon"
            variant="danger"
          />
          <StatsCard 
            title="Total Análisis"
            :value="stats.total"
            :change="stats.totalChange"
            icon="ChartBarIcon"
            variant="info"
          />
        </div>
  
        <!-- Tabla de análisis -->
        <AnalysisTable 
          :analyses="filteredAnalyses"
          :total-items="totalItems"
        />
      </div>
    </main>
  </div>
</template>
  
<script>
import { ref, computed, onMounted } from 'vue';
import AdminSidebar from '@/components/analisis/AdminSidebar.vue';
import PageHeader from '@/components/analisis/PageHeader.vue';
import SearchBar from '@/components/analisis/SearchBar.vue';
import ActionButton from '@/components/analisis/ActionButton.vue';
import FilterSelect from '@/components/analisis/FilterSelect.vue';
import DateInput from '@/components/analisis/DateInput.vue';
import StatsCard from '@/components/analisis/StatsCard.vue';
import AnalysisTable from '@/components/analisis/AnalysisTable.vue';

export default {
  name: 'AnalisisView',
  components: {
    AdminSidebar,
    PageHeader,
    SearchBar,
    ActionButton,
    FilterSelect,
    DateInput,
    StatsCard,
    AnalysisTable
  },
  setup() {
    // Estado reactivo
    const searchQuery = ref('');
    const filters = ref({
      agricultor: '',
      resultado: '',
      fecha: ''
    });

    // Datos de análisis
    const analyses = ref([
      {
        id: '#AN-001',
        farmerInitials: 'CH',
        farmerName: 'Camilo Hernandez',
        batch: 'Lote #101',
        date: '15/06/2023',
        status: 'Aceptado',
        quality: 87
      },
      {
        id: '#AN-002',
        farmerInitials: 'JA',
        farmerName: 'Jeferson Alvarez',
        batch: 'Lote #102',
        date: '18/06/2023',
        status: 'Condicional',
        quality: 65
      },
      {
        id: '#AN-003',
        farmerInitials: 'CC',
        farmerName: 'Cristian Camacho',
        batch: 'Lote #103',
        date: '20/06/2023',
        status: 'Rechazado',
        quality: 35
      },
      {
        id: '#AN-004',
        farmerInitials: 'JP',
        farmerName: 'Juan Pablo Pérez',
        batch: 'Lote #104',
        date: '22/06/2023',
        status: 'Aceptado',
        quality: 92
      }
    ]);

    // Opciones para filtros
    const farmerOptions = ref([
      { value: '', label: 'Todos los agricultores' },
      { value: 'camilo', label: 'Camilo Hernandez' },
      { value: 'jeferson', label: 'Jeferson Alvarez' },
      { value: 'cristian', label: 'Cristian Camacho' },
      { value: 'juan', label: 'Juan Pablo Pérez' }
    ]);

    const resultOptions = ref([
      { value: '', label: 'Todos los resultados' },
      { value: 'aceptado', label: 'Aceptado' },
      { value: 'condicional', label: 'Condicional' },
      { value: 'rechazado', label: 'Rechazado' }
    ]);

    // Estadísticas
    const stats = ref({
      aceptados: 124,
      aceptadosChange: 8,
      condicionales: 45,
      condicionalesChange: 3,
      rechazados: 12,
      rechazadosChange: 2,
      total: 181,
      totalChange: 5
    });

    // Computed properties
    const filteredAnalyses = computed(() => {
      let filtered = analyses.value;

      // Filtro por búsqueda
      if (searchQuery.value) {
        filtered = filtered.filter(analysis => 
          analysis.farmerName.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          analysis.id.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          analysis.batch.toLowerCase().includes(searchQuery.value.toLowerCase())
        );
      }

      // Filtro por agricultor
      if (filters.value.agricultor) {
        filtered = filtered.filter(analysis => 
          analysis.farmerName.toLowerCase().includes(filters.value.agricultor.toLowerCase())
        );
      }

      // Filtro por resultado
      if (filters.value.resultado) {
        filtered = filtered.filter(analysis => 
          analysis.status.toLowerCase() === filters.value.resultado.toLowerCase()
        );
      }

      // Filtro por fecha
      if (filters.value.fecha) {
        filtered = filtered.filter(analysis => 
          analysis.date === filters.value.fecha
        );
      }

      return filtered;
    });

    const totalItems = computed(() => filteredAnalyses.value.length);

    // Métodos
    const handleNewAnalysis = () => {
      console.log('Nuevo análisis');
      // Aquí iría la lógica para crear un nuevo análisis
    };

    const applyFilters = () => {
      console.log('Aplicando filtros:', filters.value);
      // Aquí iría la lógica para aplicar filtros
    };

    // Lifecycle
    onMounted(() => {
      console.log('Vista de análisis montada');
    });

    return {
      searchQuery,
      filters,
      analyses,
      farmerOptions,
      resultOptions,
      stats,
      filteredAnalyses,
      totalItems,
      handleNewAnalysis,
      applyFilters
    };
  }
};
</script>

<style scoped>
/* Estilos adicionales específicos de la vista si son necesarios */
</style>
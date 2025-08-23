<template>
  <div class="bg-gray-50 min-h-screen">
    <div class="flex h-screen">
      <!-- Sidebar -->
      <AdminSidebar 
        :user-initials="userInitials"
        :user-name="userName"
        :user-role="userRole"
        :sidebar-collapsed="sidebarCollapsed"
        @toggle-sidebar="toggleSidebar"
      />
      
      <!-- Contenido principal -->
      <div class="flex-1 flex flex-col min-w-0 overflow-hidden" :class="{ 'main-expanded': sidebarCollapsed }">
        <!-- Header de la página -->
        <PageHeader 
          title="Reportes"
          subtitle="Genera y gestiona reportes de análisis"
        >
        </PageHeader>
        
        <!-- Contenido principal -->
        <main class="flex-1 p-4 md:p-6 lg:p-8 pb-0 overflow-y-auto">
          <!-- Tarjetas de estadísticas -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-4 md:mb-6">
            <StatsCard 
              title="Total de Reportes"
              :value="stats.totalReports"
              :change="stats.reportsChange"
              icon="DocumentTextIcon"
              variant="info"
            />
            <StatsCard 
              title="Reportes Completados"
              :value="stats.completedReports"
              :change="stats.completedChange"
              icon="CheckCircleIcon"
              variant="success"
            />
            <StatsCard 
              title="En Proceso"
              :value="stats.inProgressReports"
              :change="stats.inProgressChange"
              icon="ClockIcon"
              variant="warning"
            />
            <StatsCard 
              title="Con Errores"
              :value="stats.errorReports"
              :change="stats.errorChange"
              icon="ExclamationTriangleIcon"
              variant="danger"
            />
          </div>

          <!-- Filtros y controles -->
          <div class="mb-4 md:mb-6">
            <div class="flex gap-4 items-center justify-between">
              <div class="flex gap-4">
                <PeriodSelector 
                  v-model="selectedPeriod"
                  :options="periodOptions"
                  @update:model-value="handlePeriodChange"
                />
              </div>
              
              <div class="flex gap-2">
                <ActionButton 
                  label="Generar Reporte"
                  short-label="Generar"
                  variant="secondary"
                  icon="ChartBarIcon"
                  @click="handleGenerateReport"
                />
                <ActionButton 
                  label="Exportar"
                  short-label="Exportar"
                  variant="secondary"
                  icon="ArrowDownTrayIcon"
                  @click="handleExport"
                />
              </div>
            </div>
          </div>
          
          <!-- Tabla de reportes -->
          <div class="flex-1 min-h-0">
            <ReportsTable 
              :reports="reports"
              :loading="loading"
              @view="handleViewReport"
              @download="handleDownloadReport"
              @delete="handleDeleteReport"
              @sort="handleSort"
            />
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import AdminSidebar from '@/components/common/AdminSidebar.vue';
import PageHeader from '@/components/reportes/PageHeader.vue';
import PeriodSelector from '@/components/reportes/PeriodSelector.vue';
import ActionButton from '@/components/reportes/ActionButton.vue';
import StatsCard from '@/components/reportes/StatsCard.vue';
import ReportsTable from '@/components/reportes/ReportsTable.vue';

export default {
  name: 'Reportes',
  components: {
    AdminSidebar,
    PageHeader,
    PeriodSelector,
    ActionButton,
    StatsCard,
    ReportsTable
  },
  setup() {
    // Estado reactivo
    const selectedPeriod = ref('month');
    const loading = ref(false);
    const sidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true');
    
    // Datos de usuario
    const userInitials = ref('JD');
    const userName = ref('Juan Doe');
    const userRole = ref('Administrador');
    
    // Opciones del selector de período
    const periodOptions = [
      { value: 'week', label: 'Esta Semana' },
      { value: 'month', label: 'Este Mes' },
      { value: 'quarter', label: 'Este Trimestre' },
      { value: 'year', label: 'Este Año' },
      { value: 'custom', label: 'Personalizado' }
    ];
    
    // Estadísticas
    const stats = ref({
      totalReports: 156,
      reportsChange: 12,
      completedReports: 142,
      completedChange: 8,
      inProgressReports: 8,
      inProgressChange: -3,
      errorReports: 6,
      errorChange: -2
    });
    
    // Lista de reportes
    const reports = ref([
      {
        id: 1,
        name: 'Reporte Mensual de Producción',
        type: 'Producción',
        period: 'Enero 2024',
        createdAt: '15/01/2024',
        status: 'Completado'
      },
      {
        id: 2,
        name: 'Análisis de Calidad Q1',
        type: 'Calidad',
        period: 'Q1 2024',
        createdAt: '10/01/2024',
        status: 'En Proceso'
      },
      {
        id: 3,
        name: 'Reporte de Rendimiento Anual',
        type: 'Rendimiento',
        period: '2023',
        createdAt: '05/01/2024',
        status: 'Completado'
      },
      {
        id: 4,
        name: 'Análisis de Costos',
        type: 'Financiero',
        period: 'Diciembre 2023',
        createdAt: '30/12/2023',
        status: 'Completado'
      },
      {
        id: 5,
        name: 'Reporte de Inventario',
        type: 'Inventario',
        period: 'Enero 2024',
        createdAt: '20/01/2024',
        status: 'Pendiente'
      }
    ]);
    
    // Métodos
    const toggleSidebar = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value;
      localStorage.setItem('sidebarCollapsed', sidebarCollapsed.value);
    };
    
    const handlePeriodChange = (period) => {
      selectedPeriod.value = period;
      // Aquí se podría hacer una llamada a la API para obtener reportes del período seleccionado
      console.log('Período cambiado:', period);
    };
    
    const handleNewReport = () => {
      console.log('Crear nuevo reporte');
      // Implementar lógica para crear nuevo reporte
    };
    
    const handleGenerateReport = () => {
      console.log('Generar reporte para período:', selectedPeriod.value);
      // Implementar lógica para generar reporte
    };
    
    const handleExport = () => {
      console.log('Exportar reportes');
      // Implementar lógica para exportar
    };
    
    const handleViewReport = (report) => {
      console.log('Ver reporte:', report);
      // Implementar lógica para ver reporte
    };
    
    const handleDownloadReport = (report) => {
      console.log('Descargar reporte:', report);
      // Implementar lógica para descargar
    };
    
    const handleDeleteReport = (report) => {
      console.log('Eliminar reporte:', report);
      // Implementar lógica para eliminar
    };
    
    const handleSort = ({ key, order }) => {
      console.log('Ordenar por:', key, 'orden:', order);
      // Implementar lógica de ordenamiento
    };
    
    // Lifecycle
    onMounted(() => {
      // Cargar datos iniciales
      console.log('Vista Reportes montada');
      checkScreenSize();
      window.addEventListener('resize', checkScreenSize);
    });
    
    const checkScreenSize = () => {
      if (window.innerWidth <= 768) {
        sidebarCollapsed.value = true;
        localStorage.setItem('sidebarCollapsed', 'true');
      }
    };
    
    return {
      // Estado
      selectedPeriod,
      loading,
      sidebarCollapsed,
      userInitials,
      userName,
      userRole,
      
      // Datos
      periodOptions,
      stats,
      reports,
      
      // Métodos
      toggleSidebar,
      handlePeriodChange,
      handleNewReport,
      handleGenerateReport,
      handleExport,
      handleViewReport,
      handleDownloadReport,
      handleDeleteReport,
      handleSort
    };
  }
};
</script>

<style scoped>
/* Estilos específicos para la vista de reportes */
.min-h-screen {
  min-height: 100vh;
}

.h-screen {
  height: 100vh;
}

/* Asegurar que el contenido principal no se desborde */
.min-w-0 {
  min-width: 0;
}

/* Eliminar espacio blanco excesivo */
.flex-1 {
  flex: 1 1 0%;
}

/* Asegurar que el contenido principal ocupe toda la altura disponible */
main {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

/* Controlar el overflow */
.overflow-hidden {
  overflow: hidden;
}

.overflow-y-auto {
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

/* Asegurar que el contenido se ajuste correctamente */
.flex.flex-col {
  display: flex;
  flex-direction: column;
}

/* Asegurar que el contenido se ajuste al viewport */
.min-h-0 {
  min-height: 0;
}

/* Layout específico para la vista de reportes */
.bg-gray-50 {
  background-color: #f9fafb;
}

/* Asegurar que el sidebar y contenido principal se alineen correctamente */
.flex.h-screen {
  height: 100vh;
  max-height: 100vh;
}

/* Estilos para cuando el sidebar está colapsado */
.main-expanded {
  margin-left: 0;
  transition: margin-left 0.3s ease;
}

/* Transición suave para el contenido principal */
.flex-1.flex.flex-col {
  transition: margin-left 0.3s ease;
}

/* Mejoras de responsividad */
@media (max-width: 768px) {
  .p-4 {
    padding: 1rem;
  }
  
  .md\:p-6 {
    padding: 1.5rem;
  }
  
  .mb-6 {
    margin-bottom: 1rem;
  }
  
  .mb-8 {
    margin-bottom: 1.5rem;
  }
  
  /* Ajustar el grid en tablets */
  .md\:grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  /* Reducir padding inferior en móviles */
  .pb-0 {
    padding-bottom: 0;
  }
  
  /* Asegurar que el layout se ajuste en móviles */
  .h-screen {
    height: 100vh;
    min-height: 100vh;
  }
  
  /* Ajustar el overflow en móviles */
  .overflow-y-auto {
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }
  
  .overflow-y-auto::-webkit-scrollbar {
    display: none;
  }
  
  /* Asegurar que el sidebar esté colapsado en móviles */
  .sidebar-collapsed {
    width: 70px;
  }
  
  /* Ajustar el contenido principal en móviles */
  .main-expanded {
    margin-left: 0;
  }
}

@media (max-width: 640px) {
  .p-4 {
    padding: 0.75rem;
  }
  
  .mb-6 {
    margin-bottom: 0.75rem;
  }
  
  .mb-8 {
    margin-bottom: 1rem;
  }
  
  .gap-4 {
    gap: 0.75rem;
  }
  
  /* Forzar una columna en móviles */
  .md\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  /* Eliminar padding inferior en pantallas pequeñas */
  .pb-0 {
    padding-bottom: 0;
  }
}

@media (max-width: 480px) {
  .p-4 {
    padding: 0.5rem;
  }
  
  .mb-6 {
    margin-bottom: 0.5rem;
  }
  
  .mb-8 {
    margin-bottom: 0.75rem;
  }
  
  .gap-4 {
    gap: 0.5rem;
  }
  
  /* Una sola columna en pantallas muy pequeñas */
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  /* Ajustar espaciado de botones en móviles */
  .flex.gap-2 {
    gap: 0.5rem;
  }
  
  /* Eliminar padding inferior en pantallas muy pequeñas */
  .pb-0 {
    padding-bottom: 0;
  }
  
  /* Asegurar que el layout se ajuste en pantallas muy pequeñas */
  .h-screen {
    height: 100vh;
    min-height: 100vh;
  }
  
  /* Ajustar el contenido para pantallas muy pequeñas */
  main {
    padding: 0.5rem;
  }
  
  /* Reducir espaciado en pantallas muy pequeñas */
  .mb-4 {
    margin-bottom: 0.5rem;
  }
  
  /* Asegurar que el sidebar esté completamente colapsado en pantallas muy pequeñas */
  .sidebar-collapsed {
    width: 60px;
  }
  
  /* Ajustar el contenido principal en pantallas muy pequeñas */
  .main-expanded {
    margin-left: 0;
  }
}

/* Transiciones suaves */
* {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

/* Mejoras para dispositivos táctiles */
@media (hover: none) and (pointer: coarse) {
  .min-h-screen {
    min-height: 100vh;
  }
  
  /* Asegurar que los botones tengan el tamaño mínimo táctil */
  button {
    min-height: 44px;
    min-width: 44px;
  }
}

/* Responsive para pantallas muy grandes */
@media (min-width: 1280px) {
  .lg\:p-8 {
    padding: 2rem;
  }
  
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

/* Mejoras para orientación landscape en móviles */
@media (max-width: 768px) and (orientation: landscape) {
  .p-4 {
    padding: 0.75rem;
  }
  
  .mb-6 {
    margin-bottom: 1rem;
  }
  
  .mb-8 {
    margin-bottom: 1.5rem;
  }
}

/* Animaciones de entrada */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

main {
  animation: fadeIn 0.5s ease-out;
}

/* Mejoras para accesibilidad */
*:focus {
  outline: 2px solid #10b981;
  outline-offset: 2px;
}

/* Estados de carga */
.loading {
  opacity: 0.6;
  pointer-events: none;
}

/* Mejoras para tablas responsivas */
@media (max-width: 640px) {
  .grid-cols-1 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .md\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  /* Ajustar el layout de filtros en móviles */
  .flex-col.sm\:flex-row {
    flex-direction: column;
  }
  
  .items-start.sm\:items-center {
    align-items: flex-start;
  }
  
  .justify-between {
    justify-content: flex-start;
  }
  
  .flex.gap-2 {
    margin-top: 1rem;
    width: 100%;
    justify-content: space-between;
  }
}

@media (max-width: 480px) {
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  /* Ajustar espaciado en pantallas muy pequeñas */
  .space-y-1 > * + * {
    margin-top: 0.25rem;
  }
  
  .space-y-1 > * + * {
    margin-top: 0.25rem;
  }
}

/* Mejoras para el scroll en móviles */
@media (max-width: 640px) {
  .overflow-x-auto {
    -webkit-overflow-scrolling: touch;
    scrollbar-width: thin;
  }
}

/* Optimizaciones para pantallas de alta densidad */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
  .bg-white {
    image-rendering: -webkit-optimize-contrast;
    image-rendering: crisp-edges;
  }
}

/* Mejoras para dispositivos con pantallas pequeñas y alta densidad */
@media (max-width: 640px) and (-webkit-min-device-pixel-ratio: 2) {
  .text-sm {
    font-size: 0.8125rem;
  }
  
  .text-xs {
    font-size: 0.6875rem;
  }
}
</style>
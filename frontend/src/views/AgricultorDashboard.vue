<template>
  <div class="farmer-dashboard">
    <DashboardHeader :farmer-name="farmerName" />
    
    <QuickActions @upload="openUploadModal" />
    
    <UploadSection @file-upload="handleFileUpload" />
    
    <RecentAnalyses 
      :analyses="recentAnalyses" 
      @view-details="viewAnalysisDetails" 
    />
    
    <StatsOverview :stats="stats" />
  </div>
</template>

<script>
import DashboardHeader from '@/components/dashboard/DashboardHeader.vue';
import QuickActions from '@/components/dashboard/QuickActions.vue';
import UploadSection from '@/components/dashboard/UploadSection.vue';
import RecentAnalyses from '@/components/dashboard/RecentAnalyses.vue';
import StatsOverview from '@/components/dashboard/StatsOverview.vue';

export default {
  name: 'AgricultorDashboard',
  components: {
    DashboardHeader,
    QuickActions,
    UploadSection,
    RecentAnalyses,
    StatsOverview
  },
  data() {
    return {
      farmerName: 'Juan Pérez',
      recentAnalyses: [
        {
          id: 'CAC-2023-045',
          status: 'completed',
          statusLabel: 'Completado',
          quality: 92,
          defects: 3.2,
          avgSize: 12.5,
          date: '15/08/2023'
        },
        {
          id: 'CAC-2023-044',
          status: 'completed',
          statusLabel: 'Completado',
          quality: 88,
          defects: 5.1,
          avgSize: 11.8,
          date: '10/08/2023'
        },
        {
          id: 'CAC-2023-043',
          status: 'completed',
          statusLabel: 'Completado',
          quality: 85,
          defects: 6.7,
          avgSize: 12.1,
          date: '05/08/2023'
        }
      ],
      stats: {
        totalBatches: 24,
        batchesChange: '+5%',
        avgQuality: 87,
        qualityChange: '+2%',
        defectRate: 5.2,
        defectChange: '-1.2%'
      }
    };
  },
  methods: {
    openUploadModal() {
      // This will be handled by the UploadSection component
    },
    handleFileUpload(files) {
      console.log('Archivos seleccionados:', files);
      // Implementar lógica para manejar la carga de archivos
      // Por ejemplo, subir a un servidor o procesar las imágenes
    },
    viewAnalysisDetails(analysis) {
      console.log('Ver detalles del análisis:', analysis);
      // Navegar a la vista de detalles o mostrar un modal
    }
  }
};
</script>

<style>
.farmer-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #2c3e50;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .farmer-dashboard {
    padding: 1rem;
  }
}
</style>

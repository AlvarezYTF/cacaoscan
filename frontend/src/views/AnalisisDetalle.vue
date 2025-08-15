<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
      <!-- Header with back button -->
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

      <!-- Main Content -->
      <div class="bg-white shadow rounded-lg overflow-hidden">
        <AnalysisHeader :analysis-id="analysisId" />

        <!-- Loading State -->
        <LoadingSpinner v-if="loading" message="Cargando resultados del análisis..." />

        <!-- Error State -->
        <div v-else-if="error" class="p-6">
          <ErrorAlert :message="error" />
          <div class="mt-4 text-center">
            <button
              @click="fetchAnalysisDetails"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              Reintentar
            </button>
          </div>
        </div>

        <!-- Analysis Results -->
        <div v-else class="p-6">
          <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
            <!-- Batch Information -->
            <BatchInfoCard :data="{
              batchName: analysisData.batchName,
              collectionDate: analysisData.collectionDate,
              origin: analysisData.origin,
              notes: analysisData.notes
            }" />

            <!-- Analysis Summary -->
            <AnalysisSummaryCard 
              :quality-score="analysisData.qualityScore || 0"
              :defect-count="analysisData.defectCount || 0"
              :metrics="analysisData.metrics || []"
            />
          </div>

          <!-- Images Grid -->
          <ImageGallery 
            :images="analysisData.images || []" 
            @image-click="openImageModal"
          />

          <!-- Actions -->
          <AnalysisActions 
            @download-pdf="downloadPdf"
            @new-analysis="startNewAnalysis"
          />
        </div>
      </div>
    </div>

    <!-- Image Modal -->
    <ImageModal 
      v-if="selectedImage"
      :show="!!selectedImage"
      :image="selectedImage"
      @close="selectedImage = null"
    />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

// Components
import AnalysisHeader from '@/components/analysis/AnalysisHeader.vue';
import BatchInfoCard from '@/components/analysis/BatchInfoCard.vue';
import AnalysisSummaryCard from '@/components/analysis/AnalysisSummaryCard.vue';
import ImageGallery from '@/components/analysis/ImageGallery.vue';
import ImageModal from '@/components/analysis/ImageModal.vue';
import AnalysisActions from '@/components/analysis/AnalysisActions.vue';
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';
import ErrorAlert from '@/components/common/ErrorAlert.vue';

export default {
  name: 'AnalisisDetalle',
  
  components: {
    AnalysisHeader,
    BatchInfoCard,
    AnalysisSummaryCard,
    ImageGallery,
    ImageModal,
    AnalysisActions,
    LoadingSpinner,
    ErrorAlert
  },
  
  setup() {
    const route = useRoute();
    const router = useRouter();
    
    const analysisId = ref(route.params.id);
    const loading = ref(true);
    const error = ref(null);
    const selectedImage = ref(null);
    
    // Mock data - replace with actual API call
    const analysisData = ref({
      batchName: 'Lote de Cacao #123',
      collectionDate: '2023-06-15',
      origin: 'Piura',
      notes: 'Lote de cosecha temprana',
      qualityScore: 87,
      defectCount: 5,
      metrics: [
        { name: 'Humedad', value: '7.2%' },
        { name: 'Granos por 100g', value: '420' },
        { name: 'Tamaño promedio', value: '1.2cm' },
        { name: 'Fermentación', value: '85%' },
      ],
      images: Array(6).fill().map((_, i) => ({
        id: i + 1,
        thumbnailUrl: `https://picsum.photos/seed/cacao-${i+1}/300/200`,
        fullSizeUrl: `https://picsum.photos/seed/cacao-${i+1}/1200/800`,
        defects: [
          { type: 'Dañado', confidence: 92 },
          { type: 'Mohoso', confidence: 87 },
        ].slice(0, Math.floor(Math.random() * 3) + 1) // Random defects for demo
      }))
    });

    const fetchAnalysisDetails = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        // TODO: Replace with actual API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Simulate API error (for testing)
        // throw new Error('No se pudo cargar el análisis. Por favor, intente nuevamente.');
        
      } catch (err) {
        error.value = err.message || 'Error al cargar los detalles del análisis';
        console.error('Error fetching analysis details:', err);
      } finally {
        loading.value = false;
      }
    };

    const openImageModal = (image) => {
      selectedImage.value = image;
    };

    const startNewAnalysis = () => {
      router.push({ name: 'nuevo-analisis' });
    };

    const downloadPdf = () => {
      // TODO: Implement PDF download functionality
      console.log('Downloading PDF...');
    };

    onMounted(() => {
      fetchAnalysisDetails();
    });

    return {
      analysisId,
      loading,
      error,
      analysisData,
      selectedImage,
      openImageModal,
      fetchAnalysisDetails,
      startNewAnalysis,
      downloadPdf
    };
  }
};
</script>

<style scoped>
/* Custom styles if needed */
</style>

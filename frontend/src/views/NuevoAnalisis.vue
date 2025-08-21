<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
      <!-- Page Header -->
      <PageHeader
        title="Nuevo Análisis de Lote"
        description="Sube imágenes de granos de cacao y completa la información del lote para iniciar un análisis de calidad detallado y preciso."
      />

      <!-- Main Content -->
      <div class="bg-white shadow rounded-lg overflow-hidden">
        <div class="p-6 space-y-8">
          <!-- Progress Indicator -->
          <ProgressIndicator
            v-if="isUploading"
            :progress="uploadProgress"
            label="Procesando imágenes..."
          />

          <!-- Error Alert -->
          <ErrorAlert
            v-if="error"
            :message="error"
          />

          <!-- Success Alert -->
          <div v-if="analysisResult" class="bg-green-50 border-l-4 border-green-400 p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-green-800">
                  Análisis completado exitosamente
                </p>
                <div class="mt-2">
                  <p class="text-sm text-green-700">
                    ID de análisis: {{ analysisResult.analysisId }}
                  </p>
                  <div class="mt-2">
                    <router-link
                      :to="{ name: 'analisis-detalle', params: { id: analysisResult.analysisId } }"
                      class="inline-flex items-center text-sm font-medium text-green-700 hover:text-green-600"
                    >
                      Ver resultados detallados
                      <svg class="ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                      </svg>
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Batch Info Form -->
          <BatchInfoForm
            v-model="batchData"
            :errors="formErrors"
            @update:modelValue="updateBatchData"
          />

          <!-- Image Capture Section -->
          <div class="space-y-4">
            <h2 class="text-lg font-medium text-gray-900">Imágenes del Lote</h2>

            <!-- Tabs -->
            <div class="border-b border-gray-200">
              <nav class="-mb-px flex space-x-8">
                <button
                  v-for="tab in tabs"
                  :key="tab.name"
                  @click="currentTab = tab.name"
                  :class="[
                    currentTab === tab.name
                      ? 'border-green-500 text-green-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                    'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
                  ]"
                >
                  {{ tab.label }}
                </button>
              </nav>
            </div>

            <!-- Tab Content -->
            <div class="mt-4">
              <!-- File Upload Tab -->
              <div v-if="currentTab === 'upload'">
                <ImageUploader
                  v-model="images"
                  @update:modelValue="updateImages"
                />
              </div>

              <!-- Camera Capture Tab -->
              <div v-else-if="currentTab === 'camera'" class="space-y-4">
                <CameraCapture @capture="handleCapturedImage" />

                <!-- Captured Images Preview -->
                <div v-if="capturedImages.length > 0" class="mt-4">
                  <h3 class="text-sm font-medium text-gray-700 mb-2">Fotos tomadas:</h3>
                  <div class="grid grid-cols-3 gap-2">
                    <div v-for="(img, index) in capturedImages" :key="index" class="relative">
                      <img :src="URL.createObjectURL(img)" class="w-full h-24 object-cover rounded" />
                      <button
                        @click="removeCapturedImage(index)"
                        class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs hover:bg-red-600"
                      >
                        
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Submit Button -->
          <div class="pt-4">
            <button
              type="button"
              @click="submitAnalysis"
              :disabled="isSubmitting || !isFormValid"
              class="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg v-if="isSubmitting" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isSubmitting ? 'Procesando...' : 'Iniciar Análisis' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useAnalysisStore } from '@/stores/analysis';
import PageHeader from '@/components/common/PageHeader.vue';
import ProgressIndicator from '@/components/common/ProgressIndicator.vue';
import ErrorAlert from '@/components/common/ErrorAlert.vue';
import BatchInfoForm from '@/components/analysis/BatchInfoForm.vue';
import ImageUploader from '@/components/analysis/ImageUploader.vue';
import CameraCapture from '@/components/analysis/CameraCapture.vue';

export default {
  name: 'NuevoAnalisis',
  components: {
    PageHeader,
    ProgressIndicator,
    ErrorAlert,
    BatchInfoForm,
    ImageUploader,
    CameraCapture
  },
  setup() {
    const analysisStore = useAnalysisStore();

    // Local state
    const batchData = ref({
      name: '',
      collectionDate: '',
      origin: '',
      notes: ''
    });

    const images = ref([]);
    const capturedImages = ref([]);
    const currentTab = ref('upload');
    const isSubmitting = ref(false);
    const formErrors = ref({});
    const analysisResult = ref(null);

    // Tabs configuration
    const tabs = [
      { name: 'upload', label: 'Subir imágenes' },
      { name: 'camera', label: 'Tomar foto' }
    ];

    // Watch for changes in captured images and update the main images array
    watch(capturedImages, (newVal) => {
      // Combine uploaded images and captured images
      const uploadedImages = images.value.filter(img => !capturedImages.value.includes(img));
      images.value = [...uploadedImages, ...newVal];
    }, { deep: true });

    // Computed properties
    const isFormValid = computed(() => {
      return (
        batchData.value.name.trim() !== '' &&
        batchData.value.collectionDate &&
        images.value.length > 0
      );
    });

    const uploadProgress = computed(() => {
      return analysisStore.uploadProgress;
    });

    const isUploading = computed(() => {
      return analysisStore.isUploading;
    });

    const error = computed(() => {
      return analysisStore.uploadError;
    });

    // Methods
    const updateBatchData = (data) => {
      batchData.value = { ...data };
    };

    const updateImages = (newImages) => {
      // Only update non-captured images
      const nonCapturedImages = newImages.filter(img => !capturedImages.value.includes(img));
      images.value = [...nonCapturedImages, ...capturedImages.value];
    };

    const handleCapturedImage = (imageFile) => {
      // Add the captured image to our array
      if (!capturedImages.value.some(img => img.name === imageFile.name)) {
        capturedImages.value = [...capturedImages.value, imageFile];
      }
    };

    const removeCapturedImage = (index) => {
      const updatedImages = [...capturedImages.value];
      updatedImages.splice(index, 1);
      capturedImages.value = updatedImages;
    };

    const validateForm = () => {
      const errors = {};

      if (!batchData.value.name.trim()) {
        errors.name = 'El nombre del lote es requerido';
      }

      if (!batchData.value.collectionDate) {
        errors.collectionDate = 'La fecha de recolección es requerida';
      }

      if (images.value.length === 0) {
        errors.images = 'Debes subir al menos una imagen';
      }

      formErrors.value = errors;
      return Object.keys(errors).length === 0;
    };

    const submitAnalysis = async () => {
      if (!validateForm()) return;

      try {
        isSubmitting.value = true;
        analysisResult.value = null;

        // Update store with form data
        analysisStore.setBatchData(batchData.value);

        // Add images to store
        analysisStore.images = [...images.value];

        // Submit to API
        const result = await analysisStore.submitBatch();

        // Handle success
        analysisResult.value = result;

        // Reset form after successful submission
        if (result) {
          resetForm();
        }

      } catch (error) {
        console.error('Error submitting analysis:', error);
      } finally {
        isSubmitting.value = false;
      }
    };

    const resetForm = () => {
      batchData.value = {
        name: '',
        collectionDate: '',
        origin: '',
        notes: ''
      };
      images.value = [];
      capturedImages.value = [];
      currentTab.value = 'upload';
      formErrors.value = {};
    };

    // Lifecycle hooks
    onMounted(() => {
      // Reset store when component is mounted
      analysisStore.clearBatch();
    });

    return {
      // State
      batchData,
      images,
      capturedImages,
      currentTab,
      tabs,
      isSubmitting,
      formErrors,
      analysisResult,

      // Computed
      isFormValid,
      uploadProgress,
      isUploading,
      error,

      // Methods
      updateBatchData,
      updateImages,
      handleCapturedImage,
      removeCapturedImage,
      submitAnalysis,
      resetForm
    };
  }
};
</script>

<style scoped>
/* Add any custom styles here */
</style>

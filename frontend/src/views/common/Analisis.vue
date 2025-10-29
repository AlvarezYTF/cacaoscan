<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar -->
    <Sidebar 
      :brand-name="'CacaoScan'"
      :user-name="userName"
      :user-role="userRole"
      :current-route="$route.path"
      :active-section="activeSection"
      :collapsed="isSidebarCollapsed"
      @menu-click="handleMenuClick"
      @logout="handleLogout"
      @toggle-collapse="toggleSidebarCollapse"
    />

    <!-- Main Content with Navbar -->
    <div :class="isSidebarCollapsed ? 'lg:pl-20' : 'lg:pl-64'">
      <!-- Navbar -->

      <!-- Page Content -->
      <main class="py-6 px-4 sm:px-6 lg:px-8">
        <div class="max-w-5xl mx-auto">
          <!-- Page Header -->
          <div class="mb-8">
            <div class="bg-white rounded-lg border border-gray-200 hover:shadow-md hover:border-green-200 transition-all duration-200">
            <div class="px-6 py-4">
              <div class="flex-1">
                <h1 class="text-3xl font-bold text-gray-900 mb-2">Nuevo Análisis de Lote</h1>
                <p class="text-gray-600 text-lg">Sube imágenes de granos de cacao y completa la información del lote para iniciar un análisis de calidad detallado y preciso.</p>
              </div>
            </div>
            </div>
          </div>

          <!-- Main Content Card -->
          <div class="bg-white shadow-sm border border-gray-200 rounded-xl overflow-hidden">
            <div class="p-8 space-y-8">
              <!-- Progress Indicator -->
              <ProgressIndicator v-if="isUploading" :progress="uploadProgress" label="Procesando imágenes..." />

              <!-- Success Alert -->
              <div v-if="analysisResult" class="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-300 rounded-xl p-8 shadow-lg">
                <div class="flex items-start">
                  <div class="flex-shrink-0">
                    <div class="flex items-center justify-center w-16 h-16 bg-green-500 rounded-full">
                      <svg class="h-10 w-10 text-white" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                      </svg>
                    </div>
                  </div>
                  <div class="ml-6 flex-1">
                    <h3 class="text-2xl font-bold text-green-900 mb-4">
                      Análisis completado exitosamente
                    </h3>
                    
                    <!-- Estadísticas principales -->
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                      <div class="bg-white rounded-lg p-4 border border-green-200">
                        <p class="text-sm text-gray-600 mb-1">Lote Analizado</p>
                        <p class="text-lg font-semibold text-green-900">{{ analysisResult.lote_name }}</p>
                      </div>
                      
                      <div class="bg-white rounded-lg p-4 border border-green-200">
                        <p class="text-sm text-gray-600 mb-1">Imágenes Procesadas</p>
                        <p class="text-lg font-semibold text-green-900">
                          {{ analysisResult.processed_images }}/{{ analysisResult.total_images }}
                        </p>
                      </div>
                      
                      <div class="bg-white rounded-lg p-4 border border-green-200">
                        <p class="text-sm text-gray-600 mb-1">Confianza Promedio</p>
                        <p class="text-lg font-semibold text-green-900">
                          {{ (analysisResult.average_confidence * 100).toFixed(1) }}%
                        </p>
                      </div>
                    </div>

                    <!-- Estadísticas adicionales -->
                    <div v-if="analysisResult.average_dimensions || analysisResult.total_weight" class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                      <div v-if="analysisResult.average_dimensions" class="bg-white rounded-lg p-3 border border-green-200">
                        <p class="text-xs text-gray-600 mb-1">Alto Promedio</p>
                        <p class="text-base font-semibold text-green-900">{{ analysisResult.average_dimensions.alto.toFixed(2) }} mm</p>
                      </div>
                      
                      <div v-if="analysisResult.average_dimensions" class="bg-white rounded-lg p-3 border border-green-200">
                        <p class="text-xs text-gray-600 mb-1">Ancho Promedio</p>
                        <p class="text-base font-semibold text-green-900">{{ analysisResult.average_dimensions.ancho.toFixed(2) }} mm</p>
                      </div>
                      
                      <div v-if="analysisResult.average_dimensions" class="bg-white rounded-lg p-3 border border-green-200">
                        <p class="text-xs text-gray-600 mb-1">Grosor Promedio</p>
                        <p class="text-base font-semibold text-green-900">{{ analysisResult.average_dimensions.grosor.toFixed(2) }} mm</p>
                      </div>
                      
                      <div v-if="analysisResult.total_weight" class="bg-white rounded-lg p-3 border border-green-200">
                        <p class="text-xs text-gray-600 mb-1">Peso Total</p>
                        <p class="text-base font-semibold text-green-900">{{ analysisResult.total_weight }} g</p>
                      </div>
                    </div>

                    <!-- Tiempo de procesamiento -->
                    <div v-if="analysisResult.processing_time_seconds" class="mb-4">
                      <p class="text-sm text-green-700">
                        <svg class="inline w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Tiempo de procesamiento: {{ analysisResult.processing_time_seconds }} segundos
                      </p>
                    </div>

                    <!-- Botones de acción -->
                    <div class="flex flex-col sm:flex-row gap-3">
                      <router-link 
                        :to="{ name: 'LoteDetail', params: { id: analysisResult.lote_id } }"
                        class="inline-flex items-center justify-center px-6 py-3 bg-green-600 text-white text-base font-semibold rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200 shadow-md"
                      >
                        Ver resultados detallados
                        <svg class="ml-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                        </svg>
                      </router-link>
                      
                      <button
                        @click="resetAndCreateNew"
                        class="inline-flex items-center justify-center px-6 py-3 bg-white text-green-700 text-base font-semibold rounded-lg hover:bg-green-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200 border-2 border-green-300 shadow-md"
                      >
                        Crear nuevo análisis
                        <svg class="ml-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Batch Info Form -->
              <div v-if="!analysisResult" class="bg-gray-50 rounded-lg p-6">
                <h2 class="text-xl font-semibold text-gray-900 mb-4">Información del Lote</h2>
                <BatchInfoForm 
                  v-model="batchData" 
                  :errors="formErrors" 
                  :user-role="userRole"
                  :user-name="userName"
                  :user-id="authStore.user?.id"
                  @update:modelValue="updateBatchData" 
                />
              </div>

              <!-- Image Capture Section -->
              <div v-if="!analysisResult" class="space-y-6">
                <div class="text-center">
                  <h2 class="text-2xl font-semibold text-gray-900 mb-3">Imágenes del Lote</h2>
                  <p class="text-gray-600 text-lg">Captura fotos de alta calidad de los granos de cacao para un análisis preciso</p>
                </div>

                <!-- Tabs -->
                <div class="bg-white border border-gray-200 rounded-lg p-1">
                  <nav class="flex space-x-1">
                    <button
                      v-for="tab in tabs"
                      :key="tab.name"
                      @click="currentTab = tab.name"
                      :class="[
                        currentTab === tab.name
                          ? 'bg-green-600 text-white shadow-sm'
                          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100',
                        'flex-1 py-3 px-4 text-sm font-medium rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500'
                      ]"
                    >
                      {{ tab.label }}
                    </button>
                  </nav>
                </div>

                <!-- Tab Content -->
                <div class="mt-6">
                  <!-- File Upload Tab -->
                  <div v-if="currentTab === 'upload'" class="bg-gray-50 rounded-lg p-6">
                    <ImageUploader
                      v-model="images"
                      @update:modelValue="updateImages"
                    />
                  </div>

                  <!-- Camera Capture Tab -->
                  <div v-else-if="currentTab === 'camera'" class="space-y-6">
                    <div class="bg-gray-50 rounded-lg p-6">
                      <CameraCapture @capture="handleCapturedImage" />
                    </div>

                    <!-- Captured Images Preview -->
                    <div v-if="capturedImages.length > 0" class="bg-white border border-gray-200 rounded-lg p-6">
                      <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                        </svg>
                        Fotos capturadas ({{ capturedImages.length }})
                      </h3>
                      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                        <div v-for="(img, index) in capturedImages" :key="index" class="relative group">
                          <div class="aspect-square rounded-lg overflow-hidden bg-gray-200 border border-gray-300">
                            <img :src="URL.createObjectURL(img)" class="w-full h-full object-cover" />
                          </div>
                          <button
                            @click="removeCapturedImage(index)"
                            class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600 transition-colors duration-200 opacity-0 group-hover:opacity-100 focus:opacity-100 focus:outline-none focus:ring-2 focus:ring-red-500"
                            title="Eliminar foto"
                          >
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                          </button>
                          <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all duration-200 rounded-lg"></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
          </div>

              <!-- Submit Button -->
              <div v-if="!analysisResult" class="bg-green-50 border border-green-200 rounded-lg p-6">
                <div class="text-center mb-6">
                  <h3 class="text-xl font-semibold text-green-900 mb-2">¿Listo para analizar?</h3>
                  <p class="text-green-700">Revisa que toda la información esté completa antes de continuar</p>
                </div>
                
                <button
                  type="button"
                  @click="submitAnalysis"
                  :disabled="isSubmitting || !isFormValid"
                  class="w-full flex justify-center items-center py-4 px-6 border border-transparent rounded-lg shadow-sm text-base font-semibold text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                >
                  <svg v-if="isSubmitting" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  
                  <svg v-else class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  
                  {{ isSubmitting ? 'Procesando análisis...' : 'Iniciar Análisis de Calidad' }}
                </button>
                
                <div v-if="!isFormValid" class="mt-4 text-center">
                  <div class="inline-flex items-center px-4 py-2 bg-amber-50 border border-amber-200 rounded-lg">
                    <svg class="w-4 h-4 mr-2 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                    </svg>
                    <p class="text-sm text-amber-700 font-medium">
                      Falta: {{ 
                        !batchData.name ? 'Nombre del lote' :
                        !batchData.collectionDate ? 'Fecha de recolección' :
                        !batchData.farm ? 'Finca' :
                        !batchData.genetics ? 'Genética' :
                        !images.length ? 'Al menos una imagen' : ''
                      }}
                    </p>
                  </div>
                </div>
              </div>

              <!-- Error Alert -->
              <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6">
                <div class="flex items-start">
                  <div class="flex-shrink-0">
                    <svg class="h-6 w-6 text-red-600" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                    </svg>
                  </div>
                  <div class="ml-4 flex-1">
                    <h3 class="text-lg font-semibold text-red-900 mb-2">
                      Error en el análisis
                    </h3>
                    <p class="text-sm text-red-700">
                      {{ error }}
                    </p>
                  </div>
                </div>
              </div>
        </div>
      </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch }  from 'vue';
import { useRouter }                        from 'vue-router';
import { useAuthStore }                     from '@/stores/auth';
import { useAnalysisStore }                 from '@/stores/analysis';
import Sidebar                              from '@/components/layout/Common/Sidebar.vue';
import ProgressIndicator                    from '@/components/admin/AdminAnalisisComponents/ProgressIndicator.vue';
import BatchInfoForm                        from '@/components/admin/AdminAnalisisComponents/BatchInfoForm.vue';
import ImageUploader                        from '@/components/admin/AdminAnalisisComponents/ImageUploader.vue';
import CameraCapture                        from '@/components/admin/AdminAnalisisComponents/CameraCapture.vue';

export default {
  name: 'NuevoAnalisis',
  components: {
    Sidebar,
    ProgressIndicator,
    BatchInfoForm,
    ImageUploader,
    CameraCapture
  },
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    const analysisStore = useAnalysisStore();

    // Sidebar collapse state
    const isSidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true');

    // Local state
    const batchData = ref({
      name: '',
      collectionDate: '',
      origin: '',
      notes: '',
      farm: '',
      originPlace: '',
      genetics: '',
      farmer: ''
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
        batchData.value.farm &&
        batchData.value.genetics &&
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

    // User data for sidebar and navbar
    const userName = computed(() => {
      return authStore.userFullName || 'Usuario';
    });

    const userRole = computed(() => {
      const role = authStore.userRole || 'Usuario';
      // Normalize role for sidebar
      if (role === 'farmer' || role === 'Agricultor') return 'agricultor';
      if (role === 'admin' || role === 'Administrador') return 'admin';
      return role;
    });

    const userEmail = computed(() => {
      return authStore.user?.email || '';
    });

    const activeSection = ref('analysis');

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
        notes: '',
        farm: '',
        originPlace: '',
        genetics: '',
        farmer: ''
      };
      images.value = [];
      capturedImages.value = [];
      currentTab.value = 'upload';
      formErrors.value = {};
    };

    // Sidebar and navbar methods
    const handleMenuClick = (item) => {
      if (item.route && item.route !== null) {
        // Navigate to external routes
        const currentPath = router.currentRoute.value.path;
        if (currentPath !== item.route) {
          router.push(item.route);
        }
      } else {
        // For internal sections without routes, navigate to dashboard with query param
        const role = authStore.userRole;
        if (role === 'farmer' || role === 'Agricultor') {
          router.push({ 
            name: 'AgricultorDashboard',
            query: { section: item.id }
          });
        } else {
          router.push({ 
            name: 'AdminDashboard',
            query: { section: item.id }
          });
        }
      }
    };

    const toggleSidebarCollapse = () => {
      isSidebarCollapsed.value = !isSidebarCollapsed.value;
      localStorage.setItem('sidebarCollapsed', isSidebarCollapsed.value);
    };

    const handleLogout = async () => {
      try {
        await authStore.logout();
      } catch (error) {
        console.error('Error during logout:', error);
      }
    };

    const resetAndCreateNew = () => {
      analysisResult.value = null;
      resetForm();
    };

    // Lifecycle hooks
    onMounted(() => {
      // Reset store when component is mounted
      analysisStore.clearBatch();
    });

    return {
      // Stores
      authStore,
      // State
      batchData,
      images,
      capturedImages,
      currentTab,
      tabs,
      isSubmitting,
      formErrors,
      analysisResult,
      isSidebarCollapsed,

      // Computed
      isFormValid,
      uploadProgress,
      isUploading,
      error,
      userName,
      userRole,
      userEmail,
      activeSection,

      // Methods
      updateBatchData,
      updateImages,
      handleCapturedImage,
      removeCapturedImage,
      submitAnalysis,
      resetForm,
      handleMenuClick,
      handleLogout,
      toggleSidebarCollapse,
      resetAndCreateNew
    };
  }
};
</script>

<style scoped>
/* Add any custom styles here */
</style>

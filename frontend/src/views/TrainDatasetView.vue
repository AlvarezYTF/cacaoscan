<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar -->
    <AdminSidebar 
      :brand-name="brandName"
      :user-name="userName"
      :user-role="userRole"
      :current-route="$route.path"
      @menu-click="handleMenuClick"
      @logout="handleLogout"
    />
    
    <!-- Navbar -->
    <AdminNavbar
      :title="navbarTitle"
      :subtitle="navbarSubtitle"
      :user-name="userName"
      :user-role="userRole"
      :search-placeholder="searchPlaceholder"
      :refresh-button-text="refreshButtonText"
      :loading="isRefreshing"
      @search="handleSearch"
      @refresh="handleRefresh"
    />
    
    <!-- Main content -->
    <div class="p-6 sm:ml-64">
      <!-- Page Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900 mb-2">Entrenamiento de Modelos ML</h1>
            <p class="text-gray-600 text-lg">Sube imágenes de granos de cacao y registra sus dimensiones para entrenar modelos de predicción</p>
          </div>
          
          <!-- Quick stats -->
          <div class="flex items-center space-x-4">
            <div class="text-center px-4 py-2 bg-white rounded-lg border border-gray-200">
              <div class="text-2xl font-bold text-green-600">{{ datasetStats.totalSamples }}</div>
              <div class="text-xs text-gray-500">Muestras</div>
            </div>
            
            <div class="text-center px-4 py-2 bg-white rounded-lg border border-gray-200">
              <div class="text-2xl font-bold text-green-600">{{ datasetStats.avgWeight }}g</div>
              <div class="text-xs text-gray-500">Peso Promedio</div>
            </div>
            
            <button
              @click="refreshDatasetStats"
              :disabled="isRefreshing"
              class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              <svg class="w-4 h-4 mr-2" :class="{ 'animate-spin': isRefreshing }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {{ isRefreshing ? 'Actualizando...' : 'Actualizar' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <!-- Left Column: Upload and Data Entry -->
        <div class="xl:col-span-2 space-y-6">
          <!-- Image Upload Card -->
          <ImageUploadCard
            :images="uploadedImages"
            :is-uploading="isUploading"
            @upload="handleImageUpload"
            @remove="handleImageRemove"
            @clear-all="handleClearAll"
          />
          
          <!-- Data Entry Card -->
          <div class="bg-white rounded-lg border border-gray-200 hover:shadow-md hover:border-green-200 transition-all duration-200">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-xl font-bold text-gray-900">Registrar Datos de Granos</h3>
              <p class="text-gray-600 mt-1">Ingresa las dimensiones y peso para cada imagen subida</p>
            </div>
            
            <div class="p-6">
              <!-- No images uploaded -->
              <div v-if="uploadedImages.length === 0" class="text-center py-8">
                <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <p class="text-gray-500 font-medium">Sube imágenes primero</p>
                <p class="text-gray-400 text-sm">Necesitas subir imágenes de granos para registrar sus datos</p>
              </div>
              
              <!-- Data entry form -->
              <div v-else class="space-y-4">
                <div
                  v-for="(image, index) in uploadedImages"
                  :key="image.id"
                  class="border border-gray-200 rounded-lg p-4 hover:border-green-200 transition-colors duration-200"
                >
                  <div class="flex items-start space-x-4">
                    <!-- Image preview -->
                    <div class="flex-shrink-0">
                      <img
                        :src="image.preview"
                        :alt="`Grano ${index + 1}`"
                        class="w-20 h-20 object-cover rounded-lg border border-gray-200"
                      />
                    </div>
                    
                    <!-- Form fields -->
                    <div class="flex-1 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                      <!-- Grain ID -->
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">ID del Grano</label>
                        <input
                          v-model="image.grainId"
                          type="text"
                          placeholder="GR-001"
                          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200"
                        />
                      </div>
                      
                      <!-- Height -->
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Alto (mm)</label>
                        <input
                          v-model.number="image.height"
                          type="number"
                          step="0.1"
                          placeholder="12.5"
                          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200"
                        />
                      </div>
                      
                      <!-- Width -->
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Ancho (mm)</label>
                        <input
                          v-model.number="image.width"
                          type="number"
                          step="0.1"
                          placeholder="8.3"
                          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200"
                        />
                      </div>
                      
                      <!-- Thickness -->
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Grosor (mm)</label>
                        <input
                          v-model.number="image.thickness"
                          type="number"
                          step="0.1"
                          placeholder="6.2"
                          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200"
                        />
                      </div>
                      
                      <!-- Weight -->
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Peso (g)</label>
                        <input
                          v-model.number="image.weight"
                          type="number"
                          step="0.01"
                          placeholder="1.25"
                          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200"
                        />
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Submit button -->
                <div class="pt-4 border-t border-gray-200">
                  <button
                    @click="submitTrainingData"
                    :disabled="!canSubmit || isSubmitting"
                    class="w-full inline-flex items-center justify-center px-6 py-3 text-base font-medium text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                  >
                    <svg v-if="isSubmitting" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <svg v-else class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                    {{ isSubmitting ? 'Enviando datos...' : `Enviar ${uploadedImages.length} muestra${uploadedImages.length !== 1 ? 's' : ''}` }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Progress and Recent Samples -->
        <div class="space-y-6">
          <!-- Training Progress -->
          <TrainingProgress
            :is-training="isTraining"
            :progress="trainingProgress"
            :current-epoch="currentEpoch"
            :total-epochs="totalEpochs"
            :training-status="trainingStatus"
            @start-training="startTraining"
            @stop-training="stopTraining"
          />
          
          <!-- Dataset Summary -->
          <div class="bg-white rounded-lg border border-gray-200 hover:shadow-md hover:border-green-200 transition-all duration-200">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-xl font-bold text-gray-900">Resumen del Dataset</h3>
            </div>
            
            <div class="p-6">
              <div class="grid grid-cols-2 gap-4">
                <div class="text-center p-4 bg-green-50 rounded-lg">
                  <div class="text-2xl font-bold text-green-600">{{ datasetStats.totalSamples }}</div>
                  <div class="text-sm text-green-700">Total Muestras</div>
                </div>
                
                <div class="text-center p-4 bg-blue-50 rounded-lg">
                  <div class="text-2xl font-bold text-blue-600">{{ datasetStats.avgWeight }}g</div>
                  <div class="text-sm text-blue-700">Peso Promedio</div>
                </div>
                
                <div class="text-center p-4 bg-purple-50 rounded-lg">
                  <div class="text-2xl font-bold text-purple-600">{{ datasetStats.avgHeight }}mm</div>
                  <div class="text-sm text-purple-700">Alto Promedio</div>
                </div>
                
                <div class="text-center p-4 bg-orange-50 rounded-lg">
                  <div class="text-2xl font-bold text-orange-600">{{ datasetStats.lastUpdate }}</div>
                  <div class="text-sm text-orange-700">Última Actualización</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Recent Samples Table -->
          <SamplesTable
            :samples="recentSamples"
            :is-loading="isLoadingSamples"
            @refresh="loadRecentSamples"
            @view-sample="viewSample"
          />
        </div>
      </div>
    </div>

    <!-- Success/Error notifications -->
    <Transition name="slide-up">
      <div 
        v-if="showNotification" 
        class="fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50"
        :class="{
          'bg-green-500 text-white': notificationType === 'success',
          'bg-red-500 text-white': notificationType === 'error',
          'bg-blue-500 text-white': notificationType === 'info'
        }"
      >
        <div class="flex items-center">
          <svg v-if="notificationType === 'success'" class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <svg v-else-if="notificationType === 'error'" class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <svg v-else class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {{ notificationMessage }}
        </div>
      </div>
    </Transition>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AdminSidebar from '@/components/layout/AdminSidebar.vue';
import AdminNavbar from '@/components/layout/AdminNavbar.vue';
import ImageUploadCard from '@/components/training/ImageUploadCard.vue';
import TrainingProgress from '@/components/training/TrainingProgress.vue';
import SamplesTable from '@/components/training/SamplesTable.vue';
import { submitTrainingData, getDatasetStats, getRecentSamples } from '@/services/trainingApi.js';

export default {
  name: 'TrainDatasetView',
  components: {
    AdminSidebar,
    AdminNavbar,
    ImageUploadCard,
    TrainingProgress,
    SamplesTable
  },
  
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    
    // Sidebar properties
    const brandName = computed(() => 'CacaoScan');
    const userName = computed(() => {
      const user = authStore.user;
      return user ? `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username : 'Usuario';
    });
    const userRole = computed(() => {
      const user = authStore.user;
      if (user?.is_superuser) return 'Superadministrador';
      if (user?.is_staff) return 'Administrador';
      return 'Usuario';
    });

    // Navbar properties
    const navbarTitle = ref('Entrenamiento de Modelos ML');
    const navbarSubtitle = ref('Sube imágenes de granos de cacao y registra sus dimensiones');
    const searchPlaceholder = ref('Buscar muestras...');
    const refreshButtonText = ref('Actualizar');
    
    // State
    const uploadedImages = ref([]);
    const isUploading = ref(false);
    const isSubmitting = ref(false);
    const isRefreshing = ref(false);
    const isTraining = ref(false);
    const trainingProgress = ref(0);
    const currentEpoch = ref(0);
    const totalEpochs = ref(100);
    const trainingStatus = ref('');
    const recentSamples = ref([]);
    const isLoadingSamples = ref(false);
    
    // Dataset stats
    const datasetStats = reactive({
      totalSamples: 0,
      avgWeight: 0,
      avgHeight: 0,
      lastUpdate: 'N/A'
    });
    
    // Notifications
    const showNotification = ref(false);
    const notificationType = ref('info');
    const notificationMessage = ref('');
    
    // Computed
    const canSubmit = computed(() => {
      return uploadedImages.value.length > 0 && 
             uploadedImages.value.every(img => 
               img.grainId && 
               img.height && 
               img.width && 
               img.thickness && 
               img.weight
             );
    });
    
    // Methods
    const handleMenuClick = (menuItem) => {
      if (menuItem.route) {
        router.push(menuItem.route);
      }
    };

    const handleLogout = async () => {
      await authStore.logout();
      router.push('/login');
    };

    const handleSearch = (query) => {
      console.log('Search:', query);
    };

    const handleRefresh = () => {
      refreshDatasetStats();
      loadRecentSamples();
    };

    const handleImageUpload = (files) => {
      isUploading.value = true;
      
      Array.from(files).forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          const imageData = {
            id: `img_${Date.now()}_${index}`,
            file: file,
            preview: e.target.result,
            grainId: '',
            height: null,
            width: null,
            thickness: null,
            weight: null
          };
          uploadedImages.value.push(imageData);
        };
        reader.readAsDataURL(file);
      });
      
      setTimeout(() => {
        isUploading.value = false;
      }, 1000);
    };

    const handleImageRemove = (imageId) => {
      uploadedImages.value = uploadedImages.value.filter(img => img.id !== imageId);
    };

    const handleClearAll = () => {
      uploadedImages.value = [];
    };

    const submitTrainingData = async () => {
      if (!canSubmit.value) return;
      
      isSubmitting.value = true;
      
      try {
        const formData = new FormData();
        
        // Add images and their data
        uploadedImages.value.forEach((image, index) => {
          formData.append(`images`, image.file);
          formData.append(`data_${index}`, JSON.stringify({
            grain_id: image.grainId,
            height: image.height,
            width: image.width,
            thickness: image.thickness,
            weight: image.weight
          }));
        });
        
        await submitTrainingData(formData);
        
        showNotificationMessage('Datos enviados exitosamente', 'success');
        handleClearAll();
        refreshDatasetStats();
        loadRecentSamples();
        
      } catch (error) {
        console.error('Error submitting data:', error);
        showNotificationMessage('Error enviando datos: ' + error.message, 'error');
      } finally {
        isSubmitting.value = false;
      }
    };

    const startTraining = async () => {
      isTraining.value = true;
      trainingProgress.value = 0;
      currentEpoch.value = 0;
      trainingStatus.value = 'Iniciando entrenamiento...';
      
      // Simulate training progress
      const interval = setInterval(() => {
        if (trainingProgress.value < 100) {
          trainingProgress.value += 1;
          currentEpoch.value = Math.floor((trainingProgress.value / 100) * totalEpochs.value);
          trainingStatus.value = `Entrenando... Época ${currentEpoch.value}/${totalEpochs.value}`;
        } else {
          clearInterval(interval);
          trainingStatus.value = 'Entrenamiento completado';
          isTraining.value = false;
          showNotificationMessage('Modelo entrenado exitosamente', 'success');
        }
      }, 100);
    };

    const stopTraining = () => {
      isTraining.value = false;
      trainingStatus.value = 'Entrenamiento detenido';
      showNotificationMessage('Entrenamiento detenido', 'info');
    };

    const refreshDatasetStats = async () => {
      isRefreshing.value = true;
      
      try {
        const stats = await getDatasetStats();
        Object.assign(datasetStats, stats);
      } catch (error) {
        console.error('Error loading dataset stats:', error);
      } finally {
        isRefreshing.value = false;
      }
    };

    const loadRecentSamples = async () => {
      isLoadingSamples.value = true;
      
      try {
        const samples = await getRecentSamples();
        recentSamples.value = samples;
      } catch (error) {
        console.error('Error loading recent samples:', error);
      } finally {
        isLoadingSamples.value = false;
      }
    };

    const viewSample = (sample) => {
      console.log('View sample:', sample);
      // Implement sample viewing logic
    };

    const showNotificationMessage = (message, type = 'info') => {
      notificationMessage.value = message;
      notificationType.value = type;
      showNotification.value = true;
      
      setTimeout(() => {
        showNotification.value = false;
      }, type === 'error' ? 5000 : 3000);
    };
    
    // Lifecycle
    onMounted(() => {
      refreshDatasetStats();
      loadRecentSamples();
    });
    
    return {
      // Sidebar & Navbar
      brandName,
      userName,
      userRole,
      navbarTitle,
      navbarSubtitle,
      searchPlaceholder,
      refreshButtonText,
      handleMenuClick,
      handleLogout,
      handleSearch,
      handleRefresh,
      
      // State
      uploadedImages,
      isUploading,
      isSubmitting,
      isRefreshing,
      isTraining,
      trainingProgress,
      currentEpoch,
      totalEpochs,
      trainingStatus,
      recentSamples,
      isLoadingSamples,
      datasetStats,
      showNotification,
      notificationType,
      notificationMessage,
      
      // Computed
      canSubmit,
      
      // Methods
      handleImageUpload,
      handleImageRemove,
      handleClearAll,
      submitTrainingData,
      startTraining,
      stopTraining,
      refreshDatasetStats,
      loadRecentSamples,
      viewSample
    };
  }
};
</script>

<style scoped>
/* Transiciones */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* Focus states */
.focus-visible:focus {
  outline: 2px solid #10b981;
  outline-offset: 2px;
}

/* Loading states */
.loading {
  opacity: 0.6;
  pointer-events: none;
}

/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}
</style>

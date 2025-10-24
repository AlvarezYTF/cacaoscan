<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold text-gray-900">
            Subir Imágenes al Dataset
          </h3>
          <p class="text-sm text-gray-600 mt-1">
            Agregue nuevas imágenes de granos de cacao para entrenamiento
          </p>
        </div>
        <div v-if="isUploading" class="flex items-center text-sm text-blue-600">
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Subiendo {{ uploadProgress.completed }} de {{ uploadProgress.total }}
        </div>
      </div>
    </div>

    <!-- Upload Form -->
    <div class="p-6">
      <form @submit.prevent="handleSubmit">
        <!-- Metadata Section -->
        <div class="mb-6">
          <h4 class="text-md font-medium text-gray-900 mb-4">Metadatos Comunes</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label for="batch_number" class="block text-sm font-medium text-gray-700 mb-1">
                Número de Lote
              </label>
              <input
                id="batch_number"
                v-model="metadata.batch_number"
                type="text"
                placeholder="Ej: DATASET_001"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
            </div>
            
            <div>
              <label for="origin" class="block text-sm font-medium text-gray-700 mb-1">
                Origen
              </label>
              <input
                id="origin"
                v-model="metadata.origin"
                type="text"
                placeholder="Ej: Colombia, Venezuela"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
            </div>
          </div>
          
          <div class="mt-4">
            <label for="notes" class="block text-sm font-medium text-gray-700 mb-1">
              Notas del Dataset
            </label>
            <textarea
              id="notes"
              v-model="metadata.notes"
              rows="3"
              placeholder="Información adicional sobre este lote de imágenes..."
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
            ></textarea>
          </div>
        </div>

        <!-- Upload Zone -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Seleccionar Imágenes
            <span class="text-red-500">*</span>
          </label>
          
          <div 
            @dragover.prevent="handleDragOver"
            @dragleave.prevent="handleDragLeave"
            @drop.prevent="handleDrop"
            @click="openFileSelector"
            class="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200"
            :class="{
              'border-green-500 bg-green-50': isDragging,
              'border-gray-300 hover:border-green-400 hover:bg-gray-50': !isDragging && selectedFiles.length === 0,
              'border-green-500 bg-green-50': selectedFiles.length > 0
            }"
          >
            <!-- Upload State -->
            <div v-if="selectedFiles.length === 0" class="flex flex-col items-center justify-center space-y-3">
              <div class="relative">
                <svg 
                  class="w-16 h-16 text-gray-400 transition-colors duration-200"
                  :class="{ 'text-green-500': isDragging }"
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path 
                    stroke-linecap="round" 
                    stroke-linejoin="round" 
                    stroke-width="1.5" 
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
                <div 
                  v-if="isDragging" 
                  class="absolute inset-0 flex items-center justify-center"
                >
                  <div class="w-16 h-16 bg-green-500 rounded-full opacity-20 animate-pulse"></div>
                </div>
              </div>
              <div class="space-y-2">
                <p class="text-lg font-medium text-gray-700">
                  {{ isDragging ? 'Suelta las imágenes aquí' : 'Selecciona imágenes del dataset' }}
                </p>
                <p class="text-sm text-gray-500">
                  Arrastra y suelta o haz clic para seleccionar múltiples archivos
                </p>
                <p class="text-xs text-gray-400">
                  Formatos: JPG, PNG, BMP, TIFF (máx. 20MB cada una)
                </p>
              </div>
            </div>

            <!-- Files Selected State -->
            <div v-else class="space-y-4">
              <div class="flex items-center justify-center space-x-3">
                <svg class="w-12 h-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <div class="text-center">
                  <p class="text-lg font-medium text-gray-700">
                    {{ selectedFiles.length }} archivo{{ selectedFiles.length !== 1 ? 's' : '' }} seleccionado{{ selectedFiles.length !== 1 ? 's' : '' }}
                  </p>
                  <p class="text-sm text-gray-500">
                    Tamaño total: {{ formatTotalSize() }}
                  </p>
                </div>
              </div>
              
              <div class="flex justify-center space-x-3">
                <button
                  type="button"
                  @click.stop="openFileSelector"
                  class="text-sm text-green-600 hover:text-green-700 underline"
                >
                  Agregar más archivos
                </button>
                <span class="text-gray-300">|</span>
                <button
                  type="button"
                  @click.stop="clearFiles"
                  class="text-sm text-red-600 hover:text-red-700 underline"
                >
                  Limpiar selección
                </button>
              </div>
            </div>
          </div>

          <!-- File Input -->
          <input
            ref="fileInput"
            type="file"
            multiple
            accept="image/jpeg,image/jpg,image/png,image/bmp,image/tiff"
            class="hidden"
            @change="handleFileSelect"
          />
        </div>

        <!-- File List -->
        <div v-if="selectedFiles.length > 0" class="mb-6">
          <h4 class="text-md font-medium text-gray-900 mb-3">
            Archivos Seleccionados ({{ selectedFiles.length }})
          </h4>
          
          <div class="max-h-48 overflow-y-auto border border-gray-200 rounded-md">
            <div class="divide-y divide-gray-200">
              <div
                v-for="(file, index) in selectedFiles"
                :key="index"
                class="flex items-center justify-between p-3 hover:bg-gray-50"
              >
                <div class="flex items-center space-x-3 flex-1 min-w-0">
                  <div class="flex-shrink-0">
                    <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 truncate">
                      {{ file.name }}
                    </p>
                    <p class="text-xs text-gray-500">
                      {{ formatFileSize(file.size) }} • {{ file.type }}
                    </p>
                  </div>
                </div>
                
                <button
                  type="button"
                  @click="removeFile(index)"
                  class="flex-shrink-0 p-1 text-red-500 hover:text-red-700 hover:bg-red-50 rounded"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Upload Progress -->
        <div v-if="isUploading" class="mb-6">
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-blue-800">
                Subiendo archivos...
              </span>
              <span class="text-sm text-blue-600">
                {{ uploadProgress.percentage }}%
              </span>
            </div>
            <div class="w-full bg-blue-200 rounded-full h-2">
              <div 
                class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${uploadProgress.percentage}%` }"
              ></div>
            </div>
            <p class="text-xs text-blue-600 mt-2">
              {{ uploadProgress.completed }} de {{ uploadProgress.total }} archivos completados
            </p>
          </div>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="mb-6">
          <div class="bg-red-50 border border-red-200 rounded-lg p-4">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-red-400 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div class="flex-1">
                <h3 class="text-sm font-medium text-red-800">Error en la subida</h3>
                <p class="text-sm text-red-700 mt-1">{{ error }}</p>
                <button
                  type="button"
                  @click="clearError"
                  class="text-sm text-red-600 hover:text-red-500 underline mt-2"
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Submit Button -->
        <div class="flex justify-end">
          <button
            type="submit"
            :disabled="selectedFiles.length === 0 || isUploading"
            class="px-6 py-3 bg-green-600 text-white font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-200"
          >
            <span v-if="isUploading" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Subiendo...
            </span>
            <span v-else>
              Subir {{ selectedFiles.length }} archivo{{ selectedFiles.length !== 1 ? 's' : '' }}
            </span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue';
import { uploadDatasetImages, validateImageFile, formatFileSize } from '@/services/datasetApi.js';

export default {
  name: 'DatasetUpload',
  
  // Props siguiendo SRP - solo configuración esencial
  props: {
    autoUpload: {
      type: Boolean,
      default: false
    },
    maxFiles: {
      type: Number,
      default: 50
    }
  },
  
  // Eventos siguiendo SRP - solo comunicación esencial
  emits: ['upload-start', 'upload-progress', 'upload-complete', 'upload-error'],
  
  setup(props, { emit }) {
    // Estado reactivo (SRP - separado por responsabilidad)
    const isDragging = ref(false);
    const selectedFiles = ref([]);
    const isUploading = ref(false);
    const error = ref('');
    const fileInput = ref(null);
    
    // Metadatos del formulario
    const metadata = reactive({
      batch_number: '',
      origin: '',
      notes: ''
    });
    
    // Progreso de subida
    const uploadProgress = reactive({
      completed: 0,
      total: 0,
      percentage: 0
    });
    
    // Métodos de archivo (SRP - solo gestión de archivos)
    const openFileSelector = () => {
      if (fileInput.value) {
        fileInput.value.click();
      }
    };
    
    const handleFileSelect = (event) => {
      const files = Array.from(event.target.files);
      processFiles(files);
      // Limpiar input para permitir selección repetida
      event.target.value = '';
    };
    
    const handleDragOver = (event) => {
      event.preventDefault();
      isDragging.value = true;
    };
    
    const handleDragLeave = (event) => {
      event.preventDefault();
      if (!event.currentTarget.contains(event.relatedTarget)) {
        isDragging.value = false;
      }
    };
    
    const handleDrop = (event) => {
      event.preventDefault();
      isDragging.value = false;
      
      const files = Array.from(event.dataTransfer.files);
      processFiles(files);
    };
    
    // Procesamiento de archivos (KISS - lógica simple)
    const processFiles = (files) => {
      if (files.length === 0) return;
      
      // Validar límite de archivos
      if (selectedFiles.value.length + files.length > props.maxFiles) {
        error.value = `Solo puedes subir un máximo de ${props.maxFiles} archivos.`;
        return;
      }
      
      const validFiles = [];
      let hasError = false;
      
      // Validar cada archivo
      files.forEach(file => {
        const validation = validateImageFile(file);
        if (!validation.isValid) {
          error.value = validation.error;
          hasError = true;
          return;
        }
        validFiles.push(file);
      });
      
      if (hasError && validFiles.length === 0) return;
      
      // Agregar archivos válidos
      selectedFiles.value = [...selectedFiles.value, ...validFiles];
      
      // Auto-upload si está habilitado
      if (props.autoUpload && validFiles.length > 0) {
        handleSubmit();
      }
    };
    
    const removeFile = (index) => {
      selectedFiles.value.splice(index, 1);
    };
    
    const clearFiles = () => {
      selectedFiles.value = [];
    };
    
    // Manejo de subida (SRP - solo lógica de subida)
    const handleSubmit = async () => {
      if (selectedFiles.value.length === 0) {
        error.value = 'Por favor selecciona al menos un archivo';
        return;
      }
      
      isUploading.value = true;
      error.value = '';
      
      // Resetear progreso
      uploadProgress.completed = 0;
      uploadProgress.total = selectedFiles.value.length;
      uploadProgress.percentage = 0;
      
      emit('upload-start', {
        fileCount: selectedFiles.value.length,
        metadata: { ...metadata }
      });
      
      try {
        const results = await uploadDatasetImages(
          selectedFiles.value,
          metadata,
          (progress) => {
            // Actualizar progreso
            uploadProgress.completed = progress.completed;
            uploadProgress.total = progress.total;
            uploadProgress.percentage = progress.percentage;
            
            emit('upload-progress', progress);
          }
        );
        
        // Procesar resultados
        const successful = results.filter(r => r.success);
        const failed = results.filter(r => !r.success);
        
        if (failed.length > 0) {
          error.value = `${failed.length} archivo(s) fallaron. Primero: ${failed[0].error}`;
        }
        
        emit('upload-complete', {
          total: results.length,
          successful: successful.length,
          failed: failed.length,
          results
        });
        
        // Limpiar formulario si todo fue exitoso
        if (failed.length === 0) {
          resetForm();
        }
        
      } catch (err) {
        error.value = err.message || 'Error durante la subida';
        emit('upload-error', err);
      } finally {
        isUploading.value = false;
      }
    };
    
    // Utilidades (DRY - funciones reutilizables)
    const formatTotalSize = () => {
      const totalBytes = selectedFiles.value.reduce((sum, file) => sum + file.size, 0);
      return formatFileSize(totalBytes);
    };
    
    const clearError = () => {
      error.value = '';
    };
    
    const resetForm = () => {
      selectedFiles.value = [];
      metadata.batch_number = '';
      metadata.origin = '';
      metadata.notes = '';
      error.value = '';
      uploadProgress.completed = 0;
      uploadProgress.total = 0;
      uploadProgress.percentage = 0;
    };
    
    return {
      // Estado
      isDragging,
      selectedFiles,
      isUploading,
      error,
      fileInput,
      metadata,
      uploadProgress,
      
      // Métodos
      openFileSelector,
      handleFileSelect,
      handleDragOver,
      handleDragLeave,
      handleDrop,
      removeFile,
      clearFiles,
      handleSubmit,
      formatTotalSize,
      formatFileSize,
      clearError,
      resetForm
    };
  }
};
</script>

<style scoped>
/* Animaciones y transiciones */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Efectos de hover */
.hover-scale:hover {
  transform: scale(1.02);
  transition: transform 0.2s ease;
}

/* Scrollbar personalizado para lista de archivos */
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

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Animación de progreso */
.progress-bar {
  transition: width 0.3s ease;
}

/* Estados de drag & drop */
.drag-over {
  border-color: #10b981;
  background-color: #ecfdf5;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .grid-cols-1.md\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}

/* Focus states */
.focus-visible:focus {
  outline: 2px solid #10b981;
  outline-offset: 2px;
}
</style>

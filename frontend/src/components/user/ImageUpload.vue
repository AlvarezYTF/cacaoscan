<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <!-- Header -->
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-gray-800 mb-2">
        Análisis de Grano de Cacao
      </h2>
      <p class="text-gray-600">
        Sube una imagen de un grano de cacao para obtener sus características físicas predichas
      </p>
    </div>

    <!-- Upload Form -->
    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Image Upload Area -->
      <div class="space-y-4">
        <label class="block text-sm font-medium text-gray-700">
          Imagen del Grano
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
            'border-gray-300 hover:border-green-400 hover:bg-gray-50': !isDragging && !selectedFile,
            'border-green-500 bg-green-50': selectedFile
          }"
        >
          <!-- Upload State -->
          <div v-if="!selectedFile" class="flex flex-col items-center justify-center space-y-3">
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
                {{ isDragging ? 'Suelta la imagen aquí' : 'Selecciona una imagen del grano' }}
              </p>
              <p class="text-sm text-gray-500">
                Arrastra y suelta o haz clic para seleccionar
              </p>
              <p class="text-xs text-gray-400">
                Formatos: JPG, PNG, BMP, TIFF (máx. 10MB)
              </p>
            </div>
          </div>

          <!-- Preview State -->
          <div v-else class="flex flex-col items-center space-y-4">
            <div class="relative">
              <img 
                :src="imagePreview" 
                :alt="selectedFile.name"
                class="w-32 h-32 object-cover rounded-lg border-2 border-green-200"
              />
              <button
                type="button"
                @click.stop="removeSelectedFile"
                class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors"
                aria-label="Eliminar imagen"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="text-center">
              <p class="font-medium text-gray-700">{{ selectedFile.name }}</p>
              <p class="text-sm text-gray-500">
                {{ formatFileSize(selectedFile.size) }} • {{ selectedFile.type }}
              </p>
              <button
                type="button"
                @click.stop="openFileSelector"
                class="mt-2 text-sm text-green-600 hover:text-green-700 underline"
              >
                Cambiar imagen
              </button>
            </div>
          </div>
        </div>

        <!-- File Input -->
        <input
          ref="fileInput"
          type="file"
          accept="image/jpeg,image/jpg,image/png,image/bmp,image/tiff"
          class="hidden"
          @change="handleFileSelect"
        />
      </div>

      <!-- Metadata Form -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label for="batch_number" class="block text-sm font-medium text-gray-700 mb-1">
            Número de Lote
          </label>
          <input
            id="batch_number"
            v-model="formData.batch_number"
            type="text"
            placeholder="Ej: LOTE001"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
          />
        </div>
        
        <div>
          <label for="origin" class="block text-sm font-medium text-gray-700 mb-1">
            Origen
          </label>
          <input
            id="origin"
            v-model="formData.origin"
            type="text"
            placeholder="Ej: Colombia, Venezuela"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
          />
        </div>
      </div>

      <div>
        <label for="notes" class="block text-sm font-medium text-gray-700 mb-1">
          Notas Adicionales
        </label>
        <textarea
          id="notes"
          v-model="formData.notes"
          rows="3"
          placeholder="Observaciones o comentarios sobre el grano..."
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
        ></textarea>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-red-400 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 class="text-sm font-medium text-red-800">Error en la predicción</h3>
            <p class="text-sm text-red-700 mt-1">{{ error }}</p>
          </div>
        </div>
      </div>

      <!-- Submit Button -->
      <div class="flex justify-end">
        <button
          type="submit"
          :disabled="!selectedFile || isLoading"
          class="px-6 py-3 bg-green-600 text-white font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-200"
        >
          <span v-if="isLoading" class="flex items-center">
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Analizando...
          </span>
          <span v-else>
            Analizar Grano
          </span>
        </button>
      </div>
    </form>

    <!-- Loading Overlay -->
    <div 
      v-if="isLoading" 
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">Procesando imagen...</h3>
          <p class="text-sm text-gray-600">
            Nuestro modelo de IA está analizando las características del grano de cacao
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import { predictImage, createImageFormData, validateImageFile } from '@/services/predictionApi.js';

export default {
  name: 'ImageUpload',
  emits: ['prediction-result', 'prediction-error'],
  
  setup(props, { emit }) {
    // Estado reactivo
    const isDragging = ref(false);
    const selectedFile = ref(null);
    const imagePreview = ref(null);
    const isLoading = ref(false);
    const error = ref('');
    const fileInput = ref(null);
    
    // Datos del formulario
    const formData = ref({
      batch_number: '',
      origin: '',
      notes: ''
    });

    // Computed
    const canSubmit = computed(() => {
      return selectedFile.value && !isLoading.value;
    });

    // Métodos para manejo de archivos
    const handleDragOver = (event) => {
      event.preventDefault();
      isDragging.value = true;
    };

    const handleDragLeave = (event) => {
      event.preventDefault();
      // Solo cambiar el estado si realmente salimos del área
      if (!event.currentTarget.contains(event.relatedTarget)) {
        isDragging.value = false;
      }
    };

    const handleDrop = (event) => {
      event.preventDefault();
      isDragging.value = false;
      
      const files = Array.from(event.dataTransfer.files);
      if (files.length > 0) {
        processFile(files[0]);
      }
    };

    const openFileSelector = () => {
      if (fileInput.value) {
        fileInput.value.click();
      }
    };

    const handleFileSelect = (event) => {
      const files = Array.from(event.target.files);
      if (files.length > 0) {
        processFile(files[0]);
      }
      // Limpiar el input para permitir seleccionar el mismo archivo nuevamente
      event.target.value = '';
    };

    const processFile = async (file) => {
      error.value = '';
      
      try {
        // Validar archivo
        const validation = await validateImageFile(file);
        if (!validation.isValid) {
          error.value = validation.error;
          return;
        }

        // Establecer archivo seleccionado
        selectedFile.value = file;
        
        // Crear vista previa
        const reader = new FileReader();
        reader.onload = (e) => {
          imagePreview.value = e.target.result;
        };
        reader.readAsDataURL(file);
        
      } catch (err) {
        error.value = 'Error al procesar el archivo: ' + err.message;
      }
    };

    const removeSelectedFile = () => {
      selectedFile.value = null;
      imagePreview.value = null;
      error.value = '';
    };

    // Método principal para enviar predicción
    const handleSubmit = async () => {
      if (!selectedFile.value) {
        error.value = 'Por favor selecciona una imagen';
        return;
      }

      isLoading.value = true;
      error.value = '';

      try {
        // Crear FormData con imagen y metadatos
        const requestFormData = createImageFormData(selectedFile.value, formData.value);
        
        // Llamar a la API
        const result = await predictImage(requestFormData);
        
        // Emitir evento con resultado exitoso
        emit('prediction-result', result);
        
        // Limpiar formulario después del éxito
        resetForm();
        
      } catch (err) {
        error.value = err.message || 'Error al procesar la imagen';
        emit('prediction-error', err);
      } finally {
        isLoading.value = false;
      }
    };

    const resetForm = () => {
      selectedFile.value = null;
      imagePreview.value = null;
      formData.value = {
        batch_number: '',
        origin: '',
        notes: ''
      };
      error.value = '';
    };

    // Utility para formatear tamaño de archivo
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes';
      
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    return {
      // Estado
      isDragging,
      selectedFile,
      imagePreview,
      isLoading,
      error,
      fileInput,
      formData,
      
      // Computed
      canSubmit,
      
      // Métodos
      handleDragOver,
      handleDragLeave,
      handleDrop,
      openFileSelector,
      handleFileSelect,
      removeSelectedFile,
      handleSubmit,
      resetForm,
      formatFileSize
    };
  }
};
</script>

<style scoped>
/* Animaciones personalizadas */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Efectos de hover mejorados */
.hover-scale:hover {
  transform: scale(1.02);
}

/* Animación del botón de carga */
@keyframes pulse-green {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.animate-pulse-green {
  animation: pulse-green 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Estilos para el área de drop mejorados */
.drop-zone {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.drop-zone:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Mejoras de accesibilidad */
.focus-visible:focus {
  outline: 2px solid #10b981;
  outline-offset: 2px;
}
</style>

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
        <label for="image-upload-file" class="block text-sm font-medium text-gray-700">
          Imagen del Grano
          <span class="text-red-500">*</span>
        </label>
        
        <div 
          @dragover.prevent="fileUpload.handleDragOver"
          @dragleave.prevent="fileUpload.handleDragLeave"
          @drop.prevent="fileUpload.handleDrop"
          @click="fileUpload.openFileSelector"
          class="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200"
          :class="{
            'border-green-500 bg-green-50': isDragging.value,
            'border-gray-300 hover:border-green-400 hover:bg-gray-50': !isDragging.value && !selectedFile.value,
            'border-green-500 bg-green-50': selectedFile.value
          }"
        >
          <!-- Upload State -->
          <div v-if="!selectedFile.value" class="flex flex-col items-center justify-center space-y-3">
            <div class="relative">
              <svg 
                class="w-16 h-16 text-gray-400 transition-colors duration-200"
                :class="{ 'text-green-500': isDragging.value }"
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
                v-if="isDragging.value" 
                class="absolute inset-0 flex items-center justify-center"
              >
                <div class="w-16 h-16 bg-green-500 rounded-full opacity-20 animate-pulse"></div>
              </div>
            </div>
            <div class="space-y-2">
              <p class="text-lg font-medium text-gray-700">
                {{ isDragging.value ? 'Suelta la imagen aquí' : 'Selecciona una imagen del grano' }}
              </p>
              <p class="text-sm text-gray-500">
                Arrastra y suelta o haz clic para seleccionar
              </p>
              <p class="text-xs text-gray-400">
                Formatos: JPG, PNG, BMP, TIFF (máx. 20MB)
              </p>
            </div>
          </div>

          <!-- Preview State -->
          <div v-else class="flex flex-col items-center space-y-4">
            <div class="relative">
              <img 
                :src="imagePreview.value" 
                :alt="selectedFile.value.name"
                class="w-32 h-32 object-cover rounded-lg border-2 border-green-200"
              />
              <button
                type="button"
                @click.stop="fileUpload.removeSelectedFile"
                class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors"
                aria-label="Eliminar imagen"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="text-center">
              <p class="font-medium text-gray-700">{{ selectedFile.value.name }}</p>
              <p class="text-sm text-gray-500">
                {{ formatFileSize(selectedFile.value.size) }} • {{ selectedFile.value.type }}
              </p>
              <button
                type="button"
                @click.stop="fileUpload.openFileSelector"
                class="mt-2 text-sm text-green-600 hover:text-green-700 underline"
              >
                Cambiar imagen
              </button>
            </div>
          </div>
        </div>

        <!-- File Input -->
        <input
          id="image-upload-file"
          ref="fileInput"
          type="file"
          accept="image/jpeg,image/jpg,image/png,image/bmp,image/tiff"
          class="hidden"
          @change="fileUpload.handleFileSelect"
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
      <div v-if="error.value" class="bg-red-50 border border-red-200 rounded-md p-4">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-red-400 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 class="text-sm font-medium text-red-800">Error en la predicción</h3>
            <p class="text-sm text-red-700 mt-1">{{ error.value }}</p>
          </div>
        </div>
      </div>

      <!-- Submit Button -->
      <div class="flex justify-end">
        <button
          type="submit"
          :disabled="!selectedFile.value || isLoading"
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

<script setup>
import { ref, computed } from 'vue'
import { createImageFormData } from '@/utils/formDataUtils'
import { useFileUpload } from '@/composables/useFileUpload'
import { usePrediction } from '@/composables/usePrediction'

const props = defineProps({
  predictionMethod: {
    type: String,
    default: 'traditional'
  }
})

const emit = defineEmits(['prediction-result', 'prediction-error'])

// Use file upload composable
const fileUpload = useFileUpload({
  allowedTypes: ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff'],
  maxSize: 20 * 1024 * 1024, // 20MB
  enablePreview: true
})

// Extract upload properties
const isDragging = fileUpload.isDragging
const selectedFile = fileUpload.selectedFile
const imagePreview = fileUpload.imagePreview
const error = fileUpload.error
const fileInput = fileUpload.fileInput
const formatFileSize = fileUpload.formatFileSize

// Datos del formulario
const formData = ref({
  batch_number: '',
  origin: '',
  notes: ''
})

// Use prediction composable
const prediction = usePrediction({
  method: props.predictionMethod,
  onSuccess: (result) => {
    emit('prediction-result', result)
    resetForm()
  },
  onError: (errorInfo) => {
    fileUpload.error.value = errorInfo.message
    emit('prediction-error', errorInfo.originalError)
  }
})

// Computed
const isLoading = computed(() => prediction.isLoading.value)
const canSubmit = computed(() => {
  return fileUpload.hasFile.value && !isLoading.value && !fileUpload.error.value
})

// Método principal para enviar predicción
const handleSubmit = async () => {
  if (!fileUpload.hasFile.value) {
    fileUpload.error.value = 'Por favor selecciona una imagen'
    return
  }

  fileUpload.error.value = ''

  try {
    // Crear FormData con imagen y metadatos
    const requestFormData = createImageFormData(selectedFile.value, formData.value)
    
    // Execute prediction using composable
    await prediction.executePrediction(requestFormData, {
      returnCroppedImage: props.predictionMethod === 'smart',
      returnTransparentImage: props.predictionMethod === 'smart'
    })
  } catch (err) {
    // Error is already handled by composable
    }
}

const resetForm = () => {
  fileUpload.removeSelectedFile()
  formData.value = {
    batch_number: '',
    origin: '',
    notes: ''
  }
  prediction.reset()
}
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

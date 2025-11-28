<template>
  <div class="bg-white rounded-lg border border-gray-200 hover:shadow-md hover:border-green-200 transition-all duration-200">
    <div class="px-6 py-4 border-b border-gray-200">
      <h3 class="text-xl font-bold text-gray-900">Subir Imágenes de Granos</h3>
      <p class="text-gray-600 mt-1">Selecciona una o múltiples imágenes de granos de cacao</p>
    </div>
    
    <div class="p-6">
      <!-- Upload Area -->
      <div
        @drop="handleDrop"
        @dragover.prevent
        @dragenter.prevent
        class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-green-400 transition-colors duration-200"
        :class="{ 'border-green-400 bg-green-50': isDragOver }"
      >
        <input
          ref="fileInput"
          type="file"
          multiple
          accept="image/*"
          @change="handleFileSelect"
          class="hidden"
        />
        
        <div v-if="images.length === 0">
          <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p class="text-lg font-medium text-gray-700 mb-2">Arrastra imágenes aquí o haz clic para seleccionar</p>
          <p class="text-sm text-gray-500 mb-4">Formatos soportados: JPG, PNG, BMP, TIFF (máx. 20MB cada una)</p>
          <button
            @click="$refs.fileInput.click()"
            class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Seleccionar Imágenes
          </button>
        </div>
        
        <div v-else>
          <svg class="w-12 h-12 text-green-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="text-lg font-medium text-gray-700 mb-2">{{ images.length }} imagen{{ images.length !== 1 ? 'es' : '' }} seleccionada{{ images.length !== 1 ? 's' : '' }}</p>
          <p class="text-sm text-gray-500 mb-4">Arrastra más imágenes aquí o haz clic para agregar más</p>
          <button
            @click="$refs.fileInput.click()"
            class="inline-flex items-center px-4 py-2 text-sm font-medium text-green-600 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Agregar Más
          </button>
        </div>
      </div>
      
      <!-- Image Preview Grid -->
      <div v-if="images.length > 0" class="mt-6">
        <div class="flex items-center justify-between mb-4">
          <h4 class="text-lg font-semibold text-gray-900">Vista Previa</h4>
          <button
            @click="handleClearAll"
            class="text-sm text-red-600 hover:text-red-700 font-medium underline"
          >
            Limpiar Todo
          </button>
        </div>
        
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <div
            v-for="(image, index) in images"
            :key="image.id"
            class="relative group"
          >
            <div class="aspect-square rounded-lg overflow-hidden bg-gray-100 border border-gray-200">
              <img
                :src="image.preview"
                :alt="`Grano ${index + 1}`"
                class="w-full h-full object-cover"
              />
            </div>
            
            <!-- Remove button -->
            <button
              @click="handleRemove(image.id)"
              class="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            
            <!-- Image info -->
            <div class="mt-2 text-center">
              <p class="text-xs text-gray-500 truncate">{{ image.file.name }}</p>
              <p class="text-xs text-gray-400">{{ formatFileSize(image.file.size) }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Upload Progress -->
      <div v-if="isUploading" class="mt-6">
        <div class="flex items-center justify-between text-sm text-gray-600 mb-2">
          <span>Subiendo imágenes...</span>
          <span>{{ uploadProgress }}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div 
            class="bg-green-600 h-2 rounded-full transition-all duration-300"
            :style="{ width: `${uploadProgress}%` }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';

export default {
  name: 'ImageUploadCard',
  props: {
    images: {
      type: Array,
      default: () => []
    },
    isUploading: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['upload', 'remove', 'clear-all'],
  
  setup(props, { emit }) {
    const fileInput = ref(null);
    const isDragOver = ref(false);
    const uploadProgress = ref(0);
    
    const handleFileSelect = (event) => {
      const files = event.target.files;
      if (files.length > 0) {
        emit('upload', files);
        // Reset file input
        if (fileInput.value) {
          fileInput.value.value = '';
        }
      }
    };
    
    const handleDrop = (event) => {
      event.preventDefault();
      isDragOver.value = false;
      
      const files = event.dataTransfer.files;
      if (files.length > 0) {
        emit('upload', files);
      }
    };
    
    const handleRemove = (imageId) => {
      emit('remove', imageId);
    };
    
    const handleClearAll = () => {
      emit('clear-all');
    };
    
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes';
      
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      
      return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };
    
    // Watch for drag events
    const handleDragEnter = () => {
      isDragOver.value = true;
    };
    
    const handleDragLeave = () => {
      isDragOver.value = false;
    };
    
    return {
      fileInput,
      isDragOver,
      uploadProgress,
      handleFileSelect,
      handleDrop,
      handleRemove,
      handleClearAll,
      formatFileSize,
      handleDragEnter,
      handleDragLeave
    };
  }
};
</script>

<style scoped>
/* Drag and drop animations */
.group:hover .group-hover\:opacity-100 {
  opacity: 1;
}

/* File input styling */
input[type="file"] {
  display: none;
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

/* Focus states */
.focus-visible:focus {
  outline: 2px solid #10b981;
  outline-offset: 2px;
}
</style>

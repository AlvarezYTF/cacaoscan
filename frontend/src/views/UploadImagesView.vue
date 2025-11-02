<template>
  <div class="max-w-5xl mx-auto mt-10 p-6 bg-white rounded-xl shadow-lg">
    <h2 class="text-2xl font-bold text-green-700 mb-4">Subir Imágenes de Cacao</h2>
    
    <form @submit.prevent="uploadImages" class="space-y-4">
      <div class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-green-500 transition-colors">
        <input
          type="file"
          multiple
          accept="image/*"
          @change="handleFiles"
          ref="fileInput"
          class="hidden"
          id="image-input"
        />
        <label
          for="image-input"
          class="cursor-pointer flex flex-col items-center"
        >
          <svg
            class="w-12 h-12 text-gray-400 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          <span class="text-gray-600 font-medium">
            {{ files.length > 0 ? `${files.length} archivo(s) seleccionado(s)` : 'Selecciona imágenes o arrastra y suelta aquí' }}
          </span>
          <span class="text-sm text-gray-500 mt-2">
            Formatos permitidos: JPG, PNG, WEBP (máx. 20MB por imagen)
          </span>
        </label>
      </div>

      <div v-if="files.length > 0" class="space-y-2">
        <h3 class="font-semibold text-gray-700">Archivos seleccionados:</h3>
        <ul class="space-y-1 max-h-40 overflow-y-auto">
          <li
            v-for="(file, index) in files"
            :key="index"
            class="text-sm text-gray-600 flex items-center justify-between bg-gray-50 p-2 rounded"
          >
            <span>{{ file.name }} ({{ formatFileSize(file.size) }})</span>
            <button
              type="button"
              @click="removeFile(index)"
              class="text-red-500 hover:text-red-700 text-xs"
            >
              ✕
            </button>
          </li>
        </ul>
      </div>

      <div class="flex gap-4">
        <button
          type="submit"
          :disabled="files.length === 0 || isUploading"
          class="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg font-medium transition-colors"
        >
          {{ isUploading ? 'Subiendo...' : `Subir ${files.length} imagen${files.length !== 1 ? 'es' : ''}` }}
        </button>
        <button
          type="button"
          @click="clearFiles"
          :disabled="files.length === 0 || isUploading"
          class="bg-gray-200 hover:bg-gray-300 disabled:bg-gray-100 disabled:cursor-not-allowed text-gray-700 px-6 py-2 rounded-lg font-medium transition-colors"
        >
          Limpiar
        </button>
      </div>
    </form>

    <div v-if="uploadStatus" class="mt-6 p-4 rounded-lg" :class="uploadStatus.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'">
      <div class="font-semibold mb-2">{{ uploadStatus.title }}</div>
      <div class="text-sm">{{ uploadStatus.message }}</div>
      <div v-if="uploadStatus.errors && uploadStatus.errors.length > 0" class="mt-2 text-sm">
        <strong>Errores:</strong>
        <ul class="list-disc list-inside mt-1">
          <li v-for="(error, idx) in uploadStatus.errors" :key="idx">
            {{ error.file }}: {{ error.error }}
          </li>
        </ul>
      </div>
    </div>

    <div v-if="uploadedImages.length > 0" class="mt-6">
      <h3 class="text-xl font-bold text-gray-700 mb-4">Imágenes Subidas ({{ uploadedImages.length }})</h3>
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        <div
          v-for="img in uploadedImages"
          :key="img.id"
          class="border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow"
        >
          <img
            :src="img.image_url || img.image"
            :alt="`Imagen ${img.id}`"
            class="w-full h-48 object-cover"
            @error="handleImageError"
          />
          <div class="p-2 bg-gray-50">
            <p class="text-xs text-gray-600 truncate">
              ID: {{ img.id }}
            </p>
            <p v-if="img.uploaded_at" class="text-xs text-gray-500">
              {{ formatDate(img.uploaded_at) }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/services/api.js'

const files = ref([])
const uploadedImages = ref([])
const isUploading = ref(false)
const uploadStatus = ref(null)
const fileInput = ref(null)

const handleFiles = (e) => {
  const selectedFiles = Array.from(e.target.files)
  files.value = [...files.value, ...selectedFiles]
}

const removeFile = (index) => {
  files.value.splice(index, 1)
}

const clearFiles = () => {
  files.value = []
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  uploadStatus.value = null
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('es-CO', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleImageError = (e) => {
  e.target.src = 'https://via.placeholder.com/300x200?text=Error+al+cargar'
}

const uploadImages = async () => {
  if (files.value.length === 0) {
    return
  }

  isUploading.value = true
  uploadStatus.value = null

  const formData = new FormData()
  for (const file of files.value) {
    formData.append('images', file)
  }

  try {
    const res = await api.post('/images/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    const { uploaded, total_uploaded, total_errors, errors } = res.data

    if (total_uploaded > 0) {
      uploadedImages.value = [...uploadedImages.value, ...uploaded]
      uploadStatus.value = {
        type: 'success',
        title: '✅ Subida completada',
        message: `Se subieron ${total_uploaded} imagen${total_uploaded !== 1 ? 'es' : ''} correctamente.${total_errors > 0 ? ` ${total_errors} imagen${total_errors !== 1 ? 'es' : ''} con errores.` : ''}`,
        errors: errors || []
      }
      
      // Limpiar archivos subidos exitosamente
      clearFiles()
    } else {
      uploadStatus.value = {
        type: 'error',
        title: '❌ Error al subir imágenes',
        message: 'No se pudo subir ninguna imagen.',
        errors: errors || []
      }
    }
  } catch (error) {
    console.error('Error al subir imágenes:', error)
    uploadStatus.value = {
      type: 'error',
      title: '❌ Error al subir imágenes',
      message: error.response?.data?.error || error.message || 'Error desconocido al subir las imágenes',
      errors: error.response?.data?.errors || []
    }
  } finally {
    isUploading.value = false
  }
}
</script>


<template>
  <div class="space-y-4">
    <!-- Drop Zone -->
    <div 
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
      @drop.prevent="handleDrop"
      @click="fileInput?.click()"
      class="border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 group"
      :class="{
        'border-green-500 bg-green-50 shadow-lg scale-[1.02]': isDragging,
        'border-gray-300 hover:border-green-400 hover:bg-green-50': !isDragging,
      }"
    >
      <div class="flex flex-col items-center justify-center space-y-3">
        <div class="p-4 bg-green-100 rounded-2xl group-hover:bg-green-200 transition-colors duration-300">
          <svg 
            class="w-12 h-12 text-green-600 group-hover:text-green-700 transition-colors" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              stroke-linecap="round" 
              stroke-linejoin="round" 
              stroke-width="1.5" 
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        </div>
        <p class="text-xl font-bold text-gray-800 group-hover:text-green-700 transition-colors">
          Arrastra tus imágenes aquí o haz clic para seleccionarlas
        </p>
        <p class="text-sm text-gray-500 font-medium">
          Formatos soportados: JPG, PNG (máx. 5MB por imagen)
        </p>
      </div>
      <input
        ref="fileInput"
        type="file"
        class="hidden"
        multiple
        accept="image/*"
        @change="handleFileSelect"
      />
    </div>

    <!-- Previews -->
    <div v-if="images.length > 0" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
      <div 
        v-for="(file, index) in images" 
        :key="getImageKey(file)"
        class="relative group overflow-hidden border-2 border-gray-200 hover:border-green-300 rounded-2xl transition-all duration-300 hover:shadow-lg"
      >
        <img 
          :src="getImageUrl(file)" 
          :alt="file.name ? `Vista previa: ${file.name.replaceAll(/\.[^/.]+$/, '')}` : `Vista previa ${index + 1}`"
          class="w-full h-32 object-cover"
        />
        <button
          @click.stop="removeImage(file)"
          type="button"
          class="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity focus:opacity-100 focus:outline-none focus:ring-2 focus:ring-red-500"
          :aria-label="`Eliminar ${file.name || 'archivo'}`"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="text-red-500 text-sm mt-2">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
// 1. Vue core
import { ref, watch } from 'vue'

// Props
const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  maxFiles: {
    type: Number,
    default: 10
  },
  maxFileSize: {
    type: Number,
    default: 5 // in MB
  }
})

// Emits
const emit = defineEmits(['update:modelValue'])

// State
const isDragging = ref(false)
const fileInput = ref(null)
const error = ref('')
const images = ref([...props.modelValue])

// Helper function to generate unique keys for images
// Uses cryptographically secure random generation to avoid security warnings
const generateSecureId = () => {
  // Use crypto.randomUUID() if available (modern browsers)
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  // Fallback to crypto.getRandomValues() for older browsers
  if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
    const randomArray = new Uint32Array(4)
    crypto.getRandomValues(randomArray)
    return Array.from(randomArray, val => val.toString(36)).join('-')
  }
  // Last resort: use timestamp + counter (not cryptographically secure but better than Math.random)
  return `id-${Date.now()}-${performance.now()}`
}

const getImageKey = (file) => {
  if (file instanceof File) {
    return `${file.name}-${file.size}-${file.lastModified}`
  }
  return file.id || file.url || file.name || generateSecureId()
}

// Functions
const getImageUrl = (file) => {
  if (file instanceof File) {
    return URL.createObjectURL(file)
  }
  return file.url || file
}

const validateFile = (file) => {
  const validTypes = ['image/jpeg', 'image/png', 'image/jpg']
  const maxSize = props.maxFileSize * 1024 * 1024

  if (!validTypes.includes(file.type)) {
    return 'Tipo de archivo no soportado. Por favor, sube solo imágenes JPG o PNG.'
  }

  if (file.size > maxSize) {
    return `El archivo ${file.name} es demasiado grande. Tamaño máximo: ${props.maxFileSize}MB.`
  }

  return ''
}

const handleFileSelect = (event) => {
  error.value = ''
  const files = Array.from(event.target.files)
  processFiles(files)
  
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const handleDrop = (event) => {
  isDragging.value = false
  error.value = ''
  const files = Array.from(event.dataTransfer.files)
  processFiles(files)
}

const processFiles = (files) => {
  if (files.length === 0) return

  if (images.value.length + files.length > props.maxFiles) {
    error.value = `Solo puedes subir un máximo de ${props.maxFiles} imágenes.`
    return
  }

  let hasError = false
  const validFiles = []

  for (const file of files) {
    const validationError = validateFile(file)
    if (validationError) {
      error.value = validationError
      hasError = true
      continue
    }
    validFiles.push(file)
  }

  if (hasError && validFiles.length === 0) return

  images.value = [...images.value, ...validFiles]
  emit('update:modelValue', images.value)
}

const removeImage = (imageToRemove) => {
  const index = images.value.findIndex(img => getImageKey(img) === getImageKey(imageToRemove))
  if (index > -1) {
    images.value.splice(index, 1)
    emit('update:modelValue', images.value)
  }
}

// Watch for changes in modelValue from parent
watch(() => props.modelValue, (newValue) => {
  images.value = [...newValue]
}, { deep: true })
</script>

<style scoped>
/* Solo estilos que no están en Tailwind si es necesario */
</style>

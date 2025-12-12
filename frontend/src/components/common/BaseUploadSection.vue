<template>
  <div class="w-full">
    <!-- Label -->
    <label
      v-if="label"
      :for="fieldId"
      class="block text-sm font-medium text-gray-700 mb-2"
    >
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>

    <!-- Upload area -->
    <div
      :class="[
        'relative border-2 border-dashed rounded-lg p-6 sm:p-8 text-center transition-colors',
        isDragging ? 'border-green-500 bg-green-50' : 'border-gray-300 hover:border-gray-400',
        error ? 'border-red-300 bg-red-50' : '',
        disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
      ]"
      @click="handleClick"
      @dragover.prevent="handleDragOver"
      @dragleave.prevent="handleDragLeave"
      @drop.prevent="handleDrop"
    >
      <!-- Input (hidden) -->
      <input
        :id="fieldId"
        ref="fileInput"
        type="file"
        :accept="accept"
        :multiple="multiple"
        :disabled="disabled"
        class="hidden"
        @change="handleFileChange"
      />

      <!-- Content -->
      <div class="space-y-4">
        <!-- Icon -->
        <div class="mx-auto flex items-center justify-center">
          <slot name="icon">
            <svg
              class="w-12 h-12"
              :class="error ? 'text-red-400' : 'text-gray-400'"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
            </svg>
          </slot>
        </div>

        <!-- Text -->
        <div>
          <p class="text-sm font-medium text-gray-900">
            {{ uploadText }}
          </p>
          <p class="mt-1 text-xs text-gray-500">
            {{ helperText || `Formatos: ${acceptText}. Tamaño máximo: ${maxSizeText}` }}
          </p>
        </div>

        <!-- Button -->
        <button
          type="button"
          :disabled="disabled"
          class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ buttonText }}
        </button>
      </div>

      <!-- Loading overlay -->
      <div v-if="uploading" class="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center rounded-lg">
        <div class="text-center">
          <div class="w-8 h-8 border-4 border-gray-300 border-t-green-600 rounded-full animate-spin mx-auto mb-2"></div>
          <p class="text-sm text-gray-600">{{ uploadingText }}</p>
          <p v-if="uploadProgress > 0" class="text-xs text-gray-500 mt-1">{{ uploadProgress }}%</p>
        </div>
      </div>
    </div>

    <!-- File list -->
    <div v-if="files && files.length > 0" class="mt-4 space-y-2">
      <div
        v-for="(file, index) in files"
        :key="index"
        class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
      >
        <div class="flex items-center space-x-3 flex-1 min-w-0">
          <svg class="w-5 h-5 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900 truncate">{{ file.name }}</p>
            <p class="text-xs text-gray-500">{{ formatFileSize(file.size) }}</p>
          </div>
        </div>
        <button
          v-if="!disabled"
          @click="handleRemoveFile(index)"
          type="button"
          class="ml-3 text-red-600 hover:text-red-800 focus:outline-none focus:ring-2 focus:ring-red-500 rounded"
          aria-label="Eliminar archivo"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
    </div>

    <!-- Error message -->
    <p v-if="error" class="mt-2 text-sm text-red-600">{{ error }}</p>

    <!-- Helper text -->
    <p v-if="helperText && !error" class="mt-2 text-xs text-gray-500">{{ helperText }}</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Generate unique ID for the input field using cryptographically secure random UUID
const generateSecureId = () => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return `upload-${crypto.randomUUID()}`
  }
  // Fallback for older browsers using crypto.getRandomValues
  const array = new Uint8Array(16)
  crypto.getRandomValues(array)
  return `upload-${Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('')}`
}
const fieldId = ref(generateSecureId())

const props = defineProps({
  modelValue: {
    type: [File, Array],
    default: null
  },
  label: {
    type: String,
    default: ''
  },
  accept: {
    type: String,
    default: 'image/*'
  },
  multiple: {
    type: Boolean,
    default: false
  },
  required: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  uploading: {
    type: Boolean,
    default: false
  },
  uploadProgress: {
    type: Number,
    default: 0
  },
  uploadingText: {
    type: String,
    default: 'Subiendo...'
  },
  uploadText: {
    type: String,
    default: 'Arrastra archivos aquí o haz clic para seleccionar'
  },
  buttonText: {
    type: String,
    default: 'Seleccionar archivos'
  },
  helperText: {
    type: String,
    default: null
  },
  error: {
    type: String,
    default: null
  },
  maxSize: {
    type: Number,
    default: 20 * 1024 * 1024 // 20MB
  }
})

const emit = defineEmits(['update:modelValue', 'file-added', 'file-removed', 'upload'])

const fileInput = ref(null)
const isDragging = ref(false)

const files = computed(() => {
  if (Array.isArray(props.modelValue)) {
    return props.modelValue
  }
  return props.modelValue ? [props.modelValue] : []
})

const acceptText = computed(() => {
  if (props.accept === 'image/*') return 'JPG, PNG, WEBP'
  return props.accept.split(',').join(', ')
})

const maxSizeText = computed(() => {
  if (props.maxSize >= 1024 * 1024) {
    return `${(props.maxSize / (1024 * 1024)).toFixed(0)}MB`
  }
  return `${(props.maxSize / 1024).toFixed(0)}KB`
})

const handleClick = () => {
  if (!props.disabled && fileInput.value) {
    fileInput.value.click()
  }
}

const handleFileChange = (event) => {
  const selectedFiles = Array.from(event.target.files || [])
  if (selectedFiles.length === 0) return

  processFiles(selectedFiles)
}

const handleDragOver = (event) => {
  if (!props.disabled) {
    isDragging.value = true
    event.preventDefault()
  }
}

const handleDragLeave = () => {
  isDragging.value = false
}

const handleDrop = (event) => {
  isDragging.value = false
  if (props.disabled) return

  const droppedFiles = Array.from(event.dataTransfer.files || [])
  if (droppedFiles.length === 0) return

  processFiles(droppedFiles)
}

const processFiles = (newFiles) => {
  const validFiles = newFiles.filter(file => {
    // Check file type
    if (props.accept && !file.type.match(props.accept.replace('*', '.*'))) {
      return false
    }
    // Check file size
    if (file.size > props.maxSize) {
      return false
    }
    return true
  })

  if (validFiles.length === 0) {
    emit('update:modelValue', null)
    return
  }

  if (props.multiple) {
    const currentFiles = Array.isArray(props.modelValue) ? props.modelValue : []
    const updatedFiles = [...currentFiles, ...validFiles]
    emit('update:modelValue', updatedFiles)
    for (const file of validFiles) {
      emit('file-added', file)
    }
  } else {
    emit('update:modelValue', validFiles[0])
    emit('file-added', validFiles[0])
  }
}

const handleRemoveFile = (index) => {
  if (props.multiple && Array.isArray(props.modelValue)) {
    const updatedFiles = [...props.modelValue]
    const removedFile = updatedFiles.splice(index, 1)[0]
    emit('update:modelValue', updatedFiles.length > 0 ? updatedFiles : null)
    emit('file-removed', removedFile, index)
  } else {
    emit('update:modelValue', null)
    emit('file-removed', props.modelValue, index)
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}
</script>

<style scoped>
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>


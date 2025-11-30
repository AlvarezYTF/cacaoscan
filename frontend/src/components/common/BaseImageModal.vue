<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 overflow-y-auto"
        @click.self="handleClose"
      >
        <!-- Backdrop -->
        <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"></div>

        <!-- Modal container -->
        <div class="flex min-h-full items-center justify-center p-4">
          <div
            class="relative bg-white rounded-lg shadow-xl max-w-7xl w-full max-h-[90vh] overflow-hidden"
            @click.stop
          >
            <!-- Header -->
            <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
              <div class="flex items-center space-x-3">
                <h3 v-if="title" class="text-lg font-semibold text-gray-900">{{ title }}</h3>
                <span v-if="imageIndex !== null && totalImages > 1" class="text-sm text-gray-500">
                  {{ imageIndex + 1 }} / {{ totalImages }}
                </span>
              </div>
              <div class="flex items-center space-x-2">
                <slot name="header-actions" />
                <button
                  @click="handleClose"
                  class="text-gray-400 hover:text-gray-600 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 rounded"
                  aria-label="Cerrar"
                >
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                </button>
              </div>
            </div>

            <!-- Image container -->
            <div class="relative bg-gray-100 flex items-center justify-center" :style="{ minHeight: '400px' }">
              <!-- Navigation buttons (if multiple images) -->
              <button
                v-if="showNavigation && canNavigatePrevious"
                @click="handlePrevious"
                class="absolute left-4 z-10 p-2 bg-white rounded-full shadow-lg hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500"
                aria-label="Imagen anterior"
              >
                <svg class="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                </svg>
              </button>

              <button
                v-if="showNavigation && canNavigateNext"
                @click="handleNext"
                class="absolute right-4 z-10 p-2 bg-white rounded-full shadow-lg hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500"
                aria-label="Imagen siguiente"
              >
                <svg class="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                </svg>
              </button>

              <!-- Image -->
              <img
                v-if="imageSrc"
                :src="imageSrc"
                :alt="alt"
                class="max-w-full max-h-[70vh] object-contain"
                @load="handleImageLoad"
                @error="handleImageError"
              />

              <!-- Loading state -->
              <div v-if="loading" class="absolute inset-0 flex items-center justify-center">
                <div class="w-12 h-12 border-4 border-gray-300 border-t-green-600 rounded-full animate-spin"></div>
              </div>

              <!-- Error state -->
              <div v-if="error && !loading" class="absolute inset-0 flex items-center justify-center bg-red-50">
                <div class="text-center p-4">
                  <svg class="w-12 h-12 text-red-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <p class="text-sm text-red-600">{{ error }}</p>
                </div>
              </div>
            </div>

            <!-- Footer -->
            <div v-if="$slots.footer || showActions" class="px-6 py-4 border-t border-gray-200 bg-gray-50">
              <slot name="footer">
                <div v-if="showActions" class="flex items-center justify-end space-x-3">
                  <button
                    v-for="action in actions"
                    :key="action.key"
                    @click="handleAction(action)"
                    :class="[
                      'px-4 py-2 rounded-md text-sm font-medium transition-colors',
                      action.variant === 'primary' ? 'bg-green-600 text-white hover:bg-green-700' : '',
                      action.variant === 'secondary' ? 'bg-gray-200 text-gray-900 hover:bg-gray-300' : '',
                      action.variant === 'danger' ? 'bg-red-600 text-white hover:bg-red-700' : '',
                      !action.variant ? 'bg-green-600 text-white hover:bg-green-700' : ''
                    ]"
                  >
                    {{ action.label }}
                  </button>
                </div>
              </slot>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  imageSrc: {
    type: String,
    default: null
  },
  alt: {
    type: String,
    default: 'Vista previa'
  },
  title: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  },
  imageIndex: {
    type: Number,
    default: null
  },
  totalImages: {
    type: Number,
    default: 1
  },
  showNavigation: {
    type: Boolean,
    default: true
  },
  showActions: {
    type: Boolean,
    default: false
  },
  actions: {
    type: Array,
    default: null,
    validator: (value) => {
      if (!value) return true
      return value.every(action => typeof action === 'object' && 'key' in action && 'label' in action)
    }
  },
  closeOnBackdrop: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue', 'close', 'previous', 'next', 'action-click'])

const canNavigatePrevious = computed(() => {
  return props.imageIndex !== null && props.imageIndex > 0
})

const canNavigateNext = computed(() => {
  return props.imageIndex !== null && props.imageIndex < props.totalImages - 1
})

const handleClose = () => {
  if (props.closeOnBackdrop) {
    emit('update:modelValue', false)
    emit('close')
  }
}

const handlePrevious = () => {
  if (canNavigatePrevious.value) {
    emit('previous')
  }
}

const handleNext = () => {
  if (canNavigateNext.value) {
    emit('next')
  }
}

const handleAction = (action) => {
  emit('action-click', action)
}

const handleImageLoad = () => {
  // Image loaded successfully
}

const handleImageError = () => {
  // Image failed to load - error state will be shown
}

// Close on Escape key
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        handleClose()
      }
    }
    document.addEventListener('keydown', handleEscape)
    return () => {
      document.removeEventListener('keydown', handleEscape)
    }
  }
})
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .bg-white,
.modal-leave-active .bg-white {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.modal-enter-from .bg-white,
.modal-leave-to .bg-white {
  transform: scale(0.95);
  opacity: 0;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>


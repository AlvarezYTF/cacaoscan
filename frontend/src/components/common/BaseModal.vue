<template>
  <div 
    v-if="show" 
    class="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-sm"
    :class="overlayClass"
    @click="handleOverlayClick"
  >
    <div 
      class="bg-white rounded-lg shadow-xl border border-gray-200 relative w-full max-h-[90vh] overflow-hidden"
      :class="containerClass"
      @click.stop
    >
      <!-- Header Slot -->
      <div v-if="$slots.header" class="modal-header border-b border-gray-200">
        <slot name="header"></slot>
      </div>
      
      <!-- Default Header -->
      <div v-else-if="title" class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <div class="flex items-center">
          <div v-if="icon" class="bg-green-100 p-2 rounded-lg mr-3">
            <component :is="icon" class="text-xl text-green-600 w-5 h-5" />
          </div>
          <div>
            <h3 class="text-xl font-bold text-gray-900">{{ title }}</h3>
            <p v-if="subtitle" class="text-sm text-gray-600 mt-1">{{ subtitle }}</p>
          </div>
        </div>
        <button 
          v-if="showCloseButton"
          @click="handleClose"
          type="button"
          class="text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg p-2 transition-all duration-200"
          aria-label="Cerrar modal"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Body Slot -->
      <div class="modal-body overflow-y-auto" :class="bodyClass">
        <slot></slot>
      </div>

      <!-- Footer Slot -->
      <div v-if="$slots.footer" class="modal-footer border-t border-gray-200 bg-gray-50">
        <slot name="footer"></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: true
  },
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  icon: {
    type: [String, Object],
    default: null
  },
  showCloseButton: {
    type: Boolean,
    default: true
  },
  closeOnOverlay: {
    type: Boolean,
    default: true
  },
  maxWidth: {
    type: String,
    default: '2xl',
    validator: (value) => ['sm', 'md', 'lg', 'xl', '2xl', '3xl', '4xl', '5xl', '6xl', 'full'].includes(value)
  },
  overlayClass: {
    type: String,
    default: 'bg-black bg-opacity-50'
  },
  containerClass: {
    type: String,
    default: ''
  },
  bodyClass: {
    type: String,
    default: 'p-6'
  }
})

const emit = defineEmits(['close', 'update:show'])

const computedContainerClass = computed(() => {
  const maxWidthClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
    '3xl': 'max-w-3xl',
    '4xl': 'max-w-4xl',
    '5xl': 'max-w-5xl',
    '6xl': 'max-w-6xl',
    full: 'max-w-full'
  }
  
  return `${maxWidthClasses[props.maxWidth]} ${props.containerClass}`.trim()
})

const handleClose = () => {
  emit('close')
  emit('update:show', false)
}

const handleOverlayClick = () => {
  if (props.closeOnOverlay) {
    handleClose()
  }
}
</script>

<style scoped>
.modal-header {
  padding: 1.5rem;
}

.modal-body {
  max-height: calc(90vh - 200px);
}

.modal-footer {
  padding: 1.5rem;
}

/* Animation */
@keyframes modalAppear {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.bg-white {
  animation: modalAppear 0.2s ease-out;
}
</style>


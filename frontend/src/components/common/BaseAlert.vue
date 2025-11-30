<template>
  <Transition
    enter-active-class="transform ease-out duration-300 transition"
    enter-from-class="opacity-0 translate-y-2"
    enter-to-class="opacity-100 translate-y-0"
    leave-active-class="transition ease-in duration-200"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div 
      v-if="show" 
      class="border-l-4 p-4 rounded-r-md shadow-sm"
      :class="alertClasses"
    >
      <div class="flex">
        <div class="flex-shrink-0">
          <svg 
            class="h-5 w-5" 
            :class="iconColorClass"
            xmlns="http://www.w3.org/2000/svg" 
            viewBox="0 0 20 20" 
            fill="currentColor"
          >
            <path :d="iconPath" fill-rule="evenodd" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3 flex-1">
          <p v-if="title" class="text-sm font-semibold" :class="titleColorClass">
            {{ title }}
          </p>
          <p class="text-sm font-medium" :class="messageColorClass">
            {{ message }}
          </p>
          <div v-if="$slots.default" class="mt-2">
            <slot></slot>
          </div>
        </div>
        <div v-if="dismissible" class="ml-3 flex-shrink-0">
          <button
            @click="handleDismiss"
            type="button"
            class="text-gray-400 hover:text-gray-600 rounded-lg p-1 focus:outline-none focus:ring-2 focus:ring-offset-2"
            :class="dismissButtonClass"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'error',
    validator: (value) => ['error', 'success', 'warning', 'info', 'critical'].includes(value)
  },
  message: {
    type: String,
    required: true
  },
  title: {
    type: String,
    default: ''
  },
  show: {
    type: Boolean,
    default: true
  },
  dismissible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['dismiss', 'update:show'])

const alertClasses = computed(() => {
  const classes = {
    error: 'bg-red-50 border-red-400',
    success: 'bg-green-50 border-green-400',
    warning: 'bg-yellow-50 border-yellow-400',
    info: 'bg-blue-50 border-blue-400',
    critical: 'bg-red-100 border-red-600'
  }
  return classes[props.variant] || classes.error
})

const iconColorClass = computed(() => {
  const classes = {
    error: 'text-red-500',
    success: 'text-green-500',
    warning: 'text-yellow-500',
    info: 'text-blue-500',
    critical: 'text-red-600'
  }
  return classes[props.variant] || classes.error
})

const titleColorClass = computed(() => {
  const classes = {
    error: 'text-red-900',
    success: 'text-green-900',
    warning: 'text-yellow-900',
    info: 'text-blue-900',
    critical: 'text-red-900'
  }
  return classes[props.variant] || classes.error
})

const messageColorClass = computed(() => {
  const classes = {
    error: 'text-red-800',
    success: 'text-green-800',
    warning: 'text-yellow-800',
    info: 'text-blue-800',
    critical: 'text-red-800'
  }
  return classes[props.variant] || classes.error
})

const dismissButtonClass = computed(() => {
  const classes = {
    error: 'hover:bg-red-100 focus:ring-red-500',
    success: 'hover:bg-green-100 focus:ring-green-500',
    warning: 'hover:bg-yellow-100 focus:ring-yellow-500',
    info: 'hover:bg-blue-100 focus:ring-blue-500',
    critical: 'hover:bg-red-200 focus:ring-red-600'
  }
  return classes[props.variant] || classes.error
})

const iconPath = computed(() => {
  const paths = {
    success: 'M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z',
    warning: 'M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z',
    error: 'M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z',
    info: 'M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z',
    critical: 'M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z'
  }
  return paths[props.variant] || paths.error
})

const handleDismiss = () => {
  emit('dismiss')
  emit('update:show', false)
}
</script>

<style scoped>
/* Transitions are handled by Tailwind classes */
</style>


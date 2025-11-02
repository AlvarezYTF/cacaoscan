<template>
  <svg
    :class="spinnerClasses"
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
  >
    <circle 
      class="opacity-25" 
      cx="12" 
      cy="12" 
      r="10" 
      stroke="currentColor" 
      :stroke-width="strokeWidth"
    ></circle>
    <path 
      class="opacity-75" 
      fill="currentColor" 
      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
    ></path>
  </svg>
</template>

<script setup>
// 1. Vue core
import { computed } from 'vue'

// Props
const props = defineProps({
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['xs', 'sm', 'md', 'lg', 'xl'].includes(value)
  },
  color: {
    type: String,
    default: 'white',
    validator: (value) => ['white', 'gray', 'blue', 'green', 'red', 'yellow', 'purple'].includes(value)
  },
  strokeWidth: {
    type: String,
    default: '4'
  },
  className: {
    type: String,
    default: ''
  }
})

// Computed
const spinnerClasses = computed(() => {
  const baseClasses = 'animate-spin'
  const sizeClasses = {
    xs: 'h-3 w-3',
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6',
    xl: 'h-8 w-8'
  }
  const colorClasses = {
    white: 'text-white',
    gray: 'text-gray-600',
    blue: 'text-blue-600',
    green: 'text-green-600',
    red: 'text-red-600',
    yellow: 'text-yellow-600',
    purple: 'text-purple-600'
  }
  
  return [
    baseClasses,
    sizeClasses[props.size],
    colorClasses[props.color],
    props.className
  ].filter(Boolean).join(' ')
})
</script>

<style scoped>
/* Solo animación personalizada que no está en Tailwind */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Variantes de tamaño - Tailwind ya tiene estas clases, pero las mantenemos por compatibilidad */
.h-3 { height: 0.75rem; width: 0.75rem; }
.h-4 { height: 1rem; width: 1rem; }
.h-5 { height: 1.25rem; width: 1.25rem; }
.h-6 { height: 1.5rem; width: 1.5rem; }
.h-8 { height: 2rem; width: 2rem; }
</style>

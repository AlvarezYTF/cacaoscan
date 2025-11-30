<template>
  <div class="w-full" :class="containerClass">
    <!-- Label (optional for search) -->
    <label
      v-if="label"
      :for="id"
      class="block text-sm font-medium text-gray-700 mb-1"
    >
      {{ label }}
    </label>

    <!-- Search input wrapper -->
    <div class="relative">
      <!-- Search icon (always on left) -->
      <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
        </svg>
      </div>

      <!-- Input -->
      <input
        :id="id"
        type="search"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :class="inputClass"
        @input="handleInput"
        @keyup.enter="handleSearch"
        @blur="handleBlur"
        @focus="handleFocus"
        v-bind="$attrs"
      />

      <!-- Clear button (when has value) -->
      <button
        v-if="modelValue && showClearButton && !disabled"
        type="button"
        @click="handleClear"
        class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 focus:outline-none"
        aria-label="Clear search"
      >
        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>

      <!-- Loading indicator -->
      <div v-if="loading" class="absolute inset-y-0 right-0 pr-3 flex items-center">
        <div class="w-5 h-5 border-2 border-gray-300 border-t-green-600 rounded-full animate-spin"></div>
      </div>
    </div>

    <!-- Helper text -->
    <p v-if="helperText" class="mt-1 text-xs text-gray-500">{{ helperText }}</p>

    <!-- Error message -->
    <p v-if="error" class="mt-1 text-xs text-red-600">{{ error }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

/**
 * Generates a cryptographically secure unique ID
 * Uses crypto.getRandomValues() for security instead of Math.random()
 * @param {string} prefix - Prefix for the ID
 * @returns {string} Unique ID
 */
const generateSecureId = (prefix = 'id') => {
  const prefixStr = prefix
  
  // Use crypto.getRandomValues() if available (cryptographically secure)
  if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
    const array = new Uint8Array(9)
    crypto.getRandomValues(array)
    // Convert to base36 string (similar to Math.random().toString(36))
    const randomStr = Array.from(array, byte => byte.toString(36)).join('').substring(0, 9)
    return `${prefixStr}-${randomStr}`
  }
  
  // Fallback: use timestamp and counter (not cryptographically secure but acceptable for DOM IDs)
  const timestamp = Date.now().toString(36)
  const counter = (generateSecureId.counter = (generateSecureId.counter || 0) + 1)
  return `${prefixStr}-${timestamp}-${counter.toString(36)}`
}

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'Buscar...'
  },
  helperText: {
    type: String,
    default: ''
  },
  error: {
    type: String,
    default: null
  },
  disabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  showClearButton: {
    type: Boolean,
    default: true
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'filled', 'outlined'].includes(value)
  },
  id: {
    type: String,
    default: () => generateSecureId('search')
  }
})

const emit = defineEmits(['update:modelValue', 'search', 'clear', 'blur', 'focus', 'input'])

const inputClass = computed(() => {
  const baseClasses = 'block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 transition-colors pl-10'
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm pr-10',
    md: 'px-3 py-2 text-sm pr-10',
    lg: 'px-4 py-3 text-base pr-12'
  }

  const variantClasses = {
    default: 'border',
    filled: 'border-0 bg-gray-100',
    outlined: 'border-2'
  }

  const stateClasses = props.error
    ? 'border-red-300 text-red-900 placeholder-red-300 focus:border-red-500 focus:ring-red-500'
    : ''

  const clearPadding = props.modelValue && props.showClearButton && !props.disabled ? 'pr-10' : ''
  const loadingPadding = props.loading ? 'pr-10' : ''

  return [
    baseClasses,
    sizeClasses[props.size],
    variantClasses[props.variant],
    stateClasses,
    clearPadding || loadingPadding,
    props.disabled ? 'bg-gray-50 text-gray-500 cursor-not-allowed' : ''
  ].filter(Boolean).join(' ')
})

const containerClass = computed(() => {
  return props.size === 'sm' ? 'text-sm' : ''
})

const handleInput = (event) => {
  emit('update:modelValue', event.target.value)
  emit('input', event)
}

const handleSearch = (event) => {
  emit('search', event.target.value, event)
}

const handleClear = () => {
  emit('update:modelValue', '')
  emit('clear')
}

const handleBlur = (event) => {
  emit('blur', event)
}

const handleFocus = (event) => {
  emit('focus', event)
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


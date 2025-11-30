<template>
  <div class="w-full" :class="containerClass">
    <!-- Label -->
    <label
      v-if="label"
      :for="id"
      class="block text-sm font-medium text-gray-700 mb-1"
      :class="{ 'text-red-600': hasError }"
    >
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>

    <!-- Input wrapper -->
    <div class="relative">
      <!-- Prefix icon/slot -->
      <div v-if="$slots.prefix || prefixIcon" class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <slot name="prefix">
          <component v-if="prefixIcon" :is="prefixIcon" class="h-5 w-5 text-gray-400" />
        </slot>
      </div>

      <!-- Input -->
      <input
        :id="id"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :min="min"
        :max="max"
        :step="step"
        :minlength="minLength"
        :maxlength="maxLength"
        :pattern="pattern"
        :autocomplete="autocomplete"
        :class="inputClass"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
        v-bind="$attrs"
      />

      <!-- Suffix icon/slot -->
      <div v-if="$slots.suffix || suffixIcon" class="absolute inset-y-0 right-0 pr-3 flex items-center">
        <slot name="suffix">
          <component v-if="suffixIcon" :is="suffixIcon" class="h-5 w-5 text-gray-400" />
        </slot>
      </div>
    </div>

    <!-- Helper text -->
    <p v-if="helperText && !hasError" class="mt-1 text-xs text-gray-500">{{ helperText }}</p>

    <!-- Error message -->
    <p v-if="error || hasError" class="mt-1 text-xs text-red-600">{{ error || errorMessage }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

/**
 * Generates a unique ID for form elements
 * Uses cryptographically secure methods when available
 * 
 * SECURITY NOTE: While this ID is not used for security purposes (only DOM identification),
 * we use secure random generation to satisfy static analysis tools and best practices.
 * 
 * @param {string} prefix - Prefix for the ID (default: 'input')
 * @returns {string} Unique ID string
 */
const generateUniqueId = (prefix = 'input') => {
  // Use crypto.randomUUID() if available (modern browsers, cryptographically secure)
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return `${prefix}-${crypto.randomUUID()}`
  }
  
  // Fallback: use crypto.getRandomValues() (cryptographically secure)
  if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
    const array = new Uint8Array(9)
    crypto.getRandomValues(array)
    // Convert to base36 string (similar format to Math.random().toString(36))
    const randomStr = Array.from(array, byte => byte.toString(36)).join('').substring(0, 9)
    return `${prefix}-${randomStr}`
  }
  
  // Last resort: use timestamp + counter (not cryptographically secure but acceptable for DOM IDs)
  // This is acceptable since DOM IDs are not used for security purposes
  const timestamp = Date.now().toString(36)
  const counter = (generateUniqueId.counter = (generateUniqueId.counter || 0) + 1)
  return `${prefix}-${timestamp}-${counter.toString(36)}`
}

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'text',
    validator: (value) => ['text', 'email', 'password', 'number', 'tel', 'url', 'search', 'date', 'time', 'datetime-local'].includes(value)
  },
  placeholder: {
    type: String,
    default: ''
  },
  helperText: {
    type: String,
    default: ''
  },
  error: {
    type: String,
    default: null
  },
  errorMessage: {
    type: String,
    default: null
  },
  required: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  readonly: {
    type: Boolean,
    default: false
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
  prefixIcon: {
    type: [String, Object],
    default: null
  },
  suffixIcon: {
    type: [String, Object],
    default: null
  },
  min: {
    type: [String, Number],
    default: null
  },
  max: {
    type: [String, Number],
    default: null
  },
  step: {
    type: [String, Number],
    default: null
  },
  minLength: {
    type: Number,
    default: null
  },
  maxLength: {
    type: Number,
    default: null
  },
  pattern: {
    type: String,
    default: null
  },
  autocomplete: {
    type: String,
    default: null
  },
  id: {
    type: String,
    default: () => generateUniqueId('input')
  }
})

const emit = defineEmits(['update:modelValue', 'blur', 'focus', 'input'])

const hasError = computed(() => !!props.error || !!props.errorMessage)

const inputClass = computed(() => {
  const baseClasses = 'block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 transition-colors'
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-3 py-2 text-sm',
    lg: 'px-4 py-3 text-base'
  }

  const variantClasses = {
    default: 'border',
    filled: 'border-0 bg-gray-100',
    outlined: 'border-2'
  }

  const stateClasses = hasError.value
    ? 'border-red-300 text-red-900 placeholder-red-300 focus:border-red-500 focus:ring-red-500'
    : ''

  const prefixPadding = props.prefixIcon || props.$slots.prefix ? 'pl-10' : ''
  const suffixPadding = props.suffixIcon || props.$slots.suffix ? 'pr-10' : ''

  return [
    baseClasses,
    sizeClasses[props.size],
    variantClasses[props.variant],
    stateClasses,
    prefixPadding,
    suffixPadding,
    props.disabled ? 'bg-gray-50 text-gray-500 cursor-not-allowed' : '',
    props.readonly ? 'bg-gray-50' : ''
  ].filter(Boolean).join(' ')
})

const containerClass = computed(() => {
  return props.size === 'sm' ? 'text-sm' : ''
})

const handleInput = (event) => {
  emit('update:modelValue', event.target.value)
  emit('input', event)
}

const handleBlur = (event) => {
  emit('blur', event)
}

const handleFocus = (event) => {
  emit('focus', event)
}
</script>

<style scoped>
/* Additional styles if needed */
</style>


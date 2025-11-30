<template>
  <div class="w-full" :class="containerClass">
    <!-- Label -->
    <div v-if="label" class="flex items-center justify-between mb-2">
      <label :for="id" class="text-sm font-medium text-gray-700">{{ label }}</label>
      <span v-if="showValue" class="text-sm text-gray-600">{{ formattedValue }}</span>
    </div>

    <!-- Progress Bar -->
    <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden relative" :class="barClass">
      <progress
        :id="id"
        class="progress-bar h-full transition-all duration-300 ease-out rounded-full"
        :class="progressBarClass"
        :value="value"
        :min="min"
        :max="max"
        :aria-label="ariaLabel || label"
      >
        {{ formattedValue }}
      </progress>
      <div v-if="animated" class="h-full w-full bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-shimmer absolute top-0 left-0 pointer-events-none"></div>
    </div>

    <!-- Helper text -->
    <p v-if="helperText" class="mt-1 text-xs text-gray-500">{{ helperText }}</p>

    <!-- Error message -->
    <p v-if="error" class="mt-1 text-xs text-red-600">{{ error }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: {
    type: Number,
    required: true,
    validator: (value) => value >= 0
  },
  max: {
    type: Number,
    default: 100
  },
  min: {
    type: Number,
    default: 0
  },
  label: {
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
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'success', 'warning', 'danger', 'info'].includes(value)
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  showValue: {
    type: Boolean,
    default: false
  },
  format: {
    type: String,
    default: 'percentage',
    validator: (value) => ['percentage', 'fraction', 'number'].includes(value)
  },
  animated: {
    type: Boolean,
    default: false
  },
  id: {
    type: String,
    default: () => {
      // Use cryptographically secure random number generator for unique ID
      // SonarQube S2245: crypto.getRandomValues() is safe for generating unique IDs
      if (typeof crypto !== 'undefined' && crypto.randomUUID) {
        return `progress-${crypto.randomUUID()}`
      }
      if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
        const array = new Uint8Array(9)
        crypto.getRandomValues(array)
        const randomStr = Array.from(array, byte => byte.toString(36)).join('').substring(0, 9)
        return `progress-${randomStr}`
      }
      // Fallback: Use timestamp + counter for uniqueness
      const timestamp = Date.now().toString(36)
      const counter = (globalThis.__progressIdCounter = (globalThis.__progressIdCounter || 0) + 1)
      return `progress-${timestamp}-${counter.toString(36)}`
    }
  },
  ariaLabel: {
    type: String,
    default: null
  }
})

const percentage = computed(() => {
  const range = props.max - props.min
  if (range === 0) return 0
  const clampedValue = Math.max(props.min, Math.min(props.max, props.value))
  return ((clampedValue - props.min) / range) * 100
})

const formattedValue = computed(() => {
  switch (props.format) {
    case 'percentage':
      return `${Math.round(percentage.value)}%`
    case 'fraction':
      return `${props.value} / ${props.max}`
    case 'number':
      return props.value.toString()
    default:
      return `${Math.round(percentage.value)}%`
  }
})

const progressBarClass = computed(() => {
  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  }

  const variantClasses = {
    default: 'bg-blue-600',
    success: 'bg-green-600',
    warning: 'bg-yellow-600',
    danger: 'bg-red-600',
    info: 'bg-blue-500'
  }

  return `${sizeClasses[props.size]} ${variantClasses[props.variant]}`
})

const barClass = computed(() => {
  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  }
  return sizeClasses[props.size]
})

const containerClass = computed(() => {
  return props.size === 'sm' ? 'text-sm' : ''
})
</script>

<style scoped>
@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.animate-shimmer {
  animation: shimmer 2s infinite;
}

/* Style progress element to match previous appearance */
.progress-bar {
  width: 100%;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  border: none;
  background: transparent;
}

.progress-bar::-webkit-progress-bar {
  background: transparent;
  border-radius: 9999px;
}

.progress-bar::-webkit-progress-value {
  border-radius: 9999px;
  transition: width 0.3s ease-out;
}

.progress-bar::-moz-progress-bar {
  border-radius: 9999px;
  transition: width 0.3s ease-out;
}
</style>


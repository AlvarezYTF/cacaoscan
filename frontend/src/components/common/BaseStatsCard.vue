<template>
  <div 
    class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-all duration-300"
    :class="{ 'opacity-60 pointer-events-none': loading }"
  >
    <div class="p-4 md:p-5">
      <div class="flex items-center">
        <!-- Icon -->
        <div class="flex-shrink-0 rounded-lg p-2 md:p-3" :class="iconBgColor">
          <slot name="icon">
            <component 
              v-if="icon" 
              :is="icon" 
              class="h-5 w-5 md:h-6 md:w-6" 
              :class="iconColor" 
            />
          </slot>
        </div>

        <!-- Content -->
        <div class="ml-3 md:ml-5 flex-1">
          <dl>
            <dt class="text-xs md:text-sm font-medium text-gray-500 truncate">{{ title }}</dt>
            <dd class="mt-1">
              <div class="text-lg md:text-2xl font-semibold text-gray-900">
                <slot name="value">
                  {{ formattedValue }}
                </slot>
              </div>
              
              <!-- Trend indicator -->
              <div v-if="trend" class="text-xs md:text-sm flex items-center mt-1" :class="trendColor">
                <svg 
                  v-if="trend.value > 0" 
                  class="w-3 h-3 md:w-4 md:w-4 mr-1" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"></path>
                </svg>
                <svg 
                  v-else-if="trend.value < 0" 
                  class="w-3 h-3 md:w-4 md:w-4 mr-1" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
                </svg>
                <span>{{ trend.label || `${Math.abs(trend.value)}% desde el mes pasado` }}</span>
              </div>
            </dd>
          </dl>
        </div>
      </div>

      <!-- Footer slot -->
      <div v-if="$slots.footer" class="mt-4 pt-4 border-t border-gray-100">
        <slot name="footer" />
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75">
      <div class="w-6 h-6 border-2 border-gray-300 border-t-green-600 rounded-full animate-spin"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  icon: {
    type: [String, Object],
    default: null
  },
  trend: {
    type: Object,
    default: null,
    validator: (value) => {
      if (!value) return true
      return typeof value.value === 'number' && (value.label === undefined || typeof value.label === 'string')
    }
  },
  format: {
    type: String,
    default: 'number',
    validator: (value) => ['number', 'currency', 'percentage'].includes(value)
  },
  loading: {
    type: Boolean,
    default: false
  },
  color: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'success', 'warning', 'danger', 'info'].includes(value)
  }
})

const iconBgColor = computed(() => {
  const colors = {
    default: 'bg-gray-50',
    success: 'bg-green-50',
    warning: 'bg-yellow-50',
    danger: 'bg-red-50',
    info: 'bg-blue-50'
  }
  return colors[props.color] || colors.default
})

const iconColor = computed(() => {
  const colors = {
    default: 'text-gray-600',
    success: 'text-green-600',
    warning: 'text-yellow-600',
    danger: 'text-red-600',
    info: 'text-blue-600'
  }
  return colors[props.color] || colors.default
})

const trendColor = computed(() => {
  if (!props.trend) return ''
  
  if (props.trend.value > 0) {
    return 'text-green-600'
  } else if (props.trend.value < 0) {
    return 'text-red-600'
  } else {
    return 'text-gray-600'
  }
})

const formattedValue = computed(() => {
  const numValue = typeof props.value === 'number' ? props.value : Number.parseFloat(props.value)
  
  if (Number.isNaN(numValue)) {
    return props.value
  }

  switch (props.format) {
    case 'currency':
      return new Intl.NumberFormat('es-CO', { 
        style: 'currency', 
        currency: 'COP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(numValue)
    case 'percentage':
      return `${numValue.toFixed(1)}%`
    case 'number':
    default:
      return new Intl.NumberFormat('es-CO').format(numValue)
  }
})
</script>

<style scoped>
/* Responsive adjustments */
@media (max-width: 768px) {
  .md\:p-5 {
    padding: 1rem;
  }
  
  .md\:ml-5 {
    margin-left: 0.75rem;
  }
  
  .md\:h-6.md\:w-6 {
    width: 1.25rem;
    height: 1.25rem;
  }
  
  .md\:text-2xl {
    font-size: 1.5rem;
    line-height: 2rem;
  }
}

/* Transitions */
* {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

/* Hover effects */
.hover\:shadow-md:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

/* Loading animation */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>

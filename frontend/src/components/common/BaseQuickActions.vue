<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6" :class="containerClass">
    <!-- Header -->
    <div v-if="title || $slots.header" class="mb-4">
      <h3 v-if="title" class="text-lg font-semibold text-gray-900 mb-1">{{ title }}</h3>
      <p v-if="subtitle" class="text-sm text-gray-600">{{ subtitle }}</p>
      <slot name="header" />
    </div>

    <!-- Actions grid -->
    <div :class="gridClass">
      <button
        v-for="action in actions"
        :key="action.key"
        @click="handleActionClick(action)"
        :disabled="action.disabled || loading"
        :class="[
          'flex flex-col items-center justify-center p-4 rounded-lg border-2 transition-all duration-200',
          'hover:shadow-md hover:scale-105 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2',
          action.variant === 'primary' ? 'border-green-500 bg-green-50 text-green-700 hover:bg-green-100' : '',
          action.variant === 'secondary' ? 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50' : '',
          action.variant === 'danger' ? 'border-red-500 bg-red-50 text-red-700 hover:bg-red-100' : '',
          action.variant === 'success' ? 'border-green-500 bg-green-50 text-green-700 hover:bg-green-100' : '',
          !action.variant ? 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50' : '',
          action.disabled || loading ? 'opacity-50 cursor-not-allowed hover:scale-100' : ''
        ]"
        :title="action.title || action.label"
      >
        <!-- Icon -->
        <div class="mb-2">
          <slot :name="`icon-${action.key}`">
            <component
              v-if="action.icon"
              :is="action.icon"
              class="w-8 h-8"
              :class="action.variant === 'primary' || action.variant === 'success' ? 'text-green-600' : 'text-gray-600'"
            />
          </slot>
        </div>

        <!-- Label -->
        <span class="text-sm font-medium text-center">{{ action.label }}</span>

        <!-- Badge (optional) -->
        <span v-if="action.badge" class="mt-1 px-2 py-0.5 text-xs font-semibold rounded-full bg-green-100 text-green-800">
          {{ action.badge }}
        </span>
      </button>

      <!-- Custom action slots -->
      <slot />
    </div>

    <!-- Footer -->
    <div v-if="$slots.footer" class="mt-4 pt-4 border-t border-gray-200">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  actions: {
    type: Array,
    required: true,
    validator: (value) => {
      return value.every(action => 
        typeof action === 'object' && 
        'key' in action && 
        'label' in action
      )
    }
  },
  columns: {
    type: Number,
    default: 4,
    validator: (value) => [2, 3, 4, 5, 6].includes(value)
  },
  loading: {
    type: Boolean,
    default: false
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'compact', 'spacious'].includes(value)
  }
})

const emit = defineEmits(['action-click'])

const gridClass = computed(() => {
  const columnClasses = {
    2: 'grid-cols-2',
    3: 'grid-cols-3',
    4: 'grid-cols-2 sm:grid-cols-4',
    5: 'grid-cols-2 sm:grid-cols-5',
    6: 'grid-cols-3 sm:grid-cols-6'
  }

  const spacingClasses = {
    default: 'gap-4',
    compact: 'gap-2',
    spacious: 'gap-6'
  }

  return `grid ${columnClasses[props.columns]} ${spacingClasses[props.variant]}`
})

const containerClass = computed(() => {
  const variantClasses = {
    default: '',
    compact: 'p-3',
    spacious: 'p-8'
  }
  return variantClasses[props.variant]
})

const handleActionClick = (action) => {
  if (!action.disabled && !props.loading) {
    emit('action-click', action)
  }
}
</script>

<style scoped>
/* Additional styles if needed */
</style>


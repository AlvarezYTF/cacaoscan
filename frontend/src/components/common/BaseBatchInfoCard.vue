<template>
  <div class="bg-white rounded-lg border border-gray-200 p-4 sm:p-6" :class="containerClass">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center space-x-3">
        <div v-if="icon" class="p-2 bg-blue-100 rounded-lg">
          <component :is="icon" class="w-5 h-5 text-blue-600" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-gray-900">{{ title || 'Información del Lote' }}</h3>
          <p v-if="subtitle" class="text-sm text-gray-600 mt-1">{{ subtitle }}</p>
        </div>
      </div>
      <slot name="header-actions" />
    </div>

    <!-- Batch info -->
    <div class="space-y-3">
      <!-- Total items -->
      <div v-if="batchInfo.total !== undefined" class="flex items-center justify-between">
        <span class="text-sm text-gray-600">Total de elementos:</span>
        <span class="text-sm font-semibold text-gray-900">{{ batchInfo.total }}</span>
      </div>

      <!-- Completed -->
      <div v-if="batchInfo.completed !== undefined" class="flex items-center justify-between">
        <span class="text-sm text-gray-600">Completados:</span>
        <span class="text-sm font-semibold text-green-600">{{ batchInfo.completed }}</span>
      </div>

      <!-- Failed -->
      <div v-if="batchInfo.failed !== undefined && batchInfo.failed > 0" class="flex items-center justify-between">
        <span class="text-sm text-gray-600">Fallidos:</span>
        <span class="text-sm font-semibold text-red-600">{{ batchInfo.failed }}</span>
      </div>

      <!-- Progress -->
      <div v-if="batchInfo.total && batchInfo.total > 0" class="mt-4">
        <BaseProgressIndicator
          :value="batchInfo.completed || 0"
          :max="batchInfo.total"
          :format="'fraction'"
          :variant="batchInfo.failed > 0 ? 'warning' : 'success'"
        />
      </div>

      <!-- Custom content slot -->
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
import BaseProgressIndicator from './BaseProgressIndicator.vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  batchInfo: {
    type: Object,
    required: true,
    validator: (value) => {
      return value && typeof value === 'object'
    }
  },
  icon: {
    type: [String, Object],
    default: null
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'compact', 'detailed'].includes(value)
  }
})

const containerClass = computed(() => {
  const variants = {
    default: '',
    compact: 'p-3',
    detailed: 'p-6'
  }
  return variants[props.variant]
})
</script>

<style scoped>
/* Additional styles if needed */
</style>


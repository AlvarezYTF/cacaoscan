<template>
  <div class="animate-pulse" :class="containerClass">
    <!-- Text skeleton -->
    <div v-if="type === 'text'" class="space-y-2">
      <div
        v-for="(line, index) in lines"
        :key="index"
        class="h-4 bg-gray-200 rounded"
        :class="lineClass"
        :style="{ width: line.width || '100%' }"
      ></div>
    </div>

    <!-- Card skeleton -->
    <div v-else-if="type === 'card'" class="bg-white rounded-lg border border-gray-200 p-4 sm:p-6">
      <div class="flex items-center space-x-4 mb-4">
        <div class="w-12 h-12 bg-gray-200 rounded-full"></div>
        <div class="flex-1 space-y-2">
          <div class="h-4 bg-gray-200 rounded w-3/4"></div>
          <div class="h-3 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
      <div class="space-y-2">
        <div class="h-3 bg-gray-200 rounded"></div>
        <div class="h-3 bg-gray-200 rounded w-5/6"></div>
      </div>
    </div>

    <!-- Table skeleton -->
    <div v-else-if="type === 'table'" class="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <div class="flex space-x-4">
          <div
            v-for="i in columns"
            :key="i"
            class="h-4 bg-gray-200 rounded flex-1"
          ></div>
        </div>
      </div>
      <!-- Rows -->
      <div class="divide-y divide-gray-200">
        <div
          v-for="i in rows"
          :key="i"
          class="px-6 py-4"
        >
          <div class="flex space-x-4">
            <div
              v-for="j in columns"
              :key="j"
              class="h-4 bg-gray-200 rounded flex-1"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Image skeleton -->
    <div v-else-if="type === 'image'" class="bg-gray-200 rounded" :class="imageClass"></div>

    <!-- Custom skeleton -->
    <div v-else class="space-y-2">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'text',
    validator: (value) => ['text', 'card', 'table', 'image', 'custom'].includes(value)
  },
  lines: {
    type: Number,
    default: 3
  },
  columns: {
    type: Number,
    default: 4
  },
  rows: {
    type: Number,
    default: 5
  },
  width: {
    type: String,
    default: '100%'
  },
  height: {
    type: String,
    default: 'auto'
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'compact', 'spacious'].includes(value)
  }
})

const containerClass = computed(() => {
  const variants = {
    default: '',
    compact: 'p-2',
    spacious: 'p-6'
  }
  return variants[props.variant]
})

const lineClass = computed(() => {
  return props.variant === 'compact' ? 'h-3' : 'h-4'
})

const imageClass = computed(() => {
  return {
    'w-full': !props.width || props.width === '100%',
    'h-48': !props.height || props.height === 'auto'
  }
})
</script>

<style scoped>
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>


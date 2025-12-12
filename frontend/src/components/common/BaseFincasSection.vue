<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden" :class="containerClass">
    <!-- Section header -->
    <div v-if="title || $slots.header || showActions" class="px-4 sm:px-6 py-4 border-b border-gray-200 bg-gray-50">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <slot name="header-icon">
            <div v-if="icon" class="p-2 bg-green-100 rounded-lg">
              <component :is="icon" class="w-5 h-5 text-green-600" />
            </div>
          </slot>
          <div>
            <h3 v-if="title" class="text-lg font-semibold text-gray-900">{{ title }}</h3>
            <p v-if="subtitle" class="mt-1 text-sm text-gray-600">{{ subtitle }}</p>
          </div>
          <slot name="header" />
        </div>

        <div v-if="showActions || $slots.actions" class="flex items-center space-x-2">
          <slot name="actions" />
        </div>
      </div>
    </div>

    <!-- Section content -->
    <div class="p-4 sm:p-6" :class="{ 'p-0': noPadding }">
      <slot />
    </div>

    <!-- Section footer -->
    <div v-if="$slots.footer" class="px-4 sm:px-6 py-4 border-t border-gray-200 bg-gray-50">
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
  icon: {
    type: [String, Object],
    default: null
  },
  showActions: {
    type: Boolean,
    default: false
  },
  noPadding: {
    type: Boolean,
    default: false
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'bordered', 'shadow'].includes(value)
  }
})

const containerClass = computed(() => {
  const variants = {
    default: '',
    bordered: 'border-2',
    shadow: 'shadow-md'
  }
  return variants[props.variant] || ''
})

// Expose computed property for testing
defineExpose({
  containerClass
})
</script>

<style scoped>
/* Additional styles if needed */
</style>


<template>
  <div :class="['base-dashboard-widget', widgetClass]">
    <!-- Header -->
    <div v-if="showHeader || $slots.header" class="base-dashboard-widget-header">
      <slot name="header">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div v-if="icon" class="p-2 rounded-lg" :class="iconBgClass">
              <i v-if="icon.startsWith('fas') || icon.startsWith('fa')" :class="icon"></i>
              <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="icon" />
              </svg>
            </div>
            <div>
              <h3 v-if="title" class="text-lg font-semibold text-gray-900">{{ title }}</h3>
              <p v-if="subtitle" class="text-sm text-gray-600">{{ subtitle }}</p>
            </div>
          </div>
          <slot name="header-actions"></slot>
        </div>
      </slot>
    </div>

    <!-- Body -->
    <div class="base-dashboard-widget-body">
      <slot name="body">
        <!-- Default body content -->
      </slot>
    </div>

    <!-- Footer -->
    <div v-if="showFooter || $slots.footer" class="base-dashboard-widget-footer">
      <slot name="footer">
        <!-- Default footer content -->
      </slot>
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
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'primary', 'success', 'warning', 'danger', 'info'].includes(value)
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  showFooter: {
    type: Boolean,
    default: false
  },
  widgetClass: {
    type: String,
    default: 'bg-white rounded-lg shadow-sm border border-gray-200 p-6'
  }
})

const iconBgClass = computed(() => {
  const variantMap = {
    default: 'bg-gray-100 text-gray-600',
    primary: 'bg-blue-100 text-blue-600',
    success: 'bg-green-100 text-green-600',
    warning: 'bg-yellow-100 text-yellow-600',
    danger: 'bg-red-100 text-red-600',
    info: 'bg-cyan-100 text-cyan-600'
  }
  return variantMap[props.variant] || variantMap.default
})
</script>

<style scoped>
.base-dashboard-widget {
  @apply transition-all duration-200;
}

.base-dashboard-widget:hover {
  @apply shadow-md;
}

.base-dashboard-widget-header {
  @apply mb-4 pb-4 border-b border-gray-200;
}

.base-dashboard-widget-body {
  @apply flex-1;
}

.base-dashboard-widget-footer {
  @apply mt-4 pt-4 border-t border-gray-200;
}
</style>

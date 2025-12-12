<template>
  <div
    class="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-lg transition-all duration-200 cursor-pointer"
    :class="{ 'border-green-500': selected }"
    @click="handleClick"
  >
    <!-- Image -->
    <div v-if="finca.image || $slots.image" class="relative h-48 bg-gray-200 overflow-hidden">
      <slot name="image">
        <img
          v-if="finca.image"
          :src="finca.image"
          :alt="finca.nombre"
          class="w-full h-full object-cover"
        />
        <div v-else class="w-full h-full flex items-center justify-center bg-gradient-to-br from-green-100 to-blue-100">
          <svg class="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
          </svg>
        </div>
      </slot>
    </div>

    <!-- Content -->
    <div class="p-4 sm:p-6">
      <!-- Header -->
      <div class="flex items-start justify-between mb-3">
        <div class="flex-1 min-w-0">
          <h3 class="text-lg font-semibold text-gray-900 truncate">{{ finca.nombre }}</h3>
          <p v-if="finca.ubicacion" class="text-sm text-gray-600 mt-1 truncate">{{ finca.ubicacion }}</p>
        </div>
        <slot name="header-actions" />
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p class="text-xs text-gray-500">Área Total</p>
          <p class="text-sm font-semibold text-gray-900">{{ formatArea(finca.area_total || finca.area) }}</p>
        </div>
        <div>
          <p class="text-xs text-gray-500">Lotes</p>
          <p class="text-sm font-semibold text-gray-900">{{ (finca.lotes || finca.lots || []).length }}</p>
        </div>
      </div>

      <!-- Description -->
      <p v-if="finca.descripcion && showDescription" class="text-sm text-gray-600 line-clamp-2 mb-4">
        {{ finca.descripcion }}
      </p>

      <!-- Footer -->
      <div v-if="$slots.footer || showActions" class="flex items-center justify-between pt-4 border-t border-gray-200">
        <slot name="footer">
          <div v-if="showActions" class="flex items-center space-x-2">
            <button
              v-for="action in actions"
              :key="action.key"
              @click.stop="handleAction(action)"
              :class="[
                'px-3 py-1.5 rounded-md text-xs font-medium transition-colors',
                action.variant === 'primary' ? 'bg-green-600 text-white hover:bg-green-700' : '',
                action.variant === 'secondary' ? 'bg-gray-200 text-gray-900 hover:bg-gray-300' : '',
                action.variant === 'danger' ? 'bg-red-600 text-white hover:bg-red-700' : '',
                !action.variant ? 'bg-green-600 text-white hover:bg-green-700' : ''
              ]"
            >
              {{ action.label }}
            </button>
          </div>
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  finca: {
    type: Object,
    required: true
  },
  selected: {
    type: Boolean,
    default: false
  },
  showDescription: {
    type: Boolean,
    default: true
  },
  showActions: {
    type: Boolean,
    default: false
  },
  actions: {
    type: Array,
    default: null,
    validator: (value) => {
      if (!value) return true
      return value.every(action => typeof action === 'object' && 'key' in action && 'label' in action)
    }
  }
})

const emit = defineEmits(['click', 'action-click'])

const formatArea = (area) => {
  if (!area) return '0 ha'
  return `${Number.parseFloat(area).toFixed(2)} ha`
}

const handleClick = () => {
  emit('click', props.finca)
}

const handleAction = (action) => {
  emit('action-click', { action, finca: props.finca })
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

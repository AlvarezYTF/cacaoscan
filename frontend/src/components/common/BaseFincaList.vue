<template>
  <div class="w-full">
    <!-- Header -->
    <div v-if="title || $slots.header" class="mb-4">
      <slot name="header">
        <h2 v-if="title" class="text-xl font-semibold text-gray-900">{{ title }}</h2>
        <p v-if="subtitle" class="text-sm text-gray-600 mt-1">{{ subtitle }}</p>
      </slot>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="grid gap-4" :class="gridClass">
      <BaseLoadingSkeleton
        v-for="i in skeletonCount"
        :key="i"
        type="card"
        variant="compact"
      />
    </div>

    <!-- Empty state -->
    <div v-else-if="!fincas || fincas.length === 0" class="text-center py-12">
      <slot name="empty">
        <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
        </svg>
        <p class="text-gray-600">{{ emptyMessage || 'No hay fincas disponibles' }}</p>
      </slot>
    </div>

    <!-- Fincas grid/list -->
    <div v-else class="grid gap-4 sm:gap-6" :class="gridClass">
      <BaseFincaCard
        v-for="finca in fincas"
        :key="finca.id"
        :finca="finca"
        :selected="selectedFinca?.id === finca.id"
        :show-description="showDescription"
        :show-actions="showActions"
        :actions="actions"
        @click="handleFincaClick"
        @action-click="handleActionClick"
      >
        <template #image>
          <slot name="finca-image" :finca="finca" />
        </template>
        <template #header-actions>
          <slot name="finca-header-actions" :finca="finca" />
        </template>
        <template #footer>
          <slot name="finca-footer" :finca="finca" />
        </template>
      </BaseFincaCard>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import BaseFincaCard from './BaseFincaCard.vue'
import BaseLoadingSkeleton from './BaseLoadingSkeleton.vue'

const props = defineProps({
  fincas: {
    type: Array,
    default: () => []
  },
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  },
  emptyMessage: {
    type: String,
    default: null
  },
  selectedFinca: {
    type: Object,
    default: null
  },
  layout: {
    type: String,
    default: 'grid',
    validator: (value) => ['grid', 'list'].includes(value)
  },
  columns: {
    type: Number,
    default: 3,
    validator: (value) => [1, 2, 3, 4].includes(value)
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
    default: null
  },
  skeletonCount: {
    type: Number,
    default: 6
  }
})

const emit = defineEmits(['finca-click', 'action-click'])

const gridClass = computed(() => {
  if (props.layout === 'list') {
    return 'grid-cols-1'
  }

  const columnClasses = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4'
  }

  return columnClasses[props.columns] || columnClasses[3]
})

const handleFincaClick = (finca) => {
  emit('finca-click', finca)
}

const handleActionClick = (payload) => {
  emit('action-click', payload)
}
</script>

<style scoped>
/* Additional styles if needed */
</style>

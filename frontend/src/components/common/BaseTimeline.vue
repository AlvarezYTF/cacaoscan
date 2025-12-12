<template>
  <div class="base-timeline">
    <!-- Loading State -->
    <div v-if="loading" class="base-timeline-loading">
      <slot name="loading">
        <div class="flex flex-col items-center justify-center py-12">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mb-4"></div>
          <p class="text-sm text-gray-600">{{ loadingText || 'Cargando...' }}</p>
        </div>
      </slot>
    </div>

    <!-- Empty State -->
    <div v-else-if="items.length === 0" class="base-timeline-empty">
      <slot name="empty">
        <div class="flex flex-col items-center justify-center py-12">
          <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
            <i class="fas fa-history text-gray-400 text-2xl"></i>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ emptyTitle || 'No hay elementos' }}</h3>
          <p class="text-sm text-gray-600">{{ emptyText || 'No se encontraron elementos para mostrar.' }}</p>
        </div>
      </slot>
    </div>

    <!-- Timeline Container -->
    <div v-else class="base-timeline-container">
      <!-- Header -->
      <div v-if="showHeader || $slots.header" class="base-timeline-header">
        <slot name="header">
          <h3 v-if="title" class="text-lg font-semibold text-gray-900">{{ title }}</h3>
          <div v-if="showStats" class="base-timeline-stats">
            <span class="text-sm text-gray-600">{{ items.length }} {{ itemsLabel || 'elementos' }}</span>
          </div>
        </slot>
      </div>

      <!-- Timeline Items -->
      <div class="base-timeline-items">
        <div
          v-for="(item, index) in items"
          :key="getItemKey(item, index)"
          class="base-timeline-item"
          :class="{ 'last': index === items.length - 1 }"
        >
          <!-- Timeline Marker -->
          <div class="base-timeline-marker">
            <slot name="marker" :item="item" :index="index">
              <div class="base-timeline-marker-icon" :class="getMarkerClass(item, index)">
                <i :class="getMarkerIcon(item, index)"></i>
              </div>
            </slot>
          </div>

          <!-- Timeline Content -->
          <div class="base-timeline-content">
            <slot name="item" :item="item" :index="index">
              <div class="base-timeline-card">
                <div class="base-timeline-card-header">
                  <slot name="item-header" :item="item" :index="index">
                    <h4 class="text-base font-semibold text-gray-900">{{ getItemTitle(item) }}</h4>
                  </slot>
                </div>
                <div class="base-timeline-card-body">
                  <slot name="item-body" :item="item" :index="index">
                    <p class="text-sm text-gray-600">{{ getItemDescription(item) }}</p>
                  </slot>
                </div>
                <div v-if="$slots['item-footer']" class="base-timeline-card-footer">
                  <slot name="item-footer" :item="item" :index="index"></slot>
                </div>
              </div>
            </slot>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>

const props = defineProps({
  items: {
    type: Array,
    required: true,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingText: {
    type: String,
    default: 'Cargando...'
  },
  emptyTitle: {
    type: String,
    default: 'No hay elementos'
  },
  emptyText: {
    type: String,
    default: 'No se encontraron elementos para mostrar.'
  },
  title: {
    type: String,
    default: ''
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  showStats: {
    type: Boolean,
    default: true
  },
  itemsLabel: {
    type: String,
    default: 'elementos'
  },
  itemKey: {
    type: [String, Function],
    default: 'id'
  },
  getMarkerClass: {
    type: Function,
    default: null
  },
  getMarkerIcon: {
    type: Function,
    default: null
  },
  getItemTitle: {
    type: Function,
    default: null
  },
  getItemDescription: {
    type: Function,
    default: null
  }
})

const emit = defineEmits(['item-click'])

/**
 * Get unique key for item
 * @param {Object} item - Item object
 * @param {number} index - Item index
 * @returns {string|number} Unique key
 */
const getItemKey = (item, index) => {
  if (typeof props.itemKey === 'function') {
    return props.itemKey(item, index)
  }
  return item[props.itemKey] || index
}

/**
 * Default marker class function
 */
const getMarkerClass = (item, index) => {
  if (props.getMarkerClass && typeof props.getMarkerClass === 'function') {
    return props.getMarkerClass(item, index)
  }
  return 'bg-green-500'
}

/**
 * Default marker icon function
 */
const getMarkerIcon = (item, index) => {
  if (props.getMarkerIcon && typeof props.getMarkerIcon === 'function') {
    return props.getMarkerIcon(item, index)
  }
  return 'fas fa-circle'
}

/**
 * Default item title function
 */
const getItemTitle = (item) => {
  if (props.getItemTitle && typeof props.getItemTitle === 'function') {
    return props.getItemTitle(item)
  }
  return item.title || item.name || 'Elemento'
}

/**
 * Default item description function
 */
const getItemDescription = (item) => {
  if (props.getItemDescription && typeof props.getItemDescription === 'function') {
    return props.getItemDescription(item)
  }
  return item.description || item.descripcion || ''
}
</script>

<style scoped>
.base-timeline {
  @apply w-full;
}

.base-timeline-loading,
.base-timeline-empty {
  @apply py-12;
}

.base-timeline-container {
  @apply w-full;
}

.base-timeline-header {
  @apply flex items-center justify-between mb-6 pb-4 border-b border-gray-200;
}

.base-timeline-stats {
  @apply text-sm text-gray-600;
}

.base-timeline-items {
  @apply relative;
}

.base-timeline-item {
  @apply relative flex gap-4 pb-8;
}

.base-timeline-item.last {
  @apply pb-0;
}

.base-timeline-marker {
  @apply flex-shrink-0 relative z-10;
}

.base-timeline-marker-icon {
  @apply w-10 h-10 rounded-full flex items-center justify-center text-white text-sm;
}

.base-timeline-content {
  @apply flex-1 min-w-0;
}

.base-timeline-card {
  @apply bg-white rounded-lg border border-gray-200 shadow-sm p-4 hover:shadow-md transition-shadow;
}

.base-timeline-card-header {
  @apply mb-2;
}

.base-timeline-card-body {
  @apply text-sm text-gray-600;
}

.base-timeline-card-footer {
  @apply mt-4 pt-4 border-t border-gray-100;
}

/* Timeline line */
.base-timeline-items::before {
  content: '';
  @apply absolute left-5 top-0 bottom-0 w-0.5 bg-gray-200;
}

.base-timeline-item.last .base-timeline-marker::after {
  display: none;
}
</style>


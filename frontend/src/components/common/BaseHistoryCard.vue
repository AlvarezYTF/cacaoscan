<template>
  <BaseCard
    :title="title"
    :icon="icon"
    :variant="variant"
    :clickable="false"
    :bordered="bordered"
    :shadow="shadow"
  >
    <template #header>
      <slot name="header"></slot>
    </template>

    <template #meta>
      <slot name="meta"></slot>
    </template>

    <!-- Filters -->
    <div v-if="showFilters && $slots.filters" class="base-history-filters">
      <slot name="filters"></slot>
    </div>

    <!-- Items List -->
    <div class="base-history-items">
      <div v-if="loading" class="base-history-loading">
        <slot name="loading">
          <div class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
            <p class="mt-2 text-sm text-gray-600">Cargando...</p>
          </div>
        </slot>
      </div>

      <div v-else-if="error" class="base-history-error">
        <slot name="error">
          <div class="text-center py-8 text-red-600">
            <p>{{ error }}</p>
          </div>
        </slot>
      </div>

      <div v-else-if="items.length === 0" class="base-history-empty">
        <slot name="empty">
          <div class="text-center py-8 text-gray-500">
            <p>No hay elementos para mostrar</p>
          </div>
        </slot>
      </div>

      <div v-else class="base-history-list">
        <slot name="items" :items="items">
          <div
            v-for="(item, index) in items"
            :key="getItemKey(item, index)"
            class="base-history-item"
          >
            <slot name="item" :item="item" :index="index"></slot>
          </div>
        </slot>
      </div>
    </div>

    <!-- Pagination -->
    <template #footer>
      <div v-if="showPagination && hasMorePages" class="base-history-pagination">
        <slot name="pagination">
          <button
            @click="loadMore"
            :disabled="loading"
            class="base-history-load-more"
          >
            {{ loading ? 'Cargando...' : 'Cargar más' }}
          </button>
        </slot>
      </div>
      <slot name="footer"></slot>
    </template>

    <template #actions>
      <slot name="actions"></slot>
    </template>
  </BaseCard>
</template>

<script setup>
import BaseCard from './BaseCard.vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'default'
  },
  bordered: {
    type: Boolean,
    default: true
  },
  shadow: {
    type: Boolean,
    default: true
  },
  items: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  showFilters: {
    type: Boolean,
    default: false
  },
  showPagination: {
    type: Boolean,
    default: true
  },
  hasMorePages: {
    type: Boolean,
    default: false
  },
  itemKey: {
    type: [String, Function],
    default: 'id'
  }
})

const emit = defineEmits(['load-more', 'item-click'])

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
 * Handle load more action
 */
const loadMore = () => {
  if (!props.loading && props.hasMorePages) {
    emit('load-more')
  }
}
</script>

<style scoped>
.base-history-filters {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.base-history-items {
  min-height: 200px;
}

.base-history-loading,
.base-history-error,
.base-history-empty {
  padding: 2rem 1.25rem;
}

.base-history-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1.25rem;
}

.base-history-item {
  transition: all 0.2s;
}

.base-history-item:hover {
  transform: translateX(4px);
}

.base-history-pagination {
  display: flex;
  justify-content: center;
  padding: 1rem 0;
}

.base-history-load-more {
  padding: 0.5rem 1.5rem;
  background: #047857;
  color: #ffffff;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.base-history-load-more:hover:not(:disabled) {
  background: #047857;
  color: #ffffff;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.base-history-load-more:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>


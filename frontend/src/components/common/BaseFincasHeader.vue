<template>
  <div class="bg-white border-b border-gray-200 px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
      <!-- Title and breadcrumbs -->
      <div class="flex-1">
        <!-- Breadcrumbs -->
        <nav v-if="breadcrumbs && breadcrumbs.length > 0" class="flex mb-2" aria-label="Breadcrumb">
          <ol class="flex items-center space-x-2">
            <li v-for="(crumb, index) in breadcrumbs" :key="index" class="flex items-center">
              <router-link
                v-if="crumb.to && index < breadcrumbs.length - 1"
                :to="crumb.to"
                class="text-sm text-gray-500 hover:text-gray-700 transition-colors"
              >
                {{ crumb.label }}
              </router-link>
              <span v-else class="text-sm font-medium text-gray-900">{{ crumb.label }}</span>
              <svg
                v-if="index < breadcrumbs.length - 1"
                class="w-4 h-4 mx-2 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </li>
          </ol>
        </nav>

        <!-- Title -->
        <h1 v-if="title" class="text-2xl sm:text-3xl font-bold text-gray-900">{{ title }}</h1>
        <p v-if="subtitle" class="mt-1 text-sm text-gray-600">{{ subtitle }}</p>
      </div>

      <!-- Actions -->
      <div v-if="$slots.actions || actions" class="flex items-center space-x-3">
        <slot name="actions">
          <button
            v-for="action in actions"
            :key="action.key"
            @click="handleAction(action)"
            :class="[
              'px-4 py-2 rounded-md text-sm font-medium transition-colors',
              action.variant === 'primary' ? 'bg-green-600 text-white hover:bg-green-700' : '',
              action.variant === 'secondary' ? 'bg-gray-200 text-gray-900 hover:bg-gray-300' : '',
              action.variant === 'danger' ? 'bg-red-600 text-white hover:bg-red-700' : '',
              !action.variant ? 'bg-green-600 text-white hover:bg-green-700' : ''
            ]"
          >
            {{ action.label }}
          </button>
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  breadcrumbs: {
    type: Array,
    default: null,
    validator: (value) => {
      if (!value) return true
      return value.every(crumb => typeof crumb === 'object' && 'label' in crumb)
    }
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

const emit = defineEmits(['action-click'])

const handleAction = (action) => {
  emit('action-click', action)
}
</script>

<style scoped>
/* Additional styles if needed */
</style>


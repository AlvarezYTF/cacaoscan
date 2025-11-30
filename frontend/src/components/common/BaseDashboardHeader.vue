<template>
  <BaseHeader
    :title="title"
    :subtitle="subtitle"
    :icon="icon"
    :header-class="headerClass"
    :show-actions="showActions || $slots.actions"
  >
    <template #brand>
      <div class="flex items-center flex-1 min-w-0">
        <!-- Breadcrumbs -->
        <nav v-if="breadcrumbs && breadcrumbs.length > 0" class="flex flex-col mb-2" aria-label="Breadcrumb">
          <ol class="flex items-center space-x-2 mb-2">
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
        
        <slot name="brand">
          <div v-if="icon || $slots.icon" class="flex-shrink-0 mr-3">
            <slot name="icon">
              <component v-if="icon" :is="icon" class="w-6 h-6 text-green-600" />
            </slot>
          </div>
          <div class="min-w-0 flex-1">
            <h1 v-if="title" class="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 truncate">
              {{ title }}
            </h1>
            <p v-if="subtitle" class="mt-1 text-sm text-gray-600 truncate">
              {{ subtitle }}
            </p>
            <slot name="subtitle"></slot>
          </div>
        </slot>
      </div>
    </template>
    
    <template #actions>
      <slot name="actions"></slot>
    </template>
  </BaseHeader>
</template>

<script setup>
import BaseHeader from './BaseHeader.vue'

defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  icon: {
    type: [Object, String],
    default: null
  },
  breadcrumbs: {
    type: Array,
    default: () => []
  },
  headerClass: {
    type: String,
    default: ''
  },
  showActions: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
/* Styles handled by Tailwind classes */
</style>


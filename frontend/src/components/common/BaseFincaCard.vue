<template>
  <div 
    :class="['base-finca-card', cardClass]"
    @click="handleCardClick"
  >
    <div class="p-6">
      <!-- Header -->
      <div class="flex justify-between items-start mb-4">
        <div class="flex-1">
          <slot name="header">
            <h3 v-if="title" class="text-lg font-bold text-gray-900 mb-1">{{ title }}</h3>
            <p v-if="subtitle" class="text-sm text-gray-600 flex items-center gap-1">
              <slot name="subtitle-icon">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
              </slot>
              {{ subtitle }}
            </p>
          </slot>
        </div>
        <slot name="status-badge">
          <span
            v-if="status !== null"
            :class="[
              'px-3 py-1 text-xs font-semibold rounded-full flex items-center gap-1',
              status ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            ]"
          >
            <svg v-if="status" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <svg v-else class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            {{ status ? statusLabelActive : statusLabelInactive }}
          </span>
        </slot>
      </div>

      <!-- Body Content -->
      <div class="space-y-3 mb-4">
        <slot name="body">
          <!-- Default body content can be provided via props or slots -->
        </slot>
      </div>

      <!-- Stats Grid -->
      <div v-if="stats && stats.length > 0" class="grid grid-cols-2 gap-4 mb-4">
        <div
          v-for="(stat, index) in stats"
          :key="index"
          :class="['rounded-lg p-3 text-center', stat.bgClass || 'bg-blue-50']"
        >
          <div :class="['text-2xl font-bold', stat.valueClass || 'text-blue-600']">
            {{ stat.value }}
          </div>
          <div class="text-xs text-gray-600">{{ stat.label }}</div>
        </div>
      </div>
      <slot name="stats"></slot>

      <!-- Actions -->
      <div v-if="showActions || $slots.actions" class="flex gap-2 flex-wrap">
        <slot name="actions">
          <!-- Default actions can be provided via props -->
        </slot>
      </div>
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
  status: {
    type: Boolean,
    default: null
  },
  statusLabelActive: {
    type: String,
    default: 'Activa'
  },
  statusLabelInactive: {
    type: String,
    default: 'Inactiva'
  },
  stats: {
    type: Array,
    default: () => []
  },
  showActions: {
    type: Boolean,
    default: true
  },
  clickable: {
    type: Boolean,
    default: true
  },
  cardClass: {
    type: String,
    default: 'relative bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 border border-gray-200'
  }
})

const emit = defineEmits(['view-details', 'edit', 'delete', 'activate', 'click'])

const handleCardClick = () => {
  if (props.clickable) {
    emit('view-details')
    emit('click')
  }
}
</script>

<style scoped>
.base-finca-card {
  @apply cursor-pointer;
}

.base-finca-card:not(.clickable) {
  @apply cursor-default;
}
</style>


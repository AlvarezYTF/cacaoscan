<template>
  <div 
    class="bg-white rounded-2xl border-2 border-gray-200 overflow-hidden hover:shadow-xl hover:border-green-300 transition-all duration-300"
    :class="{ 'opacity-60 pointer-events-none': loading }"
  >
    <!-- Header -->
    <div 
      v-if="title || $slots['header-actions'] || refreshable"
      class="px-6 py-4 border-b-2 border-gray-200 bg-gray-50 flex items-center justify-between"
    >
      <div class="flex items-center gap-2">
        <slot name="header-icon">
          <div v-if="icon" class="p-1.5 bg-green-100 rounded-lg">
            <component :is="icon" class="w-5 h-5 text-green-600" />
          </div>
        </slot>
        <h3 v-if="title" class="text-xl font-bold text-gray-900">{{ title }}</h3>
        <slot name="header" />
      </div>
      
      <div class="flex items-center gap-2">
        <slot name="header-actions" />
        
        <!-- Refresh button -->
        <button 
          v-if="refreshable"
          @click="handleRefresh"
          type="button"
          class="group p-2.5 text-gray-500 hover:text-white hover:bg-green-600 rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
          :disabled="loading"
          title="Actualizar datos"
        >
          <div v-if="loading" class="w-5 h-5 border-2 border-gray-300 border-t-green-600 rounded-full animate-spin"></div>
          <svg 
            v-else
            class="w-5 h-5 group-hover:rotate-180 transition-transform duration-500" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
        </button>
        
        <!-- Collapse button -->
        <button 
          v-if="collapsible"
          @click="toggleCollapse"
          type="button"
          class="p-2.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
          :title="isCollapsed ? 'Expandir' : 'Colapsar'"
        >
          <svg 
            class="w-5 h-5 transition-transform duration-200"
            :class="{ 'rotate-180': isCollapsed }"
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
          </svg>
        </button>
      </div>
    </div>

    <!-- Error state -->
    <div v-if="error && !loading" class="px-6 py-4 bg-red-50 border-b border-red-200">
      <div class="flex items-center gap-2 text-red-800">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <span class="text-sm font-medium">{{ error }}</span>
      </div>
    </div>

    <!-- Content -->
    <div v-show="!isCollapsed" class="p-6">
      <slot />
    </div>

    <!-- Footer -->
    <div v-if="$slots.footer && !isCollapsed" class="px-6 py-4 border-t border-gray-200 bg-gray-50">
      <slot name="footer" />
    </div>

    <!-- Loading overlay -->
    <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 z-10">
      <div class="w-8 h-8 border-4 border-gray-300 border-t-green-600 rounded-full animate-spin"></div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  },
  collapsible: {
    type: Boolean,
    default: false
  },
  refreshable: {
    type: Boolean,
    default: false
  },
  icon: {
    type: [String, Object],
    default: null
  }
})

const emit = defineEmits(['refresh', 'collapse'])

const isCollapsed = ref(false)

const handleRefresh = () => {
  emit('refresh')
}

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
  emit('collapse', isCollapsed.value)
}
</script>

<style scoped>
/* Animations */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Transitions */
* {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}
</style>


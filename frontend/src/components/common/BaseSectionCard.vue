<template>
  <div 
    class="bg-white rounded-xl border border-gray-200 shadow-sm p-6"
    :class="containerClass"
  >
    <div v-if="title || $slots.header" class="flex items-center mb-4">
      <div class="bg-green-100 p-2 rounded-lg mr-3">
        <slot name="icon">
          <component :is="icon" v-if="icon" class="w-5 h-5 text-green-600" />
          <svg v-else class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </slot>
      </div>
      <div class="flex-1">
        <slot name="header">
          <h3 class="text-lg font-semibold text-gray-900">
            {{ title }}
          </h3>
          <p v-if="description" class="text-sm text-gray-600 mt-1">{{ description }}</p>
        </slot>
      </div>
      <div v-if="$slots.headerActions" class="ml-3">
        <slot name="headerActions"></slot>
      </div>
    </div>
    
    <slot />
  </div>
</template>

<script setup>
const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  icon: {
    type: [Object, String],
    default: null
  },
  containerClass: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
/* Styles handled by Tailwind classes */
</style>


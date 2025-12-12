<template>
  <div class="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 transition-all duration-200 hover:shadow-xl">
    <div v-if="title" class="flex items-center gap-2 mb-6 pb-4 border-b border-gray-100">
      <div class="p-2 bg-green-100 rounded-lg">
        <slot name="icon">
          <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="iconPath" />
          </svg>
        </slot>
      </div>
      <h2 class="text-lg font-bold text-gray-900">{{ title }}</h2>
    </div>
    <slot></slot>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: ''
  },
  iconPath: {
    type: String,
    default: ''
  }
})
</script>


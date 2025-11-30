<template>
  <div class="px-6 py-5 border-b border-gray-200" :class="containerClass">
    <div class="flex items-center justify-between">
      <div class="flex-1 min-w-0">
        <slot name="title">
          <h2 v-if="title" class="text-2xl font-semibold text-gray-900">
            {{ title }}
          </h2>
          <h2 v-else-if="analysisId" class="text-2xl font-semibold text-gray-900">
            Detalles del Análisis #{{ analysisId }}
          </h2>
        </slot>
        <p v-if="subtitle" class="mt-1 text-sm text-gray-500">
          {{ subtitle }}
        </p>
        <slot name="subtitle"></slot>
      </div>
      <div v-if="$slots.actions" class="ml-4 flex-shrink-0">
        <slot name="actions"></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: ''
  },
  analysisId: {
    type: [String, Number],
    default: null
  },
  subtitle: {
    type: String,
    default: 'Resultados del análisis de calidad del lote'
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


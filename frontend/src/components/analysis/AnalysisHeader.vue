<template>
  <BaseAnalysisHeader
    :analysis-id="analysisId"
    :subtitle="subtitle"
  />
</template>

<script setup>
import BaseAnalysisHeader from '@/components/common/BaseAnalysisHeader.vue'

defineProps({
  analysisId: {
    type: [String, Number],
    required: true
  },
  subtitle: {
    type: String,
    default: 'Resultados del análisis de calidad del lote'
  }
})
</script>

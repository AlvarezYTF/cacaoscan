<template>
  <BaseAnalysisActions
    @download-pdf="$emit('download-pdf')"
    @new-analysis="$emit('new-analysis')"
  />
</template>

<script setup>
import BaseAnalysisActions from '@/components/common/BaseAnalysisActions.vue'

defineEmits(['download-pdf', 'new-analysis'])
</script>

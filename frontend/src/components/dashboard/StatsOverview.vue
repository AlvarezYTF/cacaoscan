<template>
  <section class="stats-overview">
    <BaseStatsCard
      title="Total de lotes"
      :value="stats.totalBatches || 0"
      icon="fas fa-seedling"
      :trend="stats.batchesChange ? { value: parseChange(stats.batchesChange), label: `${stats.batchesChange} este mes` } : null"
      color="success"
    />
    
    <BaseStatsCard
      title="Calidad promedio"
      :value="stats.avgQuality || 0"
      format="percentage"
      icon="fas fa-star"
      :trend="stats.qualityChange ? { value: parseChange(stats.qualityChange), label: `${stats.qualityChange} este mes` } : null"
      color="warning"
    />
    
    <BaseStatsCard
      title="Defectos"
      :value="stats.defectRate || 0"
      format="percentage"
      icon="fas fa-exclamation-triangle"
      :trend="stats.defectChange ? { value: parseChange(stats.defectChange), label: `${stats.defectChange} este mes` } : null"
      color="danger"
    />
  </section>
</template>

<script setup>
import BaseStatsCard from '@/components/common/BaseStatsCard.vue'
import { parseChange } from '@/utils/formatters'

const props = defineProps({
  stats: {
    type: Object,
    required: true,
    default: () => ({
      totalBatches: 24,
      batchesChange: '+5%',
      avgQuality: 87,
      qualityChange: '+2%',
      defectRate: 5.2,
      defectChange: '-1.2%'
    })
  }
})
</script>

<style scoped>
.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}
</style>

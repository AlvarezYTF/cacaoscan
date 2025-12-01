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

.stat-card {
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1.25rem;
  font-size: 1.5rem;
  color: #ffffff;
  background-color: #1f7a3b;
}

.stat-icon.quality {
  background-color: #8a4b00;
}

.stat-icon.warning {
  background-color: #b71c1c;
}

.stat-content h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
  color: #7f8c8d;
  font-weight: 500;
}

.stat-value {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
  color: #2c3e50;
}

.stat-change {
  margin: 0.25rem 0 0 0;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.stat-change.positive {
  color: #27ae60;
}

.stat-change.negative {
  color: #e74c3c;
}

.stat-change i {
  font-size: 0.7rem;
}
</style>

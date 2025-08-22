<template>
  <section class="recent-analysis">
    <div class="section-header">
      <h2>Análisis recientes</h2>
      <a href="#" class="view-all">Ver todo</a>
    </div>
    
    <div class="analysis-grid">
      <div v-for="(analysis, index) in analyses" :key="index" class="analysis-card">
        <div class="card-header">
          <span class="batch-id">Lote #{{ analysis.id }}</span>
          <span :class="['status-badge', analysis.status]">{{ analysis.statusLabel }}</span>
        </div>
        <div class="card-body">
          <div class="metric">
            <span class="label">Calidad</span>
            <div class="progress-bar">
              <div class="progress" :style="{ width: analysis.quality + '%' }"></div>
            </div>
            <span class="value">{{ analysis.quality }}%</span>
          </div>
          <div class="metric">
            <span class="label">Defectos</span>
            <span class="value">{{ analysis.defects }}%</span>
          </div>
          <div class="metric">
            <span class="label">Tamaño promedio</span>
            <span class="value">{{ analysis.avgSize }}mm</span>
          </div>
        </div>
        <div class="card-footer">
          <span class="date">{{ analysis.date }}</span>
          <router-link :to="{ name: 'detalle-analisis', query: { id: analysis.id } }" class="btn btn-sm btn-outline">Ver detalles</router-link>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'RecentAnalyses',
  props: {
    analyses: {
      type: Array,
      required: true,
      default: () => []
    }
  }
};
</script>

<style scoped>
.recent-analysis {
  margin: 2rem 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h2 {
  margin: 0;
  color: #2c3e50;
}

.view-all {
  color: #3498db;
  text-decoration: none;
  font-weight: 500;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.analysis-card {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.analysis-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #ecf0f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.batch-id {
  font-weight: 600;
  color: #2c3e50;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge.completed {
  background-color: #d4edda;
  color: #155724;
}

.card-body {
  padding: 1.25rem;
}

.metric {
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.metric:last-child {
  margin-bottom: 0;
}

.label {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.value {
  font-weight: 600;
  color: #2c3e50;
}

.progress-bar {
  flex-grow: 1;
  height: 8px;
  background-color: #ecf0f1;
  border-radius: 4px;
  margin: 0 1rem;
  overflow: hidden;
}

.progress {
  height: 100%;
  background-color: #27ae60;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.card-footer {
  padding: 0.75rem 1.25rem;
  border-top: 1px solid #ecf0f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f8f9fa;
}

.date {
  font-size: 0.85rem;
  color: #7f8c8d;
}

.btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.85rem;
}

.btn-outline {
  background: transparent;
  border: 1px solid #bdc3c7;
  color: #2c3e50;
  text-decoration: none;
  display: inline-block;
  cursor: pointer;
}

.btn-outline:hover {
  background-color: #f1f2f6;
}
</style>

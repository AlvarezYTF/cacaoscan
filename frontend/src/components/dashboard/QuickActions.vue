<template>
  <section class="quick-actions">
    <h2>Acciones rápidas</h2>
    <div class="action-buttons">
      <button class="btn btn-primary" @click="$emit('upload')">
        <i class="fas fa-upload"></i>
        Subir nuevo lote
      </button>
      <button class="btn btn-secondary">
        <i class="fas fa-chart-bar"></i>
        Ver reportes
      </button>
      <button class="btn btn-secondary">
        <i class="fas fa-history"></i>
        Historial de análisis
      </button>
    </div>
  </section>
</template>

<script>
export default {
  name: 'QuickActions',
  emits: ['upload']
};
</script>

<style scoped>
.quick-actions {
  margin-bottom: 2rem;
}

.quick-actions h2 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background-color: #27ae60;
  color: white;
}

.btn-primary:hover {
  background-color: #219653;
}

.btn-secondary {
  background-color: #f1f2f6;
  color: #2c3e50;
}

.btn-secondary:hover {
  background-color: #dfe4ea;
}
</style>

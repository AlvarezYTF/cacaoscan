<template>
  <header class="dashboard-header">
    <h1>Bienvenido, {{ farmerName }} 👨‍🌾</h1>
    <p class="welcome-text">Panel de control para el análisis de tus granos de cacao</p>
  </header>
</template>

<script>
export default {
  name: 'DashboardHeader',
  props: {
    farmerName: {
      type: String,
      default: 'Usuario'
    }
  }
};
</script>

<style scoped>
.dashboard-header {
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.welcome-text {
  color: #7f8c8d;
  font-size: 1.1rem;
}
</style>

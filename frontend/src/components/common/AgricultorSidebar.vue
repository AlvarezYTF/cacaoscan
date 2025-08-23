<template>
  <aside class="dashboard-sidebar" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <!-- Header del sidebar -->
    <div class="sidebar-header">
      <div class="farmer-info" @click="toggleSidebar" style="cursor: pointer;" :title="sidebarCollapsed ? 'Expandir menú' : 'Colapsar menú'">
        <div class="farmer-avatar">
          <i class="fas fa-user-circle"></i>
        </div>
        <div class="farmer-details" v-if="!sidebarCollapsed">
          <h3>{{ farmerName }}</h3>
          <span class="farmer-role">{{ farmerRole }}</span>
        </div>
      </div>
    </div>

    <!-- Navegación -->
    <nav class="sidebar-nav">
      <ul class="nav-menu">
        <li class="nav-item" :class="{ 'active': activeSection === 'overview' }">
          <a href="#" @click.prevent="setActiveSection('overview')" class="nav-link" :title="sidebarCollapsed ? 'Resumen' : ''">
            <i class="fas fa-chart-pie"></i>
            <span v-if="!sidebarCollapsed">Resumen</span>
          </a>
        </li>
        
        <li class="nav-item" :class="{ 'active': activeSection === 'analysis' }">
          <a href="#" @click.prevent="setActiveSection('analysis')" class="nav-link" :title="sidebarCollapsed ? 'Análisis' : ''">
            <i class="fas fa-microscope"></i>
            <span v-if="!sidebarCollapsed">Análisis</span>
          </a>
        </li>
        
        <li class="nav-item" :class="{ 'active': activeSection === 'fincas' }">
          <a href="#" @click.prevent="setActiveSection('fincas')" class="nav-link" :title="sidebarCollapsed ? 'Gestión de Fincas' : ''">
            <i class="fas fa-tree"></i>
            <span v-if="!sidebarCollapsed">Gestión de Fincas</span>
          </a>
        </li>

        <li class="nav-item" :class="{ 'active': activeSection === 'reports' }">
          <a href="#" @click.prevent="setActiveSection('reports')" class="nav-link" :title="sidebarCollapsed ? 'Reportes' : ''">
            <i class="fas fa-file-alt"></i>
            <span v-if="!sidebarCollapsed">Reportes</span>
          </a>
        </li>
        
        <li class="nav-item" :class="{ 'active': activeSection === 'history' }">
          <a href="#" @click.prevent="setActiveSection('history')" class="nav-link" :title="sidebarCollapsed ? 'Historial' : ''">
            <i class="fas fa-history"></i>
            <span v-if="!sidebarCollapsed">Historial</span>
          </a>
        </li>
        
        <li class="nav-item" :class="{ 'active': activeSection === 'settings' }">
          <a href="#" @click.prevent="setActiveSection('settings')" class="nav-link" :title="sidebarCollapsed ? 'Configuración' : ''">
            <i class="fas fa-cog"></i>
            <span v-if="!sidebarCollapsed">Configuración</span>
          </a>
        </li>
      </ul>
    </nav>

    <!-- Footer del sidebar -->
    <div class="sidebar-footer" v-if="!sidebarCollapsed">
      <div class="quick-stats">
        <div class="stat-item">
          <span class="stat-label">Lotes totales</span>
          <span class="stat-value">{{ stats.totalBatches }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Calidad prom.</span>
          <span class="stat-value">{{ stats.avgQuality }}%</span>
        </div>
      </div>
      
      <!-- Logout Section -->
      <div class="logout-section">
        <button class="logout-btn" @click="logout">
          <i class="fas fa-sign-out-alt"></i>
          <span>Cerrar Sesión</span>
        </button>
      </div>
    </div>
    
    <!-- Logout button for collapsed sidebar -->
    <div class="sidebar-footer-collapsed" v-if="sidebarCollapsed">
      <button class="logout-btn-collapsed" @click="logout" title="Cerrar Sesión">
        <i class="fas fa-sign-out-alt"></i>
      </button>
    </div>
  </aside>
</template>

<script>
export default {
  name: 'AgricultorSidebar',
  props: {
    farmerName: {
      type: String,
      default: 'Agricultor'
    },
    farmerRole: {
      type: String,
      default: 'Agricultor'
    },
    sidebarCollapsed: {
      type: Boolean,
      default: false
    },
    activeSection: {
      type: String,
      default: 'overview'
    },
    stats: {
      type: Object,
      default: () => ({
        totalBatches: 0,
        avgQuality: 0
      })
    }
  },
  emits: ['toggle-sidebar', 'set-active-section', 'logout'],
  methods: {
    toggleSidebar() {
      this.$emit('toggle-sidebar');
    },
    setActiveSection(section) {
      this.$emit('set-active-section', section);
    },
    logout() {
      this.$emit('logout');
    }
  }
};
</script>

<style scoped>
/* Estilos del sidebar del agricultor */
.dashboard-sidebar {
  width: 280px;
  background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
  color: white;
  transition: all 0.3s ease;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-collapsed {
  width: 70px;
}

.sidebar-collapsed .sidebar-header {
  padding: 1rem 0.5rem;
  justify-content: center;
}

.sidebar-collapsed .farmer-info {
  justify-content: center;
  padding: 0.5rem;
}

.sidebar-collapsed .farmer-info:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.1);
}

.sidebar-collapsed .farmer-avatar {
  animation: subtle-pulse 2s infinite;
}

@keyframes subtle-pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(255, 255, 255, 0.1);
  }
}

.sidebar-collapsed .farmer-avatar {
  width: 40px;
  height: 40px;
  font-size: 1.2rem;
}

.sidebar-collapsed .nav-link {
  padding: 1rem;
  justify-content: center;
  margin-right: 0;
}

.sidebar-collapsed .nav-link i {
  margin: 0;
}

.sidebar-collapsed .nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: none;
}

.sidebar-collapsed .nav-item.active .nav-link {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  margin: 0.5rem;
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.farmer-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.2s ease;
  border-radius: 8px;
  padding: 0.5rem;
}

.farmer-info:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.05);
}

.farmer-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  transition: all 0.2s ease;
  position: relative;
}

.farmer-info:active {
  transform: scale(0.95);
}

/* Indicador de estado del sidebar */
.sidebar-header::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 4px;
  height: 100%;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px 0 0 2px;
  transition: all 0.3s ease;
}

.sidebar-collapsed .sidebar-header::before {
  background: rgba(255, 255, 255, 0.6);
  width: 6px;
}

.farmer-details h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.farmer-role {
  font-size: 0.9rem;
  opacity: 0.8;
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
}

.nav-menu {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin: 0.25rem 0;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  margin: 0 0.5rem;
  transition: all 0.2s ease;
  position: relative;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(5px);
}

.nav-link i {
  font-size: 1.2rem;
  margin-right: 1rem;
  width: 20px;
  text-align: center;
}

.nav-item.active .nav-link {
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.nav-item.active .nav-link::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 0 2px 2px 0;
}

/* Footer del sidebar */
.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.quick-stats {
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
}

.stat-label {
  font-size: 0.8rem;
  opacity: 0.8;
}

.stat-value {
  font-weight: bold;
  font-size: 1rem;
}

.logout-section {
  margin-top: 1rem;
}

.logout-btn {
  width: 100%;
  padding: 0.75rem;
  background: rgba(231, 76, 60, 0.8);
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.logout-btn:hover {
  background: rgba(231, 76, 60, 1);
  transform: translateY(-2px);
}

.logout-btn i {
  font-size: 1rem;
}

/* Footer colapsado */
.sidebar-footer-collapsed {
  padding: 1rem 0.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: center;
}

.logout-btn-collapsed {
  width: 40px;
  height: 40px;
  background: rgba(231, 76, 60, 0.8);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logout-btn-collapsed:hover {
  background: rgba(231, 76, 60, 1);
  transform: scale(1.1);
}

.logout-btn-collapsed i {
  font-size: 1rem;
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard-sidebar {
    width: 70px;
  }
  
  .sidebar-collapsed {
    width: 70px;
  }
  
  .farmer-details,
  .sidebar-footer {
    display: none;
  }
  
  .sidebar-footer-collapsed {
    display: flex;
  }
}

@media (max-width: 640px) {
  .dashboard-sidebar {
    width: 60px;
  }
  
  .sidebar-collapsed {
    width: 60px;
  }
  
  .farmer-avatar {
    width: 40px;
    height: 40px;
    font-size: 1rem;
  }
  
  .nav-link {
    padding: 0.5rem;
    margin: 0 0.25rem;
  }
  
  .nav-link i {
    font-size: 1rem;
  }
}
</style>

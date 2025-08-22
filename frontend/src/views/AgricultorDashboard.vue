<template>
  <div class="farmer-dashboard-container">
    <!-- Sidebar -->
    <aside class="dashboard-sidebar" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <div class="sidebar-header">
        <div class="farmer-info" @click="toggleSidebar" style="cursor: pointer;" :title="sidebarCollapsed ? 'Expandir menú' : 'Colapsar menú'">
          <div class="farmer-avatar">
            <i class="fas fa-user-circle"></i>
          </div>
          <div class="farmer-details" v-if="!sidebarCollapsed">
            <h3>{{ farmerName }}</h3>
            <span class="farmer-role">Agricultor</span>
          </div>
        </div>
      </div>

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

    <!-- Main Content -->
    <main class="dashboard-main" :class="{ 'main-expanded': sidebarCollapsed }">
      <!-- Overview Section -->
      <div v-if="activeSection === 'overview'" class="dashboard-section">
        <div class="section-header">
          <h1>Resumen del Dashboard</h1>
          <p>Vista general de tu actividad y estadísticas</p>
        </div>
        
        <StatsOverview :stats="stats" />
        
        <div class="overview-grid">
          <div class="overview-card">
            <h3>Actividad Reciente</h3>
            <RecentAnalyses 
              :analyses="recentAnalyses" 
              @view-details="viewAnalysisDetails" 
            />
          </div>
          
          <div class="overview-card">
            <h3>Acciones Rápidas</h3>
            <QuickActions @upload="openUploadModal" />
          </div>
        </div>
      </div>

      <!-- Analysis Section -->
      <div v-if="activeSection === 'analysis'" class="dashboard-section">
        <div class="section-header">
          <h1>Análisis de Lotes</h1>
          <p>Sube y analiza nuevos lotes de cacao</p>
        </div>
        
        <UploadSection @file-upload="handleFileUpload" />
        
        <div class="analysis-tools">
          <h3>Herramientas de Análisis</h3>
          <div class="tools-grid">
            <div class="tool-card">
              <i class="fas fa-camera"></i>
              <h4>Captura de Imágenes</h4>
              <p>Captura imágenes directamente desde tu dispositivo</p>
              <button class="btn btn-primary">Iniciar Captura</button>
            </div>
            <div class="tool-card">
              <i class="fas fa-upload"></i>
              <h4>Subir Imágenes</h4>
              <p>Sube imágenes existentes para análisis</p>
              <button class="btn btn-secondary">Seleccionar Archivos</button>
            </div>
            <div class="tool-card">
              <i class="fas fa-batch-processing"></i>
              <h4>Procesamiento por Lotes</h4>
              <p>Procesa múltiples imágenes a la vez</p>
              <button class="btn btn-secondary">Crear Lote</button>
            </div>
            <div class="tool-card">
              <i class="fas fa-chart-pie"></i>
              <h4>Ver Detalle de Análisis</h4>
              <p>Visualiza resultados detallados con gráficos</p>
              <router-link to="/detalle-analisis" class="btn btn-primary">Ver Detalle</router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Fincas Section -->
      <div v-if="activeSection === 'fincas'" class="dashboard-section">
        <div class="section-header">
          <h1>Gestión de Fincas</h1>
          <p>Administra y monitorea tus fincas y lotes de cacao</p>
        </div>
        
        <div class="fincas-overview">
          <div class="fincas-stats">
            <div class="stat-card">
              <i class="fas fa-map-marked-alt"></i>
              <div class="stat-content">
                <h3>{{ fincasStats.totalFincas }}</h3>
                <p>Fincas Registradas</p>
              </div>
            </div>
            <div class="stat-card">
              <i class="fas fa-seedling"></i>
              <div class="stat-content">
                <h3>{{ fincasStats.totalLotes }}</h3>
                <p>Lotes Activos</p>
              </div>
            </div>
            <div class="stat-card">
              <i class="fas fa-ruler-combined"></i>
              <div class="stat-content">
                <h3>{{ fincasStats.areaTotal }} ha</h3>
                <p>Área Total</p>
              </div>
            </div>
            <div class="stat-card">
              <i class="fas fa-calendar-check"></i>
              <div class="stat-content">
                <h3>{{ fincasStats.ultimaActualizacion }}</h3>
                <p>Última Actualización</p>
              </div>
            </div>
          </div>
        </div>
        
        <div class="fincas-actions">
          <h3>Acciones de Fincas</h3>
          <div class="actions-grid">
            <div class="action-card">
              <i class="fas fa-plus-circle"></i>
              <h4>Registrar Nueva Finca</h4>
              <p>Agrega una nueva finca a tu portafolio</p>
              <button class="btn btn-primary" @click="registrarNuevaFinca">Registrar Finca</button>
            </div>
            <div class="action-card">
              <i class="fas fa-edit"></i>
              <h4>Gestionar Fincas</h4>
              <p>Edita información y configuración de fincas existentes</p>
              <button class="btn btn-secondary" @click="gestionarFincas">Gestionar</button>
            </div>
            <div class="action-card">
              <i class="fas fa-chart-line"></i>
              <h4>Monitoreo de Lotes</h4>
              <p>Visualiza el estado y rendimiento de tus lotes</p>
              <button class="btn btn-secondary" @click="monitorearLotes">Monitorear</button>
            </div>
            <div class="action-card">
              <i class="fas fa-file-export"></i>
              <h4>Reportes de Fincas</h4>
              <p>Genera reportes detallados de tus fincas</p>
              <button class="btn btn-secondary" @click="generarReportesFincas">Generar Reporte</button>
            </div>
          </div>
        </div>
        
        <div class="fincas-list" v-if="fincas.length > 0">
          <h3>Fincas Registradas</h3>
          <div class="fincas-grid">
            <div v-for="finca in fincas" :key="finca.id" class="finca-card">
              <div class="finca-header">
                <h4>{{ finca.nombre }}</h4>
                <span class="finca-status" :class="finca.status">{{ finca.statusLabel }}</span>
              </div>
              <div class="finca-details">
                <p><i class="fas fa-map-marker-alt"></i> {{ finca.ubicacion }}</p>
                <p><i class="fas fa-ruler-combined"></i> {{ finca.area }} ha</p>
                <p><i class="fas fa-seedling"></i> {{ finca.lotes }} lotes</p>
                <p><i class="fas fa-calendar-alt"></i> Registrada: {{ finca.fechaRegistro }}</p>
              </div>
              <div class="finca-actions">
                <button class="btn btn-sm btn-secondary" @click="verDetalleFinca(finca)">Ver Detalle</button>
                <button class="btn btn-sm btn-primary" @click="editarFinca(finca)">Editar</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Reports Section -->
      <div v-if="activeSection === 'reports'" class="dashboard-section">
        <div class="section-header">
          <h1>Reportes y Estadísticas</h1>
          <p>Genera reportes detallados de tus análisis</p>
        </div>
        
        <div class="reports-grid">
          <div class="report-card">
            <h3>Reporte de Calidad</h3>
            <p>Análisis detallado de la calidad de tus lotes</p>
            <button class="btn btn-primary">Generar Reporte</button>
          </div>
          <div class="report-card">
            <h3>Reporte de Defectos</h3>
            <p>Identificación y clasificación de defectos</p>
            <button class="btn btn-primary">Generar Reporte</button>
          </div>
          <div class="report-card">
            <h3>Reporte de Rendimiento</h3>
            <p>Métricas de rendimiento por período</p>
            <button class="btn btn-primary">Generar Reporte</button>
          </div>
        </div>
      </div>

      <!-- History Section -->
      <div v-if="activeSection === 'history'" class="dashboard-section">
        <div class="section-header">
          <h1>Historial de Análisis</h1>
          <p>Revisa todos tus análisis anteriores</p>
        </div>
        
        <div class="history-filters">
          <div class="filter-group">
            <label>Filtrar por fecha:</label>
            <select v-model="historyFilter.dateRange">
              <option value="all">Todas las fechas</option>
              <option value="week">Última semana</option>
              <option value="month">Último mes</option>
              <option value="quarter">Último trimestre</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Filtrar por calidad:</label>
            <select v-model="historyFilter.quality">
              <option value="all">Todas las calidades</option>
              <option value="excellent">Excelente (90%+)</option>
              <option value="good">Buena (80-89%)</option>
              <option value="fair">Regular (70-79%)</option>
              <option value="poor">Baja (<70%)</option>
            </select>
          </div>
        </div>
        
        <RecentAnalyses 
          :analyses="filteredAnalyses" 
          @view-details="viewAnalysisDetails" 
        />
      </div>

      <!-- Settings Section -->
      <div v-if="activeSection === 'settings'" class="dashboard-section">
        <div class="section-header">
          <h1>Configuración</h1>
          <p>Gestiona tu perfil y preferencias</p>
        </div>
        
        <div class="settings-grid">
          <div class="settings-card">
            <h3>Perfil de Usuario</h3>
            <form class="profile-form">
              <div class="form-group">
                <label>Nombre completo</label>
                <input type="text" v-model="userProfile.fullName" placeholder="Tu nombre completo">
              </div>
              <div class="form-group">
                <label>Email</label>
                <input type="email" v-model="userProfile.email" placeholder="tu@email.com">
              </div>
              <div class="form-group">
                <label>Teléfono</label>
                <input type="tel" v-model="userProfile.phone" placeholder="+57 300 123 4567">
              </div>
              <button type="submit" class="btn btn-primary">Guardar Cambios</button>
            </form>
          </div>
          
          <div class="settings-card">
            <h3>Preferencias</h3>
            <div class="preferences">
              <div class="preference-item">
                <label>
                  <input type="checkbox" v-model="userPreferences.notifications">
                  Recibir notificaciones por email
                </label>
              </div>
              <div class="preference-item">
                <label>
                  <input type="checkbox" v-model="userPreferences.autoReports">
                  Generar reportes automáticamente
                </label>
              </div>
              <div class="preference-item">
                <label>
                  <input type="checkbox" v-model="userPreferences.dataSharing">
                  Compartir datos anónimos para investigación
                </label>
              </div>
            </div>
            <button class="btn btn-secondary">Guardar Preferencias</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import DashboardHeader from '@/components/dashboard/DashboardHeader.vue';
import QuickActions from '@/components/dashboard/QuickActions.vue';
import UploadSection from '@/components/dashboard/UploadSection.vue';
import RecentAnalyses from '@/components/dashboard/RecentAnalyses.vue';
import StatsOverview from '@/components/dashboard/StatsOverview.vue';

export default {
  name: 'AgricultorDashboard',
  components: {
    DashboardHeader,
    QuickActions,
    UploadSection,
    RecentAnalyses,
    StatsOverview
  },
  data() {
    return {
      sidebarCollapsed: localStorage.getItem('sidebarCollapsed') === 'true',
      activeSection: 'overview',
      farmerName: 'Juan Pérez',
      historyFilter: {
        dateRange: 'all',
        quality: 'all'
      },
      userProfile: {
        fullName: 'Juan Pérez',
        email: 'juan.perez@email.com',
        phone: '+57 300 123 4567'
      },
      userPreferences: {
        notifications: true,
        autoReports: false,
        dataSharing: true
      },
      recentAnalyses: [
        {
          id: 'CAC-2023-045',
          status: 'completed',
          statusLabel: 'Completado',
          quality: 92,
          defects: 3.2,
          avgSize: 12.5,
          date: '15/08/2023'
        },
        {
          id: 'CAC-2023-044',
          status: 'completed',
          statusLabel: 'Completado',
          quality: 88,
          defects: 5.1,
          avgSize: 11.8,
          date: '10/08/2023'
        },
        {
          id: 'CAC-2023-043',
          status: 'completed',
          statusLabel: 'Completado',
          quality: 85,
          defects: 6.7,
          avgSize: 12.1,
          date: '05/08/2023'
        }
      ],
      stats: {
        totalBatches: 24,
        batchesChange: '+5%',
        avgQuality: 87,
        qualityChange: '+2%',
        defectRate: 5.2,
        defectChange: '-1.2%'
      },
      fincasStats: {
        totalFincas: 3,
        totalLotes: 12,
        areaTotal: 8.5,
        ultimaActualizacion: 'Hoy'
      },
      fincas: [
        {
          id: 1,
          nombre: 'Finca El Paraíso',
          ubicacion: 'Vereda La Esperanza, Santander',
          area: 3.2,
          lotes: 5,
          fechaRegistro: '15/01/2023',
          status: 'active',
          statusLabel: 'Activa'
        },
        {
          id: 2,
          nombre: 'Finca Los Cacaos',
          ubicacion: 'Vereda San José, Antioquia',
          area: 2.8,
          lotes: 4,
          fechaRegistro: '20/02/2023',
          status: 'active',
          statusLabel: 'Activa'
        },
        {
          id: 3,
          nombre: 'Finca La Esperanza',
          ubicacion: 'Vereda El Progreso, Caldas',
          area: 2.5,
          lotes: 3,
          fechaRegistro: '10/03/2023',
          status: 'active',
          statusLabel: 'Activa'
        }
      ]
    };
  },
  computed: {
    filteredAnalyses() {
      let filtered = [...this.recentAnalyses];
      
      if (this.historyFilter.quality !== 'all') {
        const qualityRanges = {
          excellent: analysis => analysis.quality >= 90,
          good: analysis => analysis.quality >= 80 && analysis.quality < 90,
          fair: analysis => analysis.quality >= 70 && analysis.quality < 80,
          poor: analysis => analysis.quality < 70
        };
        filtered = filtered.filter(qualityRanges[this.historyFilter.quality]);
      }
      
      return filtered;
    }
  },
  mounted() {
    this.checkScreenSize();
    window.addEventListener('resize', this.checkScreenSize);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.checkScreenSize);
  },
  methods: {
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed;
      localStorage.setItem('sidebarCollapsed', this.sidebarCollapsed);
    },
    checkScreenSize() {
      if (window.innerWidth <= 768) {
        this.sidebarCollapsed = true;
        localStorage.setItem('sidebarCollapsed', 'true');
      }
    },
    setActiveSection(section) {
      this.activeSection = section;
    },
    openUploadModal() {
      // This will be handled by the UploadSection component
    },
    handleFileUpload(files) {
      console.log('Archivos seleccionados:', files);
      // Implementar lógica para manejar la carga de archivos
      // Por ejemplo, subir a un servidor o procesar las imágenes
    },
    viewAnalysisDetails(analysis) {
      console.log('Ver detalles del análisis:', analysis);
      // Navegar a la vista de detalles o mostrar un modal
    },
    // Métodos para gestión de fincas
    registrarNuevaFinca() {
      console.log('Registrar nueva finca');
      // Aquí se implementaría la lógica para registrar una nueva finca
      // Por ahora solo mostramos un mensaje
      alert('Función de registro de finca en desarrollo');
    },
    gestionarFincas() {
      console.log('Gestionar fincas existentes');
      // Aquí se implementaría la lógica para gestionar fincas
      alert('Función de gestión de fincas en desarrollo');
    },
    monitorearLotes() {
      console.log('Monitorear lotes');
      // Aquí se implementaría la lógica para monitorear lotes
      alert('Función de monitoreo de lotes en desarrollo');
    },
    generarReportesFincas() {
      console.log('Generar reportes de fincas');
      // Aquí se implementaría la lógica para generar reportes
      alert('Función de reportes de fincas en desarrollo');
    },
    verDetalleFinca(finca) {
      console.log('Ver detalle de finca:', finca);
      // Aquí se implementaría la lógica para ver detalles de la finca
      alert(`Ver detalles de: ${finca.nombre}`);
    },
    editarFinca(finca) {
      console.log('Editar finca:', finca);
      // Aquí se implementaría la lógica para editar la finca
      alert(`Editar finca: ${finca.nombre}`);
    },
    logout() {
      // Mostrar mensaje de confirmación
      if (confirm('¿Estás seguro de que quieres cerrar sesión?')) {
        // Limpiar datos de sesión del localStorage
        localStorage.removeItem('userToken');
        localStorage.removeItem('userRole');
        localStorage.removeItem('sidebarCollapsed');
        
        // Limpiar cualquier otro dato de sesión que pueda existir
        localStorage.removeItem('userData');
        localStorage.removeItem('authToken');
        
        // Redirigir al login
        this.$router.push('/login');
      }
    }
  }
};
</script>

<style>
.farmer-dashboard-container {
  display: flex;
  min-height: 100vh;
  background-color: #f8f9fa;
}

/* Sidebar Styles */
.dashboard-sidebar {
  width: 280px;
  background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
  color: white;
  transition: all 0.3s ease;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
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

.farmer-avatar::after {
  content: '';
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 12px;
  height: 12px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.6rem;
  color: #27ae60;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.farmer-info:hover .farmer-avatar::after {
  opacity: 1;
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

.sidebar-toggle {
  background: none;
  border: none;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.sidebar-toggle:hover {
  background: rgba(255, 255, 255, 0.1);
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
  margin: 0.5rem 0;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  color: white;
  text-decoration: none;
  transition: all 0.2s ease;
  border-radius: 0 25px 25px 0;
  margin-right: 1rem;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(5px);
}

.nav-item.active .nav-link {
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.nav-link i {
  font-size: 1.2rem;
  width: 20px;
  text-align: center;
}

.sidebar-footer {
  padding: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.quick-stats {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.8;
}

.stat-value {
  font-weight: 600;
  font-size: 1.1rem;
}

/* Logout Section Styles */
.logout-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  animation: fadeInUp 0.3s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.logout-btn {
  width: 100%;
  background: rgba(231, 76, 60, 0.8);
  color: white;
  border: none;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.logout-btn:hover {
  background: rgba(231, 76, 60, 1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

.logout-btn:active {
  transform: translateY(0);
}

.logout-btn i {
  font-size: 1rem;
}

/* Collapsed sidebar logout button */
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
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.logout-btn-collapsed:hover {
  background: rgba(231, 76, 60, 1);
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

.logout-btn-collapsed:active {
  transform: scale(0.95);
}

/* Indicador de logout en sidebar colapsado */
.sidebar-collapsed .logout-btn-collapsed {
  position: relative;
}

.sidebar-collapsed .logout-btn-collapsed::after {
  content: '';
  position: absolute;
  top: -2px;
  right: -2px;
  width: 8px;
  height: 8px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.sidebar-collapsed .logout-btn-collapsed:hover::after {
  opacity: 1;
}

/* Main Content Styles */
.dashboard-main {
  flex: 1;
  padding: 2rem;
  transition: all 0.3s ease;
}

.main-expanded {
  margin-left: 0;
}

.dashboard-main {
  flex: 1;
  padding: 2rem;
  transition: all 0.3s ease;
  margin-left: 0;
  position: relative;
}

.mobile-sidebar-toggle {
  position: fixed;
  top: 20px;
  left: 20px;
  background: #27ae60;
  color: white;
  border: none;
  padding: 0.75rem 1rem;
  border-radius: 25px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  transition: all 0.2s ease;
}

.mobile-sidebar-toggle:hover {
  background: #219653;
  transform: translateX(5px);
}

.dashboard-section {
  max-width: 1200px;
  margin: 0 auto;
}

.section-header {
  margin-bottom: 2rem;
  text-align: center;
}

.section-header h1 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 2.5rem;
}

.section-header p {
  color: #7f8c8d;
  font-size: 1.1rem;
}

/* Overview Grid */
.overview-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  margin-top: 2rem;
}

.overview-card {
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.overview-card h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.3rem;
}

/* Analysis Tools */
.analysis-tools {
  margin-top: 2rem;
}

.analysis-tools h3 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.tool-card {
  background: white;
  border-radius: 10px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease;
}

.tool-card:hover {
  transform: translateY(-5px);
}

.tool-card i {
  font-size: 3rem;
  color: #27ae60;
  margin-bottom: 1rem;
}

.tool-card h4 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.3rem;
}

.tool-card p {
  color: #7f8c8d;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

/* Reports Grid */
.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.report-card {
  background: white;
  border-radius: 10px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease;
}

.report-card:hover {
  transform: translateY(-5px);
}

.report-card h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.3rem;
}

.report-card p {
  color: #7f8c8d;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

/* History Filters */
.history-filters {
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 600;
  color: #2c3e50;
}

.filter-group select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

/* Settings Grid */
.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.settings-card {
  background: white;
  border-radius: 10px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.settings-card h3 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-size: 1.3rem;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #2c3e50;
}

.form-group input {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.preferences {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.preference-item label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  color: #2c3e50;
}

.preference-item input[type="checkbox"] {
  width: auto;
}

/* Button Styles */
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
  text-decoration: none;
  justify-content: center;
}

.btn-primary {
  background-color: #27ae60;
  color: white;
}

.btn-primary:hover {
  background-color: #219653;
  transform: translateY(-2px);
}

.btn-secondary {
  background-color: #f1f2f6;
  color: #2c3e50;
}

.btn-secondary:hover {
  background-color: #dfe4ea;
  transform: translateY(-2px);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .dashboard-sidebar {
    width: 250px;
  }
  
  .overview-grid {
    grid-template-columns: 1fr;
  }
  
  .tools-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .farmer-dashboard-container {
    flex-direction: column;
  }
  
  .dashboard-sidebar {
    width: 100%;
    position: sticky;
    top: 0;
    z-index: 100;
  }
  
  .sidebar-collapsed {
    width: 100%;
  }
  
  .dashboard-main {
    padding: 1rem;
  }
  
  .section-header h1 {
    font-size: 2rem;
  }
  
  .history-filters {
    flex-direction: column;
  }
  
  .settings-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .overview-grid,
  .tools-grid,
  .reports-grid,
  .settings-grid {
    grid-template-columns: 1fr;
  }
  
  .tool-card,
  .report-card,
  .settings-card {
    padding: 1.5rem;
  }
}

/* Estilos para el módulo de Fincas */
.fincas-overview {
  margin-bottom: 2rem;
}

.fincas-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-3px);
}

.stat-card i {
  font-size: 2rem;
  color: #27ae60;
  width: 40px;
  text-align: center;
}

.stat-content h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.8rem;
  font-weight: 600;
}

.stat-content p {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.fincas-actions {
  margin-bottom: 2rem;
}

.fincas-actions h3 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.action-card {
  background: white;
  border-radius: 10px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease;
}

.action-card:hover {
  transform: translateY(-5px);
}

.action-card i {
  font-size: 3rem;
  color: #27ae60;
  margin-bottom: 1rem;
}

.action-card h4 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.3rem;
}

.action-card p {
  color: #7f8c8d;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.fincas-list {
  margin-bottom: 2rem;
}

.fincas-list h3 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.fincas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.finca-card {
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease;
}

.finca-card:hover {
  transform: translateY(-3px);
}

.finca-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #ecf0f1;
}

.finca-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.finca-status {
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.finca-status.active {
  background: rgba(39, 174, 96, 0.1);
  color: #27ae60;
}

.finca-status.inactive {
  background: rgba(231, 76, 60, 0.1);
  color: #e74c3c;
}

.finca-details {
  margin-bottom: 1.5rem;
}

.finca-details p {
  margin: 0.5rem 0;
  color: #7f8c8d;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.finca-details i {
  width: 16px;
  color: #27ae60;
}

.finca-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

/* Responsive para fincas */
@media (max-width: 768px) {
  .fincas-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
  
  .fincas-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .fincas-stats {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    padding: 1rem;
  }
  
  .action-card {
    padding: 1.5rem;
  }
  
  .finca-card {
    padding: 1rem;
  }
}
</style>

<template>
  <div class="farmer-dashboard-container">

    <!-- Sidebar -->
    <Sidebar
      :brand-name="'CacaoScan'"
      :user-name="farmerName"
      :user-role="'agricultor'"
      :current-route="''"
      :active-section="activeSection"
      :collapsed="isSidebarCollapsed"
      @menu-click="handleMenuClick"
      @logout="logout"
      @toggle-collapse="toggleSidebarCollapse"
    />

    <!-- Main Content -->
    <main class="dashboard-main" :class="isSidebarCollapsed ? 'ml-20' : 'ml-64'">
      <!-- Overview Section -->
      <div v-if="activeSection === 'overview'" class="dashboard-section">
        <WelcomeHeader :farmer-name="farmerName" />
        
        <StatsCards 
          :total-batches="formattedStats.totalBatches"
          :avg-quality="formattedStats.avgQuality"
          :defect-rate="formattedStats.defectRate"
        />
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <RecentActivity :recent-analyses="recentAnalyses" />
          <QuickActions 
            @nuevo-analisis="handleNuevoAnalisis"
            @gestionar-fincas="handleGestionarFincas"
          />
        </div>
      </div>

      <!-- Settings Section -->
      <div v-if="activeSection === 'settings'" class="dashboard-section">
            <div class="mb-8">
          <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
            <h1 class="text-3xl font-bold text-gray-900">Configuración</h1>
            <p class="text-gray-600 mt-1">Gestiona tu perfil y preferencias</p>
                </div>
                </div>
                
        <div class="settings-grid">
          <div class="settings-card">
            <h3 class="text-lg font-bold text-gray-900 mb-4">Perfil de Usuario</h3>
            <div class="space-y-4">
                <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Nombre completo</label>
                <input type="text" v-model="userProfile.fullName" placeholder="Tu nombre completo" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200">
                </div>
                <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Email</label>
                <input type="email" v-model="userProfile.email" placeholder="tu@email.com" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200">
                </div>
                <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Teléfono</label>
                <input type="tel" v-model="userProfile.phone" placeholder="+57 300 123 4567" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200">
                </div>
              <button type="button" class="w-full bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-all duration-200 font-semibold shadow-md hover:shadow-lg">
                Guardar Cambios
              </button>
        </div>
      </div>

          <div class="settings-card">
            <h3 class="text-lg font-bold text-gray-900 mb-4">Preferencias</h3>
            <div class="space-y-4 mb-6">
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <label class="flex items-center cursor-pointer">
                  <input type="checkbox" v-model="userPreferences.notifications" class="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500">
                  <span class="ml-3 text-sm font-medium text-gray-700">Recibir notificaciones por email</span>
                </label>
              </div>
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <label class="flex items-center cursor-pointer">
                  <input type="checkbox" v-model="userPreferences.autoReports" class="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500">
                  <span class="ml-3 text-sm font-medium text-gray-700">Generar reportes automáticamente</span>
                </label>
              </div>
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <label class="flex items-center cursor-pointer">
                  <input type="checkbox" v-model="userPreferences.dataSharing" class="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500">
                  <span class="ml-3 text-sm font-medium text-gray-700">Compartir datos anónimos para investigación</span>
                </label>
              </div>
            </div>
            <button type="button" class="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-all duration-200 font-semibold shadow-md hover:shadow-lg">
              Guardar Preferencias
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useImageStats } from '@/composables/useImageStats'
import ImageHistoryCard from '@/components/dashboard/ImageHistoryCard.vue'
import Sidebar from '@/components/layout/Common/Sidebar.vue'
import WelcomeHeader from '@/components/agricultor/WelcomeHeader.vue'
import StatsCards from '@/components/agricultor/StatsCards.vue'
import RecentActivity from '@/components/agricultor/RecentActivity.vue'
import QuickActions from '@/components/agricultor/QuickActions.vue'

export default {
  name: 'AgricultorDashboard',
  components: {
    Sidebar,
    ImageHistoryCard,
    WelcomeHeader,
    StatsCards,
    RecentActivity,
    QuickActions
  },
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    const isSidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true');
    
    // Initialize activeSection from query parameter if present
    const sectionParam = router.currentRoute.value.query.section;
    const activeSection = ref(sectionParam || 'overview');
    
    // Usar composable para estadísticas reales
    const { 
      stats, 
      loading, 
      error, 
      fetchStats, 
      fetchImages, 
      generateReport,
      totalImages,
      processedImages,
      processingRate,
      averageConfidence,
      averageDimensions,
      regionStats,
      topFincas
    } = useImageStats();
    
    // Usar datos reales del usuario autenticado
    const farmerName = computed(() => authStore.userFullName || 'Usuario');
    
    // Datos de análisis recientes (ahora desde API)
    const recentAnalyses = ref([]);
    const imagesLoading = ref(false);
    
    // Cargar datos reales al montar el componente
    onMounted(async () => {
      await Promise.all([
        fetchStats(),
        loadRecentAnalyses()
      ]);
    });
    
    // Función para cargar análisis recientes
    async function loadRecentAnalyses() {
      imagesLoading.value = true;
      try {
        const data = await fetchImages(1, { page_size: '5' });
        recentAnalyses.value = data.results.map(image => ({
          id: `CAC-${image.id}`,
          status: image.processed ? 'completed' : 'pending',
          statusLabel: image.processed ? 'Completado' : 'Pendiente',
          quality: image.prediction ? Math.round(image.prediction.average_confidence * 100) : 0,
          defects: image.prediction ? Math.round((1 - image.prediction.average_confidence) * 100 * 10) / 10 : 0,
          avgSize: image.prediction ? Math.round((image.prediction.alto_mm + image.prediction.ancho_mm + image.prediction.grosor_mm) / 3 * 10) / 10 : 0,
          date: new Date(image.created_at).toLocaleDateString('es-ES')
        }));
      } catch (err) {
        console.error('Error loading recent analyses:', err);
      } finally {
        imagesLoading.value = false;
      }
    }
    
    // Función para generar reportes
    async function handleGenerateReport(reportType) {
      const success = await generateReport(reportType, {});
      if (success) {
        // Mostrar mensaje de éxito
        console.log(`Reporte ${reportType} generado exitosamente`);
      }
    }
    
    // Función para refrescar datos
    async function refreshData() {
      await Promise.all([
        fetchStats(),
        loadRecentAnalyses()
      ]);
    }
    
    // Función para manejar selección de imagen
    function handleImageSelected(image) {
      console.log('Imagen seleccionada:', image);
      // Aquí se puede agregar lógica adicional si es necesario
    }

    const handleNuevoAnalisis = () => {
      // Navegar a la vista de nuevo análisis (se debe crear como vista separada)
      alert('Redirigiendo a Nuevo Análisis...');
    };

    const handleGestionarFincas = () => {
      router.push({ name: 'AgricultorFincas' });
    };
    
    // Computed para estadísticas formateadas
    const formattedStats = computed(() => ({
      totalBatches: totalImages.value,
      batchesChange: '+0%', // TODO: Calcular cambio porcentual
      avgQuality: Math.round(averageConfidence.value * 100),
      qualityChange: '+0%', // TODO: Calcular cambio porcentual
      defectRate: Math.round((1 - averageConfidence.value) * 100 * 10) / 10,
      defectChange: '+0%' // TODO: Calcular cambio porcentual
    }));
    
    

    const checkScreenSize = () => {
      if (window.innerWidth <= 768) {
        isSidebarCollapsed.value = true;
        localStorage.setItem('sidebarCollapsed', 'true');
      }
    };

    const setActiveSection = (section) => {
      activeSection.value = section;
    };

    const handleMenuClick = (item) => {
      if (item.route && item.route !== null) {
        // If navigating to the same route, just update the activeSection
        if (router.currentRoute.value.path === item.route) {
          activeSection.value = 'overview';
        } else {
          router.push(item.route);
        }
      } else {
        // For internal sections without routes, just update activeSection
        // This allows switching between sections within the dashboard
        activeSection.value = item.id;
      }
    };

    const toggleSidebarCollapse = () => {
      isSidebarCollapsed.value = !isSidebarCollapsed.value;
      localStorage.setItem('sidebarCollapsed', isSidebarCollapsed.value);
    };

    const logout = async () => {
        try {
          await authStore.logout();
        } catch (error) {
          console.error('Error al cerrar sesión:', error);
          authStore.clearAll();
      }
    };

    // Variables para configuración
    const userProfile = ref({
      fullName: authStore.user?.full_name || '',
      email: authStore.user?.email || '',
      phone: ''
    });

    const userPreferences = ref({
      notifications: true,
      autoReports: false,
      dataSharing: false
    });

    return {
      // Stores
      authStore,
      // Sidebar
      isSidebarCollapsed,
      activeSection,
      // Dashboard
      farmerName,
      recentAnalyses,
      formattedStats,
      loading,
      error,
      imagesLoading,
      userProfile,
      userPreferences,
      checkScreenSize,
      setActiveSection,
      handleMenuClick,
      toggleSidebarCollapse,
      logout,
      handleGenerateReport,
      refreshData,
      loadRecentAnalyses,
      handleImageSelected,
      handleNuevoAnalisis,
      handleGestionarFincas
    };
  },
  mounted() {
    this.checkScreenSize();
    window.addEventListener('resize', this.checkScreenSize);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.checkScreenSize);
  }
};
</script>

<style scoped>
.farmer-dashboard-container {
  display: flex;
  min-height: 100vh;
  background-color: #F9FAFB;
}

.dashboard-main {
  min-height: 100vh;
  width: 100%;
  padding: 2rem;
  overflow-y: auto;
}

.dashboard-section {
  max-width: 100%;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.settings-card {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
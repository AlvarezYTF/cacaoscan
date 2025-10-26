<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar -->
    <Sidebar 
      :brand-name="'CacaoScan'"
      :user-name="userName"
      :user-role="userRole"
      :current-route="$route.path"
      :active-section="activeSection"
      :collapsed="isSidebarCollapsed"
      @menu-click="handleMenuClick"
      @logout="handleLogout"
      @toggle-collapse="toggleSidebarCollapse"
    />

    <!-- Main Content -->
    <div :class="isSidebarCollapsed ? 'lg:pl-20' : 'lg:pl-64'">
      <main class="py-6 px-4 sm:px-6 lg:px-8">
        <div class="max-w-7xl mx-auto">
          <!-- Header -->
          <div class="mb-8">
            <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
              <h1 class="text-3xl font-bold text-gray-900">Configuración</h1>
              <p class="text-gray-600 mt-1">Gestiona tu perfil y preferencias</p>
            </div>
          </div>
        
          <!-- Settings Content -->
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
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import Sidebar from '@/components/layout/Common/Sidebar.vue';

export default {
  name: 'Configuracion',
  components: {
    Sidebar
  },
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();

    const isSidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true');
    const activeSection = ref('settings');

    // Computed properties
    const userName = computed(() => {
      return authStore.userFullName || 'Usuario';
    });

    const userRole = computed(() => {
      const role = authStore.userRole || 'Usuario';
      if (role === 'admin') return 'admin';
      if (role === 'farmer') return 'agricultor';
      return 'agricultor';
    });

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

    // Sidebar methods
    const handleMenuClick = (item) => {
      if (item.route && item.route !== null) {
        const currentPath = router.currentRoute.value.path;
        if (currentPath !== item.route) {
          router.push(item.route);
        }
      } else {
        const role = authStore.userRole;
        if (role === 'farmer' || role === 'Agricultor') {
          router.push({ 
            name: 'AgricultorDashboard',
            query: { section: item.id }
          });
        } else {
          router.push({ 
            name: 'AdminDashboard',
            query: { section: item.id }
          });
        }
      }
    };

    const toggleSidebarCollapse = () => {
      isSidebarCollapsed.value = !isSidebarCollapsed.value;
      localStorage.setItem('sidebarCollapsed', isSidebarCollapsed.value);
    };

    const handleLogout = async () => {
      try {
        await authStore.logout();
      } catch (error) {
        console.error('Error during logout:', error);
      }
    };

    return {
      activeSection,
      userName,
      userRole,
      isSidebarCollapsed,
      userProfile,
      userPreferences,
      handleMenuClick,
      handleLogout,
      toggleSidebarCollapse
    };
  }
};
</script>

<style scoped>
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


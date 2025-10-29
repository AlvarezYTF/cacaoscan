<template>
  <div class="space-y-6">
    <h2 class="text-lg font-medium text-gray-900">Información del Lote</h2>
    
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
      <!-- Agricultor (First) -->
      <div>
        <label for="farmer" class="block text-sm font-medium text-gray-700">
          Agricultor <span class="text-red-500">*</span>
        </label>
        
        <!-- Select for admin -->
        <select
          v-if="userRole === 'admin'"
          id="farmer"
          v-model="formData.farmer"
          :disabled="loadingAgricultores"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
          :class="{ 'border-red-500': errors.farmer, 'bg-gray-100 cursor-wait': loadingAgricultores }"
        >
          <option value="">{{ loadingAgricultores ? 'Cargando agricultores...' : 'Selecciona un agricultor' }}</option>
          <option v-for="agricultor in agricultores" :key="agricultor.id" :value="agricultor.username">
            {{ agricultor.first_name }} {{ agricultor.last_name }} ({{ agricultor.email }})
          </option>
        </select>
        
        <!-- Input readonly for agricultor -->
        <input
          v-else
          type="text"
          id="farmer"
          v-model="formData.farmer"
          @input="updateForm"
          readonly
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 bg-gray-100 cursor-not-allowed"
          :class="{ 'border-red-500': errors.farmer }"
        />
        
        <p v-if="errors.farmer" class="mt-1 text-sm text-red-600">{{ errors.farmer }}</p>
        <p v-if="userRole === 'agricultor'" class="mt-1 text-xs text-gray-500">
          Este campo se completa automáticamente con tu nombre
        </p>
        <p v-if="agricultores.length === 0 && !loadingAgricultores && userRole === 'admin'" class="mt-1 text-xs text-amber-600">
          No hay agricultores registrados
        </p>
      </div>

      <!-- Finca -->
      <div>
        <label for="farm" class="block text-sm font-medium text-gray-700">
          Finca <span class="text-red-500">*</span>
        </label>
        <select
          id="farm"
          v-model="formData.farm"
          :disabled="loadingFincas"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
          :class="{ 'border-red-500': errors.farm, 'bg-gray-100 cursor-wait': loadingFincas }"
        >
          <option value="">{{ loadingFincas ? 'Cargando fincas...' : 'Selecciona una finca' }}</option>
          <option v-for="finca in fincas" :key="finca.id" :value="finca.nombre">
            {{ finca.nombre }} - {{ finca.ubicacion || 'Sin ubicación' }}
          </option>
        </select>
        <p v-if="errors.farm" class="mt-1 text-sm text-red-600">{{ errors.farm }}</p>
        <p v-if="fincas.length === 0 && !loadingFincas" class="mt-1 text-xs text-amber-600">
          {{ userRole === 'agricultor' ? 'No tienes fincas registradas' : 'No hay fincas disponibles' }}
        </p>
      </div>

      <!-- Lugar de Origen -->
      <div>
        <label for="originPlace" class="block text-sm font-medium text-gray-700">
          Lugar de origen <span class="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="originPlace"
          v-model="formData.originPlace"
          @input="updateForm"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
          :class="{ 'border-red-500': errors.originPlace }"
        />
        <p v-if="errors.originPlace" class="mt-1 text-sm text-red-600">{{ errors.originPlace }}</p>
      </div>

      <!-- Genética -->
      <div>
        <label for="genetics" class="block text-sm font-medium text-gray-700">
          Genética <span class="text-red-500">*</span>
        </label>
        <select
          id="genetics"
          v-model="formData.genetics"
          @change="updateForm"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
          :class="{ 'border-red-500': errors.genetics }"
        >
          <option value="">Selecciona la genética</option>
          <option value="Criollo">Criollo</option>
          <option value="Forastero">Forastero</option>
          <option value="Trinitario">Trinitario</option>
          <option value="Nacional">Nacional</option>
          <option value="Híbrido">Híbrido</option>
          <option value="Otra">Otra</option>
        </select>
        <p v-if="errors.genetics" class="mt-1 text-sm text-red-600">{{ errors.genetics }}</p>
      </div>

      <!-- Nombre del Lote -->
      <div class="col-span-full sm:col-span-2">
        <label for="batchName" class="block text-sm font-medium text-gray-700">
          Nombre o código del lote <span class="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="batchName"
          v-model="formData.name"
          @input="updateForm"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
          :class="{ 'border-red-500': errors.name }"
        />
        <p v-if="errors.name" class="mt-1 text-sm text-red-600">{{ errors.name }}</p>
      </div>

      <!-- Fecha de Recolección -->
      <div>
        <label for="collectionDate" class="block text-sm font-medium text-gray-700">
          Fecha de recolección <span class="text-red-500">*</span>
        </label>
        <input
          type="date"
          id="collectionDate"
          v-model="formData.collectionDate"
          @input="updateForm"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
          :class="{ 'border-red-500': errors.collectionDate }"
          max=""
        />
        <p v-if="errors.collectionDate" class="mt-1 text-sm text-red-600">{{ errors.collectionDate }}</p>
      </div>

      <!-- Origen -->
      <div>
        <label for="origin" class="block text-sm font-medium text-gray-700">
          Origen
        </label>
        <div class="mt-1">
          <select
            id="origin"
            v-model="formData.origin"
            @change="updateForm"
            class="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
          >
            <option value="">Selecciona un origen</option>
            <option value="Piura">Piura</option>
            <option value="San Martín">San Martín</option>
            <option value="Cajamarca">Cajamarca</option>
            <option value="Otro">Otro</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Observaciones -->
    <div>
      <label for="notes" class="block text-sm font-medium text-gray-700">
        Observaciones (opcional)
      </label>
      <div class="mt-1">
        <textarea
          id="notes"
          v-model="formData.notes"
          @input="updateForm"
          rows="3"
          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
          placeholder="Notas adicionales sobre el lote..."
        ></textarea>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue';
import { getFincas } from '@/services/fincasApi';
import { useAuthStore } from '@/stores/auth';
import authApi from '@/services/authApi';

export default {
  name: 'BatchInfoForm',
  props: {
    modelValue: {
      type: Object,
      required: true
    },
    errors: {
      type: Object,
      default: () => ({})
    },
    userRole: {
      type: String,
      default: 'admin'
    },
    userName: {
      type: String,
      default: ''
    },
    userId: {
      type: Number,
      default: null
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const authStore = useAuthStore();
    const formData = ref({
      farm: '',
      originPlace: '',
      farmer: '',
      genetics: '',
      ...props.modelValue
    });

    const fincas = ref([]);
    const loadingFincas = ref(false);
    
    const agricultores = ref([]);
    const loadingAgricultores = ref(false);
    
    // All fincas (keep track of all loaded fincas to filter them)
    const allFincas = ref([]);

    
    // Load agricultores from backend (only for admin)
    const loadAgricultores = async () => {
      if (props.userRole !== 'admin') return;
      
      loadingAgricultores.value = true;
      try {
        const response = await authApi.getUsers();
        // Filter to get only farmers (non-admin, non-staff users)
        agricultores.value = response.results?.filter(user => 
          !user.is_superuser && !user.is_staff && user.role === 'farmer'
        ) || [];
      } catch (error) {
        console.error('Error loading agricultores:', error);
        agricultores.value = [];
      } finally {
        loadingAgricultores.value = false;
      }
    };

    // Set max date to today and auto-fill farmer name for agricultor role
    onMounted(async () => {
      const today = new Date().toISOString().split('T')[0];
      document.getElementById('collectionDate')?.setAttribute('max', today);
      
      // Load all fincas
      await loadAllFincas();
      
      // Load agricultores (only for admin)
      await loadAgricultores();
      
      // Set initial fincas based on role
      if (props.userRole === 'agricultor' && props.userId) {
        // Filter only fincas owned by the current user
        console.log('🔍 Filtering fincas for agricultor ID:', props.userId);
        console.log('🔍 All fincas:', allFincas.value);
        fincas.value = allFincas.value.filter(finca => finca.agricultor_id === props.userId) || [];
        console.log('🔍 Filtered fincas:', fincas.value);
      } else {
        // Admin sees all fincas initially
        fincas.value = allFincas.value;
      }
      
      // Auto-fill farmer name if user is agricultor
      if (props.userRole === 'agricultor' && props.userName && !formData.value.farmer) {
        formData.value.farmer = props.userName;
        emit('update:modelValue', { ...formData.value });
      }
    });

    // Load all fincas from backend
    const loadAllFincas = async () => {
      try {
        const response = await getFincas();
        allFincas.value = response.results || [];
      } catch (error) {
        console.error('Error loading all fincas:', error);
        allFincas.value = [];
      }
    };

    const updateForm = () => {
      // Mapear los campos al formato que espera el store
      const mappedData = {
        name: formData.value.name || '',
        farm: formData.value.farm || '',
        originPlace: formData.value.originPlace || '',
        genetics: formData.value.genetics || '',
        collectionDate: formData.value.collectionDate || '',
        origin: '',  // Este campo no se usa por ahora
        notes: formData.value.notes || '',
        farmer: formData.value.farmer || '',
      };
      emit('update:modelValue', mappedData);
    };

    // When farmer changes, filter fincas by that farmer
    const handleFarmerChange = () => {
      if (props.userRole === 'agricultor') return;
      
      if (formData.value.farmer) {
        const selectedAgricultor = agricultores.value.find(a => a.username === formData.value.farmer);
        console.log('🔍 Selected agricultor:', selectedAgricultor);
        if (selectedAgricultor) {
          fincas.value = allFincas.value.filter(finca => finca.agricultor_id === selectedAgricultor.id);
          console.log('🔍 Filtered fincas for agricultor:', fincas.value);
        } else {
          fincas.value = allFincas.value;
        }
      } else {
        fincas.value = allFincas.value;
      }
      
      updateForm();
    };

    // When finca changes, auto-select the associated farmer
    const handleFincaChange = () => {
      if (props.userRole === 'agricultor') return;
      
      if (formData.value.farm) {
        const selectedFinca = allFincas.value.find(f => f.nombre === formData.value.farm);
        console.log('🔍 Selected finca:', selectedFinca);
        if (selectedFinca && selectedFinca.agricultor_id) {
          const associatedAgricultor = agricultores.value.find(a => a.id === selectedFinca.agricultor_id);
          console.log('🔍 Associated agricultor:', associatedAgricultor);
          if (associatedAgricultor) {
            formData.value.farmer = associatedAgricultor.username;
          }
        }
      }
      
      updateForm();
    };

    // Watch for changes in modelValue from parent
    watch(() => props.modelValue, (newValue) => {
      formData.value = { ...newValue };
    }, { deep: true });
    
    // Watch for farmer changes
    watch(() => formData.value.farmer, () => {
      handleFarmerChange();
    });
    
    // Watch for finca changes
    watch(() => formData.value.farm, () => {
      handleFincaChange();
    });

    return {
      formData,
      updateForm,
      userRole: props.userRole,
      fincas,
      loadingFincas,
      agricultores,
      loadingAgricultores
    };
  }
};
</script>

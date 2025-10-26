<template>
  <!-- Modal -->
  <div 
    id="edit-farmer-modal" 
    tabindex="-1" 
    aria-hidden="true" 
    class="hidden overflow-y-auto overflow-x-hidden fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-sm"
    ref="modalContainer"
  >
    <div class="relative w-full max-w-4xl max-h-[90vh]">
      <!-- Modal content -->
      <div class="relative bg-white rounded-lg shadow-lg border border-gray-200">
        <!-- Modal header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <div class="flex items-center">
            <div class="bg-green-100 p-3 rounded-lg mr-4">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900">
                Editar Agricultor
              </h3>
              <p class="text-sm text-gray-600 mt-1">Modifica la información del agricultor y gestiona sus fincas</p>
            </div>
          </div>
          <button 
            type="button" 
            @click="closeModal"
            class="text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg p-2 transition-all duration-200"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- Modal body -->
        <div class="p-6 max-h-[calc(90vh-200px)] overflow-y-auto">
          <!-- Tabs -->
          <ul class="flex flex-wrap text-sm font-medium text-center text-gray-500 border-b border-gray-200 mb-6">
            <li class="mr-2">
              <button 
                @click="activeTab = 'info'"
                :class="activeTab === 'info' ? 'text-green-600 border-green-600' : 'text-gray-500 border-transparent'"
                class="inline-block p-4 border-b-2 rounded-t-lg hover:text-gray-600 transition-all duration-200"
              >
                Información Personal
              </button>
            </li>
            <li>
              <button 
                @click="activeTab = 'fincas'"
                :class="activeTab === 'fincas' ? 'text-green-600 border-green-600' : 'text-gray-500 border-transparent'"
                class="inline-block p-4 border-b-2 rounded-t-lg hover:text-gray-600 transition-all duration-200"
              >
                Fincas ({{ fincasList.length }})
              </button>
            </li>
          </ul>

          <!-- Tab Content: Information -->
          <div v-if="activeTab === 'info'" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <!-- Nombre -->
              <div>
                <label for="edit_first_name" class="block mb-2 text-sm font-semibold text-gray-700">
                  Nombre <span class="text-red-500">*</span>
                </label>
                <input 
                  type="text" 
                  id="edit_first_name" 
                  v-model="formData.first_name"
                  class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200" 
                  placeholder="Ingrese el nombre"
                  required 
                />
                <p v-if="errors.first_name" class="mt-1 text-sm text-red-600 font-medium">{{ errors.first_name }}</p>
              </div>

              <!-- Apellido -->
              <div>
                <label for="edit_last_name" class="block mb-2 text-sm font-semibold text-gray-700">
                  Apellido <span class="text-red-500">*</span>
                </label>
                <input 
                  type="text" 
                  id="edit_last_name" 
                  v-model="formData.last_name"
                  class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200" 
                  placeholder="Ingrese el apellido"
                  required 
                />
                <p v-if="errors.last_name" class="mt-1 text-sm text-red-600 font-medium">{{ errors.last_name }}</p>
              </div>

              <!-- Email -->
              <div>
                <label for="edit_email" class="block mb-2 text-sm font-semibold text-gray-700">
                  Email <span class="text-red-500">*</span>
                </label>
                <input 
                  type="email" 
                  id="edit_email" 
                  v-model="formData.email"
                  class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200" 
                  placeholder="nombre@email.com"
                  required 
                />
                <p v-if="errors.email" class="mt-1 text-sm text-red-600 font-medium">{{ errors.email }}</p>
              </div>

              <!-- Teléfono -->
              <div>
                <label for="edit_phone_number" class="block mb-2 text-sm font-semibold text-gray-700">
                  Teléfono
                </label>
                <input 
                  type="tel" 
                  id="edit_phone_number" 
                  v-model="formData.phone_number"
                  class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200" 
                  placeholder="+57 300 1234567"
                />
              </div>

              <!-- Región -->
              <div>
                <label for="edit_region" class="block mb-2 text-sm font-semibold text-gray-700">
                  Región
                </label>
                <select 
                  id="edit_region"
                  v-model="formData.region"
                  class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200"
                >
                  <option value="">Seleccionar región</option>
                  <option value="Antioquia">Antioquia</option>
                  <option value="Santander">Santander</option>
                  <option value="Nariño">Nariño</option>
                  <option value="Huila">Huila</option>
                  <option value="Cauca">Cauca</option>
                </select>
              </div>

              <!-- Municipio -->
              <div>
                <label for="edit_municipality" class="block mb-2 text-sm font-semibold text-gray-700">
                  Municipio
                </label>
                <input 
                  type="text" 
                  id="edit_municipality" 
                  v-model="formData.municipality"
                  class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200" 
                  placeholder="Ingrese el municipio"
                />
              </div>
            </div>
          </div>

          <!-- Tab Content: Fincas -->
          <div v-else-if="activeTab === 'fincas'">
            <!-- Lista de fincas existentes -->
            <div class="mb-6">
              <div class="flex items-center justify-between mb-4">
                <h4 class="text-lg font-bold text-gray-900">Fincas Registradas</h4>
                <button 
                  @click="showCreateFinca = !showCreateFinca"
                  class="inline-flex items-center px-4 py-2 text-sm font-semibold text-white bg-green-600 rounded-lg hover:bg-green-700 transition-all duration-200"
                >
                  <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                  </svg>
                  Nueva Finca
                </button>
              </div>

              <!-- Formulario para crear finca -->
              <div v-if="showCreateFinca" class="bg-green-50 border-2 border-green-200 rounded-lg p-6 mb-6">
                <h5 class="text-base font-bold text-gray-900 mb-4">Crear Nueva Finca</h5>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label for="finca_nombre" class="block mb-2 text-sm font-semibold text-gray-700">
                      Nombre de la Finca <span class="text-red-500">*</span>
                    </label>
                    <input 
                      type="text" 
                      id="finca_nombre" 
                      v-model="newFinca.nombre"
                      class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200" 
                      placeholder="Ej: Finca El Paraíso"
                      required 
                    />
                  </div>

                  <div>
                    <label for="finca_municipio" class="block mb-2 text-sm font-semibold text-gray-700">
                      Municipio <span class="text-red-500">*</span>
                    </label>
                    <input 
                      type="text" 
                      id="finca_municipio" 
                      v-model="newFinca.municipio"
                      class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200" 
                      placeholder="Ej: Medellín"
                      required 
                    />
                  </div>

                  <div>
                    <label for="finca_departamento" class="block mb-2 text-sm font-semibold text-gray-700">
                      Departamento <span class="text-red-500">*</span>
                    </label>
                    <input 
                      type="text" 
                      id="finca_departamento" 
                      v-model="newFinca.departamento"
                      class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200" 
                      placeholder="Ej: Antioquia"
                      required 
                    />
                  </div>

                  <div>
                    <label for="finca_hectareas" class="block mb-2 text-sm font-semibold text-gray-700">
                      Hectáreas <span class="text-red-500">*</span>
                    </label>
                    <input 
                      type="number" 
                      id="finca_hectareas" 
                      v-model.number="newFinca.hectareas"
                      class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200" 
                      placeholder="0.00"
                      step="0.01"
                      min="0.01"
                      required 
                    />
                  </div>

                  <div class="md:col-span-2">
                    <label for="finca_ubicacion" class="block mb-2 text-sm font-semibold text-gray-700">
                      Ubicación
                    </label>
                    <input 
                      type="text" 
                      id="finca_ubicacion" 
                      v-model="newFinca.ubicacion"
                      class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200" 
                      placeholder="Dirección específica o referencia"
                    />
                  </div>

                  <div>
                    <label for="finca_coordenadas_lat" class="block mb-2 text-sm font-semibold text-gray-700">
                      Latitud GPS
                    </label>
                    <input 
                      type="number" 
                      id="finca_coordenadas_lat" 
                      v-model.number="newFinca.coordenadas_lat"
                      class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200" 
                      placeholder="Ej: 4.6097"
                      step="0.0000001"
                    />
                  </div>

                  <div>
                    <label for="finca_coordenadas_lng" class="block mb-2 text-sm font-semibold text-gray-700">
                      Longitud GPS
                    </label>
                    <input 
                      type="number" 
                      id="finca_coordenadas_lng" 
                      v-model.number="newFinca.coordenadas_lng"
                      class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200" 
                      placeholder="Ej: -74.0817"
                      step="0.0000001"
                    />
                  </div>
                </div>

                <div class="flex items-center justify-end gap-3 mt-4">
                  <button 
                    @click="showCreateFinca = false; resetNewFinca()"
                    class="px-4 py-2 text-sm font-semibold text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-all duration-200"
                  >
                    Cancelar
                  </button>
                  <button 
                    @click="handleCreateFinca"
                    :disabled="isCreatingFinca"
                    class="inline-flex items-center px-4 py-2 text-sm font-semibold text-white bg-green-600 rounded-lg hover:bg-green-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span v-if="!isCreatingFinca">Crear Finca</span>
                    <span v-else class="flex items-center">
                      <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Guardando...
                    </span>
                  </button>
                </div>
              </div>

              <!-- Lista de fincas -->
              <div v-if="fincasList.length > 0" class="space-y-3">
                <div 
                  v-for="(finca, index) in fincasList" 
                  :key="index"
                  class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all duration-200"
                >
                  <div class="flex items-start justify-between">
                    <div class="flex-1">
                      <div class="flex items-center gap-3 mb-2">
                        <div class="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
                          <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                          </svg>
                        </div>
                        <div>
                          <h5 class="text-base font-bold text-gray-900">{{ finca.nombre }}</h5>
                          <p class="text-sm text-gray-600">{{ finca.municipio }}, {{ finca.departamento }}</p>
                        </div>
                      </div>
                      <div class="flex items-center gap-4 text-sm flex-wrap">
                        <span class="flex items-center gap-2 text-gray-600 bg-gray-50 px-3 py-1.5 rounded-lg">
                          <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9"></path>
                          </svg>
                          {{ finca.hectareas }} hectáreas
                        </span>
                        <span :class="finca.activa ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="px-3 py-1.5 rounded-lg font-semibold flex items-center gap-1.5">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                          </svg>
                          {{ finca.activa ? 'Activa' : 'Inactiva' }}
                        </span>
                      </div>
                      
                      <!-- Coordenadas GPS -->
                      <div v-if="finca.coordenadas_lat && finca.coordenadas_lng" class="mt-2 flex items-center gap-2 text-xs text-gray-500">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        <span>📍 GPS: {{ finca.coordenadas_lat }}, {{ finca.coordenadas_lng }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Empty state -->
              <div v-else class="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
                <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                </svg>
                <h4 class="text-lg font-bold text-gray-900 mb-2">Sin fincas registradas</h4>
                <p class="text-gray-600">Este agricultor no tiene fincas asociadas aún</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal footer -->
        <div class="flex items-center justify-end gap-3 pt-6 border-t border-gray-200 px-6">
          <button 
            type="button"
            @click="closeModal"
            class="px-6 py-3 text-sm font-semibold text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-all duration-200"
          >
            Cancelar
          </button>
          <button 
            type="button"
            @click="handleUpdate"
            :disabled="isSubmitting"
            class="inline-flex items-center px-6 py-3 text-sm font-semibold text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg"
          >
            <span v-if="!isSubmitting">Guardar Cambios</span>
            <span v-else class="flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Guardando...
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, watch } from 'vue';
import Swal from 'sweetalert2';
import { createFinca, getFincas } from '@/services/fincasApi';
import authApi from '@/services/authApi';

export default {
  name: 'EditFarmerModal',
  props: {
    farmer: {
      type: Object,
      default: () => ({
        id: null,
        name: '',
        email: '',
        first_name: '',
        last_name: '',
        phone_number: '',
        region: '',
        municipality: '',
        fincas: []
      })
    }
  },
  emits: ['farmer-updated', 'close'],
  setup(props, { emit }) {
    const modalContainer = ref(null);
    const isSubmitting = ref(false);
    const isCreatingFinca = ref(false);
    const activeTab = ref('info');
    const showCreateFinca = ref(false);
    const fincasList = ref([]); // Estado local para las fincas

    const formData = reactive({
      first_name: '',
      last_name: '',
      email: '',
      phone_number: '',
      region: '',
      municipality: ''
    });

    const newFinca = reactive({
      nombre: '',
      municipio: '',
      departamento: '',
      hectareas: '',
      ubicacion: '',
      coordenadas_lat: null,
      coordenadas_lng: null
    });

    const errors = reactive({});

    // Cargar datos del agricultor al abrir el modal
    watch(() => props.farmer, (newFarmer) => {
      if (newFarmer && newFarmer.id) {
        // Extraer first_name y last_name del name
        const nameParts = newFarmer.name?.split(' ') || [];
        formData.first_name = nameParts[0] || '';
        formData.last_name = nameParts.slice(1).join(' ') || '';
        formData.email = newFarmer.email || '';
        formData.phone_number = newFarmer.phone_number || '';
        formData.region = newFarmer.region || '';
        formData.municipality = newFarmer.municipality || '';
        
        // Cargar las fincas del agricultor desde el backend
        loadFarmersFincas(newFarmer.id);
      }
    }, { immediate: true });
    
    // Función para cargar las fincas del agricultor
    const loadFarmersFincas = async (agricultorId) => {
      try {
        const response = await getFincas({ agricultor: agricultorId });
        console.log('✅ [EditFarmerModal] Fincas cargadas:', response.results);
        
        // Actualizar el estado local de fincas
        fincasList.value = response.results || [];
      } catch (error) {
        console.error('❌ [EditFarmerModal] Error cargando fincas:', error);
        fincasList.value = [];
      }
    };

    const resetNewFinca = () => {
      newFinca.nombre = '';
      newFinca.municipio = '';
      newFinca.departamento = '';
      newFinca.hectareas = '';
      newFinca.ubicacion = '';
      newFinca.coordenadas_lat = null;
      newFinca.coordenadas_lng = null;
    };

    const handleCreateFinca = async () => {
      // Validar campos requeridos
      if (!newFinca.nombre || !newFinca.municipio || !newFinca.departamento || !newFinca.hectareas) {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'Por favor completa todos los campos requeridos',
          confirmButtonColor: '#ef4444'
        });
        return;
      }

      isCreatingFinca.value = true;

      try {
        // Obtener el ID del agricultor del prop farmer
        const agricultorId = props.farmer.id;

        const fincaData = {
          nombre: newFinca.nombre,
          municipio: newFinca.municipio,
          departamento: newFinca.departamento,
          hectareas: parseFloat(newFinca.hectareas),
          ubicacion: newFinca.ubicacion || '',
          agricultor: props.farmer.id,  // Incluir el ID del agricultor
          coordenadas_lat: newFinca.coordenadas_lat || null,
          coordenadas_lng: newFinca.coordenadas_lng || null
        };

        console.log('📤 [EditFarmerModal] Creando finca:', fincaData);
        console.log('📤 [EditFarmerModal] Agricultor ID:', props.farmer.id);

        // Crear la finca asignando el agricultor al que pertenece la finca
        const createdFinca = await createFinca(fincaData);
        console.log('✅ [EditFarmerModal] Finca creada:', createdFinca);

        Swal.fire({
          icon: 'success',
          title: 'Finca creada',
          text: 'La finca ha sido registrada exitosamente',
          confirmButtonColor: '#10b981'
        });

        // Reset form
        resetNewFinca();
        showCreateFinca.value = false;

        // Recargar las fincas del agricultor
        await loadFarmersFincas(props.farmer.id);

        // Emit event to reload data
        emit('farmer-updated', { type: 'finca-created' });

      } catch (error) {
        console.error('Error creando finca:', error);
        
        let errorMessage = 'Error al crear la finca';
        if (error.response?.data) {
          const data = error.response.data;
          errorMessage = data.message || data.error || errorMessage;
          if (data.details) {
            const details = Object.entries(data.details)
              .map(([key, value]) => `${key}: ${Array.isArray(value) ? value[0] : value}`)
              .join(', ');
            if (details) {
              errorMessage += `\n\nDetalles: ${details}`;
            }
          }
        }

        Swal.fire({
          icon: 'error',
          title: 'Error',
          html: errorMessage.replace(/\n/g, '<br>'),
          confirmButtonColor: '#ef4444'
        });
      } finally {
        isCreatingFinca.value = false;
      }
    };

    const handleUpdate = async () => {
      // Validar campos requeridos
      if (!formData.first_name || !formData.last_name || !formData.email) {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'Por favor completa todos los campos requeridos',
          confirmButtonColor: '#ef4444'
        });
        return;
      }

      isSubmitting.value = true;

      try {
        const updateData = {
          first_name: formData.first_name,
          last_name: formData.last_name,
          email: formData.email
        };

        console.log('📤 [EditFarmerModal] Actualizando agricultor:', props.farmer.id, updateData);

        // Llamar al endpoint de actualización de usuario
        const response = await authApi.updateUser(props.farmer.id, updateData);
        
        console.log('✅ [EditFarmerModal] Respuesta recibida:', response);

        Swal.fire({
          icon: 'success',
          title: 'Agricultor actualizado',
          text: 'La información del agricultor ha sido actualizada exitosamente',
          confirmButtonColor: '#10b981'
        });

        emit('farmer-updated', { type: 'user-updated', user: response.user });
        closeModal();
      } catch (error) {
        console.error('Error actualizando agricultor:', error);
        
        let errorMessage = 'Error al actualizar el agricultor';
        if (error.response?.data) {
          const data = error.response.data;
          errorMessage = data.message || data.error || errorMessage;
          if (data.details) {
            const details = Object.entries(data.details)
              .map(([key, value]) => `${key}: ${Array.isArray(value) ? value[0] : value}`)
              .join(', ');
            if (details) {
              errorMessage += `\n\nDetalles: ${details}`;
            }
          }
        }

        Swal.fire({
          icon: 'error',
          title: 'Error',
          html: errorMessage.replace(/\n/g, '<br>'),
          confirmButtonColor: '#ef4444'
        });
      } finally {
        isSubmitting.value = false;
      }
    };

    const closeModal = () => {
      if (modalContainer.value) {
        const modalElement = modalContainer.value;
        modalElement.classList.add('hidden');
        modalElement.setAttribute('aria-hidden', 'true');
      }
      showCreateFinca.value = false;
      resetNewFinca();
      emit('close');
    };

    const openModal = () => {
      if (modalContainer.value) {
        const modalElement = modalContainer.value;
        modalElement.classList.remove('hidden');
        modalElement.setAttribute('aria-hidden', 'false');
      }
    };

    return {
      modalContainer,
      formData,
      newFinca,
      errors,
      isSubmitting,
      isCreatingFinca,
      activeTab,
      showCreateFinca,
      fincasList,
      resetNewFinca,
      handleCreateFinca,
      handleUpdate,
      closeModal,
      openModal
    };
  }
};
</script>


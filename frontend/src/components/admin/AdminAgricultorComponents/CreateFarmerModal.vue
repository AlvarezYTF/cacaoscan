<template>
  <!-- Modal -->
  <div 
    id="create-farmer-modal" 
    tabindex="-1" 
    aria-hidden="true" 
    class="hidden overflow-y-auto overflow-x-hidden fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-sm"
    ref="modalContainer"
  >
    <div class="relative w-full max-w-2xl max-h-[90vh]">
      <!-- Modal content -->
      <div class="relative bg-white rounded-lg shadow-lg border border-gray-200">
        <!-- Modal header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <div class="flex items-center">
            <div class="bg-green-100 p-2 rounded-lg mr-4">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900">
                Crear Nuevo Agricultor
              </h3>
              <p class="text-sm text-gray-600 mt-1">Complete el formulario para registrar un nuevo agricultor</p>
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
        <form @submit.prevent="handleSubmit" class="p-6">
          <div class="space-y-4">
            <!-- Nombre -->
            <div>
              <label for="first_name" class="block mb-2 text-sm font-semibold text-gray-700">
                Nombre <span class="text-red-500">*</span>
              </label>
              <input 
                type="text" 
                id="first_name" 
                v-model="formData.first_name"
                class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200" 
                placeholder="Ingrese el nombre del agricultor"
                required 
              />
              <p v-if="errors.first_name" class="mt-1 text-sm text-red-600 font-medium">{{ errors.first_name }}</p>
            </div>

            <!-- Apellido -->
            <div>
              <label for="last_name" class="block mb-2 text-sm font-semibold text-gray-700">
                Apellido <span class="text-red-500">*</span>
              </label>
              <input 
                type="text" 
                id="last_name" 
                v-model="formData.last_name"
                class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200" 
                placeholder="Ingrese el apellido del agricultor"
                required 
              />
              <p v-if="errors.last_name" class="mt-1 text-sm text-red-600 font-medium">{{ errors.last_name }}</p>
            </div>

            <!-- Email -->
            <div>
              <label for="email" class="block mb-2 text-sm font-semibold text-gray-700">
                Email <span class="text-red-500">*</span>
              </label>
              <input 
                type="email" 
                id="email" 
                v-model="formData.email"
                class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200" 
                placeholder="nombre@email.com"
                required 
              />
              <p v-if="errors.email" class="mt-1 text-sm text-red-600 font-medium">{{ errors.email }}</p>
            </div>

            <!-- Teléfono -->
            <div>
              <label for="phone_number" class="block mb-2 text-sm font-semibold text-gray-700">
                Teléfono
              </label>
              <input 
                type="tel" 
                id="phone_number" 
                v-model="formData.phone_number"
                class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200" 
                placeholder="+57 300 1234567"
              />
            </div>

            <!-- Contraseña -->
            <div>
              <label for="password" class="block mb-2 text-sm font-semibold text-gray-700">
                Contraseña <span class="text-red-500">*</span>
              </label>
              <input 
                type="password" 
                id="password" 
                v-model="formData.password"
                class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200" 
                placeholder="••••••••"
                required 
              />
              <p class="mt-1 text-xs text-gray-500">
                Mínimo 8 caracteres, incluyendo mayúsculas, minúsculas y números
              </p>
              <p v-if="errors.password" class="mt-1 text-sm text-red-600 font-medium">{{ errors.password }}</p>
            </div>

            <!-- Confirmar Contraseña -->
            <div>
              <label for="password_confirm" class="block mb-2 text-sm font-semibold text-gray-700">
                Confirmar Contraseña <span class="text-red-500">*</span>
              </label>
              <input 
                type="password" 
                id="password_confirm" 
                v-model="formData.password_confirm"
                class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200" 
                placeholder="••••••••"
                required 
              />
              <p v-if="errors.password_confirm" class="mt-1 text-sm text-red-600 font-medium">{{ errors.password_confirm }}</p>
            </div>

            <!-- Región -->
            <div>
              <label for="region" class="block mb-2 text-sm font-semibold text-gray-700">
                Región
              </label>
              <select 
                id="region"
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
              <label for="municipality" class="block mb-2 text-sm font-semibold text-gray-700">
                Municipio
              </label>
              <input 
                type="text" 
                id="municipality" 
                v-model="formData.municipality"
                class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200" 
                placeholder="Ingrese el municipio"
              />
            </div>
          </div>

          <!-- Modal footer -->
          <div class="flex items-center justify-end gap-3 pt-6 border-t border-gray-200">
            <button 
              type="button"
              @click="closeModal"
              class="px-6 py-3 text-sm font-semibold text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-all duration-200"
            >
              Cancelar
            </button>
            <button 
              type="submit"
              :disabled="isSubmitting"
              class="inline-flex items-center px-6 py-3 text-sm font-semibold text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg"
            >
              <span v-if="!isSubmitting">Crear Agricultor</span>
              <span v-else class="flex items-center">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Guardando...
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import authApi from '@/services/authApi';
import Swal from 'sweetalert2';

export default {
  name: 'CreateFarmerModal',
  emits: ['farmer-created', 'close'],
  setup(props, { emit }) {
    const modalContainer = ref(null);
    const isSubmitting = ref(false);

    const formData = reactive({
      first_name: '',
      last_name: '',
      email: '',
      phone_number: '',
      password: '',
      password_confirm: '',
      region: '',
      municipality: ''
    });

    const errors = reactive({
      first_name: '',
      last_name: '',
      email: '',
      password: '',
      password_confirm: ''
    });

    const resetForm = () => {
      formData.first_name = '';
      formData.last_name = '';
      formData.email = '';
      formData.phone_number = '';
      formData.password = '';
      formData.password_confirm = '';
      formData.region = '';
      formData.municipality = '';

      Object.keys(errors).forEach(key => errors[key] = '');
    };

    const validateForm = () => {
      let isValid = true;

      // Validar nombre
      if (!formData.first_name.trim()) {
        errors.first_name = 'El nombre es requerido';
        isValid = false;
      }

      // Validar apellido
      if (!formData.last_name.trim()) {
        errors.last_name = 'El apellido es requerido';
        isValid = false;
      }

      // Validar email
      if (!formData.email.trim()) {
        errors.email = 'El email es requerido';
        isValid = false;
      } else {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(formData.email)) {
          errors.email = 'Ingresa un email válido';
          isValid = false;
        }
      }

      // Validar contraseña
      if (!formData.password) {
        errors.password = 'La contraseña es requerida';
        isValid = false;
      } else if (formData.password.length < 8) {
        errors.password = 'La contraseña debe tener al menos 8 caracteres';
        isValid = false;
      }

      // Validar confirmación de contraseña
      if (!formData.password_confirm) {
        errors.password_confirm = 'Confirma tu contraseña';
        isValid = false;
      } else if (formData.password !== formData.password_confirm) {
        errors.password_confirm = 'Las contraseñas no coinciden';
        isValid = false;
      }

      return isValid;
    };

    const handleSubmit = async () => {
      if (!validateForm()) {
        return;
      }

      isSubmitting.value = true;

      try {
        const farmerData = {
          username: formData.email,
          email: formData.email,
          first_name: formData.first_name,
          last_name: formData.last_name,
          password: formData.password,
          password_confirm: formData.password_confirm
        };

        const response = await authApi.register(farmerData);

        Swal.fire({
          icon: 'success',
          title: 'Agricultor creado',
          text: 'El agricultor ha sido registrado exitosamente',
          confirmButtonColor: '#10b981'
        });

        emit('farmer-created', response);
        resetForm();
        closeModal();
      } catch (error) {
        console.error('Error creando agricultor:', error);
        
        const errorMessage = error.response?.data?.message || 
                           error.response?.data?.error || 
                           'Error al crear el agricultor';
        
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: errorMessage,
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
      resetForm();
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
      errors,
      isSubmitting,
      handleSubmit,
      closeModal,
      openModal
    };
  }
};
</script>


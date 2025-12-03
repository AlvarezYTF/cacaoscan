<template>
  <BaseModal
    :show="true"
    :title="mode === 'create' ? 'Crear Usuario' : 'Editar Usuario'"
    subtitle="Complete el formulario para gestionar el usuario"
    max-width="2xl"
    @close="closeModal"
  >
    <template #header>
      <div class="flex items-center">
        <div class="bg-blue-100 p-2 rounded-lg mr-3">
          <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
          </svg>
        </div>
        <div>
          <h3 class="text-xl font-bold text-gray-900">{{ mode === 'create' ? 'Crear Usuario' : 'Editar Usuario' }}</h3>
          <p class="text-sm text-gray-600 mt-1">Complete el formulario para gestionar el usuario</p>
        </div>
      </div>
    </template>

    <form @submit.prevent="saveUser" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <!-- Nombre de Usuario -->
          <BaseFormField
            name="username"
            label="Nombre de Usuario"
            :required="true"
            :error="errors.username"
          >
            <input 
              type="text" 
              id="username"
              v-model="formData.username"
              class="w-full rounded-lg border-2 px-4 py-3 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
              :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/30': errors.username }"
              required
            />
          </BaseFormField>
          
          <!-- Email -->
          <BaseFormField
            name="email"
            label="Email"
            :required="true"
            :error="errors.email"
          >
            <input 
              type="email" 
              id="email"
              v-model="formData.email"
              class="w-full rounded-lg border-2 px-4 py-3 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
              :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/30': errors.email }"
              required
            />
          </BaseFormField>

          <!-- Nombre -->
          <BaseFormField
            name="first_name"
            label="Nombre"
            :required="true"
            :error="errors.first_name"
          >
            <input 
              type="text" 
              id="first_name"
              v-model="formData.first_name"
              class="w-full rounded-lg border-2 px-4 py-3 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
              :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/30': errors.first_name }"
              required
            />
          </BaseFormField>
          
          <!-- Apellido -->
          <BaseFormField
            name="last_name"
            label="Apellido"
            :required="true"
            :error="errors.last_name"
          >
            <input 
              type="text" 
              id="last_name"
              v-model="formData.last_name"
              class="w-full rounded-lg border-2 px-4 py-3 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
              :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/30': errors.last_name }"
              required
            />
          </BaseFormField>

          <!-- Rol -->
          <div>
            <label for="role" class="block text-sm font-semibold text-gray-700 mb-2">
              Rol <span class="text-red-500">*</span>
            </label>
            <select 
              id="role"
              v-model="formData.role"
              class="w-full rounded-lg border-2 px-4 py-3 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
              :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/30': errors.role }"
              required
            >
              <option value="">Seleccionar rol</option>
              <option value="Agricultor">Agricultor</option>
              <option value="Técnico">Técnico</option>
              <option value="Administrador">Administrador</option>
            </select>
            <p v-if="errors.role" class="mt-1 text-sm text-red-600">{{ errors.role }}</p>
          </div>
          
          <!-- Teléfono -->
          <div>
            <label for="phone" class="block text-sm font-semibold text-gray-700 mb-2">
              Teléfono
            </label>
            <input 
              type="tel" 
              id="phone"
              v-model="formData.phone"
              class="w-full rounded-lg border-2 px-4 py-3 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
              :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/30': errors.phone }"
            >
            <p v-if="errors.phone" class="mt-1 text-sm text-red-600">{{ errors.phone }}</p>
          </div>

          <!-- Ubicación -->
          <div>
            <label for="location" class="block text-sm font-semibold text-gray-700 mb-2">
              Ubicación
            </label>
            <input 
              type="text" 
              id="location"
              v-model="formData.location"
              class="w-full rounded-lg border-2 px-4 py-3 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
              placeholder="Ciudad, Departamento"
            >
          </div>
          
          <!-- Organización -->
          <div>
            <label for="organization" class="block text-sm font-semibold text-gray-700 mb-2">
              Organización
            </label>
            <input 
              type="text" 
              id="organization"
              v-model="formData.organization"
              class="w-full rounded-lg border-2 px-4 py-3 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
              placeholder="Cooperativa, Asociación, etc."
            >
          </div>
        </div>

        <!-- Contraseñas para crear -->
        <div v-if="mode === 'create'" class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label for="password" class="block text-sm font-semibold text-gray-700 mb-2">
              Contraseña <span class="text-red-500">*</span>
            </label>
            <input 
              type="password" 
              id="password"
              v-model="formData.password"
              class="w-full rounded-lg border-2 px-4 py-3 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
              :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/30': errors.password }"
              required
            >
            <p v-if="errors.password" class="mt-1 text-sm text-red-600">{{ errors.password }}</p>
          </div>
          
          <div>
            <label for="password_confirm" class="block text-sm font-semibold text-gray-700 mb-2">
              Confirmar Contraseña <span class="text-red-500">*</span>
            </label>
            <input 
              type="password" 
              id="password_confirm"
              v-model="formData.password_confirm"
              class="w-full rounded-lg border-2 px-4 py-3 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
              :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/30': errors.password_confirm }"
              required
            >
            <p v-if="errors.password_confirm" class="mt-1 text-sm text-red-600">{{ errors.password_confirm }}</p>
          </div>
        </div>

        <!-- Contraseñas para editar -->
        <div v-if="mode === 'edit'" class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label for="new_password" class="block text-sm font-semibold text-gray-700 mb-2">
              Nueva Contraseña
            </label>
            <input 
              type="password" 
              id="new_password"
              v-model="formData.new_password"
              class="w-full rounded-lg border-2 px-4 py-3 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
              :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/30': errors.new_password }"
              placeholder="Dejar vacío para mantener la actual"
            >
            <p v-if="errors.new_password" class="mt-1 text-sm text-red-600">{{ errors.new_password }}</p>
          </div>
          
          <div>
            <label for="new_password_confirm" class="block text-sm font-semibold text-gray-700 mb-2">
              Confirmar Nueva Contraseña
            </label>
            <input 
              type="password" 
              id="new_password_confirm"
              v-model="formData.new_password_confirm"
              class="w-full rounded-lg border-2 px-4 py-3 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
              :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/30': errors.new_password_confirm }"
            >
            <p v-if="errors.new_password_confirm" class="mt-1 text-sm text-red-600">{{ errors.new_password_confirm }}</p>
          </div>
        </div>

        <!-- Checkboxes -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div class="flex items-center">
            <input 
              type="checkbox" 
              id="is_active"
              v-model="formData.is_active"
              class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
            >
            <label for="is_active" class="ml-2 text-sm font-medium text-gray-700">
              Usuario activo
            </label>
          </div>
          
          <div class="flex items-center">
            <input 
              type="checkbox" 
              id="is_staff"
              v-model="formData.is_staff"
              :disabled="!canSetStaff"
              class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            >
            <label for="is_staff" class="ml-2 text-sm font-medium text-gray-700">
              Personal administrativo
            </label>
          </div>
        </div>

        <div v-if="canSetSuperuser" class="mb-6">
          <div class="flex items-center">
            <input 
              type="checkbox" 
              id="is_superuser"
              v-model="formData.is_superuser"
              class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
            >
            <label for="is_superuser" class="ml-2 text-sm font-medium text-gray-700">
              Superusuario
            </label>
          </div>
        </div>

        <!-- Notas -->
        <div class="mb-6">
          <label for="notes" class="block text-sm font-semibold text-gray-700 mb-2">
            Notas
          </label>
          <textarea 
            id="notes"
            v-model="formData.notes"
            rows="3"
            class="w-full rounded-lg border-2 px-4 py-3 shadow-sm focus:border-green-500 focus:ring-2 focus:ring-green-500/30 transition-all duration-200"
            placeholder="Información adicional sobre el usuario..."
          ></textarea>
        </div>

      </form>

    <template #footer>
      <div class="flex items-center justify-end gap-3">
        <button 
          type="button" 
          @click="closeModal"
          class="px-6 py-3 bg-gray-500 text-white rounded-lg font-medium hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200"
        >
          Cancelar
        </button>
        <button 
          type="submit" 
          @click="saveUser"
          class="px-6 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-60 disabled:cursor-not-allowed transition-colors duration-200 flex items-center gap-2"
          :disabled="loading"
        >
          <svg v-if="loading" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
          {{ mode === 'create' ? 'Crear Usuario' : 'Guardar Cambios' }}
        </button>
      </div>
    </template>
  </BaseModal>
</template>

<script setup>
// 1. Vue core
import { ref, reactive, computed, watch } from 'vue'

// 2. Stores
import { useAdminStore } from '@/stores/admin'
import { useAuthStore } from '@/stores/auth'

// 3. Composables
import { useFormValidation } from '@/composables/useFormValidation'
import { useNotifications } from '@/composables/useNotifications'
import BaseModal from '@/components/common/BaseModal.vue'
import BaseFormField from '@/components/common/BaseFormField.vue'

// Props
const props = defineProps({
  user: {
    type: Object,
    default: null
  },
  mode: {
    type: String,
    default: 'create',
    validator: (value) => ['create', 'edit'].includes(value)
  }
})

// Emits
const emit = defineEmits(['close', 'saved'])

// Stores
const adminStore = useAdminStore()
const authStore = useAuthStore()

// Composables
const { errors, isValidEmail, isValidPhone, validatePassword, setError, clearErrors } = useFormValidation()
const { showSuccess, showError } = useNotifications()

// State
const loading = ref(false)

// Form data
const formData = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  role: '',
  phone: '',
  location: '',
  organization: '',
  password: '',
  password_confirm: '',
  new_password: '',
  new_password_confirm: '',
  is_active: true,
  is_staff: false,
  is_superuser: false,
  notes: ''
})

// Computed
const canSetStaff = computed(() => {
  return authStore.user?.is_superuser || false
})

const canSetSuperuser = computed(() => {
  return authStore.user?.is_superuser || false
})

// Functions
const initializeForm = () => {
  if (props.mode === 'edit' && props.user) {
    formData.username = props.user.username || ''
    formData.email = props.user.email || ''
    formData.first_name = props.user.first_name || ''
    formData.last_name = props.user.last_name || ''
    formData.role = props.user.role || ''
    formData.phone = props.user.phone || ''
    formData.location = props.user.location || ''
    formData.organization = props.user.organization || ''
    formData.is_active = props.user.is_active || false
    formData.is_staff = props.user.is_staff || false
    formData.is_superuser = props.user.is_superuser || false
    formData.notes = props.user.notes || ''
  } else {
    for (const key of Object.keys(formData)) {
      if (key === 'is_active') {
        formData[key] = true
      } else if (key.startsWith('is_')) {
        formData[key] = false
      } else {
        formData[key] = ''
      }
    }
  }
}

const validateBasicFields = () => {
  if (!formData.username.trim()) {
    setError('username', 'El nombre de usuario es requerido')
  } else if (formData.username.length < 3) {
    setError('username', 'El nombre de usuario debe tener al menos 3 caracteres')
  }

  if (!formData.email.trim()) {
    setError('email', 'El email es requerido')
  } else if (!isValidEmail(formData.email)) {
    setError('email', 'El email no es válido')
  }

  if (!formData.first_name.trim()) {
    setError('first_name', 'El nombre es requerido')
  }

  if (!formData.last_name.trim()) {
    setError('last_name', 'El apellido es requerido')
  }

  if (!formData.role) {
    setError('role', 'El rol es requerido')
  }
}

const validateCreatePassword = () => {
  if (!formData.password) {
    setError('password', 'La contraseña es requerida')
  } else if (formData.password.length < 8) {
    setError('password', 'La contraseña debe tener al menos 8 caracteres')
  }

  if (!formData.password_confirm) {
    setError('password_confirm', 'La confirmación de contraseña es requerida')
  } else if (formData.password !== formData.password_confirm) {
    setError('password_confirm', 'Las contraseñas no coinciden')
  }
}

const validateEditPassword = () => {
  if (!formData.new_password) {
    return
  }

  if (formData.new_password.length < 8) {
    setError('new_password', 'La contraseña debe tener al menos 8 caracteres')
  }

  if (!formData.new_password_confirm) {
    setError('new_password_confirm', 'La confirmación de contraseña es requerida')
  } else if (formData.new_password !== formData.new_password_confirm) {
    setError('new_password_confirm', 'Las contraseñas no coinciden')
  }
}

const validateForm = () => {
  clearErrors()

  validateBasicFields()

  if (props.mode === 'create') {
    validateCreatePassword()
  } else {
    validateEditPassword()
  }

  if (formData.phone && !isValidPhone(formData.phone)) {
    setError('phone', 'El teléfono no es válido')
  }

  return Object.keys(errors).length === 0
}

const buildUserData = () => {
  const userData = {
    username: formData.username.trim(),
    email: formData.email.trim(),
    first_name: formData.first_name.trim(),
    last_name: formData.last_name.trim(),
    role: formData.role,
    phone: formData.phone.trim(),
    location: formData.location.trim(),
    organization: formData.organization.trim(),
    is_active: formData.is_active,
    is_staff: formData.is_staff,
    is_superuser: formData.is_superuser,
    notes: formData.notes.trim()
  }

  if (props.mode === 'create') {
    userData.password = formData.password
  } else if (formData.new_password) {
    userData.password = formData.new_password
  }

  return userData
}

const processUserErrors = (errorData) => {
  if (errorData.username) {
    setError('username', Array.isArray(errorData.username) ? errorData.username[0] : errorData.username)
  }
  if (errorData.email) {
    setError('email', Array.isArray(errorData.email) ? errorData.email[0] : errorData.email)
  }
  if (errorData.password) {
    setError('password', Array.isArray(errorData.password) ? errorData.password[0] : errorData.password)
  }
}

const saveUser = async () => {
  if (!validateForm()) {
    return
  }

  loading.value = true
  clearErrors()

  try {
    const userData = buildUserData()
    const response = props.mode === 'create'
      ? await adminStore.createUser(userData)
      : await adminStore.updateUser(props.user.id, userData)

    showSuccess(`El usuario ha sido ${props.mode === 'create' ? 'creado' : 'actualizado'} exitosamente`)

    emit('saved', response.data)
    closeModal()
  } catch (error) {
    console.error('Error saving user:', error)
    
    if (error.response?.data) {
      const errorData = error.response.data
      processUserErrors(errorData)
      
      if (Object.keys(errors).length === 0) {
        showError(errorData.detail || 'No se pudo guardar el usuario')
      }
    } else {
      showError('No se pudo guardar el usuario')
    }
  } finally {
    loading.value = false
  }
}

const closeModal = () => {
  emit('close')
}

// Expose for testing
defineExpose({
  errors,
  formData,
  processUserErrors,
  buildUserData,
  validateForm
})

// Watchers
watch(() => props.user, () => {
  initializeForm()
}, { immediate: true })

watch(() => props.mode, () => {
  initializeForm()
})
</script>

<style scoped>
/* Solo estilos que no están en Tailwind si es necesario */
</style>

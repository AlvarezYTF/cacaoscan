<template>
  <div class="modal-overlay" @click="closeModal">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h3>
          <i class="fas fa-user"></i>
          {{ mode === 'create' ? 'Crear Usuario' : 'Editar Usuario' }}
        </h3>
        <button class="close-btn" @click="closeModal">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <form @submit.prevent="saveUser" class="modal-body">
        <div class="form-row">
          <div class="form-group">
            <label for="username">Nombre de Usuario *</label>
            <input 
              type="text" 
              id="username"
              v-model="formData.username"
              :class="{ 'error': errors.username }"
              required
            >
            <span v-if="errors.username" class="error-message">{{ errors.username }}</span>
          </div>
          
          <div class="form-group">
            <label for="email">Email *</label>
            <input 
              type="email" 
              id="email"
              v-model="formData.email"
              :class="{ 'error': errors.email }"
              required
            >
            <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="first_name">Nombre *</label>
            <input 
              type="text" 
              id="first_name"
              v-model="formData.first_name"
              :class="{ 'error': errors.first_name }"
              required
            >
            <span v-if="errors.first_name" class="error-message">{{ errors.first_name }}</span>
          </div>
          
          <div class="form-group">
            <label for="last_name">Apellido *</label>
            <input 
              type="text" 
              id="last_name"
              v-model="formData.last_name"
              :class="{ 'error': errors.last_name }"
              required
            >
            <span v-if="errors.last_name" class="error-message">{{ errors.last_name }}</span>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="role">Rol *</label>
            <select 
              id="role"
              v-model="formData.role"
              :class="{ 'error': errors.role }"
              required
            >
              <option value="">Seleccionar rol</option>
              <option value="Agricultor">Agricultor</option>
              <option value="Técnico">Técnico</option>
              <option value="Administrador">Administrador</option>
            </select>
            <span v-if="errors.role" class="error-message">{{ errors.role }}</span>
          </div>
          
          <div class="form-group">
            <label for="phone">Teléfono</label>
            <input 
              type="tel" 
              id="phone"
              v-model="formData.phone"
              :class="{ 'error': errors.phone }"
            >
            <span v-if="errors.phone" class="error-message">{{ errors.phone }}</span>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="location">Ubicación</label>
            <input 
              type="text" 
              id="location"
              v-model="formData.location"
              :class="{ 'error': errors.location }"
              placeholder="Ciudad, Departamento"
            >
            <span v-if="errors.location" class="error-message">{{ errors.location }}</span>
          </div>
          
          <div class="form-group">
            <label for="organization">Organización</label>
            <input 
              type="text" 
              id="organization"
              v-model="formData.organization"
              :class="{ 'error': errors.organization }"
              placeholder="Cooperativa, Asociación, etc."
            >
            <span v-if="errors.organization" class="error-message">{{ errors.organization }}</span>
          </div>
        </div>

        <div v-if="mode === 'create'" class="form-row">
          <div class="form-group">
            <label for="password">Contraseña *</label>
            <input 
              type="password" 
              id="password"
              v-model="formData.password"
              :class="{ 'error': errors.password }"
              required
            >
            <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
          </div>
          
          <div class="form-group">
            <label for="password_confirm">Confirmar Contraseña *</label>
            <input 
              type="password" 
              id="password_confirm"
              v-model="formData.password_confirm"
              :class="{ 'error': errors.password_confirm }"
              required
            >
            <span v-if="errors.password_confirm" class="error-message">{{ errors.password_confirm }}</span>
          </div>
        </div>

        <div v-if="mode === 'edit'" class="form-row">
          <div class="form-group">
            <label for="new_password">Nueva Contraseña</label>
            <input 
              type="password" 
              id="new_password"
              v-model="formData.new_password"
              :class="{ 'error': errors.new_password }"
              placeholder="Dejar vacío para mantener la actual"
            >
            <span v-if="errors.new_password" class="error-message">{{ errors.new_password }}</span>
          </div>
          
          <div class="form-group">
            <label for="new_password_confirm">Confirmar Nueva Contraseña</label>
            <input 
              type="password" 
              id="new_password_confirm"
              v-model="formData.new_password_confirm"
              :class="{ 'error': errors.new_password_confirm }"
            >
            <span v-if="errors.new_password_confirm" class="error-message">{{ errors.new_password_confirm }}</span>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group checkbox-group">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="formData.is_active"
              >
              <span class="checkmark"></span>
              Usuario activo
            </label>
          </div>
          
          <div class="form-group checkbox-group">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="formData.is_staff"
                :disabled="!canSetStaff"
              >
              <span class="checkmark"></span>
              Personal administrativo
            </label>
          </div>
        </div>

        <div v-if="canSetSuperuser" class="form-row">
          <div class="form-group checkbox-group">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="formData.is_superuser"
              >
              <span class="checkmark"></span>
              Superusuario
            </label>
          </div>
        </div>

        <div class="form-group">
          <label for="notes">Notas</label>
          <textarea 
            id="notes"
            v-model="formData.notes"
            rows="3"
            placeholder="Información adicional sobre el usuario..."
          ></textarea>
        </div>
      </form>

      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" @click="closeModal">
          Cancelar
        </button>
        <button 
          type="submit" 
          class="btn btn-primary"
          @click="saveUser"
          :disabled="loading"
        >
          <i v-if="loading" class="fas fa-spinner fa-spin"></i>
          <i v-else class="fas fa-save"></i>
          {{ mode === 'create' ? 'Crear Usuario' : 'Guardar Cambios' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, watch } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { useAuthStore } from '@/stores/auth'
import Swal from 'sweetalert2'

export default {
  name: 'UserFormModal',
  props: {
    user: {
      type: Object,
      default: null
    },
    mode: {
      type: String,
      default: 'create',
      validator: (value) => ['create', 'edit'].includes(value)
    }
  },
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const adminStore = useAdminStore()
    const authStore = useAuthStore()

    const loading = ref(false)
    const errors = ref({})

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

    // Methods
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
        // Reset form for create mode
        Object.keys(formData).forEach(key => {
          if (key === 'is_active') {
            formData[key] = true
          } else if (key.startsWith('is_')) {
            formData[key] = false
          } else {
            formData[key] = ''
          }
        })
      }
    }

    const validateForm = () => {
      errors.value = {}

      // Required fields
      if (!formData.username.trim()) {
        errors.value.username = 'El nombre de usuario es requerido'
      } else if (formData.username.length < 3) {
        errors.value.username = 'El nombre de usuario debe tener al menos 3 caracteres'
      }

      if (!formData.email.trim()) {
        errors.value.email = 'El email es requerido'
      } else if (!isValidEmail(formData.email)) {
        errors.value.email = 'El email no es válido'
      }

      if (!formData.first_name.trim()) {
        errors.value.first_name = 'El nombre es requerido'
      }

      if (!formData.last_name.trim()) {
        errors.value.last_name = 'El apellido es requerido'
      }

      if (!formData.role) {
        errors.value.role = 'El rol es requerido'
      }

      // Password validation for create mode
      if (props.mode === 'create') {
        if (!formData.password) {
          errors.value.password = 'La contraseña es requerida'
        } else if (formData.password.length < 8) {
          errors.value.password = 'La contraseña debe tener al menos 8 caracteres'
        }

        if (!formData.password_confirm) {
          errors.value.password_confirm = 'La confirmación de contraseña es requerida'
        } else if (formData.password !== formData.password_confirm) {
          errors.value.password_confirm = 'Las contraseñas no coinciden'
        }
      }

      // Password validation for edit mode
      if (props.mode === 'edit' && formData.new_password) {
        if (formData.new_password.length < 8) {
          errors.value.new_password = 'La contraseña debe tener al menos 8 caracteres'
        }

        if (!formData.new_password_confirm) {
          errors.value.new_password_confirm = 'La confirmación de contraseña es requerida'
        } else if (formData.new_password !== formData.new_password_confirm) {
          errors.value.new_password_confirm = 'Las contraseñas no coinciden'
        }
      }

      // Phone validation
      if (formData.phone && !isValidPhone(formData.phone)) {
        errors.value.phone = 'El teléfono no es válido'
      }

      return Object.keys(errors.value).length === 0
    }

    const isValidEmail = (email) => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(email)
    }

    const isValidPhone = (phone) => {
      const phoneRegex = /^[\+]?[0-9\s\-\(\)]{7,15}$/
      return phoneRegex.test(phone)
    }

    const saveUser = async () => {
      if (!validateForm()) {
        return
      }

      loading.value = true
      errors.value = {}

      try {
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

        // Add password for create mode
        if (props.mode === 'create') {
          userData.password = formData.password
        }

        // Add new password for edit mode if provided
        if (props.mode === 'edit' && formData.new_password) {
          userData.password = formData.new_password
        }

        let response
        if (props.mode === 'create') {
          response = await adminStore.createUser(userData)
        } else {
          response = await adminStore.updateUser(props.user.id, userData)
        }

        Swal.fire({
          icon: 'success',
          title: 'Usuario guardado',
          text: `El usuario ha sido ${props.mode === 'create' ? 'creado' : 'actualizado'} exitosamente`
        })

        emit('saved', response.data)
        closeModal()

      } catch (error) {
        console.error('Error saving user:', error)
        
        if (error.response?.data) {
          const errorData = error.response.data
          
          // Handle field-specific errors
          if (errorData.username) {
            errors.value.username = Array.isArray(errorData.username) ? errorData.username[0] : errorData.username
          }
          if (errorData.email) {
            errors.value.email = Array.isArray(errorData.email) ? errorData.email[0] : errorData.email
          }
          if (errorData.password) {
            errors.value.password = Array.isArray(errorData.password) ? errorData.password[0] : errorData.password
          }
          
          // Show general error if no specific field errors
          if (Object.keys(errors.value).length === 0) {
            Swal.fire({
              icon: 'error',
              title: 'Error',
              text: errorData.detail || 'No se pudo guardar el usuario'
            })
          }
        } else {
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No se pudo guardar el usuario'
          })
        }
      } finally {
        loading.value = false
      }
    }

    const closeModal = () => {
      emit('close')
    }

    // Watchers
    watch(() => props.user, () => {
      initializeForm()
    }, { immediate: true })

    watch(() => props.mode, () => {
      initializeForm()
    })

    return {
      loading,
      errors,
      formData,
      canSetStaff,
      canSetSuperuser,
      saveUser,
      closeModal
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: white;
  border-radius: 10px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #ecf0f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.3rem;
}

.modal-header h3 i {
  margin-right: 10px;
  color: #3498db;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #7f8c8d;
  cursor: pointer;
  padding: 5px;
  border-radius: 3px;
  transition: all 0.2s;
}

.close-btn:hover {
  background-color: #ecf0f1;
  color: #2c3e50;
}

.modal-body {
  padding: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  margin-bottom: 5px;
  font-weight: 500;
  color: #2c3e50;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-group input.error,
.form-group select.error,
.form-group textarea.error {
  border-color: #e74c3c;
}

.error-message {
  color: #e74c3c;
  font-size: 0.8rem;
  margin-top: 5px;
}

.checkbox-group {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: normal;
}

.checkbox-label input[type="checkbox"] {
  margin-right: 8px;
  width: auto;
}

.checkbox-label input[type="checkbox"]:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #ecf0f1;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #7f8c8d;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2980b9;
}

@media (max-width: 768px) {
  .modal-container {
    width: 95%;
    margin: 10px;
  }
  
  .form-row {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>

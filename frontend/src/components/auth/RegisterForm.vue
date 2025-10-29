<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <!-- Header del formulario -->
    <div class="text-center">
      <img src="@/assets/sena-logo.png" alt="Logo CacaoScan"
        class="mx-auto h-16 w-auto mb-4 animate-fade-in drop-shadow-lg">
      <h1 class="text-2xl font-bold text-gray-900 mb-2">Crear una cuenta</h1>
      <p class="text-sm text-gray-600">
        ¿Ya tienes una cuenta?
        <router-link to="/login" class="font-semibold text-green-600 hover:text-green-700 transition-colors">
          Inicia sesión aquí
        </router-link>
      </p>
    </div>

    <!-- Mensaje de estado global -->
    <Transition enter-active-class="transform ease-out duration-300 transition"
      enter-from-class="opacity-0 translate-y-2" enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-200" leave-from-class="opacity-100" leave-to-class="opacity-0">
      <div v-if="statusMessage" class="p-4 rounded-xl flex items-start gap-3 shadow-md" :class="statusMessageClass">
        <svg v-if="statusType === 'success'" class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor"
          viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <svg v-else class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-sm font-medium">{{ statusMessage }}</p>
      </div>
    </Transition>

    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- SECCIÓN 1: Información Personal -->
      <div
        class="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 transition-all duration-200 hover:shadow-xl">
        <div class="flex items-center gap-2 mb-6 pb-4 border-b border-gray-100">
          <div class="p-2 bg-green-100 rounded-lg">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <h2 class="text-lg font-bold text-gray-900">Información Personal</h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Nombre -->
          <div>
            <label for="firstName" class="block text-sm font-semibold text-gray-700 mb-2">
              Nombre *
            </label>
            <input id="firstName" v-model="form.firstName" type="text" autocomplete="given-name" required
              :disabled="isLoading"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
              placeholder="Juan" />
          </div>

          <!-- Segundo Nombre -->
          <div>
            <label for="segundoNombre" class="block text-sm font-semibold text-gray-700 mb-2">
              Segundo Nombre
            </label>
            <input id="segundoNombre" v-model="form.segundoNombre" type="text" :disabled="isLoading"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
              placeholder="Carlos" />
          </div>

          <!-- Apellido -->
          <div>
            <label for="lastName" class="block text-sm font-semibold text-gray-700 mb-2">
              Apellido *
            </label>
            <input id="lastName" v-model="form.lastName" type="text" autocomplete="family-name" required
              :disabled="isLoading"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
              placeholder="Pérez" />
          </div>

          <!-- Segundo Apellido -->
          <div>
            <label for="segundoApellido" class="block text-sm font-semibold text-gray-700 mb-2">
              Segundo Apellido
            </label>
            <input id="segundoApellido" v-model="form.segundoApellido" type="text" :disabled="isLoading"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
              placeholder="Gómez" />
          </div>

          <!-- Teléfono -->
          <div>
            <label for="phoneNumber" class="block text-sm font-semibold text-gray-700 mb-2">
              Teléfono
            </label>
            <input id="phoneNumber" v-model="form.phoneNumber" type="tel" autocomplete="tel" :disabled="isLoading"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
              placeholder="+57 300 123 4567" />
          </div>

          <!-- Género -->
          <div>
            <label for="genero" class="block text-sm font-semibold text-gray-700 mb-2">
              Género *
            </label>
            <select id="genero" v-model="form.genero" required :disabled="isLoading"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200">
              <option value="M">Masculino</option>
              <option value="F">Femenino</option>
            </select>
          </div>

          <!-- Fecha de Nacimiento -->
          <div>
            <label for="fechaNacimiento" class="block text-sm font-semibold text-gray-700 mb-2">
              Fecha de Nacimiento
            </label>
            <input id="fechaNacimiento" v-model="form.fechaNacimiento" type="date" :disabled="isLoading"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200" />
          </div>
        </div>
      </div>

      <!-- SECCIÓN 2: Documentación -->
      <div
        class="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 transition-all duration-200 hover:shadow-xl">
        <div class="flex items-center gap-2 mb-6 pb-4 border-b border-gray-100">
          <div class="p-2 bg-green-100 rounded-lg">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h2 class="text-lg font-bold text-gray-900">Documentación</h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Tipo Documento -->
          <div>
            <label for="tipoDocumento" class="block text-sm font-semibold text-gray-700 mb-2">
              Tipo Documento *
            </label>
            <select id="tipoDocumento" v-model="form.tipoDocumento" required :disabled="isLoading"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200">
              <option value="CC">CC - Cédula de Ciudadanía</option>
              <option value="CE">CE - Cédula de Extranjería</option>
              <option value="PA">PA - Pasaporte</option>
              <option value="TI">TI - Tarjeta de Identidad</option>
              <option value="RC">RC - Registro Civil</option>
            </select>
          </div>

          <!-- Número de Documento -->
          <div class="md:col-span-2">
            <label for="numeroDocumento" class="block text-sm font-semibold text-gray-700 mb-2">
              Número de Documento *
            </label>
            <input id="numeroDocumento" v-model="form.numeroDocumento" type="text" required :disabled="isLoading"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
              placeholder="1234567890" />
          </div>
        </div>
      </div>

      <!-- SECCIÓN 3: Ubicación -->
      <div
        class="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 transition-all duration-200 hover:shadow-xl">
        <div class="flex items-center gap-2 mb-6 pb-4 border-b border-gray-100">
          <div class="p-2 bg-green-100 rounded-lg">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <h2 class="text-lg font-bold text-gray-900">Ubicación</h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Municipio -->
          <div>
            <label for="municipio" class="block text-sm font-semibold text-gray-700 mb-2">
              Municipio *
            </label>
            <input id="municipio" v-model="form.municipio" type="text" required :disabled="isLoading"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
              placeholder="San José del Guaviare" />
          </div>

          <!-- Departamento -->
          <div>
            <label for="departamento" class="block text-sm font-semibold text-gray-700 mb-2">
              Departamento *
            </label>
            <input id="departamento" v-model="form.departamento" type="text" required :disabled="isLoading"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
              placeholder="Guaviare" />
          </div>

          <!-- Dirección -->
          <div class="md:col-span-2">
            <label for="direccion" class="block text-sm font-semibold text-gray-700 mb-2">
              Dirección
            </label>
            <input id="direccion" v-model="form.direccion" type="text" :disabled="isLoading"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
              placeholder="Calle 10 #5-20" />
          </div>
        </div>
      </div>

      <!-- SECCIÓN 4: Credenciales -->
      <div
        class="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 transition-all duration-200 hover:shadow-xl">
        <div class="flex items-center gap-2 mb-6 pb-4 border-b border-gray-100">
          <div class="p-2 bg-green-100 rounded-lg">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h2 class="text-lg font-bold text-gray-900">Credenciales de Acceso</h2>
        </div>

        <div class="space-y-4">
          <!-- Email -->
          <div>
            <label for="email" class="block text-sm font-semibold text-gray-700 mb-2">
              Email *
            </label>
            <input id="email" v-model="form.email" type="email" autocomplete="email" required :disabled="isLoading"
              class="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
              placeholder="juan@ejemplo.com" />
          </div>

          <!-- Contraseña -->
          <div>
            <label for="password" class="block text-sm font-semibold text-gray-700 mb-2">
              Contraseña *
            </label>
            <div class="relative">
              <input id="password" v-model="form.password" :type="showPassword ? 'text' : 'password'"
                autocomplete="new-password" required :disabled="isLoading"
                class="w-full px-4 py-2.5 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
                placeholder="••••••••••••" />
              <button type="button" @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-500 hover:text-green-600 transition-colors">
                <svg v-if="showPassword" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <svg v-else class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L12 12m-3.122-3.122l4.243 4.243M12 12l3 3m0 0l6-6" />
                </svg>
              </button>
            </div>

            <!-- Validación de contraseña -->
            <Transition enter-active-class="transform ease-out duration-300" enter-from-class="opacity-0 scale-95"
              enter-to-class="opacity-100 scale-100" leave-active-class="transition ease-in duration-200"
              leave-from-class="opacity-100" leave-to-class="opacity-0">
              <div v-if="form.password"
                class="mt-3 p-4 bg-green-50 border border-green-200 rounded-lg text-sm">
                <h4 class="font-semibold text-gray-900 mb-2">Requisitos de la contraseña:</h4>
                <ul class="space-y-1">
                  <li class="flex items-center gap-2" :class="passwordChecks.length ? 'text-green-700' : 'text-gray-600'">
                    <svg class="h-4 w-4" :class="passwordChecks.length ? 'text-green-600' : 'text-gray-400'" fill="none"
                      stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        :d="passwordChecks.length ? 'M5 13l4 4L19 7' : 'M6 18L18 6M6 6l12 12'"></path>
                    </svg>
                    Al menos 8 caracteres
                  </li>
                  <li class="flex items-center gap-2"
                    :class="passwordChecks.uppercase ? 'text-green-700' : 'text-gray-600'">
                    <svg class="h-4 w-4" :class="passwordChecks.uppercase ? 'text-green-600' : 'text-gray-400'"
                      fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        :d="passwordChecks.uppercase ? 'M5 13l4 4L19 7' : 'M6 18L18 6M6 6l12 12'"></path>
                    </svg>
                    Una letra mayúscula
                  </li>
                  <li class="flex items-center gap-2"
                    :class="passwordChecks.lowercase ? 'text-green-700' : 'text-gray-600'">
                    <svg class="h-4 w-4" :class="passwordChecks.lowercase ? 'text-green-600' : 'text-gray-400'"
                      fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        :d="passwordChecks.lowercase ? 'M5 13l4 4L19 7' : 'M6 18L18 6M6 6l12 12'"></path>
                    </svg>
                    Una letra minúscula
                  </li>
                  <li class="flex items-center gap-2" :class="passwordChecks.number ? 'text-green-700' : 'text-gray-600'">
                    <svg class="h-4 w-4" :class="passwordChecks.number ? 'text-green-600' : 'text-gray-400'" fill="none"
                      stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        :d="passwordChecks.number ? 'M5 13l4 4L19 7' : 'M6 18L18 6M6 6l12 12'"></path>
                    </svg>
                    Un número
                  </li>
                </ul>
              </div>
            </Transition>
          </div>

          <!-- Confirmar Contraseña -->
          <div>
            <label for="confirmPassword" class="block text-sm font-semibold text-gray-700 mb-2">
              Confirmar Contraseña *
            </label>
            <div class="relative">
              <input id="confirmPassword" v-model="form.confirmPassword" :type="showPassword ? 'text' : 'password'"
                autocomplete="new-password" required :disabled="isLoading"
                class="w-full px-4 py-2.5 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
                placeholder="••••••••••••" />
              <div v-if="form.confirmPassword && form.password === form.confirmPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center">
                <svg class="h-5 w-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- SECCIÓN 5: Términos y Condiciones -->
      <div
        class="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 transition-all duration-200 hover:shadow-xl">
        <div class="space-y-3">
          <div class="flex items-start gap-3 cursor-pointer group">
            <input id="acceptTerms" v-model="form.acceptTerms" type="checkbox" required :disabled="isLoading"
              class="mt-1 h-5 w-5 text-green-600 focus:ring-green-500 border-gray-300 rounded cursor-pointer" />
            <label for="acceptTerms"
              class="text-sm text-gray-700 cursor-pointer group-hover:text-gray-900 transition-colors">
              Acepto los
              <a href="#" class="font-semibold text-green-600 hover:text-green-700 transition-colors">términos y
                condiciones</a>
              y la
              <a href="#" class="font-semibold text-green-600 hover:text-green-700 transition-colors">política de
                privacidad</a>
            </label>
          </div>

          <div class="flex items-start gap-3 cursor-pointer group">
            <input id="emailNotifications" v-model="form.emailNotifications" type="checkbox" :disabled="isLoading"
              class="mt-1 h-5 w-5 text-green-600 focus:ring-green-500 border-gray-300 rounded cursor-pointer" />
            <label for="emailNotifications"
              class="text-sm text-gray-700 cursor-pointer group-hover:text-gray-900 transition-colors">
              Quiero recibir notificaciones por email sobre mi cuenta
            </label>
          </div>
        </div>
      </div>

      <!-- Botón de envío -->
      <div>
        <button type="submit" :disabled="isLoading || !isFormValid"
          class="w-full py-3 px-6 rounded-xl shadow-lg text-base font-semibold text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-4 focus:ring-green-500/50 disabled:opacity-60 disabled:cursor-not-allowed transition-all duration-200 hover:shadow-xl active:scale-[0.98] flex items-center justify-center gap-2">
          <svg v-if="isLoading" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
            </path>
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
          </svg>
          <span>{{ isLoading ? 'Creando cuenta...' : 'Crear Cuenta' }}</span>
        </button>

        <!-- Mensaje de validación -->
        <Transition enter-active-class="transform ease-out duration-200" enter-from-class="opacity-0 -translate-y-2"
          enter-to-class="opacity-100 translate-y-0" leave-active-class="transition ease-in duration-150"
          leave-from-class="opacity-100" leave-to-class="opacity-0">
          <div v-if="!isFormValid && !isLoading" class="mt-4 text-center">
            <div class="inline-flex items-center gap-2 px-4 py-2.5 bg-amber-50 border border-amber-300 rounded-xl">
              <svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z">
                </path>
              </svg>
              <p class="text-sm font-bold text-amber-800">
                {{ getValidationMessage() }}
              </p>
            </div>
          </div>
        </Transition>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Router y store
const router = useRouter()
const authStore = useAuthStore()

// Estado del formulario
const form = ref({
  firstName: '',
  lastName: '',
  email: '',
  phoneNumber: '',
  password: '',
  confirmPassword: '',
  acceptTerms: false,
  emailNotifications: true,
  tipoDocumento: 'CC',
  numeroDocumento: '',
  segundoNombre: '',
  segundoApellido: '',
  direccion: '',
  genero: 'M',
  fechaNacimiento: '',
  municipio: '',
  departamento: ''
})

const errors = ref({})
const isLoading = ref(false)
const showPassword = ref(false)
const statusMessage = ref('')
const statusType = ref('info')

// Computed
const passwordChecks = computed(() => {
  const password = form.value.password
  return {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /\d/.test(password)
  }
})

const isPasswordValid = computed(() => {
  return Object.values(passwordChecks.value).every(check => check)
})

const isFormValid = computed(() => {
  return (
    form.value.firstName.trim() &&
    form.value.lastName.trim() &&
    form.value.email.trim() &&
    form.value.tipoDocumento &&
    form.value.numeroDocumento.trim() &&
    form.value.genero &&
    form.value.municipio.trim() &&
    form.value.departamento.trim() &&
    isPasswordValid.value &&
    form.value.password === form.value.confirmPassword &&
    form.value.acceptTerms
  )
})

const statusMessageClass = computed(() => {
  return statusType.value === 'success'
    ? 'bg-green-50 border border-green-200 text-green-800'
    : 'bg-red-50 border border-red-200 text-red-800'
})

const validateForm = () => {
  errors.value = {}

  if (!form.value.firstName.trim()) {
    errors.value.firstName = 'El nombre es requerido'
  }

  if (!form.value.lastName.trim()) {
    errors.value.lastName = 'El apellido es requerido'
  }

  if (!form.value.email.trim()) {
    errors.value.email = 'El email es requerido'
  } else if (!isValidEmail(form.value.email)) {
    errors.value.email = 'Ingresa un email válido'
  }

  if (form.value.phoneNumber && !isValidPhone(form.value.phoneNumber)) {
    errors.value.phoneNumber = 'Ingresa un número de teléfono válido'
  }

  if (!form.value.password) {
    errors.value.password = 'La contraseña es requerida'
  } else if (form.value.password.length < 6) {
    errors.value.password = 'La contraseña debe tener al menos 6 caracteres'
  }

  if (!form.value.confirmPassword) {
    errors.value.confirmPassword = 'Confirma tu contraseña'
  } else if (form.value.password !== form.value.confirmPassword) {
    errors.value.confirmPassword = 'Las contraseñas no coinciden'
  }

  if (!form.value.acceptTerms) {
    errors.value.acceptTerms = 'Debes aceptar los términos y condiciones'
  }

  return Object.keys(errors.value).length === 0
}

const isValidEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

const isValidPhone = (phone) => {
  const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/
  return phoneRegex.test(phone.replace(/\s/g, ''))
}

const getValidationMessage = () => {
  if (!form.value.firstName.trim()) return 'Completa tu nombre'
  if (!form.value.lastName.trim()) return 'Completa tu apellido'
  if (!form.value.email.trim()) return 'Ingresa tu email'
  if (!form.value.tipoDocumento) return 'Selecciona el tipo de documento'
  if (!form.value.numeroDocumento.trim()) return 'Ingresa el número de documento'
  if (!form.value.genero) return 'Selecciona tu género'
  if (!form.value.municipio.trim()) return 'Ingresa el municipio'
  if (!form.value.departamento.trim()) return 'Ingresa el departamento'
  if (!isPasswordValid.value) return 'La contraseña no cumple con los requisitos'
  if (form.value.password !== form.value.confirmPassword) return 'Las contraseñas no coinciden'
  if (!form.value.acceptTerms) return 'Debes aceptar los términos y condiciones'
  return 'Completa todos los campos obligatorios'
}

const setStatusMessage = (message, type = 'info') => {
  statusMessage.value = message
  statusType.value = type

  setTimeout(() => {
    statusMessage.value = ''
  }, 5000)
}

const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  window.dispatchEvent(new CustomEvent('api-loading-start', {
    detail: { type: 'register', message: 'Creando tu cuenta...' }
  }))

  isLoading.value = true

  try {
    const result = await authStore.register({
      email: form.value.email.trim(),
      password: form.value.password,
      primer_nombre: form.value.firstName.trim(),
      segundo_nombre: form.value.segundoNombre.trim() || '',
      primer_apellido: form.value.lastName.trim(),
      segundo_apellido: form.value.segundoApellido.trim() || '',
      tipo_documento: form.value.tipoDocumento,
      numero_documento: form.value.numeroDocumento.trim() || '',
      telefono: form.value.phoneNumber.trim() || '',
      direccion: form.value.direccion.trim() || '',
      genero: form.value.genero,
      fecha_nacimiento: form.value.fechaNacimiento || '',
      municipio: form.value.municipio.trim() || '',
      departamento: form.value.departamento.trim() || ''
    })

    if (result.success) {
      setStatusMessage('¡Registro exitoso! Bienvenido a CacaoScan 🌱', 'success')
      setTimeout(() => {
        router.push({ name: 'AgricultorDashboard' })
      }, 2000)
    } else {
      setStatusMessage(result.error || 'Error al crear la cuenta', 'error')
    }
  } catch (error) {
    console.error('Error en registro:', error)

    let errorMessage = 'Error inesperado. Intenta nuevamente.'
    if (error.response?.data) {
      if (error.response.data.detail) {
        errorMessage = error.response.data.detail
      } else if (error.response.data.error) {
        errorMessage = error.response.data.error
      } else if (typeof error.response.data === 'string') {
        errorMessage = error.response.data
      } else if (error.response.data.non_field_errors) {
        errorMessage = error.response.data.non_field_errors[0]
      } else {
        const errorKeys = Object.keys(error.response.data)
        if (errorKeys.length > 0) {
          const firstKey = errorKeys[0]
          const firstError = error.response.data[firstKey]
          if (Array.isArray(firstError)) {
            errorMessage = firstError[0]
          } else if (typeof firstError === 'string') {
            errorMessage = firstError
          }
        }
      }
    } else if (error.message) {
      errorMessage = error.message
    }

    setStatusMessage(errorMessage, 'error')
  } finally {
    isLoading.value = false
    window.dispatchEvent(new CustomEvent('api-loading-end'))
  }
}
</script>

<style scoped>
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.6s ease-out;
}
</style>
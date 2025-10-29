<template>
  <div>
    <!-- Header del formulario de registro -->
    <div class="text-center mb-8">
      <img src="@/assets/sena-logo.png" alt="Logo CacaoScan" class="mx-auto h-16 w-auto mb-5 animate-fade-in drop-shadow-lg">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Crear una cuenta</h1>
      <p class="text-gray-600 text-base">
        ¿Ya tienes una cuenta? 
        <router-link to="/login" class="font-semibold text-green-600 hover:text-green-700 transition-colors">
          Inicia sesión aquí
        </router-link>
      </p>
    </div>

    <!-- Mensaje de estado mejorado con transiciones -->
    <Transition
      enter-active-class="transform ease-out duration-300 transition"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="statusMessage" class="mb-6 p-4 rounded-xl flex items-start gap-3" :class="statusMessageClass">
        <svg v-if="statusType === 'success'" class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <svg v-else class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-sm font-medium">{{ statusMessage }}</p>
      </div>
    </Transition>

    <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Nombres con mejor diseño -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label for="firstName" class="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                Nombre *
              </label>
              <div class="relative">
                <input
                  id="firstName"
                  v-model="form.firstName"
                  type="text"
                  autocomplete="given-name"
                  required
                  :disabled="isLoading"
                  class="w-full pl-4 pr-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
                  :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/50': errors.firstName, 'border-green-300': form.firstName && !errors.firstName }"
                  placeholder="Juan"
                />
                <div v-if="form.firstName && !errors.firstName && isLoading === false" class="absolute inset-y-0 right-0 pr-3 flex items-center">
                  <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
              <Transition
                enter-active-class="transform ease-out duration-200"
                enter-from-class="opacity-0 -translate-y-1"
                enter-to-class="opacity-100 translate-y-0"
                leave-active-class="transition ease-in duration-150"
                leave-from-class="opacity-100"
                leave-to-class="opacity-0"
              >
                <p v-if="errors.firstName" class="mt-1.5 text-sm text-red-600 font-medium flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {{ errors.firstName }}
                </p>
              </Transition>
            </div>

            <div>
              <label for="lastName" class="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                Apellido *
              </label>
              <div class="relative">
                <input
                  id="lastName"
                  v-model="form.lastName"
                  type="text"
                  autocomplete="family-name"
                  required
                  :disabled="isLoading"
                  class="w-full pl-4 pr-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
                  :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/50': errors.lastName, 'border-green-300': form.lastName && !errors.lastName }"
                  placeholder="Pérez"
                />
                <div v-if="form.lastName && !errors.lastName && isLoading === false" class="absolute inset-y-0 right-0 pr-3 flex items-center">
                  <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
              <Transition
                enter-active-class="transform ease-out duration-200"
                enter-from-class="opacity-0 -translate-y-1"
                enter-to-class="opacity-100 translate-y-0"
                leave-active-class="transition ease-in duration-150"
                leave-from-class="opacity-100"
                leave-to-class="opacity-0"
              >
                <p v-if="errors.lastName" class="mt-1.5 text-sm text-red-600 font-medium flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {{ errors.lastName }}
                </p>
              </Transition>
            </div>
          </div>

          <!-- Email con ícono y validación visual -->
          <div>
            <label for="email" class="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              Email *
            </label>
            <div class="relative">
              <input
                id="email"
                v-model="form.email"
                type="email"
                autocomplete="email"
                required
                :disabled="isLoading"
                class="w-full pl-4 pr-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
                :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/50': errors.email, 'border-green-300': form.email && !errors.email }"
                placeholder="juan@ejemplo.com"
              />
              <div v-if="form.email && !errors.email && isLoading === false" class="absolute inset-y-0 right-0 pr-3 flex items-center">
                <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>
            <Transition
              enter-active-class="transform ease-out duration-200"
              enter-from-class="opacity-0 -translate-y-1"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition ease-in duration-150"
              leave-from-class="opacity-100"
              leave-to-class="opacity-0"
            >
              <p v-if="errors.email" class="mt-1.5 text-sm text-red-600 font-medium flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ errors.email }}
              </p>
            </Transition>
          </div>

          <!-- Teléfono con ícono -->
          <div>
            <label for="phoneNumber" class="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              Teléfono (opcional)
            </label>
            <div class="relative">
              <input
                id="phoneNumber"
                v-model="form.phoneNumber"
                type="tel"
                autocomplete="tel"
                :disabled="isLoading"
                class="w-full pl-4 pr-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
                :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/50': errors.phoneNumber, 'border-green-300': form.phoneNumber && !errors.phoneNumber }"
                placeholder="+57 300 123 4567"
              />
              <div v-if="form.phoneNumber && !errors.phoneNumber && isLoading === false" class="absolute inset-y-0 right-0 pr-3 flex items-center">
                <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>
            <Transition
              enter-active-class="transform ease-out duration-200"
              enter-from-class="opacity-0 -translate-y-1"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition ease-in duration-150"
              leave-from-class="opacity-100"
              leave-to-class="opacity-0"
            >
              <p v-if="errors.phoneNumber" class="mt-1.5 text-sm text-red-600 font-medium flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ errors.phoneNumber }}
              </p>
            </Transition>
          </div>

          <!-- Rol eliminado - todos los usuarios registrados son agricultores automáticamente -->

          <!-- Contraseña con mejor diseño -->
          <div>
            <label for="password" class="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              Contraseña *
            </label>
            <div class="relative">
              <input
                id="password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="new-password"
                required
                :disabled="isLoading"
                class="w-full pl-4 pr-12 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
                :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/50': errors.password, 'border-green-300': form.password && !errors.password }"
                placeholder="••••••••••••"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center hover:bg-gray-50 rounded-r-lg transition-all duration-200"
                :disabled="isLoading"
                :title="showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
              >
                <svg
                  v-if="showPassword"
                  class="h-5 w-5 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <svg
                  v-else
                  class="h-5 w-5 text-gray-400 hover:text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L12 12m-3.122-3.122l4.243 4.243M12 12l3 3m0 0l6-6" />
                </svg>
              </button>
            </div>
            <Transition
              enter-active-class="transform ease-out duration-200"
              enter-from-class="opacity-0 -translate-y-1"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition ease-in duration-150"
              leave-from-class="opacity-100"
              leave-to-class="opacity-0"
            >
              <p v-if="errors.password" class="mt-1.5 text-sm text-red-600 font-medium flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ errors.password }}
              </p>
            </Transition>
          </div>

          <div>
            <label for="confirmPassword" class="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Confirmar Contraseña *
            </label>
            <div class="relative">
              <input
                id="confirmPassword"
                v-model="form.confirmPassword"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="new-password"
                required
                :disabled="isLoading"
                class="w-full pl-4 pr-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200"
                :class="{ 'border-red-500 focus:border-red-500 focus:ring-red-500/50': errors.confirmPassword, 'border-green-300': form.confirmPassword && !errors.confirmPassword && form.password === form.confirmPassword }"
                placeholder="••••••••••••"
              />
              <div v-if="form.confirmPassword && !errors.confirmPassword && form.password === form.confirmPassword && isLoading === false" class="absolute inset-y-0 right-0 pr-3 flex items-center">
                <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>
            <Transition
              enter-active-class="transform ease-out duration-200"
              enter-from-class="opacity-0 -translate-y-1"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition ease-in duration-150"
              leave-from-class="opacity-100"
              leave-to-class="opacity-0"
            >
              <p v-if="errors.confirmPassword" class="mt-1.5 text-sm text-red-600 font-medium flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ errors.confirmPassword }}
              </p>
            </Transition>
          </div>

          <!-- Validador de contraseña mejorado -->
          <Transition
            enter-active-class="transform ease-out duration-300"
            enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100"
            leave-active-class="transition ease-in duration-200"
            leave-from-class="opacity-100"
            leave-to-class="opacity-0"
          >
            <div v-if="form.password" class="bg-gradient-to-br from-green-50 to-gray-50 border-2 border-green-200 rounded-xl p-5 transition-all duration-200 shadow-sm">
              <h4 class="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                </svg>
                Requisitos de la contraseña:
              </h4>
            <ul class="space-y-1">
              <li class="flex items-center text-sm" :class="passwordChecks.length ? 'text-green-600' : 'text-gray-500'">
                <svg class="mr-2 h-4 w-4" :class="passwordChecks.length ? 'text-green-500' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="passwordChecks.length ? 'M5 13l4 4L19 7' : 'M6 18L18 6M6 6l12 12'"></path>
                </svg>
                Al menos 8 caracteres
              </li>
              <li class="flex items-center text-sm" :class="passwordChecks.uppercase ? 'text-green-600' : 'text-gray-500'">
                <svg class="mr-2 h-4 w-4" :class="passwordChecks.uppercase ? 'text-green-500' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="passwordChecks.uppercase ? 'M5 13l4 4L19 7' : 'M6 18L18 6M6 6l12 12'"></path>
                </svg>
                Una letra mayúscula
              </li>
              <li class="flex items-center text-sm" :class="passwordChecks.lowercase ? 'text-green-600' : 'text-gray-500'">
                <svg class="mr-2 h-4 w-4" :class="passwordChecks.lowercase ? 'text-green-500' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="passwordChecks.lowercase ? 'M5 13l4 4L19 7' : 'M6 18L18 6M6 6l12 12'"></path>
                </svg>
                Una letra minúscula
              </li>
              <li class="flex items-center text-sm" :class="passwordChecks.number ? 'text-green-600' : 'text-gray-500'">
                <svg class="mr-2 h-4 w-4" :class="passwordChecks.number ? 'text-green-500' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="passwordChecks.number ? 'M5 13l4 4L19 7' : 'M6 18L18 6M6 6l12 12'"></path>
                </svg>
                Un número
              </li>
            </ul>
            </div>
          </Transition>

          <!-- Términos y condiciones con mejor diseño -->
          <div class="flex items-start group cursor-pointer">
            <input
              id="acceptTerms"
              v-model="form.acceptTerms"
              type="checkbox"
              required
              :disabled="isLoading"
              class="h-5 w-5 mt-0.5 text-green-600 focus:ring-green-500 border-gray-300 rounded cursor-pointer"
            />
            <label for="acceptTerms" class="ml-3 block text-sm text-gray-700 group-hover:text-gray-900 transition-colors">
              Acepto los 
              <a href="#" class="font-semibold text-green-600 hover:text-green-700 transition-colors">términos y condiciones</a> 
              y la 
              <a href="#" class="font-semibold text-green-600 hover:text-green-700 transition-colors">política de privacidad</a>
            </label>
          </div>
          
          <div class="flex items-start group cursor-pointer">
            <input
              id="emailNotifications"
              v-model="form.emailNotifications"
              type="checkbox"
              :disabled="isLoading"
              class="h-5 w-5 mt-0.5 text-green-600 focus:ring-green-500 border-gray-300 rounded cursor-pointer"
            />
            <label for="emailNotifications" class="ml-3 block text-sm text-gray-700 group-hover:text-gray-900 transition-colors">
              Quiero recibir notificaciones por email sobre mi cuenta
            </label>
          </div>

          <!-- Botón de envío mejorado con gradiente -->
          <div>
            <button
              type="submit"
              :disabled="isLoading || !isFormValid"
              class="w-full flex justify-center items-center gap-2 py-3.5 px-4 border border-transparent rounded-xl shadow-lg text-base font-semibold text-white bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 focus:outline-none focus:ring-4 focus:ring-green-500/50 disabled:opacity-60 disabled:cursor-not-allowed transition-all duration-200 hover:shadow-xl active:scale-[0.97] group"
            >
              <svg
                v-if="isLoading"
                class="animate-spin h-5 w-5 text-white"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else class="w-5 h-5 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
              </svg>
              <span>{{ isLoading ? 'Creando cuenta...' : 'Crear Cuenta' }}</span>
            </button>
            
            <!-- Mensaje de ayuda cuando el formulario no es válido -->
            <Transition
              enter-active-class="transform ease-out duration-200"
              enter-from-class="opacity-0 -translate-y-2"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition ease-in duration-150"
              leave-from-class="opacity-100"
              leave-to-class="opacity-0"
            >
              <div v-if="!isFormValid && !isLoading" class="mt-4 text-center">
                <div class="inline-flex items-center gap-2 px-4 py-2.5 bg-amber-50 border-2 border-amber-300 rounded-xl">
                  <svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
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
  emailNotifications: true
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
    isPasswordValid.value && // Usar validación completa de contraseña
    form.value.password === form.value.confirmPassword &&
    form.value.acceptTerms
  )
})

const statusMessageClass = computed(() => {
  return statusType.value === 'success' 
    ? 'bg-green-50 border border-green-200'
    : 'bg-red-50 border border-red-200'
})

// Validación simplificada para UX (validaciones críticas en backend)
const validateForm = () => {
  errors.value = {}
  
  // Validaciones básicas de UX
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
  
  // Validación básica de contraseña (detalles en backend)
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

// Manejar envío del formulario
const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  // Emitir evento de loading
  window.dispatchEvent(new CustomEvent('api-loading-start', {
    detail: { type: 'register', message: 'Creando tu cuenta...' }
  }))

  isLoading.value = true

  try {
    const result = await authStore.register({
      first_name: form.value.firstName.trim(),
      last_name: form.value.lastName.trim(),
      email: form.value.email.trim(),
      password: form.value.password,
      confirm_password: form.value.confirmPassword, // Este campo se mapea a password_confirm en authApi
      phone_number: form.value.phoneNumber.trim() || null,
      email_notifications: form.value.emailNotifications
    })

    if (result.success) {
      setStatusMessage('¡Registro exitoso! Bienvenido a CacaoScan 🌱', 'success')
      
      // Redirigir después de 2 segundos al dashboard de agricultor
      setTimeout(() => {
        router.push({ name: 'AgricultorDashboard' })
      }, 2000)
    } else {
      setStatusMessage(result.error || 'Error al crear la cuenta', 'error')
    }
  } catch (error) {
    console.error('Error en registro:', error)
    
    // Extraer mensaje de error más específico
    let errorMessage = 'Error inesperado. Intenta nuevamente.'
    if (error.response?.data) {
      // Intentar extraer mensaje del backend
      if (error.response.data.detail) {
        errorMessage = error.response.data.detail
      } else if (error.response.data.error) {
        errorMessage = error.response.data.error
      } else if (typeof error.response.data === 'string') {
        errorMessage = error.response.data
      } else if (error.response.data.non_field_errors) {
        errorMessage = error.response.data.non_field_errors[0]
      } else {
        // Mostrar los primeros errores de validación
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
    // Emitir evento de fin de loading
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
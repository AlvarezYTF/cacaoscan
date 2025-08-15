<template>
  <div class="max-w-md w-full mx-auto">
    <!-- Progress Indicator -->
    <div class="mb-8 text-center">
      <div class="flex justify-between items-center mb-2">
        <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium text-white"
             :class="{ 'bg-green-600': currentStep >= 1, 'bg-gray-300': currentStep < 1 }">
          1
        </div>
        <div class="flex-1 h-1 mx-2 bg-gray-200">
          <div class="h-full bg-green-600 transition-all duration-300 ease-in-out"
               :style="{ width: (currentStep / 2 * 100) + '%' }"></div>
        </div>
        <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium"
             :class="{ 'bg-green-600 text-white': currentStep === 2, 'bg-gray-200 text-gray-600': currentStep < 2 }">
          2
        </div>
      </div>
      <p class="text-sm text-gray-600">Paso {{ currentStep }} de 2</p>
    </div>

    <!-- Step 1: Personal Information -->
    <div v-if="currentStep === 1" class="space-y-4">
      <h2 class="text-2xl font-bold text-gray-900 text-center mb-6">Información Personal</h2>
      
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label for="firstName" class="block text-sm font-medium text-gray-700">Nombre</label>
          <input type="text" id="firstName" 
                 class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm p-2 border"
                 placeholder="Ingresa tu nombre">
        </div>
        
        <div>
          <label for="lastName" class="block text-sm font-medium text-gray-700">Apellido</label>
          <input type="text" id="lastName" 
                 class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm p-2 border"
                 placeholder="Ingresa tu apellido">
        </div>
      </div>
      
      <div>
        <label for="phone" class="block text-sm font-medium text-gray-700">Teléfono</label>
        <input type="tel" id="phone" 
               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm p-2 border"
               placeholder="Ingresa tu teléfono">
      </div>
      
      <div>
        <label for="birthDate" class="block text-sm font-medium text-gray-700">Fecha de Nacimiento</label>
        <input type="date" id="birthDate" 
               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm p-2 border">
      </div>
      
      <div class="flex justify-end pt-4">
        <button type="button" 
                @click="currentStep++"
                class="inline-flex justify-center rounded-md border border-transparent bg-green-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2">
          Siguiente
        </button>
      </div>
    </div>

    <!-- Step 2: Account Information -->
    <div v-else class="space-y-4">
      <h2 class="text-2xl font-bold text-gray-900 text-center mb-6">Crear Cuenta</h2>
      
      <div>
        <label for="email" class="block text-sm font-medium text-gray-700">Correo Electrónico</label>
        <div class="mt-1 relative rounded-md shadow-sm">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
              <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
            </svg>
          </div>
          <input type="email" id="email" 
                 class="focus:ring-green-500 focus:border-green-500 block w-full pl-10 sm:text-sm border-gray-300 rounded-md p-2 border"
                 placeholder="tucorreo@ejemplo.com">
        </div>
      </div>
      
      <div>
        <label for="password" class="block text-sm font-medium text-gray-700">Contraseña</label>
        <div class="mt-1 relative rounded-md shadow-sm">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
            </svg>
          </div>
          <input type="password" id="password" 
                 class="focus:ring-green-500 focus:border-green-500 block w-full pl-10 sm:text-sm border-gray-300 rounded-md p-2 border"
                 placeholder="••••••••">
        </div>
      </div>
      
      <div>
        <label for="confirmPassword" class="block text-sm font-medium text-gray-700">Confirmar Contraseña</label>
        <div class="mt-1 relative rounded-md shadow-sm">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
            </svg>
          </div>
          <input type="password" id="confirmPassword" 
                 class="focus:ring-green-500 focus:border-green-500 block w-full pl-10 sm:text-sm border-gray-300 rounded-md p-2 border"
                 placeholder="••••••••">
        </div>
      </div>
      
      <div class="flex justify-between pt-4">
        <button type="button" 
                @click="currentStep--"
                class="inline-flex justify-center rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2">
          Anterior
        </button>
        <button type="button" 
                class="inline-flex justify-center rounded-md border border-transparent bg-green-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2">
          Crear Cuenta
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RegisterForm',
  data() {
    return {
      currentStep: 1
    }
  }
}
</script>

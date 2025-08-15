<template>
  <div class="min-h-screen bg-gradient-to-b from-green-50 to-white flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <img src="#" alt="Logo CacaoScan" class="mx-auto h-16 w-auto">
        <h1 class="mt-6 text-3xl font-bold text-gray-900">Crear una cuenta</h1>
        <p class="mt-2 text-sm text-gray-600">
          ¿Ya tienes una cuenta? 
          <router-link to="/login" class="font-medium text-green-600 hover:text-green-500">
            Inicia sesión aquí
          </router-link>
        </p>
      </div>
      
      <div class="bg-white py-8 px-6 shadow rounded-lg sm:px-10">
        <RegisterForm />
      </div>
    </div>
  </div>
</template>

<script>
import RegisterForm from '@/components/auth/RegisterForm.vue';

export default {
  name: 'RegisterView',
  components: {
    RegisterForm
  }
}
</script>

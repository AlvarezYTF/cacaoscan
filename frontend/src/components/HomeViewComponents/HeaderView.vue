<template>
  <header class="bg-white shadow-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16 items-center">
        <div class="flex-shrink-0 flex items-center">
          <h1 class="text-2xl font-bold text-emerald-700">CacaoScan</h1>
        </div>
        <nav class="hidden md:ml-6 md:flex space-x-8">
          <a href="#" class="text-gray-900 hover:text-emerald-600 px-3 py-2 text-sm font-medium">Inicio</a>
          <a href="#features" class="text-gray-500 hover:text-emerald-600 px-3 py-2 text-sm font-medium">Funcionalidades</a>
          <a href="#about" class="text-gray-500 hover:text-emerald-600 px-3 py-2 text-sm font-medium">Sobre el sistema</a>
        </nav>
        <button class="md:hidden text-gray-500 hover:text-gray-900">
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
// No se necesita funcionalidad de navegación en el header superior
</script>

<template>
  <!-- Layout compartido para documentos legales con estructura común -->
  <section class="min-h-screen bg-gray-50 py-8 md:py-12 px-4">
    <div class="max-w-5xl mx-auto">
      <!-- Contenedor principal con diseño profesional -->
      <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 md:p-8 mb-8 transition-all duration-200 hover:shadow-xl">
        <!-- Encabezado común -->
        <div class="border-b border-gray-200 pb-6 mb-8">
          <slot name="header">
            <!-- Título y subtítulo se pasan como slot -->
          </slot>
        </div>

        <!-- Índice de navegación (slot opcional) -->
        <div v-if="$slots.index" class="mb-8">
          <slot name="index"></slot>
        </div>

        <!-- Contenido principal -->
        <div class="prose max-w-none text-gray-700 leading-relaxed">
          <slot name="content"></slot>
        </div>

        <!-- Acciones al final (slot opcional) -->
        <div v-if="$slots.actions" class="mt-8 pt-6 border-t border-gray-200">
          <slot name="actions"></slot>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
// Componente de layout compartido para documentos legales
// Proporciona estructura común: encabezado, índice, contenido y acciones
</script>

<style scoped>
/* Scroll suave para anclas */
html {
  scroll-behavior: smooth;
}

/* Estilos para el contenido legal */
.prose h2 {
  margin-top: 2rem;
  margin-bottom: 1rem;
  scroll-margin-top: 80px; /* Offset para anclas con header fijo */
}

.prose h3 {
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

.prose ul,
.prose ol {
  margin-left: 1.5rem;
  margin-top: 0.5rem;
  margin-bottom: 1rem;
}

.prose li {
  margin-bottom: 0.5rem;
}
</style>


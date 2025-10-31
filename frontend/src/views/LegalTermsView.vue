<template>
  <section class="max-w-4xl mx-auto py-10 px-6">
    <div v-if="loading" class="flex justify-center items-center min-h-screen">
      <div class="text-gray-600">Cargando términos y condiciones...</div>
    </div>
    
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6">
      <h2 class="text-xl font-bold text-red-800 mb-2">Error al cargar el contenido</h2>
      <p class="text-red-600">{{ error }}</p>
    </div>
    
    <div v-else>
      <h1 class="text-3xl font-bold text-green-700 mb-6">{{ title }}</h1>
      <div class="prose max-w-none">
        <p class="whitespace-pre-line text-gray-700 leading-relaxed">
          {{ content }}
        </p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const title = ref('')
const content = ref('')
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    const { data } = await api.get('/legal/terms/')
    title.value = data.title
    content.value = data.content
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Error al cargar los términos y condiciones'
    console.error('Error cargando términos:', err)
  } finally {
    loading.value = false
  }
})
</script>


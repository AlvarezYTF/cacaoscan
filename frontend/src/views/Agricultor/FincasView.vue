<template>
  <div class="space-y-4">
    <h1 class="text-xl font-semibold">Mis Fincas</h1>
    <ul class="space-y-2">
      <li v-for="f in fincas" :key="f.id" class="p-3 border rounded">
        <div class="font-medium">{{ f.nombre }}</div>
        <div class="text-sm text-gray-600">{{ f.departamento }} • {{ f.hectareas }} ha</div>
      </li>
    </ul>
  </div>
  </template>

<script setup>
import { ref, onMounted } from 'vue'
import { getFincasByAgricultor } from '@/services/fincasApi'
import { useAuthStore } from '@/stores/auth'

const fincas = ref([])
const auth = useAuthStore()

onMounted(async () => {
  const res = await getFincasByAgricultor(auth.user.id)
  const data = res.data
  fincas.value = Array.isArray(data?.results) ? data.results : (Array.isArray(data) ? data : [])
})
</script>



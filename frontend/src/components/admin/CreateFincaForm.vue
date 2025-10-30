<template>
  <form @submit.prevent="submitForm" class="space-y-4">
    <div>
      <label class="block text-sm font-medium">Nombre de la finca</label>
      <input v-model="form.nombre" class="input" required />
    </div>

    <div>
      <label class="block text-sm font-medium">Agricultor asignado</label>
      <select v-model="form.agricultor" class="input" required>
        <option value="">Selecciona un agricultor</option>
        <option v-for="a in agricultores" :key="a.id" :value="a.id">
          {{ a.username }}
        </option>
      </select>
    </div>

    <button type="submit" class="btn btn-primary bg-green-600 hover:bg-green-700 text-white">
      Crear Finca
    </button>
  </form>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { createFinca, getAgricultores } from '@/services/fincasApi'
import { useToast } from '@/composables/useToast'

const form = ref({ nombre: '', agricultor: '' })
const agricultores = ref([])
const toast = useToast()

onMounted(async () => {
  try {
    const res = await getAgricultores()
    // El endpoint devuelve axios response; tomamos los resultados (paginados o no)
    const data = res.data
    agricultores.value = Array.isArray(data?.results) ? data.results : (Array.isArray(data) ? data : data?.results || [])
  } catch (e) {
    toast.error('No se pudo cargar la lista de agricultores')
  }
})

const submitForm = async () => {
  try {
    await createFinca(form.value)
    toast.success('Finca creada correctamente')
    form.value = { nombre: '', agricultor: '' }
  } catch (error) {
    toast.error('Error al crear la finca')
  }
}
</script>



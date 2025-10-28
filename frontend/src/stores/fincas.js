import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createFinca, getFincas, updateFinca, deleteFinca, getFincaById } from '@/services/fincasApi'

export const useFincasStore = defineStore('fincas', () => {
  const fincas = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchFincas(params = {}) {
    loading.value = true
    error.value = null
    try {
      const data = await getFincas(params)
      fincas.value = Array.isArray(data) ? data : (data?.results ?? [])
    } catch (err) {
      const errorDetail = err?.response?.data?.detail || err?.response?.data?.message || err?.message || 'No se pudieron cargar las fincas'
      error.value = errorDetail
      console.error('Error fetching fincas:', err)
    } finally {
      loading.value = false
    }
  }

  async function create(payload) {
    loading.value = true
    error.value = null
    try {
      await createFinca(payload)
      // Refrescar la lista tras crear
      await fetchFincas()
      return true
    } catch (err) {
      const errorDetail = err?.response?.data?.detail || err?.response?.data?.message || err?.message || 'No se pudo crear la finca'
      error.value = errorDetail
      throw err
    } finally {
      loading.value = false
    }
  }

  async function update(fincaId, payload) {
    loading.value = true
    error.value = null
    try {
      await updateFinca(fincaId, payload)
      // Refrescar la lista tras actualizar
      await fetchFincas()
      return true
    } catch (err) {
      const errorDetail = err?.response?.data?.detail || err?.response?.data?.message || err?.message || 'No se pudo actualizar la finca'
      error.value = errorDetail
      throw err
    } finally {
      loading.value = false
    }
  }

  async function remove(fincaId) {
    loading.value = true
    error.value = null
    try {
      await deleteFinca(fincaId)
      // Refrescar la lista tras eliminar
      await fetchFincas()
      return true
    } catch (err) {
      const errorDetail = err?.response?.data?.detail || err?.response?.data?.message || err?.message || 'No se pudo eliminar la finca'
      error.value = errorDetail
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchById(fincaId) {
    try {
      return await getFincaById(fincaId)
    } catch (err) {
      console.error('Error fetching finca by id:', err)
      throw err
    }
  }

  function clearError() {
    error.value = null
  }

  return { 
    fincas, 
    loading, 
    error, 
    fetchFincas, 
    create, 
    update, 
    remove, 
    fetchById,
    clearError 
  }
})


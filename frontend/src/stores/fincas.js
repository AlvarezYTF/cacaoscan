import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createFinca, getFincas, updateFinca, deleteFinca, getFincaById, activateFinca } from '@/services/fincasApi'

export const useFincasStore = defineStore('fincas', () => {
  const fincas = ref([])
  const selected = ref(null)
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
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchById(fincaId) {
    loading.value = true
    error.value = null
    try {
      selected.value = await getFincaById(fincaId)
      return selected.value
    } catch (err) {
      const errorDetail = err?.response?.data?.detail || err?.response?.data?.message || err?.message || 'No se pudo cargar la finca'
      error.value = errorDetail
      throw err
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
      // Soft delete: desactivar la finca
      await deleteFinca(fincaId)
      // Refrescar la lista tras desactivar
      await fetchFincas()
      // Limpiar selected si era la finca desactivada
      if (selected.value?.id === fincaId) {
        selected.value = null
      }
      return true
    } catch (err) {
      const errorDetail = err?.response?.data?.detail || err?.response?.data?.message || err?.message || 'No se pudo desactivar la finca'
      error.value = errorDetail
      throw err
    } finally {
      loading.value = false
    }
  }

  async function activate(fincaId) {
    loading.value = true
    error.value = null
    try {
      await activateFinca(fincaId)
      // Refrescar la lista tras reactivar
      await fetchFincas()
      return true
    } catch (err) {
      const errorDetail = err?.response?.data?.detail || err?.response?.data?.message || err?.message || 'No se pudo reactivar la finca'
      error.value = errorDetail
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  function setSelected(finca) {
    selected.value = finca
  }

  function clearSelected() {
    selected.value = null
  }

  return { 
    fincas,
    selected,
    loading, 
    error, 
    fetchFincas, 
    fetchById,
    create, 
    update, 
    remove,
    activate, 
    clearError,
    setSelected,
    clearSelected
  }
})


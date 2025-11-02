/**
 * Composable para manejar catálogos (tipos de documento, géneros, departamentos, municipios)
 */
import { ref, onMounted } from 'vue'
import { catalogosApi } from '@/services'

export function useCatalogos() {
  const tiposDocumento = ref([])
  const generos = ref([])
  const departamentos = ref([])
  const municipios = ref([])
  const isLoadingCatalogos = ref(false)
  const error = ref(null)

  /**
   * Carga todos los catálogos básicos
   */
  const cargarCatalogos = async () => {
    isLoadingCatalogos.value = true
    error.value = null
    
    try {
      const [tiposDoc, gens, deptos] = await Promise.all([
        catalogosApi.getParametrosPorTema('TIPO_DOC'),
        catalogosApi.getParametrosPorTema('SEXO'),
        catalogosApi.getDepartamentos()
      ])
      
      tiposDocumento.value = tiposDoc || []
      generos.value = gens || []
      departamentos.value = deptos || []
    } catch (e) {
      console.error('Error cargando catálogos:', e)
      error.value = 'Error al cargar catálogos'
      // Valores por defecto
      tiposDocumento.value = []
      generos.value = []
      departamentos.value = []
    } finally {
      isLoadingCatalogos.value = false
    }
  }

  /**
   * Carga municipios por departamento
   * @param {number|string} departamentoId - ID o código del departamento
   */
  const cargarMunicipios = async (departamentoId) => {
    if (!departamentoId) {
      municipios.value = []
      return
    }

    try {
      // Si es un número, usar getMunicipiosByDepartamento (por ID)
      if (typeof departamentoId === 'number') {
        const response = await catalogosApi.getMunicipiosByDepartamento(departamentoId)
        municipios.value = response || []
        return
      }

      // Si es string (código), buscar el departamento primero
      if (typeof departamentoId === 'string') {
        const departamentoEncontrado = departamentos.value.find(
          d => d.codigo === departamentoId || d.codigo === String(departamentoId) || d.id === departamentoId
        )
        if (departamentoEncontrado) {
          // Usar ID del departamento
          const response = await catalogosApi.getMunicipiosByDepartamento(departamentoEncontrado.id)
          municipios.value = response || []
        } else {
          // Intentar usar como ID directamente
          const response = await catalogosApi.getMunicipiosByDepartamento(departamentoId)
          municipios.value = response || []
        }
      }
    } catch (e) {
      console.error('Error cargando municipios:', e)
      municipios.value = []
    }
  }

  /**
   * Limpia municipios (útil al cambiar departamento)
   */
  const limpiarMunicipios = () => {
    municipios.value = []
  }

  // Cargar catálogos básicos al montar
  onMounted(() => {
    cargarCatalogos()
  })

  return {
    tiposDocumento,
    generos,
    departamentos,
    municipios,
    isLoadingCatalogos,
    error,
    cargarCatalogos,
    cargarMunicipios,
    limpiarMunicipios
  }
}


/**
 * Ejemplo de uso de la función predictImage() para CacaoScan
 * 
 * Este archivo demuestra cómo usar la nueva función predictImage() implementada
 * en src/services/api.js para realizar predicciones de granos de cacao.
 */

import { predictImage, createPredictionFormData, validateImageFile } from '@/services/api.js'

// Ejemplo 1: Uso básico con validación
export async function ejemploBasico(fileInput) {
  try {
    // Obtener el archivo del input
    const file = fileInput.files[0]
    
    // Validar el archivo
    const validation = validateImageFile(file)
    if (!validation.isValid) {
      console.error('❌ Archivo inválido:', validation.errors)
      return
    }
    
    // Crear FormData
    const formData = createPredictionFormData(file)
    
    // Realizar predicción
    console.log('🚀 Iniciando predicción...')
    const resultado = await predictImage(formData)
    
    console.log('✅ Predicción exitosa:', resultado)
    
    // Mostrar resultados
    console.log(`📏 Altura: ${resultado.alto_mm} mm`)
    console.log(`📐 Ancho: ${resultado.ancho_mm} mm`)
    console.log(`📏 Grosor: ${resultado.grosor_mm} mm`)
    console.log(`⚖️ Peso: ${resultado.peso_g} g`)
    
    return resultado
    
  } catch (error) {
    console.error('❌ Error en predicción:', error.message)
    throw error
  }
}

// Ejemplo 2: Uso con metadatos adicionales
export async function ejemploConMetadatos(fileInput, metadatos) {
  try {
    const file = fileInput.files[0]
    
    // Validar archivo
    const validation = validateImageFile(file)
    if (!validation.isValid) {
      throw new Error(`Archivo inválido: ${validation.errors.join(', ')}`)
    }
    
    // Crear FormData con metadatos
    const formData = createPredictionFormData(file, {
      lote_id: metadatos.loteId,
      finca: metadatos.finca,
      region: metadatos.region,
      variedad: metadatos.variedad,
      fecha_cosecha: metadatos.fechaCosecha,
      notas: metadatos.notas
    })
    
    // Realizar predicción
    const resultado = await predictImage(formData)
    
    // Procesar resultado con información adicional
    const resultadoCompleto = {
      ...resultado,
      metadatos: metadatos,
      timestamp: new Date().toISOString(),
      densidad_estimada: resultado.peso_g / ((resultado.alto_mm * resultado.ancho_mm * resultado.grosor_mm) / 1000)
    }
    
    return resultadoCompleto
    
  } catch (error) {
    console.error('❌ Error en predicción con metadatos:', error.message)
    throw error
  }
}

// Ejemplo 3: Uso en un componente Vue
export const ejemploVueComponent = {
  template: `
    <div class="prediction-form">
      <input 
        type="file" 
        @change="handleFileSelect" 
        accept="image/*"
        ref="fileInput"
      />
      <button @click="processImage" :disabled="!selectedFile || isLoading">
        {{ isLoading ? 'Procesando...' : 'Analizar Imagen' }}
      </button>
      
      <div v-if="resultado" class="results">
        <h3>Resultados del Análisis</h3>
        <p>📏 Altura: {{ resultado.alto_mm }} mm</p>
        <p>📐 Ancho: {{ resultado.ancho_mm }} mm</p>
        <p>📏 Grosor: {{ resultado.grosor_mm }} mm</p>
        <p>⚖️ Peso: {{ resultado.peso_g }} g</p>
        
        <div v-if="resultado.confidences">
          <h4>Niveles de Confianza:</h4>
          <p>Altura: {{ (resultado.confidences.alto * 100).toFixed(1) }}%</p>
          <p>Ancho: {{ (resultado.confidences.ancho * 100).toFixed(1) }}%</p>
          <p>Grosor: {{ (resultado.confidences.grosor * 100).toFixed(1) }}%</p>
          <p>Peso: {{ (resultado.confidences.peso * 100).toFixed(1) }}%</p>
        </div>
        
        <div v-if="resultado.crop_url">
          <h4>Imagen Procesada:</h4>
          <img :src="resultado.crop_url" alt="Crop procesado" />
        </div>
      </div>
      
      <div v-if="error" class="error">
        ❌ Error: {{ error }}
      </div>
    </div>
  `,
  
  data() {
    return {
      selectedFile: null,
      isLoading: false,
      resultado: null,
      error: null
    }
  },
  
  methods: {
    handleFileSelect(event) {
      this.selectedFile = event.target.files[0]
      this.error = null
      this.resultado = null
    },
    
    async processImage() {
      if (!this.selectedFile) return
      
      try {
        this.isLoading = true
        this.error = null
        
        // Crear FormData
        const formData = createPredictionFormData(this.selectedFile, {
          lote_id: 'LOTE-' + Date.now(),
          notas: 'Análisis desde frontend Vue.js'
        })
        
        // Realizar predicción
        this.resultado = await predictImage(formData)
        
        console.log('✅ Predicción completada:', this.resultado)
        
      } catch (error) {
        this.error = error.message
        console.error('❌ Error:', error)
      } finally {
        this.isLoading = false
      }
    }
  }
}

// Ejemplo 4: Manejo de errores específicos
export async function ejemploManejoErrores(fileInput) {
  try {
    const file = fileInput.files[0]
    const formData = createPredictionFormData(file)
    
    const resultado = await predictImage(formData)
    return resultado
    
  } catch (error) {
    // Manejar diferentes tipos de errores
    if (error.status === 400) {
      console.error('❌ Error de validación:', error.message)
      // Mostrar mensaje al usuario sobre el formato de imagen
    } else if (error.status === 413) {
      console.error('❌ Archivo demasiado grande:', error.message)
      // Sugerir comprimir la imagen
    } else if (error.status === 500) {
      console.error('❌ Error del servidor:', error.message)
      // Sugerir reintentar más tarde
    } else if (error.status === 503) {
      console.error('❌ Servicio no disponible:', error.message)
      // El sistema está inicializando automáticamente
      console.log('🔄 El sistema está inicializando automáticamente. Intenta en unos minutos.')
    } else if (!error.status) {
      console.error('❌ Error de conexión:', error.message)
      // Verificar conexión a internet
    }
    
    throw error
  }
}

// Ejemplo 5: Uso con progress callback (usando createFormDataRequest existente)
export async function ejemploConProgress(fileInput, onProgress) {
  try {
    const file = fileInput.files[0]
    
    // Usar la función helper existente para manejo de progreso
    const { createFormDataRequest } = await import('@/services/api.js')
    
    const { formData, config } = createFormDataRequest({
      image: file
    }, onProgress)
    
    // Realizar predicción con progreso
    const response = await api.post('/api/predict/', formData, {
      ...config,
      timeout: 60000
    })
    
    return response.data
    
  } catch (error) {
    console.error('❌ Error en predicción con progreso:', error.message)
    throw error
  }
}

// Ejemplo 6: Función utilitaria para formatear resultados
export function formatearResultados(resultado) {
  return {
    dimensiones: {
      altura: `${resultado.alto_mm} mm`,
      ancho: `${resultado.ancho_mm} mm`,
      grosor: `${resultado.grosor_mm} mm`
    },
    peso: `${resultado.peso_g} g`,
    volumen_estimado: `${((resultado.alto_mm * resultado.ancho_mm * resultado.grosor_mm) / 1000).toFixed(2)} mm³`,
    densidad_estimada: `${(resultado.peso_g / ((resultado.alto_mm * resultado.ancho_mm * resultado.grosor_mm) / 1000)).toFixed(3)} g/mm³`,
    confianza_promedio: resultado.confidences ? 
      `${((Object.values(resultado.confidences).reduce((a, b) => a + b, 0) / Object.keys(resultado.confidences).length) * 100).toFixed(1)}%` : 
      'N/A'
  }
}

// Ejemplo de uso de formateo
export async function ejemploConFormateo(fileInput) {
  try {
    const file = fileInput.files[0]
    const formData = createPredictionFormData(file)
    
    const resultado = await predictImage(formData)
    const resultadoFormateado = formatearResultados(resultado)
    
    console.log('📊 Resultados formateados:', resultadoFormateado)
    
    return {
      raw: resultado,
      formatted: resultadoFormateado
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message)
    throw error
  }
}

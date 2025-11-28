import { defineStore } from 'pinia';
import { predictImage, predictImageYolo, predictImageSmart, getImageHistory, getPredictionStats } from '@/services/predictionApi.js';

export const usePredictionStore = defineStore('prediction', {
  state: () => ({
    // Estado de la predicción actual
    currentPrediction: null,
    
    // Estado de la imagen actual
    currentImage: null,
    
    // Estado de carga
    isLoading: false,
    
    // Errores
    error: null,
    uploadError: null,
    
    // Historial de predicciones
    predictions: [],
    
    // Estadísticas
    stats: {
      totalPredictions: 0,
      predictionsToday: 0,
      avgProcessingTime: 0,
      qualityDistribution: {},
      avgDimensions: {}
    },
    
    // Configuración de paginación para historial
    pagination: {
      currentPage: 1,
      totalPages: 1,
      totalItems: 0,
      itemsPerPage: 10
    },
    
    // Filtros para el historial
    filters: {
      processed: null,
      quality: '',
      batch: '',
      origin: '',
      dateFrom: '',
      dateTo: ''
    },
    
    // Estado de la última subida
    lastUpload: {
      fileName: '',
      fileSize: 0,
      uploadTime: null
    }
  }),

  getters: {
    // Verificar si hay una predicción actual
    hasPrediction: (state) => state.currentPrediction !== null,
    
    // Verificar si hay una imagen cargada
    hasImage: (state) => state.currentImage !== null,
    
    // Obtener el nivel de confianza de la predicción actual
    currentConfidenceLevel: (state) => {
      return state.currentPrediction?.confidence_level || 'unknown';
    },
    
    // Obtener el score de confianza como porcentaje
    currentConfidenceScore: (state) => {
      const score = state.currentPrediction?.confidence_score;
      return score ? Math.round(score * 100) : 0;
    },
    
    // Verificar si la predicción actual tiene alta confianza
    isHighConfidence: (state) => {
      const level = state.currentPrediction?.confidence_level;
      return level === 'very_high' || level === 'high';
    },
    
    // Obtener predicciones recientes (últimas 5)
    recentPredictions: (state) => {
      return state.predictions.slice(0, 5);
    },
    
    // Verificar si hay predicciones en el historial
    hasHistory: (state) => state.predictions.length > 0,
    
    // Obtener dimensiones formateadas de la predicción actual
    currentDimensions: (state) => {
      if (!state.currentPrediction) return null;
      
      const { width, height, thickness } = state.currentPrediction;
      return {
        width: Number.parseFloat(width).toFixed(2),
        height: Number.parseFloat(height).toFixed(2),
        thickness: Number.parseFloat(thickness).toFixed(2),
        formatted: `${Number.parseFloat(width).toFixed(2)} × ${Number.parseFloat(height).toFixed(2)} × ${Number.parseFloat(thickness).toFixed(2)} mm`
      };
    },
    
    // Obtener peso formateado de la predicción actual
    currentWeight: (state) => {
      if (!state.currentPrediction) return null;
      
      const weight = state.currentPrediction.predicted_weight;
      return {
        value: Number.parseFloat(weight).toFixed(3),
        formatted: `${Number.parseFloat(weight).toFixed(3)} g`
      };
    },
    
    // Verificar si hay filtros activos en el historial
    hasActiveFilters: (state) => {
      return Object.values(state.filters).some(value => 
        value !== null && value !== '' && value !== undefined
      );
    },
    
    // Calcular estadísticas rápidas
    quickStats: (state) => {
      const predictions = state.predictions;
      if (predictions.length === 0) {
        return {
          total: 0,
          avgWeight: 0,
          avgConfidence: 0,
          highConfidenceCount: 0
        };
      }
      
      const avgWeight = predictions.reduce((sum, p) => sum + (p.predicted_weight || 0), 0) / predictions.length;
      const avgConfidence = predictions.reduce((sum, p) => sum + (p.confidence_score || 0), 0) / predictions.length;
      const highConfidenceCount = predictions.filter(p => 
        p.confidence_level === 'very_high' || p.confidence_level === 'high'
      ).length;
      
      return {
        total: predictions.length,
        avgWeight: Number.parseFloat(avgWeight).toFixed(3),
        avgConfidence: Math.round(avgConfidence * 100),
        highConfidenceCount
      };
    }
  },

  actions: {
    // Realizar una nueva predicción
    async makePrediction(formData) {
      this.isLoading = true;
      this.error = null;
      this.uploadError = null;
      
      try {
        // Obtener información de la imagen del FormData
        const imageFile = formData.get('image');
        if (imageFile) {
          this.lastUpload = {
            fileName: imageFile.name,
            fileSize: imageFile.size,
            uploadTime: new Date().toISOString()
          };
          this.currentImage = imageFile;
        }
        
        // Realizar la predicción
        const result = await predictImage(formData);
        
        // Actualizar el estado con el resultado
        this.currentPrediction = result;
        
        // Agregar al historial (al principio)
        this.predictions.unshift(result);
        
        // Mantener solo los últimos 50 en memoria
        if (this.predictions.length > 50) {
          this.predictions = this.predictions.slice(0, 50);
        }
        
        // Actualizar estadísticas
        this.stats.totalPredictions = this.predictions.length;
        this.updateTodayStats();
        
        return result;
        
      } catch (error) {
        this.error = error.message || 'Error al realizar la predicción';
        this.uploadError = error.message;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
    
    // Realizar predicción con YOLOv8
    async makePredictionYolo(formData) {
      this.isLoading = true;
      this.error = null;
      this.uploadError = null;
      
      try {
        // Obtener información de la imagen del FormData
        const imageFile = formData.get('image');
        if (imageFile) {
          this.lastUpload = {
            fileName: imageFile.name,
            fileSize: imageFile.size,
            uploadTime: new Date().toISOString()
          };
          this.currentImage = imageFile;
        }
        
        // Realizar la predicción YOLOv8
        const result = await predictImageYolo(formData);
        
        if (result.success) {
          // Actualizar el estado con el resultado
          this.currentPrediction = result.data;
          
          // Agregar al historial (al principio)
          this.predictions.unshift(result.data);
          
          // Mantener solo los últimos 50 en memoria
          if (this.predictions.length > 50) {
            this.predictions = this.predictions.slice(0, 50);
          }
          
          // Actualizar estadísticas
          this.stats.totalPredictions = this.predictions.length;
          this.updateTodayStats();
          
          return result.data;
        } else {
          throw new Error(result.error);
        }
        
      } catch (error) {
        this.error = error.message || 'Error al realizar la predicción YOLOv8';
        this.uploadError = error.message;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
    
    // Realizar predicción con recorte inteligente
    async makePredictionSmart(formData, options = {}) {
      this.isLoading = true;
      this.error = null;
      this.uploadError = null;
      
      try {
        // Obtener información de la imagen del FormData
        const imageFile = formData.get('image');
        if (imageFile) {
          this.lastUpload = {
            fileName: imageFile.name,
            fileSize: imageFile.size,
            uploadTime: new Date().toISOString()
          };
          this.currentImage = imageFile;
        }
        
        // Realizar la predicción con recorte inteligente
        const result = await predictImageSmart(formData, options);
        
        if (result.success) {
          // Actualizar el estado con el resultado
          this.currentPrediction = result.data;
          
          // Agregar al historial (al principio)
          this.predictions.unshift(result.data);
          
          // Mantener solo los últimos 50 en memoria
          if (this.predictions.length > 50) {
            this.predictions = this.predictions.slice(0, 50);
          }
          
          // Actualizar estadísticas
          this.stats.totalPredictions = this.predictions.length;
          this.updateTodayStats();
          
          return result.data;
        } else {
          throw new Error(result.error);
        }
        
      } catch (error) {
        this.error = error.message || 'Error al realizar la predicción con recorte inteligente';
        this.uploadError = error.message;
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
    
    // Actualizar los resultados de predicción
    updateResults(predictionData) {
      this.currentPrediction = predictionData;
      this.error = null;
      
      // Agregar al historial si no existe
      const existingIndex = this.predictions.findIndex(p => p.id === predictionData.id);
      if (existingIndex === -1) {
        this.predictions.unshift(predictionData);
      } else {
        this.predictions[existingIndex] = predictionData;
      }
    },
    
    // Limpiar la predicción actual
    clearCurrentPrediction() {
      this.currentPrediction = null;
      this.currentImage = null;
      this.error = null;
      this.uploadError = null;
    },
    
    // Seleccionar una predicción del historial
    selectPrediction(predictionId) {
      const prediction = this.predictions.find(p => p.id === predictionId);
      if (prediction) {
        this.currentPrediction = prediction;
        this.error = null;
      }
    },
    
    // Cargar historial de predicciones
    async loadHistory(page = 1, filters = {}) {
      try {
        const params = {
          page,
          page_size: this.pagination.itemsPerPage,
          ...filters
        };
        
        // Filtrar parámetros vacíos
        Object.keys(params).forEach(key => {
          if (params[key] === '' || params[key] === null || params[key] === undefined) {
            delete params[key];
          }
        });
        
        const response = await getImageHistory(params);
        
        if (response.results) {
          // Si es la primera página, reemplazar. Si no, agregar
          if (page === 1) {
            this.predictions = response.results;
          } else {
            this.predictions = [...this.predictions, ...response.results];
          }
          
          // Actualizar paginación
          this.pagination = {
            currentPage: page,
            totalPages: Math.ceil(response.count / this.pagination.itemsPerPage),
            totalItems: response.count,
            itemsPerPage: this.pagination.itemsPerPage
          };
        }
        
        return response;
        
      } catch (error) {
        console.warn('Error cargando historial:', error.message);
        // No lanzar error para que no afecte la UX
        return { results: [], count: 0 };
      }
    },
    
    // Cargar estadísticas
    async loadStats() {
      try {
        const stats = await getPredictionStats();
        this.stats = { ...this.stats, ...stats };
        return stats;
      } catch (error) {
        console.warn('Error cargando estadísticas:', error.message);
        return this.stats;
      }
    },
    
    // Actualizar filtros
    updateFilters(newFilters) {
      this.filters = { ...this.filters, ...newFilters };
    },
    
    // Limpiar filtros
    clearFilters() {
      this.filters = {
        processed: null,
        quality: '',
        batch: '',
        origin: '',
        dateFrom: '',
        dateTo: ''
      };
    },
    
    // Reiniciar todo el estado
    resetState() {
      this.currentPrediction = null;
      this.currentImage = null;
      this.isLoading = false;
      this.error = null;
      this.uploadError = null;
      this.predictions = [];
      this.clearFilters();
      this.pagination.currentPage = 1;
    },
    
    // Eliminar una predicción del historial
    removePrediction(predictionId) {
      const index = this.predictions.findIndex(p => p.id === predictionId);
      if (index !== -1) {
        this.predictions.splice(index, 1);
        
        // Si era la predicción actual, limpiarla
        if (this.currentPrediction && this.currentPrediction.id === predictionId) {
          this.currentPrediction = null;
        }
        
        // Actualizar estadísticas
        this.stats.totalPredictions = this.predictions.length;
      }
    },
    
    // Marcar una predicción como favorita (si se implementa en el futuro)
    toggleFavorite(predictionId) {
      const prediction = this.predictions.find(p => p.id === predictionId);
      if (prediction) {
        prediction.isFavorite = !prediction.isFavorite;
      }
    },
    
    // Exportar datos de predicción
    exportPrediction(predictionId = null) {
      const prediction = predictionId 
        ? this.predictions.find(p => p.id === predictionId)
        : this.currentPrediction;
      
      if (!prediction) return null;
      
      const exportData = {
        id: prediction.id,
        fecha: prediction.created_at,
        dimensiones: {
          ancho: `${Number.parseFloat(prediction.width).toFixed(2)} mm`,
          alto: `${Number.parseFloat(prediction.height).toFixed(2)} mm`,
          grosor: `${Number.parseFloat(prediction.thickness).toFixed(2)} mm`
        },
        peso_predicho: `${Number.parseFloat(prediction.predicted_weight).toFixed(3)} g`,
        confianza: {
          nivel: prediction.confidence_level,
          score: prediction.confidence_score ? `${Math.round(prediction.confidence_score * 100)}%` : 'N/A'
        },
        metodo: prediction.prediction_method,
        tiempo_procesamiento: prediction.processing_time ? `${prediction.processing_time}s` : 'N/A',
        metricas_derivadas: prediction.derived_metrics,
        comparacion_pesos: prediction.weight_comparison
      };
      
      return exportData;
    },
    
    // Actualizar estadísticas del día actual
    updateTodayStats() {
      const today = new Date().toDateString();
      const todayPredictions = this.predictions.filter(p => {
        const predictionDate = new Date(p.created_at).toDateString();
        return predictionDate === today;
      });
      
      this.stats.predictionsToday = todayPredictions.length;
      
      // Calcular tiempo promedio de procesamiento
      const validTimes = this.predictions
        .map(p => p.processing_time)
        .filter(time => time && !Number.isNaN(time));
      
      if (validTimes.length > 0) {
        this.stats.avgProcessingTime = validTimes.reduce((sum, time) => sum + time, 0) / validTimes.length;
      }
    },
    
    // Manejar errores
    setError(error) {
      this.error = typeof error === 'string' ? error : error.message;
    },
    
    // Limpiar errores
    clearError() {
      this.error = null;
      this.uploadError = null;
    },
    
    // Inicializar el store (cargar datos previos si existen)
    async initialize() {
      // Cargar historial reciente
      await this.loadHistory(1);
      
      // Cargar estadísticas
      await this.loadStats();
      
      // Actualizar estadísticas del día
      this.updateTodayStats();
    }
  }
});

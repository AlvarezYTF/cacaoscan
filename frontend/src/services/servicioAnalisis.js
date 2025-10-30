// Reexportar el servicio de predicción como servicio de análisis para compatibilidad
export * from './predictionApi'
import predictionApi from './predictionApi'
export default predictionApi

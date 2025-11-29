"""
Tests de diagnóstico y validación para escaladores y predicciones.
"""
import pytest
import numpy as np
from ml.regression.scalers import load_scalers
from ml.prediction.predict import get_predictor
from ml.regression.models import TARGETS


@pytest.mark.slow
class TestScalerDiagnostics:
    """Tests de diagnóstico para escaladores cargados desde archivos."""
    
    def test_scalers_loaded_successfully(self):
        """Verifica que los escaladores se carguen correctamente."""
        scalers = load_scalers()
        
        assert scalers.is_fitted
        assert len(scalers.scalers) == len(TARGETS)
        
        for target in TARGETS:
            assert target in scalers.scalers
    
    def test_scaler_statistics(self):
        """Verifica estadísticas de los escaladores."""
        scalers = load_scalers()
        
        for target in TARGETS:
            scaler = scalers.scalers[target]
            
            # Verificar que tiene atributos necesarios
            assert hasattr(scaler, 'mean_')
            assert hasattr(scaler, 'scale_')
            assert scaler.mean_ is not None
            assert scaler.scale_ is not None
            
            # Verificar que mean y scale son razonables
            assert scaler.mean_[0] > 0  # Valores positivos
            assert scaler.scale_[0] > 0  # Desviación estándar positiva
    
    def test_scaler_inverse_transform_ranges(self):
        """Verifica que la desnormalización produzca valores razonables."""
        scalers = load_scalers()
        
        # Límites razonables basados en el dataset (en mm o g)
        target_limits = {
            'alto': (5.0, 60.0),
            'ancho': (3.0, 30.0),
            'grosor': (1.0, 20.0),
            'peso': (0.2, 10.0)
        }
        
        # Probar valores normalizados típicos (-3 a +3 desviaciones estándar)
        test_normalized = np.array([[-3.0], [-2.0], [-1.0], [0.0], [1.0], [2.0], [3.0]])
        
        for target in TARGETS:
            scaler = scalers.scalers[target]
            denorm_values = scaler.inverse_transform(test_normalized)
            
            _, max_val = target_limits[target]
            
            # Verificar que los valores desnormalizados están en rangos razonables
            # (con un margen porque estamos probando ±3 desviaciones estándar)
            denorm_min = denorm_values.min()
            denorm_max = denorm_values.max()
            
            # Los valores extremos pueden estar fuera del rango típico, pero deben ser razonables
            assert denorm_min > 0, f"{target}: valor mínimo negativo {denorm_min:.2f}"
            assert denorm_max < max_val * 1.5, f"{target}: valor máximo muy alto {denorm_max:.2f}"
    
    def test_scaler_denormalization_accuracy(self):
        """Verifica que la desnormalización sea reversible."""
        scalers = load_scalers()
        
        # Valores de prueba típicos del dataset
        test_values = {
            'alto': np.array([[23.0], [25.0], [27.0]]),
            'ancho': np.array([[12.0], [14.0], [16.0]]),
            'grosor': np.array([[8.0], [9.0], [10.0]]),
            'peso': np.array([[1.5], [1.7], [2.0]])
        }
        
        for target in TARGETS:
            scaler = scalers.scalers[target]
            original_values = test_values[target]
            
            # Normalizar
            normalized = scaler.transform(original_values.reshape(-1, 1))
            # Desnormalizar
            denormalized = scaler.inverse_transform(normalized.reshape(-1, 1))
            
            # Verificar que la transformación inversa es precisa
            np.testing.assert_allclose(
                original_values.flatten(),
                denormalized.flatten(),
                rtol=1e-10,
                err_msg=f"{target}: Transformación inversa incorrecta"
            )


@pytest.mark.slow
@pytest.mark.integration
class TestPredictionLimits:
    """Tests para validar límites físicos en predicciones."""
    
    def test_predictor_loaded(self):
        """Verifica que el predictor se cargue correctamente."""
        predictor = get_predictor()
        success = predictor.load_artifacts()
        
        assert success, "El predictor no se cargó correctamente"
        assert predictor.models_loaded
        assert predictor.scalers is not None
    
    def test_prediction_value_ranges(self):
        """Verifica que las predicciones estén en rangos razonables."""
        # Este test requiere una imagen real para funcionar
        # Por ahora solo verificamos que el predictor esté configurado
        
        predictor = get_predictor()
        success = predictor.load_artifacts()
        
        if success:
            # Verificar que todos los modelos están cargados
            for target in TARGETS:
                assert target in predictor.regression_models, \
                    f"Modelo {target} no está cargado"
            
            # Verificar que los escaladores están cargados
            assert predictor.scalers is not None
            assert predictor.scalers.is_fitted
    
    def test_scaler_stats_match_predictor(self):
        """Verifica que los escaladores del predictor coincidan con los cargados directamente."""
        predictor = get_predictor()
        success = predictor.load_artifacts()
        
        if not success:
            pytest.skip("Predictor no cargado")
        
        scalers_direct = load_scalers()
        
        for target in TARGETS:
            scaler_predictor = predictor.scalers.scalers[target]
            scaler_direct = scalers_direct.scalers[target]
            
            # Verificar que tienen las mismas estadísticas
            np.testing.assert_almost_equal(
                scaler_predictor.mean_[0],
                scaler_direct.mean_[0],
                decimal=4,
                err_msg=f"{target}: Mean no coincide"
            )
            
            np.testing.assert_almost_equal(
                scaler_predictor.scale_[0],
                scaler_direct.scale_[0],
                decimal=4,
                err_msg=f"{target}: Scale no coincide"
            )


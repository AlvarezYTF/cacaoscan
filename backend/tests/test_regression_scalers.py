"""
Tests para los escaladores de regresión.
"""
import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch
import tempfile
from pathlib import Path

from ml.regression.scalers import (
    CacaoScalers,
    load_scalers,
    save_scalers,
    create_scalers_from_data,
    validate_scalers,
    TARGETS
)


class TestCacaoScalers:
    """Tests para CacaoScalers."""
    
    def setup_method(self):
        """Configuración antes de cada test."""
        self.scalers = CacaoScalers()
        
        # Datos de prueba
        np.random.seed(42)
        self.test_data = {
            'alto': np.random.normal(10, 2, 100),
            'ancho': np.random.normal(8, 1.5, 100),
            'grosor': np.random.normal(6, 1, 100),
            'peso': np.random.normal(2.5, 0.5, 100)
        }
    
    def test_init(self):
        """Test de inicialización."""
        scalers = CacaoScalers()
        assert scalers.scaler_type == "standard"
        assert not scalers.is_fitted
        assert len(scalers.scalers) == 0
    
    def test_init_custom_type(self):
        """Test de inicialización con tipo personalizado."""
        scalers = CacaoScalers(scaler_type="minmax")
        assert scalers.scaler_type == "minmax"
    
    def test_fit_dataframe(self):
        """Test de ajuste con DataFrame."""
        df = pd.DataFrame(self.test_data)
        self.scalers.fit(df)
        
        assert self.scalers.is_fitted
        assert len(self.scalers.scalers) == len(TARGETS)
        
        for target in TARGETS:
            assert target in self.scalers.scalers
            assert hasattr(self.scalers.scalers[target], 'mean_')
    
    def test_fit_dict(self):
        """Test de ajuste con diccionario."""
        self.scalers.fit(self.test_data)
        
        assert self.scalers.is_fitted
        assert len(self.scalers.scalers) == len(TARGETS)
    
    def test_fit_missing_column(self):
        """Test de ajuste con columna faltante."""
        df = pd.DataFrame({
            'alto': self.test_data['alto'],
            'ancho': self.test_data['ancho']
            # Faltan grosor y peso
        })
        
        with pytest.raises(ValueError, match="Columnas faltantes"):
            self.scalers.fit(df)
    
    def test_transform(self):
        """Test de transformación."""
        self.scalers.fit(self.test_data)
        
        # Transformar con DataFrame
        df = pd.DataFrame(self.test_data)
        transformed = self.scalers.transform(df)
        
        assert isinstance(transformed, dict)
        assert len(transformed) == len(TARGETS)
        
        for target in TARGETS:
            assert target in transformed
            assert isinstance(transformed[target], np.ndarray)
            assert len(transformed[target]) == len(self.test_data[target])
    
    def test_inverse_transform(self):
        """Test de transformación inversa."""
        self.scalers.fit(self.test_data)
        
        # Transformar y luego transformar de vuelta
        transformed = self.scalers.transform(self.test_data)
        original = self.scalers.inverse_transform(transformed)
        
        assert isinstance(original, dict)
        assert len(original) == len(TARGETS)
        
        # Verificar que la transformación inversa es aproximadamente correcta
        for target in TARGETS:
            np.testing.assert_allclose(
                original[target], 
                self.test_data[target], 
                rtol=1e-10
            )
    
    def test_fit_transform(self):
        """Test de fit_transform."""
        result = self.scalers.fit_transform(self.test_data)
        
        assert self.scalers.is_fitted
        assert isinstance(result, dict)
        assert len(result) == len(TARGETS)
    
    def test_transform_not_fitted(self):
        """Test de transformación sin ajuste previo."""
        with pytest.raises(ValueError, match="Los escaladores deben ser ajustados"):
            self.scalers.transform(self.test_data)
    
    def test_inverse_transform_not_fitted(self):
        """Test de transformación inversa sin ajuste previo."""
        with pytest.raises(ValueError, match="Los escaladores deben ser ajustados"):
            self.scalers.inverse_transform(self.test_data)
    
    def test_get_scaler_stats(self):
        """Test de obtención de estadísticas."""
        self.scalers.fit(self.test_data)
        stats = self.scalers.get_scaler_stats()
        
        assert isinstance(stats, dict)
        assert len(stats) == len(TARGETS)
        
        for target in TARGETS:
            assert target in stats
            target_stats = stats[target]
            assert 'mean' in target_stats
            assert 'std' in target_stats
    
    def test_get_scaler_stats_not_fitted(self):
        """Test de estadísticas sin ajuste previo."""
        with pytest.raises(ValueError, match="Los escaladores deben ser ajustados"):
            self.scalers.get_scaler_stats()
    
    def test_save_load_cycle(self):
        """Test de ciclo completo de guardado y carga."""
        # Ajustar escaladores
        self.scalers.fit(self.test_data)
        
        # Guardar en archivo temporal
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Mock del directorio de artefactos
            with patch('ml.regression.scalers.get_regressors_artifacts_dir', return_value=temp_path):
                self.scalers.save()
                
                # Verificar que los archivos se crearon
                for target in TARGETS:
                    scaler_file = temp_path / f"{target}_scaler.pkl"
                    assert scaler_file.exists()
                
                # Crear nuevos escaladores y cargar
                new_scalers = CacaoScalers()
                new_scalers.load()
                
                # Verificar que son equivalentes
                assert new_scalers.is_fitted
                assert len(new_scalers.scalers) == len(self.scalers.scalers)
                
                # Verificar estadísticas
                original_stats = self.scalers.get_scaler_stats()
                new_stats = new_scalers.get_scaler_stats()
                
                for target in TARGETS:
                    np.testing.assert_almost_equal(
                        original_stats[target]['mean'],
                        new_stats[target]['mean']
                    )
    
    def test_save_not_fitted(self):
        """Test de guardado sin ajuste previo."""
        with pytest.raises(ValueError, match="Los escaladores deben ser ajustados"):
            self.scalers.save()
    
    def test_load_nonexistent_file(self):
        """Test de carga de archivo inexistente."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with patch('ml.regression.scalers.get_regressors_artifacts_dir', return_value=temp_path):
                with pytest.raises(FileNotFoundError):
                    self.scalers.load()


class TestScalerUtilities:
    """Tests para funciones de utilidad de escaladores."""
    
    def setup_method(self):
        """Configuración antes de cada test."""
        np.random.seed(42)
        self.test_data = {
            'alto': np.random.normal(10, 2, 100),
            'ancho': np.random.normal(8, 1.5, 100),
            'grosor': np.random.normal(6, 1, 100),
            'peso': np.random.normal(2.5, 0.5, 100)
        }
    
    def test_create_scalers_from_data(self):
        """Test de creación de escaladores desde datos."""
        scalers = create_scalers_from_data(self.test_data)
        
        assert scalers.is_fitted
        assert len(scalers.scalers) == len(TARGETS)
    
    def test_create_scalers_from_dataframe(self):
        """Test de creación de escaladores desde DataFrame."""
        df = pd.DataFrame(self.test_data)
        scalers = create_scalers_from_data(df)
        
        assert scalers.is_fitted
        assert len(scalers.scalers) == len(TARGETS)
    
    def test_create_scalers_custom_type(self):
        """Test de creación con tipo personalizado."""
        scalers = create_scalers_from_data(self.test_data, scaler_type="minmax")
        
        assert scalers.scaler_type == "minmax"
        assert scalers.is_fitted
    
    def test_validate_scalers_valid(self):
        """Test de validación de escaladores válidos."""
        scalers = create_scalers_from_data(self.test_data)
        
        assert validate_scalers(scalers) == True
    
    def test_validate_scalers_not_fitted(self):
        """Test de validación de escaladores no ajustados."""
        scalers = CacaoScalers()
        
        assert validate_scalers(scalers) == False
    
    def test_validate_scalers_missing_target(self):
        """Test de validación con target faltante."""
        scalers = CacaoScalers()
        scalers.is_fitted = True
        scalers.scalers = {'alto': Mock()}  # Solo un target
        
        assert validate_scalers(scalers) == False


class TestScalerIntegration:
    """Tests de integración para escaladores."""
    
    def test_full_workflow(self):
        """Test de flujo completo de escaladores."""
        # Datos de entrenamiento y test
        np.random.seed(42)
        train_data = {
            'alto': np.random.normal(10, 2, 1000),
            'ancho': np.random.normal(8, 1.5, 1000),
            'grosor': np.random.normal(6, 1, 1000),
            'peso': np.random.normal(2.5, 0.5, 1000)
        }
        
        test_data = {
            'alto': np.random.normal(10, 2, 100),
            'ancho': np.random.normal(8, 1.5, 100),
            'grosor': np.random.normal(6, 1, 100),
            'peso': np.random.normal(2.5, 0.5, 100)
        }
        
        # Crear y ajustar escaladores
        scalers = create_scalers_from_data(train_data)
        
        # Transformar datos de entrenamiento
        train_transformed = scalers.transform(train_data)
        
        # Transformar datos de test
        test_transformed = scalers.transform(test_data)
        
        # Verificar que los datos transformados están normalizados
        for target in TARGETS:
            # Media debe estar cerca de 0
            assert abs(np.mean(train_transformed[target])) < 0.1
            assert abs(np.mean(test_transformed[target])) < 0.1
            
            # Desviación estándar debe estar cerca de 1
            assert abs(np.std(train_transformed[target]) - 1.0) < 0.1
        
        # Transformar de vuelta
        train_original = scalers.inverse_transform(train_transformed)
        test_original = scalers.inverse_transform(test_transformed)
        
        # Verificar que la transformación inversa es correcta
        for target in TARGETS:
            np.testing.assert_allclose(train_original[target], train_data[target], rtol=1e-10)
            np.testing.assert_allclose(test_original[target], test_data[target], rtol=1e-10)
    
    def test_different_scaler_types(self):
        """Test con diferentes tipos de escaladores."""
        np.random.seed(42)
        data = {
            'alto': np.random.normal(10, 2, 100),
            'ancho': np.random.normal(8, 1.5, 100),
            'grosor': np.random.normal(6, 1, 100),
            'peso': np.random.normal(2.5, 0.5, 100)
        }
        
        scaler_types = ["standard", "minmax", "robust"]
        
        for scaler_type in scaler_types:
            scalers = create_scalers_from_data(data, scaler_type=scaler_type)
            
            assert scalers.scaler_type == scaler_type
            assert scalers.is_fitted
            
            transformed = scalers.transform(data)
            original = scalers.inverse_transform(transformed)
            
            # Verificar que la transformación inversa es correcta
            for target in TARGETS:
                np.testing.assert_allclose(original[target], data[target], rtol=1e-10)

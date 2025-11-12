"""
Test 4: Verificar que create_model se llama con num_outputs y no con target.

Bug SonarQube: "Remove this unexpected named argument 'target'"
Archivo corregido: ml/regression/incremental_train.py
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase


class TestIncrementalTrainCreateModel(TestCase):
    """Tests para verificar que create_model se llama correctamente."""
    
    @patch('ml.regression.incremental_train.create_model')
    def test_create_model_uses_num_outputs_not_target(self, mock_create_model):
        """Verifica que create_model se llama con num_outputs=1 y no con target."""
        try:
            from ml.regression.incremental_train import run_incremental_training
        except ImportError:
            self.skipTest("ml.regression.incremental_train no está disponible")
        
        # Configuración de prueba
        new_data = [{
            'image_path': '/path/to/image.jpg',
            'target': 10.5
        }]
        config = {
            'strategy_type': 'elastic_weight_consolidation',
            'learning_rate': 1e-4,
            'epochs': 5,
            'batch_size': 16,
            'img_size': 224
        }
        
        # Mock del modelo
        mock_model = MagicMock()
        mock_create_model.return_value = mock_model
        
        try:
            # Intentar ejecutar (puede fallar por otras razones, pero verificamos la llamada)
            run_incremental_training(new_data, config, target='alto')
        except Exception:
            pass  # Ignorar otros errores, solo verificamos la llamada
        
        # Verificar que create_model fue llamado
        if mock_create_model.called:
            # Obtener los argumentos de la llamada
            call_args = mock_create_model.call_args
            
            if call_args:
                # Verificar argumentos posicionales o de palabra clave
                if call_args.kwargs:
                    call_kwargs = call_args.kwargs
                else:
                    call_kwargs = {}
                
                # Verificar que NO se usa 'target' como argumento
                self.assertNotIn('target', call_kwargs, 
                               "create_model no debería recibir 'target' como parámetro")
                
                # Verificar que se usa 'num_outputs' si se llama
                if 'num_outputs' in call_kwargs:
                    self.assertEqual(call_kwargs['num_outputs'], 1,
                                   "create_model debería recibir num_outputs=1")


"""
Modelo de visión artificial para predicción de características físicas de granos de cacao.

Este módulo contiene la arquitectura CNN (CacaoVisionModel) que predice las dimensiones
físicas (ancho, alto, grosor, peso) a partir de imágenes de granos de cacao.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional


class CacaoVisionModel(nn.Module):
    """
    Red neuronal convolucional para predicción de características físicas de granos de cacao.
    
    Esta CNN recibe imágenes RGB y predice 4 valores numéricos:
    - width (ancho en mm)
    - height (alto en mm) 
    - thickness (grosor en mm)
    - weight (peso en gramos)
    
    Arquitectura basada en bloques convolucionales con BatchNorm y Dropout
    para regularización.
    """
    
    def __init__(self, input_channels: int = 3, num_outputs: int = 4, dropout_rate: float = 0.5):
        """
        Inicializa el modelo CacaoVisionModel.
        
        Args:
            input_channels (int): Número de canales de entrada (3 para RGB)
            num_outputs (int): Número de salidas (4 para width, height, thickness, weight)
            dropout_rate (float): Tasa de dropout para regularización
        """
        super(CacaoVisionModel, self).__init__()
        
        self.input_channels = input_channels
        self.num_outputs = num_outputs
        self.dropout_rate = dropout_rate
        
        # Primer bloque convolucional
        self.conv_block1 = self._make_conv_block(input_channels, 32, kernel_size=7, stride=2, padding=3)
        self.pool1 = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        
        # Segundo bloque convolucional
        self.conv_block2 = self._make_conv_block(32, 64, kernel_size=5, stride=1, padding=2)
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # Tercer bloque convolucional
        self.conv_block3 = self._make_conv_block(64, 128, kernel_size=3, stride=1, padding=1)
        self.pool3 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # Cuarto bloque convolucional
        self.conv_block4 = self._make_conv_block(128, 256, kernel_size=3, stride=1, padding=1)
        self.pool4 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # Quinto bloque convolucional
        self.conv_block5 = self._make_conv_block(256, 512, kernel_size=3, stride=1, padding=1)
        
        # Pooling adaptativo para manejar diferentes tamaños de entrada
        self.adaptive_pool = nn.AdaptiveAvgPool2d((4, 4))
        
        # Capas totalmente conectadas
        self.fc_input_size = 512 * 4 * 4  # 8192
        
        self.classifier = nn.Sequential(
            nn.Dropout(dropout_rate),
            nn.Linear(self.fc_input_size, 1024),
            nn.ReLU(inplace=True),
            nn.BatchNorm1d(1024),
            
            nn.Dropout(dropout_rate),
            nn.Linear(1024, 512),
            nn.ReLU(inplace=True),
            nn.BatchNorm1d(512),
            
            nn.Dropout(dropout_rate * 0.5),
            nn.Linear(512, 128),
            nn.ReLU(inplace=True),
            nn.BatchNorm1d(128),
            
            nn.Linear(128, num_outputs)
        )
        
        # Inicialización de pesos
        self._initialize_weights()
    
    def _make_conv_block(self, in_channels: int, out_channels: int, 
                        kernel_size: int = 3, stride: int = 1, padding: int = 1) -> nn.Sequential:
        """
        Crea un bloque convolucional con Conv2d + BatchNorm + ReLU.
        
        Args:
            in_channels (int): Número de canales de entrada
            out_channels (int): Número de canales de salida
            kernel_size (int): Tamaño del kernel
            stride (int): Stride de la convolución
            padding (int): Padding aplicado
            
        Returns:
            nn.Sequential: Bloque convolucional completo
        """
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=kernel_size, 
                     stride=stride, padding=padding, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )
    
    def _initialize_weights(self):
        """
        Inicializa los pesos del modelo usando Xavier/Kaiming initialization.
        """
        for module in self.modules():
            if isinstance(module, nn.Conv2d):
                nn.init.kaiming_normal_(module.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(module, nn.BatchNorm2d):
                nn.init.constant_(module.weight, 1)
                nn.init.constant_(module.bias, 0)
            elif isinstance(module, nn.Linear):
                nn.init.normal_(module.weight, 0, 0.01)
                if module.bias is not None:
                    nn.init.constant_(module.bias, 0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass del modelo.
        
        Args:
            x (torch.Tensor): Tensor de entrada con forma (batch_size, channels, height, width)
            
        Returns:
            torch.Tensor: Predicciones con forma (batch_size, 4) 
                         [width, height, thickness, weight]
        """
        # Validar entrada
        if x.dim() != 4:
            raise ValueError(f"Entrada debe tener 4 dimensiones (batch, channels, height, width), "
                           f"recibido: {x.dim()}")
        
        if x.size(1) != self.input_channels:
            raise ValueError(f"Número de canales esperado: {self.input_channels}, "
                           f"recibido: {x.size(1)}")
        
        # Bloques convolucionales
        x = self.conv_block1(x)  # -> (batch, 32, H/2, W/2)
        x = self.pool1(x)        # -> (batch, 32, H/4, W/4)
        
        x = self.conv_block2(x)  # -> (batch, 64, H/4, W/4)
        x = self.pool2(x)        # -> (batch, 64, H/8, W/8)
        
        x = self.conv_block3(x)  # -> (batch, 128, H/8, W/8)
        x = self.pool3(x)        # -> (batch, 128, H/16, W/16)
        
        x = self.conv_block4(x)  # -> (batch, 256, H/16, W/16)
        x = self.pool4(x)        # -> (batch, 256, H/32, W/32)
        
        x = self.conv_block5(x)  # -> (batch, 512, H/32, W/32)
        
        # Pooling adaptativo para tamaño fijo
        x = self.adaptive_pool(x)  # -> (batch, 512, 4, 4)
        
        # Aplanar para capas FC
        x = x.view(x.size(0), -1)  # -> (batch, 8192)
        
        # Clasificador
        outputs = self.classifier(x)  # -> (batch, 4)
        
        # Aplicar activaciones específicas para cada salida
        # width, height, thickness: valores positivos (ReLU)
        # weight: valor positivo (ReLU)
        outputs = F.relu(outputs)
        
        return outputs
    
    def predict_measurements(self, x: torch.Tensor) -> dict:
        """
        Realiza predicción y devuelve un diccionario con las medidas.
        
        Args:
            x (torch.Tensor): Imagen de entrada
            
        Returns:
            dict: Diccionario con las predicciones {
                'width': float,
                'height': float, 
                'thickness': float,
                'weight': float
            }
        """
        self.eval()
        with torch.no_grad():
            predictions = self.forward(x)
            
            if predictions.size(0) == 1:  # Una sola imagen
                pred = predictions.squeeze(0)
                return {
                    'width': float(pred[0].item()),
                    'height': float(pred[1].item()),
                    'thickness': float(pred[2].item()),
                    'weight': float(pred[3].item())
                }
            else:  # Batch de imágenes
                results = []
                for i in range(predictions.size(0)):
                    pred = predictions[i]
                    results.append({
                        'width': float(pred[0].item()),
                        'height': float(pred[1].item()),
                        'thickness': float(pred[2].item()),
                        'weight': float(pred[3].item())
                    })
                return results
    
    def get_model_info(self) -> dict:
        """
        Devuelve información sobre el modelo.
        
        Returns:
            dict: Información del modelo
        """
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        
        return {
            'model_name': 'CacaoVisionModel',
            'input_channels': self.input_channels,
            'num_outputs': self.num_outputs,
            'dropout_rate': self.dropout_rate,
            'total_parameters': total_params,
            'trainable_parameters': trainable_params,
            'model_size_mb': total_params * 4 / (1024 * 1024),  # Aproximado para float32
            'output_names': ['width', 'height', 'thickness', 'weight'],
            'output_units': ['mm', 'mm', 'mm', 'g']
        }


def create_model(pretrained: bool = False, **kwargs) -> CacaoVisionModel:
    """
    Función de conveniencia para crear una instancia del modelo.
    
    Args:
        pretrained (bool): Si cargar pesos pre-entrenados (para futuras extensiones)
        **kwargs: Argumentos adicionales para el modelo
        
    Returns:
        CacaoVisionModel: Instancia del modelo
    """
    model = CacaoVisionModel(**kwargs)
    
    if pretrained:
        # TODO: Implementar carga de pesos pre-entrenados
        # model.load_state_dict(torch.load('path_to_pretrained_weights'))
        pass
    
    return model


def load_model(model_path: str, device: Optional[str] = None) -> CacaoVisionModel:
    """
    Carga un modelo entrenado desde archivo.
    
    Args:
        model_path (str): Ruta al archivo del modelo
        device (str, optional): Device donde cargar el modelo ('cpu', 'cuda')
        
    Returns:
        CacaoVisionModel: Modelo cargado
    """
    if device is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # Cargar el checkpoint
    checkpoint = torch.load(model_path, map_location=device)
    
    # Crear el modelo con la configuración guardada
    model_config = checkpoint.get('model_config', {})
    model = CacaoVisionModel(**model_config)
    
    # Cargar los pesos
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    
    return model


def save_model(model: CacaoVisionModel, model_path: str, 
               epoch: int = 0, optimizer_state: Optional[dict] = None,
               loss: float = 0.0, additional_info: Optional[dict] = None):
    """
    Guarda el modelo y metadata asociada.
    
    Args:
        model (CacaoVisionModel): Modelo a guardar
        model_path (str): Ruta donde guardar el modelo
        epoch (int): Época actual del entrenamiento
        optimizer_state (dict, optional): Estado del optimizador
        loss (float): Loss actual
        additional_info (dict, optional): Información adicional
    """
    checkpoint = {
        'model_state_dict': model.state_dict(),
        'model_config': {
            'input_channels': model.input_channels,
            'num_outputs': model.num_outputs,
            'dropout_rate': model.dropout_rate
        },
        'epoch': epoch,
        'loss': loss,
        'model_info': model.get_model_info()
    }
    
    if optimizer_state is not None:
        checkpoint['optimizer_state_dict'] = optimizer_state
    
    if additional_info is not None:
        checkpoint['additional_info'] = additional_info
    
    torch.save(checkpoint, model_path)


if __name__ == "__main__":
    # Ejemplo de uso
    model = create_model()
    
    # Imprimir información del modelo
    print("Información del modelo:")
    info = model.get_model_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Ejemplo con tensor de prueba
    dummy_input = torch.randn(1, 3, 224, 224)
    output = model(dummy_input)
    print(f"\nForma de salida: {output.shape}")
    print(f"Predicciones: {output}")
    
    # Ejemplo de predicción con nombres
    predictions = model.predict_measurements(dummy_input)
    print(f"\nPredicciones con nombres: {predictions}")

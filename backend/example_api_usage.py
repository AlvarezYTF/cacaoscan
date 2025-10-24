"""
Ejemplo de uso de la API REST de CacaoScan.
"""
import requests
import json
from pathlib import Path
from PIL import Image
import io


def test_models_status():
    """Test del endpoint de estado de modelos."""
    print("=== Probando estado de modelos ===")
    
    try:
        response = requests.get('http://localhost:8000/api/v1/models/status/')
        
        if response.status_code == 200:
            data = response.json()
            print(f"Estado: {data['status']}")
            print(f"YOLO: {data['yolo_segmentation']}")
            print(f"Modelos de regresión: {data['regression_models']}")
            
            if 'device' in data:
                print(f"Dispositivo: {data['device']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: No se puede conectar al servidor. ¿Está Django ejecutándose?")
    except Exception as e:
        print(f"Error: {e}")


def test_load_models():
    """Test del endpoint de carga de modelos."""
    print("\n=== Cargando modelos ===")
    
    try:
        response = requests.post('http://localhost:8000/api/v1/models/load/')
        
        if response.status_code == 200:
            data = response.json()
            print(f"Estado: {data['status']}")
            if 'message' in data:
                print(f"Mensaje: {data['message']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: No se puede conectar al servidor.")
    except Exception as e:
        print(f"Error: {e}")


def test_scan_measure(image_path):
    """Test del endpoint de medición."""
    print(f"\n=== Probando medición con {image_path} ===")
    
    if not Path(image_path).exists():
        print(f"Error: Imagen no encontrada en {image_path}")
        return
    
    try:
        # Leer imagen
        with open(image_path, 'rb') as f:
            files = {'image': f}
            
            response = requests.post(
                'http://localhost:8000/api/v1/scan/measure/',
                files=files
            )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Predicción exitosa:")
            print(f"  Altura: {data['alto_mm']:.2f} mm")
            print(f"  Ancho: {data['ancho_mm']:.2f} mm")
            print(f"  Grosor: {data['grosor_mm']:.2f} mm")
            print(f"  Peso: {data['peso_g']:.2f} g")
            
            print("\nConfianzas:")
            for target, confidence in data['confidences'].items():
                print(f"  {target}: {confidence:.3f}")
            
            print(f"\nCrop URL: {data['crop_url']}")
            
            debug = data['debug']
            print(f"\nDebug:")
            print(f"  Segmentado: {debug['segmented']}")
            print(f"  Confianza YOLO: {debug['yolo_conf']:.3f}")
            print(f"  Latencia: {debug['latency_ms']} ms")
            print(f"  Dispositivo: {debug.get('device', 'N/A')}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"  Mensaje: {error_data.get('error', 'Error desconocido')}")
            except:
                print(f"  Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: No se puede conectar al servidor.")
    except Exception as e:
        print(f"Error: {e}")


def test_dataset_validation():
    """Test del endpoint de validación de dataset."""
    print("\n=== Validando dataset ===")
    
    try:
        response = requests.get('http://localhost:8000/api/v1/dataset/validation/')
        
        if response.status_code == 200:
            data = response.json()
            print(f"Estado: {data['status']}")
            print(f"Válido: {data['valid']}")
            
            if 'stats' in data:
                stats = data['stats']
                print(f"Registros totales: {stats.get('total_records', 'N/A')}")
                print(f"Registros válidos: {stats.get('valid_records', 'N/A')}")
                print(f"Imágenes faltantes: {stats.get('missing_images', 'N/A')}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: No se puede conectar al servidor.")
    except Exception as e:
        print(f"Error: {e}")


def create_test_image():
    """Crea una imagen de prueba."""
    print("\n=== Creando imagen de prueba ===")
    
    # Crear imagen de prueba (simulando un grano de cacao)
    image = Image.new('RGB', (224, 224), color='brown')
    
    # Guardar imagen de prueba
    test_image_path = 'test_cacao_image.jpg'
    image.save(test_image_path)
    
    print(f"Imagen de prueba creada: {test_image_path}")
    return test_image_path


def main():
    """Función principal."""
    print("CacaoScan API - Ejemplo de Uso")
    print("=" * 50)
    
    # 1. Verificar estado de modelos
    test_models_status()
    
    # 2. Cargar modelos si es necesario
    test_load_models()
    
    # 3. Verificar estado de modelos después de cargar
    test_models_status()
    
    # 4. Validar dataset
    test_dataset_validation()
    
    # 5. Crear imagen de prueba
    test_image_path = create_test_image()
    
    # 6. Probar medición
    test_scan_measure(test_image_path)
    
    # 7. Limpiar imagen de prueba
    Path(test_image_path).unlink(missing_ok=True)
    
    print("\n" + "=" * 50)
    print("Ejemplo completado!")
    print("\nPara usar con tu propia imagen:")
    print("python example_api_usage.py --image path/to/your/image.jpg")
    
    print("\nPara ver la documentación de la API:")
    print("http://localhost:8000/swagger/")
    print("http://localhost:8000/redoc/")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 2 and sys.argv[1] == '--image':
        # Usar imagen específica
        image_path = sys.argv[2]
        print(f"Usando imagen: {image_path}")
        test_scan_measure(image_path)
    else:
        # Ejecutar ejemplo completo
        main()

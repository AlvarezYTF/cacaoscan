"""
Ejemplo de uso del sistema CacaoScan completamente automático.
"""
import requests
import json
import time
from pathlib import Path


def test_auto_system():
    """Prueba el sistema completamente automático."""
    print("🚀 CacaoScan - Sistema Completamente Automático")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api/v1"
    
    try:
        # Paso 1: Inicialización automática completa
        print("\n📋 PASO 1: Inicialización Automática Completa")
        print("-" * 50)
        
        print("Ejecutando inicialización automática...")
        response = requests.post(f"{base_url}/auto-initialize/")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Inicialización exitosa!")
            print(f"⏱️  Tiempo total: {data['total_time_seconds']} segundos")
            print("📝 Pasos completados:")
            for step in data['steps_completed']:
                print(f"   {step}")
        else:
            print(f"❌ Error en inicialización: {response.status_code}")
            print(f"   {response.text}")
            return False
        
        # Paso 2: Verificar estado del sistema
        print("\n📊 PASO 2: Verificar Estado del Sistema")
        print("-" * 50)
        
        response = requests.get(f"{base_url}/models/status/")
        if response.status_code == 200:
            status = response.json()
            print("✅ Estado del sistema:")
            print(f"   YOLO: {status['yolo_segmentation']}")
            print(f"   Modelos: {status['regression_models']}")
            print(f"   Estado: {status['status']}")
        else:
            print(f"❌ Error verificando estado: {response.status_code}")
        
        # Paso 3: Probar predicción (simulado)
        print("\n🔮 PASO 3: Sistema Listo para Predicciones")
        print("-" * 50)
        print("✅ El sistema está completamente inicializado y listo!")
        print("📋 Para probar predicciones:")
        print("   1. Sube una imagen de grano de cacao")
        print("   2. POST a /api/v1/scan/measure/")
        print("   3. Recibe predicciones automáticamente")
        
        print("\n" + "=" * 60)
        print("🎉 ¡Sistema CacaoScan listo para usar!")
        print("💡 Todo el entrenamiento se hizo automáticamente")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor Django")
        print("   Asegúrate de que el servidor esté ejecutándose:")
        print("   python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


def test_with_image(image_path: str):
    """Prueba el sistema con una imagen específica."""
    print(f"\n🖼️  Probando con imagen: {image_path}")
    print("-" * 50)
    
    if not Path(image_path).exists():
        print(f"❌ Imagen no encontrada: {image_path}")
        return False
    
    try:
        base_url = "http://localhost:8000/api/v1"
        
        # Subir imagen y obtener predicción
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(f"{base_url}/scan/measure/", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Predicción exitosa:")
            print(f"   📏 Altura: {data['alto_mm']:.2f} mm")
            print(f"   📐 Ancho: {data['ancho_mm']:.2f} mm")
            print(f"   📏 Grosor: {data['grosor_mm']:.2f} mm")
            print(f"   ⚖️  Peso: {data['peso_g']:.2f} g")
            
            print("\n🎯 Confianzas:")
            for target, confidence in data['confidences'].items():
                print(f"   {target}: {confidence:.3f}")
            
            print(f"\n🔗 Crop URL: {data['crop_url']}")
            print(f"⏱️  Latencia: {data['debug']['latency_ms']} ms")
            
            return True
        else:
            print(f"❌ Error en predicción: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Error desconocido')}")
            except:
                print(f"   Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error procesando imagen: {e}")
        return False


def main():
    """Función principal."""
    print("🎯 CacaoScan - Sistema Automático de Predicción")
    print("=" * 60)
    print("Este sistema:")
    print("✅ Entrena automáticamente los modelos la primera vez")
    print("✅ Genera crops automáticamente")
    print("✅ Predice dimensiones y peso de granos de cacao")
    print("✅ Todo desde el frontend, sin comandos manuales")
    
    # Probar inicialización automática
    success = test_auto_system()
    
    if success:
        print("\n📋 Instrucciones para usar desde el frontend:")
        print("1. POST /api/v1/auto-initialize/ (solo la primera vez)")
        print("2. POST /api/v1/scan/measure/ con imagen")
        print("3. Recibir predicciones en JSON")
        print("\n🚀 ¡Sistema completamente automático y listo!")
    
    return success


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--image":
        if len(sys.argv) > 2:
            image_path = sys.argv[2]
            main()  # Inicializar sistema
            test_with_image(image_path)  # Probar con imagen
        else:
            print("❌ Usar: python example_auto_system.py --image path/to/image.jpg")
    else:
        main()

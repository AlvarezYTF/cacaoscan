"""
Script simple para probar el modelo entrenado con una imagen específica.
Uso: python manage.py shell < test_model.py
O: docker compose exec backend python test_model.py
"""
import sys
from pathlib import Path
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')
import django
django.setup()

from PIL import Image
from ml.prediction.predict import CacaoPredictor
from ml.data.dataset_loader import CacaoDatasetLoader

def test_image(image_id=None, image_path=None):
    """
    Prueba el modelo con una imagen específica.
    
    Args:
        image_id: ID de la imagen en el dataset (ej: 497)
        image_path: Ruta directa a una imagen (ej: 'media/cacao_images/raw/497.bmp')
    """
    print("=" * 60)
    print("🧪 PRUEBA DEL MODELO ENTRENADO")
    print("=" * 60)
    
    # Cargar predictor
    print("\n📦 Cargando predictor y artefactos...")
    predictor = CacaoPredictor()
    if not predictor.load_artifacts():
        print("❌ Error: No se pudieron cargar los artefactos del modelo")
        print("   Asegúrate de que el entrenamiento se completó correctamente.")
        return
    
    print("✅ Modelo cargado exitosamente")
    
    # Determinar qué imagen usar
    image = None
    image_record = None
    
    if image_id:
        # Buscar imagen por ID en el dataset
        print(f"\n🔍 Buscando imagen con ID={image_id}...")
        loader = CacaoDatasetLoader()
        records = loader.get_valid_records()
        
        for record in records:
            if record['id'] == image_id:
                image_record = record
                break
        
        if not image_record:
            print(f"❌ Error: No se encontró imagen con ID={image_id}")
            return
        
        # Construir ruta de imagen
        image_path_str = str(image_record['image_path'])
        if image_path_str.startswith('media'):
            image_path = Path(image_path_str)
        else:
            image_path = Path('media') / image_path_str
        
        # Intentar diferentes extensiones
        if not image_path.exists():
            for ext in ['.bmp', '.png', '.jpg', '.jpeg']:
                alt_path = image_path.with_suffix(ext)
                if alt_path.exists():
                    image_path = alt_path
                    break
        
        if not image_path.exists():
            print(f"❌ Error: Imagen no encontrada en: {image_path}")
            print(f"   Ruta del record: {image_record['image_path']}")
            return
        
        print(f"✅ Imagen encontrada: {image_path}")
        
        # Mostrar valores reales si están disponibles
        if image_record:
            print("\n📊 Valores reales del dataset:")
            print(f"   ALTO:   {image_record.get('alto', 'N/A')} mm")
            print(f"   ANCHO:  {image_record.get('ancho', 'N/A')} mm")
            print(f"   GROSOR: {image_record.get('grosor', 'N/A')} mm")
            print(f"   PESO:   {image_record.get('peso', 'N/A')} g")
    
    elif image_path:
        # Usar ruta directa
        image_path = Path(image_path)
        if not image_path.exists():
            print(f"❌ Error: Imagen no encontrada en: {image_path}")
            return
        print(f"✅ Imagen encontrada: {image_path}")
    
    else:
        print("❌ Error: Debes proporcionar image_id o image_path")
        print("\nEjemplos de uso:")
        print("  test_image(image_id=497)")
        print("  test_image(image_path='media/cacao_images/raw/497.bmp')")
        return
    
    # Cargar imagen
        print("\n🖼️  Cargando imagen...")
    try:
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        print(f"✅ Imagen cargada: {image.size[0]}x{image.size[1]} pixels")
    except Exception as e:
        print(f"❌ Error al cargar imagen: {e}")
        return
    
    # Hacer predicción
        print("\n🤖 Ejecutando predicción...")
    try:
        result = predictor.predict(image)
        
        print("\n" + "=" * 60)
        print("📈 RESULTADOS DE LA PREDICCIÓN")
        print("=" * 60)
        print(f"\n   ALTO:   {result['alto_mm']:.2f} mm")
        print(f"   ANCHO:  {result['ancho_mm']:.2f} mm")
        print(f"   GROSOR: {result['grosor_mm']:.2f} mm")
        print(f"   PESO:   {result['peso_g']:.2f} g")
        
        # Mostrar confianzas si están disponibles
        if 'confidence_alto' in result:
            print("\n📊 Confianzas:")
            print(f"   ALTO:   {result['confidence_alto']:.2%}")
            print(f"   ANCHO:  {result['confidence_ancho']:.2%}")
            print(f"   GROSOR: {result['confidence_grosor']:.2%}")
            print(f"   PESO:   {result['confidence_peso']:.2%}")
        
        # Comparar con valores reales si están disponibles
        if image_record:
            print("\n📊 Comparación con valores reales:")
            targets = ['alto', 'ancho', 'grosor', 'peso']
            for target in targets:
                real = image_record.get(target)
                pred = result.get(f'{target}_mm' if target != 'peso' else 'peso_g')
                if real is not None:
                    error = abs(pred - real)
                    error_pct = (error / real) * 100 if real > 0 else 0
                    print(f"   {target.upper():6s}: Real={real:6.2f}, Pred={pred:6.2f}, Error={error:6.2f} ({error_pct:5.1f}%)")
        
        print("\n" + "=" * 60)
        print("✅ Predicción completada exitosamente")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error durante la predicción: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    # Ejemplo de uso: probar con imagen ID 497
    if len(sys.argv) > 1:
        # Si se pasa un argumento, intentar como ID o ruta
        arg = sys.argv[1]
        if arg.isdigit():
            test_image(image_id=int(arg))
        else:
            test_image(image_path=arg)
    else:
        # Por defecto, probar con imagen 497
        print("No se especificó imagen. Usando imagen ID=497 como ejemplo.")
        print("Uso: python test_model.py <image_id> o python test_model.py <image_path>")
        print("\n")
        test_image(image_id=497)


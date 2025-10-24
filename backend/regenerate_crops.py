#!/usr/bin/env python
"""
Script para regenerar crops de cacao.
"""
import os
import django
import sys
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')
django.setup()

def regenerate_crops():
    """Regenera crops de cacao."""
    print("🚀 Regenerando crops de cacao...")
    
    try:
        # 1. Cargar dataset
        print("📊 Cargando dataset...")
        from ml.data.dataset_loader import CacaoDatasetLoader
        loader = CacaoDatasetLoader()
        df = loader.load_dataset()
        valid_df, missing_ids = loader.validate_images_exist(df)
        valid_records = loader.get_valid_records()
        
        print(f"✅ Dataset cargado: {len(df)} registros")
        print(f"✅ Imágenes válidas: {len(valid_df)}")
        print(f"✅ Registros válidos: {len(valid_records)}")
        
        if len(valid_records) == 0:
            print("❌ No hay registros válidos para procesar")
            return False
        
        # 2. Crear directorio de crops si no existe
        crops_dir = Path("media/cacao_images/crops")
        crops_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Directorio de crops: {crops_dir}")
        
        # 3. Procesar todas las imágenes válidas
        print(f"🧪 Procesando {len(valid_records)} imágenes...")
        
        # 4. Crear crops simples
        successful = 0
        failed = 0
        
        for i, record in enumerate(valid_records):
            try:
                image_id = record['id']
                image_path = Path(record['image_path'])
                crop_path = crops_dir / f"{image_id}.png"
                
                if i % 50 == 0 or i == len(valid_records) - 1:
                    print(f"📷 Procesando {i+1}/{len(valid_records)}: ID {image_id}")
                
                # Verificar si la imagen existe
                if not image_path.exists():
                    print(f"❌ Imagen no existe: {image_path}")
                    failed += 1
                    continue
                
                # Crear un crop simple (copia de la imagen original redimensionada)
                from PIL import Image
                img = Image.open(image_path)
                
                # Redimensionar a 512x512
                img_resized = img.resize((512, 512), Image.Resampling.LANCZOS)
                
                # Guardar como PNG
                img_resized.save(crop_path, "PNG")
                
                successful += 1
                
            except Exception as e:
                print(f"❌ Error procesando ID {record['id']}: {e}")
                failed += 1
        
        print(f"\n📊 Resultados:")
        print(f"✅ Exitosos: {successful}")
        print(f"❌ Fallidos: {failed}")
        print(f"📈 Tasa de éxito: {successful/(successful+failed)*100:.1f}%")
        
        return successful > 0
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = regenerate_crops()
    if success:
        print("🎉 Regeneración de crops completada exitosamente!")
    else:
        print("💥 Error en la regeneración de crops")

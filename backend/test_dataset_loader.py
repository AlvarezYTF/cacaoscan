"""
Script de prueba para el dataset loader adaptado.
"""
import sys
import os
sys.path.append('.')

from ml.data.dataset_loader import CacaoDatasetLoader
import pandas as pd


def test_dataset_loader():
    """Prueba el dataset loader con el CSV real."""
    print("🧪 Probando Dataset Loader de CacaoScan")
    print("=" * 50)
    
    try:
        # 1. Crear loader
        print("1. Inicializando loader...")
        loader = CacaoDatasetLoader()
        print(f"   ✅ CSV detectado: {loader.csv_path}")
        
        # 2. Cargar dataset
        print("\n2. Cargando dataset...")
        df = loader.load_dataset()
        print(f"   ✅ Dataset cargado: {len(df)} registros")
        print(f"   📊 Columnas: {list(df.columns)}")
        print(f"   📈 Tipos de datos:")
        for col in df.columns:
            print(f"      - {col}: {df[col].dtype}")
        
        # 3. Mostrar primeras filas
        print("\n3. Primeras 5 filas:")
        print(df.head())
        
        # 4. Validar imágenes
        print("\n4. Validando existencia de imágenes...")
        valid_df, missing_ids = loader.validate_images_exist(df)
        print(f"   ✅ Imágenes válidas: {len(valid_df)}")
        print(f"   ❌ Imágenes faltantes: {len(missing_ids)}")
        
        if missing_ids:
            print(f"   📝 IDs faltantes: {missing_ids[:10]}{'...' if len(missing_ids) > 10 else ''}")
        
        # 5. Estadísticas
        print("\n5. Estadísticas del dataset:")
        stats = loader.get_dataset_stats()
        print(f"   📊 Total registros: {stats['total_records']}")
        print(f"   ✅ Registros válidos: {stats['valid_records']}")
        print(f"   ❌ Imágenes faltantes: {stats['missing_images']}")
        
        # 6. Estadísticas por target
        print("\n6. Estadísticas por target:")
        for target in ['alto', 'ancho', 'grosor', 'peso']:
            if target in stats['dimensions_stats']:
                target_stats = stats['dimensions_stats'][target]
                print(f"   {target.upper()}:")
                print(f"      - Min: {target_stats['min']:.2f}")
                print(f"      - Max: {target_stats['max']:.2f}")
                print(f"      - Media: {target_stats['mean']:.2f}")
                print(f"      - Std: {target_stats['std']:.2f}")
        
        # 7. Probar filtrado por target
        print("\n7. Probando filtrado por target 'peso':")
        try:
            target_values, records = loader.get_target_data('peso')
            print(f"   ✅ Valores de peso obtenidos: {len(target_values)}")
            print(f"   📊 Rango de peso: {target_values.min():.2f} - {target_values.max():.2f} g")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 ¡Prueba completada exitosamente!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_dataset_loader()
    
    if success:
        print("\n📋 Instrucciones para completar:")
        print("1. Coloca las imágenes .bmp en: backend/media/cacao_images/raw/")
        print("2. Nombra las imágenes como: 1.bmp, 2.bmp, 3.bmp, ..., 503.bmp")
        print("3. Ejecuta este script nuevamente para verificar")
    else:
        print("\n🔧 Revisa los errores antes de continuar")

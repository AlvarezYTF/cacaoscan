import os
from pathlib import Path
from PIL import Image
import numpy as np
import pytest

# Importa la función principal desde tu módulo
from ml.segmentation.processor import segment_and_crop_cacao_bean


@pytest.mark.unit
def test_segment_and_crop_cacao_bean_creates_png(tmp_path):
    """
    🧪 Test IA: segmenta y recorta una imagen de cacao.
    Verifica que:
    1️⃣ El archivo existe.
    2️⃣ El resultado sea PNG.
    3️⃣ Contenga canal alfa (transparencia).
    """

    # 🖼️ Crear imagen de prueba
    test_image_path = tmp_path / "pruebas2.jpg"
    test_image = Image.new('RGB', (512, 512), color='red')
    test_image.save(test_image_path, format='JPEG')
    input_image = str(test_image_path)

    # 🚀 Ejecutar el procesamiento
    output_path = segment_and_crop_cacao_bean(input_image)

    # ✅ Validaciones de salida
    assert output_path.endswith(".png"), "El archivo resultante no es PNG"
    assert os.path.exists(output_path), "El archivo de salida no fue creado"

    # 🔍 Validar que tenga canal alfa (RGBA)
    img = Image.open(output_path)
    assert img.mode == "RGBA", f"El modo de imagen no es RGBA, es {img.mode}"

    # 🩸 Comprobar que hay transparencia real (no fondo sólido)
    alpha_channel = np.array(img.split()[-1])
    transparent_ratio = np.mean(alpha_channel < 250)  # % de píxeles transparentes
    assert transparent_ratio > 0.1, "La imagen no presenta fondo eliminado adecuadamente"

    # 🧼 Limpieza automática del archivo de salida
    os.remove(output_path)


def test_processor_handles_missing_file():
    """
    🧱 Test de robustez: el procesador debe lanzar error si el archivo no existe.
    """
    with pytest.raises(FileNotFoundError):
        segment_and_crop_cacao_bean("media/datasets/inexistente.jpg")

"""
Genera dataset sintetico de granos de cacao para validar el pipeline de training
end-to-end. NO sirve para un modelo real - son elipses sobre fondo blanco con
mediciones inventadas pero internamente consistentes.

Uso:
    python scripts/generate_synthetic_dataset.py --n 100 --out backend/media/synthetic

Estructura generada:
    <out>/raw/cacao_images/001.jpg ... NNN.jpg
    <out>/processed/dataset_cacao.csv
"""
import argparse
import csv
import random
from pathlib import Path

from PIL import Image, ImageDraw


def generate_grain_image(grain_id: int, alto_mm: float, ancho_mm: float, out: Path) -> None:
    """Pinta una elipse marron sobre fondo blanco con tamano proporcional a las medidas."""
    # 1 mm = 20 px aprox (calibracion arbitraria pero consistente)
    px_per_mm = 20
    w_px = int(ancho_mm * px_per_mm)
    h_px = int(alto_mm * px_per_mm)

    # Canvas con margen
    canvas_w, canvas_h = w_px + 200, h_px + 200
    img = Image.new("RGB", (canvas_w, canvas_h), (245, 245, 245))
    draw = ImageDraw.Draw(img)

    cx, cy = canvas_w // 2, canvas_h // 2
    bbox = (cx - w_px // 2, cy - h_px // 2, cx + w_px // 2, cy + h_px // 2)
    # Color marron con variacion
    r = random.randint(80, 120)
    g = random.randint(40, 70)
    b = random.randint(20, 40)
    draw.ellipse(bbox, fill=(r, g, b), outline=(40, 20, 10), width=3)

    img.save(out, "BMP")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=100, help="Numero de granos a generar")
    parser.add_argument("--out", type=Path, required=True, help="Directorio de salida")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)

    raw_dir = args.out / "raw" / "cacao_images"
    processed_dir = args.out / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    csv_path = processed_dir / "dataset_cacao.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "ALTO", "ANCHO", "GROSOR", "PESO"])

        for i in range(1, args.n + 1):
            # IDs sin padding: pandas los lee como int (1, 2, ... 100).
            # Los nombres de archivo deben coincidir.
            grain_id = str(i)
            # Rangos realistas para granos de cacao fermentados
            alto = round(random.uniform(20.0, 28.0), 2)
            ancho = round(random.uniform(12.0, 18.0), 2)
            grosor = round(random.uniform(6.0, 10.0), 2)
            # Peso correlacionado con volumen aproximado (densidad ~ 0.5 g/cm3)
            volume_cm3 = (alto * ancho * grosor) / 1000.0
            peso = round(volume_cm3 * random.uniform(0.45, 0.55), 3)

            img_path = raw_dir / f"{grain_id}.bmp"
            generate_grain_image(i, alto, ancho, img_path)
            writer.writerow([grain_id, alto, ancho, grosor, peso])

            if i % 20 == 0:
                print(f"  {i}/{args.n} granos generados...")

    print(f"\nDataset sintetico listo:")
    print(f"  Imagenes: {raw_dir} ({args.n} archivos)")
    print(f"  CSV: {csv_path}")


if __name__ == "__main__":
    main()

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pathlib import Path
import csv


class Command(BaseCommand):
    help = (
        "Convert backend/media/datasets/dataset.csv (semicolon; ID;ALTO;GROSOR;ANCHO;PESO) "
        "to dataset_cacao.csv (comma, columns: ID,ALTO,ANCHO,GROSOR,PESO)."
    )

    def handle(self, *args, **options):
        # Use MEDIA_ROOT from settings (expected backend/media)
        media_root = Path(settings.MEDIA_ROOT)
        base_dir = media_root / "datasets"
        in_path = base_dir / "dataset.csv"
        out_path = base_dir / "dataset_cacao.csv"

        if not in_path.exists():
            # Fallback: try under backend/media if MEDIA_ROOT points elsewhere
            fallback = Path(__file__).resolve().parents[4] / "backend" / "media" / "datasets" / "dataset.csv"
            if fallback.exists():
                in_path = fallback
                out_path = fallback.parent / "dataset_cacao.csv"
            else:
                raise CommandError(
                    f"Input file not found: {in_path}. Expected at {media_root / 'datasets' / 'dataset.csv'}"
                )

        rows_converted = 0
        with in_path.open("r", encoding="utf-8", newline="") as fin, out_path.open(
            "w", encoding="utf-8", newline=""
        ) as fout:
            reader = csv.DictReader(fin, delimiter=";")
            fieldnames = ["ID", "ALTO", "ANCHO", "GROSOR", "PESO"]
            writer = csv.DictWriter(fout, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                try:
                    writer.writerow(
                        {
                            "ID": row.get("ID"),
                            "ALTO": row.get("ALTO"),
                            "ANCHO": row.get("ANCHO"),
                            "GROSOR": row.get("GROSOR"),
                            "PESO": row.get("PESO"),
                        }
                    )
                    rows_converted += 1
                except Exception:
                    continue

        self.stdout.write(
            self.style.SUCCESS(
                f"dataset.csv converted -> dataset_cacao.csv | rows: {rows_converted} | output: {out_path}"
            )
        )


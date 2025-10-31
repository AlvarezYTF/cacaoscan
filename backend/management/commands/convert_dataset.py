from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
import csv


class Command(BaseCommand):
    help = "Convert backend/media/datasets/dataset.csv (semicolon; ID;ALTO;GROSOR;ANCHO;PESO) to dataset_cacao.csv (comma, ID,ALTO,ANCHO,GROSOR,PESO)."

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parents[3] / "media" / "datasets"
        in_path = base_dir / "dataset.csv"
        out_path = base_dir / "dataset_cacao.csv"

        if not in_path.exists():
            raise CommandError(f"Input file not found: {in_path}")

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
                    # skip malformed rows silently
                    continue

        self.stdout.write(
            self.style.SUCCESS(
                f"dataset.csv converted -> dataset_cacao.csv | rows: {rows_converted} | output: {out_path}"
            )
        )



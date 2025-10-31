from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import csv


class Command(BaseCommand):
    help = "Append filename and image_path to dataset_cacao.csv by matching ID to files in media/cacao_images/raw/."

    def add_arguments(self, parser):
        parser.add_argument("--exts", nargs="*", default=[".bmp", ".jpg", ".jpeg", ".png"], help="Extensions to search in raw directory")

    def handle(self, *args, **options):
        media_root = Path(settings.MEDIA_ROOT)
        datasets_dir = media_root / "datasets"
        raw_dir = media_root / "cacao_images" / "raw"

        in_path = datasets_dir / "dataset_cacao.csv"
        if not in_path.exists():
            self.stderr.write(self.style.ERROR(f"dataset_cacao.csv not found at {in_path}"))
            return

        exts = [e.lower() for e in options["exts"]]

        # index raw files by stem (e.g., 510 -> 510.bmp)
        stem_to_path = {}
        for p in raw_dir.glob("**/*"):
            if p.is_file() and p.suffix.lower() in exts:
                stem_to_path.setdefault(p.stem, p)

        out_rows = []
        found, missing = 0, 0
        with in_path.open("r", encoding="utf-8", newline="") as fin:
            reader = csv.DictReader(fin)
            fieldnames = reader.fieldnames or []
            # ensure columns
            for col in ("ID", "ALTO", "ANCHO", "GROSOR", "PESO"):
                if col not in fieldnames:
                    self.stderr.write(self.style.ERROR(f"Missing column {col} in dataset_cacao.csv"))
                    return
            new_fieldnames = fieldnames + [c for c in ("filename", "image_path") if c not in fieldnames]

            for row in reader:
                stem = str(row["ID"]).strip()
                file_path = stem_to_path.get(stem)
                if file_path:
                    row["filename"] = file_path.name
                    # store path relative to media root for portability
                    try:
                        row["image_path"] = str(file_path.relative_to(media_root))
                    except ValueError:
                        row["image_path"] = str(file_path)
                    found += 1
                else:
                    row.setdefault("filename", "")
                    row.setdefault("image_path", "")
                    missing += 1
                out_rows.append(row)

        # overwrite with new columns
        with in_path.open("w", encoding="utf-8", newline="") as fout:
            writer = csv.DictWriter(fout, fieldnames=new_fieldnames)
            writer.writeheader()
            writer.writerows(out_rows)

        self.stdout.write(self.style.SUCCESS(f"Mapped images for dataset: matched={found}, missing={missing}, file={in_path}"))



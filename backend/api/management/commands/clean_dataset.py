from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import csv


class Command(BaseCommand):
    help = (
        "Clean dataset_cacao.csv: drop rows without filename/image_path, "
        "non-numeric values, and obvious outliers. Save as dataset_cacao.clean.csv and report stats."
    )

    def add_arguments(self, parser):
        parser.add_argument("--max-alto", type=float, default=60.0)
        parser.add_argument("--max-ancho", type=float, default=30.0)
        parser.add_argument("--max-grosor", type=float, default=20.0)
        parser.add_argument("--max-peso", type=float, default=10.0)
        parser.add_argument("--min-alto", type=float, default=5.0)
        parser.add_argument("--min-ancho", type=float, default=3.0)
        parser.add_argument("--min-grosor", type=float, default=1.0)
        parser.add_argument("--min-peso", type=float, default=0.2)

    def handle(self, *args, **opts):
        media_root = Path(settings.MEDIA_ROOT)
        datasets_dir = media_root / "datasets"
        in_path = datasets_dir / "dataset_cacao.csv"
        out_path = datasets_dir / "dataset_cacao.clean.csv"
        report_path = datasets_dir / "dataset_cacao.clean.report.txt"

        if not in_path.exists():
            self.stderr.write(self.style.ERROR(f"dataset_cacao.csv not found at {in_path}"))
            return

        kept, dropped = 0, 0
        reasons = {
            "missing_file": 0,
            "non_numeric": 0,
            "outlier": 0,
        }
        rows_out = []

        with in_path.open("r", encoding="utf-8", newline="") as fin:
            reader = csv.DictReader(fin)
            fieldnames = reader.fieldnames or []
            required = ["ID", "ALTO", "ANCHO", "GROSOR", "PESO"]
            for r in required:
                if r not in fieldnames:
                    self.stderr.write(self.style.ERROR(f"Missing column {r} in {in_path}"))
                    return
            # ensure filename/image_path in output
            new_fieldnames = fieldnames
            for c in ("filename", "image_path"):
                if c not in new_fieldnames:
                    new_fieldnames.appendé

            for row in reader:
                # require mapped file
                if not row.get("filename") or not row.get("image_path"):
                    dropped += 1
                    reasons["missing_file"] += 1
                    continue
                try:
                    alto = float(str(row["ALTO"]).replace(",", "."))
                    ancho = float(str(row["ANCHO"]).replace(",", "."))
                    grosor = float(str(row["GROSOR"]).replace(",", "."))
                    peso = float(str(row["PESO"]).replace(",", "."))
                except Exception:
                    dropped += 1
                    reasons["non_numeric"] += 1
                    continue

                # outlier rules (banda ancha, ajustable por flags)
                if not (opts["min_alto"] <= alto <= opts["max_alto"] and
                        opts["min_ancho"] <= ancho <= opts["max_ancho"] and
                        opts["min_grosor"] <= grosor <= opts["max_grosor"] and
                        opts["min_peso"] <= peso <= opts["max_peso"]):
                    dropped += 1
                    reasons["outlier"] += 1
                    continue

                rows_out.append(row)
                kept += 1

        with out_path.open("w", encoding="utf-8", newline="") as fout:
            writer = csv.DictWriter(fout, fieldnames=new_fieldnames)
            writer.writeheader()
            writer.writerows(rows_out)

        with report_path.open("w", encoding="utf-8") as frep:
            frep.write(f"Input: {in_path}\nOutput: {out_path}\n\n")
            frep.write(f"Kept: {kept}\nDropped: {dropped}\n\n")
            for k, v in reasons.items():
                frep.write(f"{k}: {v}\n")

        self.stdout.write(self.style.SUCCESS(
            f"Cleaned dataset -> {out_path.name} | kept={kept}, dropped={dropped} (missing_file={reasons['missing_file']}, non_numeric={reasons['non_numeric']}, outlier={reasons['outlier']})"
        ))



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
            
            if not self._validate_required_columns(fieldnames, in_path):
                return
            
            new_fieldnames = self._ensure_output_columns(fieldnames)

            for row in reader:
                result = self._process_row(row, opts, reasons)
                if result is None:
                    dropped += 1
                    continue
                
                rows_out.append(result)
                kept += 1

        self._write_output_files(out_path, report_path, new_fieldnames, rows_out, kept, dropped, reasons)

    def _validate_required_columns(self, fieldnames, in_path):
        """Validate that all required columns are present."""
        required = ["ID", "ALTO", "ANCHO", "GROSOR", "PESO"]
        for r in required:
            if r not in fieldnames:
                self.stderr.write(self.style.ERROR(f"Missing column {r} in {in_path}"))
                return False
        return True

    def _ensure_output_columns(self, fieldnames):
        """Ensure filename and image_path columns exist in output."""
        new_fieldnames = list(fieldnames)
        for c in ("filename", "image_path"):
            if c not in new_fieldnames:
                new_fieldnames.append(c)
        return new_fieldnames

    def _process_row(self, row, opts, reasons):
        """Process a single row and return it if valid, None otherwise."""
        if not row.get("filename") or not row.get("image_path"):
            reasons["missing_file"] += 1
            return None
        
        measurements = self._parse_measurements(row)
        if measurements is None:
            reasons["non_numeric"] += 1
            return None
        
        if not self._validate_outliers(measurements, opts):
            reasons["outlier"] += 1
            return None
        
        return row

    def _parse_measurements(self, row):
        """Parse measurement values from row."""
        try:
            return {
                "alto": float(str(row["ALTO"]).replace(",", ".")),
                "ancho": float(str(row["ANCHO"]).replace(",", ".")),
                "grosor": float(str(row["GROSOR"]).replace(",", ".")),
                "peso": float(str(row["PESO"]).replace(",", ".")),
            }
        except (ValueError, KeyError):
            return None

    def _validate_outliers(self, measurements, opts):
        """Validate that measurements are within acceptable ranges."""
        return (opts["min_alto"] <= measurements["alto"] <= opts["max_alto"] and
                opts["min_ancho"] <= measurements["ancho"] <= opts["max_ancho"] and
                opts["min_grosor"] <= measurements["grosor"] <= opts["max_grosor"] and
                opts["min_peso"] <= measurements["peso"] <= opts["max_peso"])

    def _write_output_files(self, out_path, report_path, fieldnames, rows_out, kept, dropped, reasons):
        """Write output CSV and report files."""
        with out_path.open("w", encoding="utf-8", newline="") as fout:
            writer = csv.DictWriter(fout, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows_out)

        with report_path.open("w", encoding="utf-8") as frep:
            frep.write(f"Input: {out_path.parent / 'dataset_cacao.csv'}\nOutput: {out_path}\n\n")
            frep.write(f"Kept: {kept}\nDropped: {dropped}\n\n")
            for k, v in reasons.items():
                frep.write(f"{k}: {v}\n")

        self.stdout.write(self.style.SUCCESS(
            f"Cleaned dataset -> {out_path.name} | kept={kept}, dropped={dropped} (missing_file={reasons['missing_file']}, non_numeric={reasons['non_numeric']}, outlier={reasons['outlier']})"
        ))



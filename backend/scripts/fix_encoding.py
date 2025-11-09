# Reescribo todo el archivo con la nueva implementación.
"""
Corrige texto con problemas de codificación en el backend.

Convierte archivos que contienen mojibake (por ejemplo "NÃºmero")
restaurando los caracteres UTF-8 correctos y reemplazando símbolos no ASCII
como emojis por equivalentes en texto plano.
"""
from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
CURRENT_FILE = Path(__file__).resolve()

TEXT_EXTENSIONS = {
    ".py",
    ".txt",
    ".md",
    ".json",
    ".csv",
    ".yml",
    ".yaml",
    ".html",
    ".htm",
}

ASCII_REPLACEMENTS = {
    "✔": "[OK]",
    "❌": "[ERROR]",
    "⚠️": "[WARN]",
    "⚠": "[WARN]",
    "✓": "[OK]",
    "✗": "[FAIL]",
}


def has_mojibake(text: str) -> bool:
    return any(marker in text for marker in ("Ã", "â", "ð"))


def repair_content(data: bytes) -> str:
    """Intenta reparar el contenido detectando mojibake clásico."""
    try:
        decoded = data.decode("utf-8")
    except UnicodeDecodeError:
        decoded = ""

    if decoded and not has_mojibake(decoded):
        result = decoded
    else:
        # Interpretar los bytes como cp1252 para recuperar los caracteres latinos.
        result = data.decode("cp1252")

    for original, replacement in ASCII_REPLACEMENTS.items():
        result = result.replace(original, replacement)

    result = result.replace("(c)", "é")

    return result


def process_file(path: Path) -> bool:
    if path.resolve() == CURRENT_FILE:
        return False
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return False

    data = path.read_bytes()
    repaired = repair_content(data)

    try:
        original = data.decode("utf-8")
    except UnicodeDecodeError:
        original = ""

    if repaired == original:
        return False

    path.write_text(repaired, encoding="utf-8")
    return True


def main() -> int:
    fixed_files = []

    for file_path in BACKEND_DIR.rglob("*"):
        if not file_path.is_file():
            continue
        try:
            if process_file(file_path):
                fixed_files.append(file_path.relative_to(BACKEND_DIR))
        except (UnicodeDecodeError, UnicodeEncodeError):
            continue

    if fixed_files:
        print("Archivos corregidos:")
        for relative_path in fixed_files:
            print(f" - {relative_path}")
    else:
        print("No se detectaron archivos con mojibake.")
    return 0


if __name__ == "__main__":
    sys.exit(main())


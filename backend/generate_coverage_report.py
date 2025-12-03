"""
Script para generar un reporte detallado de cobertura en formato texto.
Muestra qué archivos y qué líneas están cubiertas y cuáles no.
"""
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Verificar que coverage esté instalado
try:
    import coverage
except ImportError:
    print(" Error: El módulo 'coverage' no está instalado.")
    print("")
    print("Para instalarlo, ejecuta:")
    print("  pip install coverage")
    print("")
    print("O si estás usando un entorno virtual:")
    print("  venv\\Scripts\\pip install coverage  (Windows)")
    print("  source venv/bin/activate && pip install coverage  (Linux/Mac)")
    print("")
    sys.exit(1)


def run_tests_with_coverage() -> bool:
    """Ejecuta los tests con coverage y retorna True si fueron exitosos."""
    print("Ejecutando tests con coverage...")
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', '--cov=.', '--cov-report=', '--cov-branch'],
        cwd=Path(__file__).parent,
        capture_output=False
    )
    return result.returncode == 0


def get_coverage_data() -> coverage.CoverageData:
    """Obtiene los datos de cobertura."""
    cov = coverage.Coverage()
    cov.load()
    return cov.get_data()


def format_line_status(lines: Dict[int, int], missing_lines: List[int]) -> str:
    """
    Formatea el estado de las líneas en un formato legible.
    
    Args:
        lines: Diccionario con líneas ejecutadas {line_number: count}
        missing_lines: Lista de líneas no ejecutadas
    
    Returns:
        String formateado con el estado de las líneas
    """
    if not lines and not missing_lines:
        return "  (archivo vacío o sin código ejecutable)"
    
    covered_lines = sorted(lines.keys())
    all_lines = sorted(set(covered_lines + missing_lines))
    
    if not all_lines:
        return "  (sin líneas ejecutables)"
    
    # Agrupar líneas consecutivas
    covered_ranges = []
    missing_ranges = []
    
    def add_range(ranges_list: List[Tuple[int, int]], start: int, end: int):
        if start == end:
            ranges_list.append((start, start))
        else:
            ranges_list.append((start, end))
    
    # Procesar líneas cubiertas
    if covered_lines:
        start = covered_lines[0]
        end = covered_lines[0]
        for line in covered_lines[1:]:
            if line == end + 1:
                end = line
            else:
                add_range(covered_ranges, start, end)
                start = line
                end = line
        add_range(covered_ranges, start, end)
    
    # Procesar líneas faltantes
    if missing_lines:
        start = missing_lines[0]
        end = missing_lines[0]
        for line in missing_lines[1:]:
            if line == end + 1:
                end = line
            else:
                add_range(missing_ranges, start, end)
                start = line
                end = line
        add_range(missing_ranges, start, end)
    
    # Formatear resultado
    parts = []
    
    if covered_ranges:
        covered_str = ", ".join(
            f"{start}" if start == end else f"{start}-{end}"
            for start, end in covered_ranges
        )
        parts.append(f"✅ Cubiertas: {covered_str}")
    
    if missing_ranges:
        missing_str = ", ".join(
            f"{start}" if start == end else f"{start}-{end}"
            for start, end in missing_ranges
        )
        parts.append(f"❌ Faltantes: {missing_str}")
    
    return "\n".join(f"  {part}" for part in parts)


def generate_report(output_file: str = "coverage_report.txt") -> None:
    """Genera el reporte de cobertura en formato texto."""
    print("\n" + "="*80)
    print("GENERADOR DE REPORTE DE COBERTURA")
    print("="*80 + "\n")
    
    # Ejecutar tests con coverage
    tests_passed = run_tests_with_coverage()
    
    if not tests_passed:
        print("⚠️  ADVERTENCIA: Algunos tests fallaron, pero se generará el reporte de cobertura.")
    
    print("\nGenerando reporte detallado...")
    
    # Obtener datos de cobertura
    try:
        cov_data = get_coverage_data()
    except Exception as e:
        print(f"❌ Error al obtener datos de cobertura: {e}")
        print("Asegúrate de haber ejecutado los tests con coverage primero.")
        sys.exit(1)
    
    # Obtener archivos medidos
    measured_files = cov_data.measured_files()
    
    if not measured_files:
        print("❌ No se encontraron archivos con datos de cobertura.")
        sys.exit(1)
    
    # Generar reporte
    report_lines = []
    report_lines.append("="*80)
    report_lines.append("REPORTE DE COBERTURA DE CÓDIGO")
    report_lines.append(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("="*80)
    report_lines.append("")
    
    # Estadísticas generales
    total_statements = 0
    total_executed = 0
    total_missing = 0
    
    files_with_coverage = []
    files_without_coverage = []
    
    for filename in sorted(measured_files):
        # Obtener líneas ejecutadas y faltantes
        lines = cov_data.lines(filename)
        missing_lines = cov_data.missing_lines(filename)
        
        # Calcular porcentaje
        total = len(lines) + len(missing_lines)
        if total == 0:
            continue
        
        executed = len(lines)
        missing = len(missing_lines)
        percentage = (executed / total * 100) if total > 0 else 0
        
        total_statements += total
        total_executed += executed
        total_missing += missing
        
        # Formatear nombre de archivo (relativo al directorio backend)
        try:
            rel_path = Path(filename).relative_to(Path(__file__).parent)
        except ValueError:
            rel_path = Path(filename)
        
        file_info = {
            'path': str(rel_path),
            'percentage': percentage,
            'executed': executed,
            'missing': missing,
            'total': total,
            'lines': lines,
            'missing_lines': missing_lines
        }
        
        if missing > 0:
            files_without_coverage.append(file_info)
        else:
            files_with_coverage.append(file_info)
    
    # Resumen general
    overall_percentage = (total_executed / total_statements * 100) if total_statements > 0 else 0
    report_lines.append("RESUMEN GENERAL")
    report_lines.append("-"*80)
    report_lines.append(f"Total de archivos analizados: {len(measured_files)}")
    report_lines.append(f"Total de líneas ejecutables: {total_statements}")
    report_lines.append(f"Líneas ejecutadas: {total_executed} ({overall_percentage:.1f}%)")
    report_lines.append(f"Líneas no ejecutadas: {total_missing} ({100-overall_percentage:.1f}%)")
    report_lines.append(f"Archivos con cobertura completa: {len(files_with_coverage)}")
    report_lines.append(f"Archivos con líneas faltantes: {len(files_without_coverage)}")
    report_lines.append("")
    
    # Archivos con líneas faltantes (prioridad)
    if files_without_coverage:
        report_lines.append("="*80)
        report_lines.append("ARCHIVOS CON LÍNEAS NO CUBIERTAS")
        report_lines.append("="*80)
        report_lines.append("")
        
        # Ordenar por porcentaje (menor primero)
        files_without_coverage.sort(key=lambda x: x['percentage'])
        
        for file_info in files_without_coverage:
            report_lines.append(f"📄 {file_info['path']}")
            report_lines.append(f"   Cobertura: {file_info['percentage']:.1f}% "
                              f"({file_info['executed']}/{file_info['total']} líneas)")
            report_lines.append("")
            
            # Mostrar líneas cubiertas y faltantes
            status = format_line_status(
                {line: 1 for line in file_info['lines']},
                file_info['missing_lines']
            )
            report_lines.append(status)
            report_lines.append("")
    
    # Archivos con cobertura completa
    if files_with_coverage:
        report_lines.append("="*80)
        report_lines.append("ARCHIVOS CON COBERTURA COMPLETA (100%)")
        report_lines.append("="*80)
        report_lines.append("")
        
        for file_info in sorted(files_with_coverage, key=lambda x: x['path']):
            report_lines.append(f"✅ {file_info['path']} - {file_info['total']} líneas")
    
    # Escribir archivo
    output_path = Path(__file__).parent / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"\n✅ Reporte generado exitosamente: {output_path}")
    print(f"   Total de archivos: {len(measured_files)}")
    print(f"   Cobertura general: {overall_percentage:.1f}%")
    print(f"   Archivos con líneas faltantes: {len(files_without_coverage)}")
    print(f"\n📄 Abre el archivo '{output_file}' para ver el reporte detallado.")


if __name__ == '__main__':
    output_file = sys.argv[1] if len(sys.argv) > 1 else "coverage_report.txt"
    generate_report(output_file)


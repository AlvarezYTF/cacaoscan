#!/bin/bash
# Script para ejecutar tests en Linux/Mac
cd "$(dirname "$0")"
python run_tests.py "$@"


#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para cerrar todas las conexiones activas a la base de datos de test.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')
django.setup()

import psycopg2
from django.conf import settings

def close_test_db_connections():
    """Cierra todas las conexiones a la base de datos de test."""
    db = settings.DATABASES['default']
    test_db_name = db.get('TEST', {}).get('NAME', 'cacaoscan_db_test')
    
    try:
        # Conectar a postgres para poder cerrar conexiones
        conn = psycopg2.connect(
            host=db['HOST'],
            port=db['PORT'],
            user=db['USER'],
            password=db['PASSWORD'],
            database='postgres'
        )
        cur = conn.cursor()
        
        # Terminar todas las conexiones a la base de datos de test
        cur.execute("""
            SELECT pg_terminate_backend(pid) 
            FROM pg_stat_activity 
            WHERE datname = %s AND pid <> pg_backend_pid()
        """, (test_db_name,))
        
        terminated = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✅ Cerradas {terminated} conexiones a '{test_db_name}'")
        return True
        
    except Exception as e:
        print(f"❌ Error al cerrar conexiones: {e}")
        return False

if __name__ == '__main__':
    close_test_db_connections()


"""
Script para verificar la conexión a Redis.
"""
import sys
import os

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_redis():
    """Verifica si Redis está disponible y funcionando."""
    try:
        import redis
    except ImportError:
        print("❌ El paquete 'redis' no está instalado")
        print("💡 Instálalo con: pip install redis")
        return False
    
    try:
        
        # Obtener configuración desde variables de entorno
        redis_host = os.environ.get('REDIS_HOST', 'localhost')
        redis_port = int(os.environ.get('REDIS_PORT', 6379))
        redis_db = int(os.environ.get('REDIS_DB', 0))
        redis_password = os.environ.get('REDIS_PASSWORD', None)
        
        print(f"🔍 Verificando conexión a Redis...")
        print(f"   Host: {redis_host}")
        print(f"   Port: {redis_port}")
        print(f"   DB: {redis_db}")
        
        # Intentar conectar
        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password,
            socket_connect_timeout=3,
            decode_responses=True
        )
        
        # Hacer ping
        result = r.ping()
        
        if result:
            print("✅ Redis está funcionando correctamente!")
            
            # Probar operaciones básicas
            r.set('test_key', 'test_value', ex=5)
            value = r.get('test_key')
            if value == 'test_value':
                print("✅ Operaciones de lectura/escritura funcionan correctamente")
            else:
                print("⚠️  Advertencia: Las operaciones de lectura/escritura pueden tener problemas")
            
            return True
        else:
            print("❌ Redis no respondió al ping")
            return False
            
    except (redis.ConnectionError, redis.TimeoutError) as e:
        print(f"❌ Error de conexión a Redis: {e}")
        print("\n💡 Soluciones:")
        print("   1. Verifica que Redis esté instalado y corriendo")
        print("   2. En Windows, instala Memurai: https://www.memurai.com/get-memurai")
        print("   3. O usa WSL2: sudo apt install redis-server")
        print("   4. O usa Docker: docker run -d -p 6379:6379 redis:7-alpine")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == '__main__':
    success = check_redis()
    sys.exit(0 if success else 1)


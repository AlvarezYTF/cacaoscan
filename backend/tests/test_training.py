import os
import requests

# Load credentials from environment variables for security
# These should be set in a .env file or environment, not hardcoded
ADMIN_USERNAME = os.getenv('TEST_ADMIN_USERNAME', 'admin_training')
ADMIN_PASSWORD = os.getenv('TEST_ADMIN_PASSWORD', '')  # noqa: S106  # NOSONAR: S2068 - credentials from environment

# 1. Login
login_response = requests.post(
    'http://127.0.0.1:8000/api/v1/auth/login/',
    json={'username': ADMIN_USERNAME, 'password': ADMIN_PASSWORD}  # noqa: S106  # NOSONAR: S2068
)

print("Login response:", login_response.json())
print("\n---\n")

# 2. Obtener token
login_data = login_response.json()
token = login_data.get('access') or login_data.get('data', {}).get('access')

if not token:
    print("ERROR: No se pudo obtener el token")
    print("Estructura de respuesta:", login_data)
    exit(1)

print(f"Token obtenido: {token[:50]}...")

# 3. Crear entrenamiento
training_response = requests.post(
    'http://127.0.0.1:8000/api/v1/ml/train/',
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    },
    json={
        'job_type': 'regression',
        'model_name': 'resnet18',
        'dataset_size': 490,
        'epochs': 30,
        'batch_size': 16,
        'learning_rate': 0.001,
        'config_params': {
            'multi_head': False,
            'model_type': 'resnet18',
            'img_size': 224,
            'early_stopping_patience': 10,
            'save_best_only': True
        }
    }
)

print("\nTraining response:", training_response.json())
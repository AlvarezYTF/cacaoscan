"""
Script para ejecutar solo los tests que hemos corregido.
"""
import subprocess
import sys

# Tests corregidos que queremos verificar
corrected_tests = [
    "tests/test_ml_prediction_predict.py::TestCacaoPredictor::test_predict_segmentation_error",
    "tests/test_ml_prediction_predict.py::TestCacaoPredictor::test_predict_success",
    "tests/test_ml_segmentation_cropper.py::TestCacaoCropper::test_process_with_opencv_fallback",
    "tests/test_ml_segmentation_cropper.py::TestCreateCacaoCropper::test_create_cacao_cropper_with_yolo",
    "tests/test_api_services_analysis_service.py::TestAnalysisService::test_get_analysis_history_success",
    "tests/test_api_services_analysis_service.py::TestAnalysisService::test_get_analysis_details_success",
    "tests/test_api_services_analysis_service.py::TestAnalysisService::test_delete_analysis_success",
    "tests/test_api_services_analysis_service.py::TestAnalysisService::test_get_analysis_statistics_success",
    "tests/test_api_services_auth_password_service.py::TestPasswordService::test_forgot_password_success",
    "tests/test_api_services_auth_registration_service.py::TestRegistrationService::test_register_user_success",
    "tests/test_images_services_management_service.py::TestImageManagementService::test_get_image_details_success",
    "tests/test_images_services_management_service.py::TestImageManagementService::test_delete_image_success",
]

if __name__ == "__main__":
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "--tb=short",
        "--ignore=tests/test_api.py",
        "--ignore=tests/test_auth.py",
    ] + corrected_tests
    
    print("Ejecutando tests corregidos...")
    print(f"Comando: {' '.join(cmd)}")
    print("\n" + "="*80 + "\n")
    
    result = subprocess.run(cmd, cwd=".")
    sys.exit(result.returncode)


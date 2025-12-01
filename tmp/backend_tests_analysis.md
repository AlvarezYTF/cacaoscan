# Análisis de Tests del Backend - CacaoScan

## Metodología

1. Extraer todas las rutas de código fuente del backend desde `session-valid-tests.txt`
2. Mapear cada ruta a su test esperado según convenciones del proyecto
3. Verificar existencia de tests
4. Clasificar en: faltantes, existentes a refactorizar, existentes correctos

## Convenciones de Nombres de Tests

- **Services**: `backend/api/tests/test_services.py` (consolidado) o `backend/tests/test_api_services_*.py`
- **Views**: `backend/api/tests/test_views.py` (consolidado) o archivos específicos
- **Serializers**: `backend/api/tests/test_serializers_*.py`
- **Commands**: `backend/tests/test_*_commands_*.py`
- **Models**: `backend/api/tests/test_models.py` (consolidado) o `backend/tests/test_models_*.py`
- **ML Pipeline**: `backend/tests/test_ml_*.py`
- **Utils/Middleware**: `backend/tests/test_*_utils_*.py` o `backend/tests/test_*_middleware.py`
- **Tasks**: `backend/api/tests/test_tasks.py`

## Tabla 1 - Tests Requeridos que Faltan

| test_path | exists | in_session | action | reason |
|-----------|--------|------------|--------|--------|
| backend/api/tests/test_serializers_auth.py | ❌ | ✅ | CREATE | Serializers de auth listados en BLOQUE 4 |
| backend/api/tests/test_serializers_common.py | ❌ | ✅ | CREATE | Serializers comunes listados en BLOQUE 4 |
| backend/api/tests/test_serializers_finca.py | ❌ | ✅ | CREATE | Serializers de finca listados en BLOQUE 4 |
| backend/api/tests/test_serializers_image.py | ❌ | ✅ | CREATE | Serializers de imagen listados en BLOQUE 4 |
| backend/api/tests/test_serializers_ml.py | ❌ | ✅ | CREATE | Serializers ML listados en BLOQUE 4 |
| backend/personas/tests/test_serializers.py | ❌ | ✅ | CREATE | Serializers de personas listados en BLOQUE 4 |
| backend/api/tests/test_admin_audit_views.py | ❌ | ✅ | CREATE | Views admin/audit_views listadas en BLOQUE 3 |
| backend/api/tests/test_admin_config_views.py | ❌ | ✅ | CREATE | Views admin/config_views listadas en BLOQUE 3 |
| backend/api/tests/test_admin_email_views.py | ❌ | ✅ | CREATE | Views admin/email_views listadas en BLOQUE 3 |
| backend/api/tests/test_admin_task_status_views.py | ❌ | ✅ | CREATE | Views admin/task_status_views listadas en BLOQUE 3 |
| backend/api/tests/test_notification_views.py | ❌ | ✅ | CREATE | Views notifications listadas en BLOQUE 3 |
| backend/api/tests/test_ml_calibration_views.py | ❌ | ✅ | CREATE | Views ml/calibration_views listadas en BLOQUE 3 |
| backend/api/tests/test_ml_incremental_views.py | ❌ | ✅ | CREATE | Views ml/incremental_views listadas en BLOQUE 3 |
| backend/api/tests/test_ml_metrics_analysis_views.py | ❌ | ✅ | CREATE | Views ml/metrics_analysis_views listadas en BLOQUE 3 |
| backend/api/tests/test_ml_metrics_comparison_views.py | ❌ | ✅ | CREATE | Views ml/metrics_comparison_views listadas en BLOQUE 3 |
| backend/api/tests/test_ml_metrics_crud_views.py | ❌ | ✅ | CREATE | Views ml/metrics_crud_views listadas en BLOQUE 3 |
| backend/api/tests/test_ml_model_views.py | ❌ | ✅ | CREATE | Views ml/model_views listadas en BLOQUE 3 |
| backend/tests/test_api_commands_cancel_training.py | ❌ | ✅ | CREATE | Command cancel_training listado en BLOQUE 5 |
| backend/tests/test_api_commands_check_fk_lotes.py | ❌ | ✅ | CREATE | Command check_fk_lotes listado en BLOQUE 5 |
| backend/tests/test_api_commands_check_training.py | ❌ | ✅ | CREATE | Command check_training listado en BLOQUE 5 |
| backend/tests/test_api_commands_clean_dataset.py | ❌ | ✅ | CREATE | Command clean_dataset listado en BLOQUE 5 |
| backend/tests/test_api_commands_convert_cacao_images.py | ❌ | ✅ | CREATE | Command convert_cacao_images listado en BLOQUE 5 |
| backend/tests/test_api_commands_create_admin_user.py | ❌ | ✅ | CREATE | Command create_admin_user listado en BLOQUE 5 |
| backend/tests/test_api_commands_make_cacao_crops.py | ❌ | ✅ | CREATE | Command make_cacao_crops listado en BLOQUE 5 |
| backend/tests/test_fincas_commands_clean_orphaned_lotes.py | ❌ | ✅ | CREATE | Command fincas clean_orphaned_lotes listado en BLOQUE 5 |
| backend/tests/test_fincas_commands_fix_lote_foreign_key.py | ❌ | ✅ | CREATE | Command fincas fix_lote_foreign_key listado en BLOQUE 5 |
| backend/tests/test_catalogos_commands_seed_colombia.py | ❌ | ✅ | CREATE | Command catalogos seed_colombia listado en BLOQUE 5 |
| backend/tests/test_training_commands_calibrate_dataset_pixels.py | ❌ | ✅ | CREATE | Command training calibrate_dataset_pixels listado en BLOQUE 5 |
| backend/tests/test_training_commands_convert_cacao_images.py | ❌ | ✅ | CREATE | Command training convert_cacao_images listado en BLOQUE 5 |
| backend/tests/test_training_commands_init_api.py | ❌ | ✅ | CREATE | Command training init_api listado en BLOQUE 5 |
| backend/tests/test_ml_regression_augmentation.py | ❌ | ✅ | CREATE | ML regression/augmentation listado en BLOQUE 7 |
| backend/tests/test_ml_regression_evaluate.py | ❌ | ✅ | CREATE | ML regression/evaluate listado en BLOQUE 7 |
| backend/tests/test_ml_regression_hybrid_trainer.py | ❌ | ✅ | CREATE | ML regression/hybrid_trainer listado en BLOQUE 7 |
| backend/tests/test_ml_regression_incremental_train.py | ❌ | ✅ | CREATE | ML regression/incremental_train listado en BLOQUE 7 |
| backend/tests/test_ml_regression_optimized_models.py | ❌ | ✅ | CREATE | ML regression/optimized_models listado en BLOQUE 7 |
| backend/tests/test_ml_regression_predict.py | ❌ | ✅ | CREATE | ML regression/predict listado en BLOQUE 7 |
| backend/tests/test_ml_prediction_calibrated_predict.py | ❌ | ✅ | CREATE | ML prediction/calibrated_predict listado en BLOQUE 7 |
| backend/tests/test_ml_segmentation_infer_yolo_seg.py | ❌ | ✅ | CREATE | ML segmentation/infer_yolo_seg listado en BLOQUE 7 |
| backend/tests/test_ml_segmentation_processor.py | ❌ | ✅ | CREATE | ML segmentation/processor listado en BLOQUE 7 |
| backend/tests/test_ml_data_cacao_dataset.py | ❌ | ✅ | CREATE | ML data/cacao_dataset listado en BLOQUE 7 |
| backend/tests/test_ml_data_dataset_loader.py | ❌ | ✅ | CREATE | ML data/dataset_loader listado en BLOQUE 7 |
| backend/tests/test_ml_data_improved_dataloader.py | ❌ | ✅ | CREATE | ML data/improved_dataloader listado en BLOQUE 7 |
| backend/tests/test_ml_data_pixel_feature_extractor.py | ❌ | ✅ | CREATE | ML data/pixel_feature_extractor listado en BLOQUE 7 |
| backend/tests/test_ml_data_pixel_features_loader.py | ❌ | ✅ | CREATE | ML data/pixel_features_loader listado en BLOQUE 7 |
| backend/tests/test_ml_data_measurement_calibration.py | ❌ | ✅ | CREATE | ML data/measurement/calibration listado en BLOQUE 7 |
| backend/tests/test_ml_pipeline_hybrid_training.py | ❌ | ✅ | CREATE | ML pipeline/hybrid_training listado en BLOQUE 7 |
| backend/tests/test_ml_utils_early_stopping.py | ❌ | ✅ | CREATE | ML utils/early_stopping listado en BLOQUE 7 |
| backend/tests/test_ml_utils_io.py | ❌ | ✅ | CREATE | ML utils/io listado en BLOQUE 7 |
| backend/tests/test_ml_utils_logs.py | ❌ | ✅ | CREATE | ML utils/logs listado en BLOQUE 7 |
| backend/tests/test_ml_utils_losses.py | ❌ | ✅ | CREATE | ML utils/losses listado en BLOQUE 7 |
| backend/tests/test_ml_utils_ml_validators.py | ❌ | ✅ | CREATE | ML utils/ml_validators listado en BLOQUE 7 |
| backend/tests/test_ml_utils_model_imports.py | ❌ | ✅ | CREATE | ML utils/model_imports listado en BLOQUE 7 |
| backend/tests/test_core_utils_cache_helpers.py | ❌ | ✅ | CREATE | Core utils/cache_helpers listado en BLOQUE 8 |
| backend/tests/test_core_utils_response_helpers.py | ❌ | ✅ | CREATE | Core utils/response_helpers listado en BLOQUE 8 |
| backend/tests/test_core_utils_security.py | ❌ | ✅ | CREATE | Core utils/security listado en BLOQUE 8 |
| backend/tests/test_api_utils_decorators.py | ❌ | ✅ | CREATE | API utils/decorators listado en BLOQUE 8 |
| backend/tests/test_api_utils_ml_helpers.py | ❌ | ✅ | CREATE | API utils/ml_helpers listado en BLOQUE 8 |
| backend/tests/test_api_utils_pagination.py | ❌ | ✅ | CREATE | API utils/pagination listado en BLOQUE 8 |
| backend/tests/test_api_utils_model_imports.py | ❌ | ✅ | CREATE | API utils/model_imports listado en BLOQUE 8 |
| backend/tests/test_api_middleware.py | ❌ | ✅ | CREATE | API middleware listado en BLOQUE 8 |
| backend/tests/test_api_realtime_middleware.py | ❌ | ✅ | CREATE | API realtime_middleware listado en BLOQUE 8 |
| backend/tests/test_api_realtime_service.py | ❌ | ✅ | CREATE | API realtime_service listado en BLOQUE 8 |
| backend/tests/test_api_cache_config.py | ❌ | ✅ | CREATE | API cache_config listado en BLOQUE 8 |
| backend/api/tests/test_tasks.py | ❌ | ✅ | CREATE | Tasks listadas en BLOQUE 9 |
| backend/tests/test_images_views_batch_process_views.py | ❌ | ✅ | CREATE | Images views batch/batch_process_views listado en BLOQUE 10 |
| backend/tests/test_images_views_batch_upload_views.py | ❌ | ✅ | CREATE | Images views batch/batch_upload_views listado en BLOQUE 10 |
| backend/tests/test_images_views_admin_bulk_views.py | ❌ | ✅ | CREATE | Images views admin/bulk_views listado en BLOQUE 10 |
| backend/tests/test_images_views_admin_crud_views.py | ❌ | ✅ | CREATE | Images views admin/crud_views listado en BLOQUE 10 |
| backend/tests/test_images_views_admin_list_views.py | ❌ | ✅ | CREATE | Images views admin/list_views listado en BLOQUE 10 |
| backend/tests/test_images_views_user_crud_views.py | ❌ | ✅ | CREATE | Images views user/crud_views listado en BLOQUE 10 |
| backend/tests/test_images_views_user_list_views.py | ❌ | ✅ | CREATE | Images views user/list_views listado en BLOQUE 10 |
| backend/tests/test_images_views_user_scan_views.py | ❌ | ✅ | CREATE | Images views user/scan_views listado en BLOQUE 10 |
| backend/tests/test_images_views_export_views.py | ❌ | ✅ | CREATE | Images views export/export_views listado en BLOQUE 10 |
| backend/tests/test_images_views_user_stats_views.py | ❌ | ✅ | CREATE | Images views user/stats_views listado en BLOQUE 10 |
| backend/tests/test_images_views_admin_stats_views.py | ❌ | ✅ | CREATE | Images views admin/stats_views listado en BLOQUE 10 |
| backend/tests/test_images_views_mixins.py | ❌ | ✅ | CREATE | Images views/mixins listado en BLOQUE 10 |

## Tabla 2 - Tests Existentes que Deben Refactorizarse

| test_path | in_session | issues_detected | action | reason |
|-----------|------------|-----------------|--------|--------|
| backend/api/tests/test_services.py | ✅ | Coverage incompleta, falta tests para profile_service, stats_service | REFACTOR | Cubre algunos servicios pero faltan profile_service, stats_service del BLOQUE 2 |
| backend/api/tests/test_views.py | ✅ | Coverage incompleta, solo cubre auth views, faltan admin y ML views | REFACTOR | Solo cubre vistas de autenticación, faltan todas las vistas del BLOQUE 3 |
| backend/api/tests/test_models.py | ✅ | Coverage incompleta, solo cubre modelos de api, faltan otros modelos | REFACTOR | Solo cubre api.models, faltan modelos de fincas_app, ml, core, auth_app, reports, training, audit, images_app, personas, catalogos del BLOQUE 6 |
| backend/api/tests/test_fincas.py | ✅ | Verificar cobertura completa | REVIEW | Listado en BLOQUE 20 y SESSION_BACKEND_TESTS, necesita revisión |
| backend/api/tests/test_images_endpoints.py | ✅ | Verificar cobertura completa | REVIEW | Listado en BLOQUE 20 y SESSION_BACKEND_TESTS, necesita revisión |
| backend/api/tests/test_integration.py | ✅ | Verificar cobertura completa | REVIEW | Listado en BLOQUE 20 y SESSION_BACKEND_TESTS, necesita revisión |
| backend/api/tests/test_constants.py | ✅ | Archivo de constantes, verificar uso correcto | REVIEW | Listado en BLOQUE 20 y SESSION_BACKEND_TESTS |
| backend/api/tests/test_sonarqube/test_error_response_details.py | ✅ | Test específico de SonarQube | REVIEW | Listado en BLOQUE 20 y SESSION_BACKEND_TESTS |
| backend/api/tests/test_sonarqube/test_redundant_elif.py | ✅ | Test específico de SonarQube | REVIEW | Listado en SESSION_BACKEND_TESTS |
| backend/api/tests/test_sonarqube/test_simple_verification.py | ✅ | Test específico de SonarQube | REVIEW | Listado en SESSION_BACKEND_TESTS |
| backend/api/tests/test_sonarqube/test_model_metrics_error_response.py | ✅ | Test específico de SonarQube | REVIEW | Listado en BLOQUE 20 |
| backend/api/management/commands/test_model.py | ✅ | Command de test, verificar funcionalidad | REVIEW | Listado en BLOQUE 5 y SESSION_BACKEND_TESTS |
| backend/scripts/test_model.py | ✅ | Script de test, verificar funcionalidad | REVIEW | Listado en BLOQUE 20 y SESSION_BACKEND_TESTS |
| backend/api/management/commands/test_predictions.py | ✅ | Command de test, verificar funcionalidad | REVIEW | Listado en SESSION_BACKEND_TESTS |
| backend/scripts/test_predictions.py | ✅ | Script de test, verificar funcionalidad | REVIEW | Listado en SESSION_BACKEND_TESTS |
| backend/tests/test_api_services_analysis_service.py | ✅ | Test parcial, verificar cobertura completa | REVIEW | Existe pero necesita verificación de cobertura completa |
| backend/tests/test_api_services_auth_login_service.py | ✅ | Test parcial, verificar cobertura completa | REVIEW | Existe pero necesita verificación de cobertura completa |
| backend/tests/test_api_services_auth_password_service.py | ✅ | Test parcial, verificar cobertura completa | REVIEW | Existe pero necesita verificación de cobertura completa |
| backend/tests/test_ml_regression_scalers.py | ✅ | Test parcial, verificar cobertura completa | REVIEW | Existe pero necesita verificación de cobertura completa |
| backend/tests/test_ml_segmentation_cropper.py | ✅ | Test parcial, verificar cobertura completa | REVIEW | Existe pero necesita verificación de cobertura completa |
| backend/tests/test_ml_prediction_predict.py | ✅ | Test parcial, verificar cobertura completa | REVIEW | Existe pero necesita verificación de cobertura completa |

## Notas Importantes

1. **BLOQUE 1 (Init files)**: No requieren tests según el documento
2. **BLOQUE 18 (Templates email)**: No requieren tests unitarios, son templates HTML
3. **BLOQUE 19 (Django admin)**: No están explícitamente listados para tests
4. **Tests duplicados en session-valid-tests.txt**: Se eliminaron duplicados en el análisis
5. **Convención de nombres**: Se sigue la convención observada en el proyecto donde los tests están en `backend/api/tests/` para tests de API y `backend/tests/` para tests más generales

## Resumen

- **Tests a crear**: ~75 archivos de test nuevos
- **Tests a refactorizar/revisar**: ~20 archivos de test existentes
- **Total de trabajo**: ~95 archivos de test a procesar


# Plan: Aumentar Cobertura de Tests Frontend

## Objetivo
Aumentar la cobertura de código extendiendo tests existentes para archivos que ya tienen tests pero no alcanzan 100%, y crear tests nuevos para archivos con 0% coverage. Excluir automáticamente solo archivos que no deben testearse (entry points, ejemplos, barrel exports). Asegurar que SonarQube tenga 0 issues excepto cobertura.

## Estrategia General

### 1. Exclusión de Archivos No Testeables
- Agregar exclusiones en `frontend/vitest.config.js` SOLO para:
  - Entry points: `src/App.vue`, `src/main.js`
  - Archivos de ejemplo: `src/components/common/BaseFormField.example.vue`
  - Barrel exports: `src/services/api/index.js`
- Actualizar `sonar-project.properties` con las mismas exclusiones

### 2. Extensión de Tests Existentes
Para cada archivo con tests pero cobertura < 100%:
- Identificar líneas exactas no cubiertas del reporte
- Analizar la lógica de esas líneas (branches, métodos, edge cases)
- Extender el test existente agregando casos específicos
- Mantener el estilo y estructura de los tests existentes
- Aplicar principios KISS, DRY, SOLID

### 3. Creación de Tests Nuevos
Para cada archivo con 0% coverage:
- Crear archivo de test siguiendo el patrón existente
- Cubrir funcionalidad principal, props, eventos, métodos
- Aplicar principios KISS, DRY, SOLID, Clean Code
- Mantener consistencia con tests existentes

### 4. Limpieza SonarQube
- Revisar y corregir code smells en tests nuevos/extendidos
- Asegurar formato correcto para evitar violaciones SonarJS
- Verificar que no se introduzcan nuevos issues

## Archivos a Excluir (No Testeables)

- `src/App.vue` - Entry point de la aplicación
- `src/main.js` - Entry point de la aplicación
- `src/components/common/BaseFormField.example.vue` - Archivo de ejemplo
- `src/services/api/index.js` - Barrel export

## Archivos a Extender (Tests Existentes < 100%)

### Componentes AdminAgricultorComponents
- **CreateFarmerModal.vue** (77.64% → 100%)
- **EditFarmerModal.vue** (80.91% → 100%)
- **DataTable.vue** (85.15% → 100%)
- **FarmerDetailModal.vue** (84.88% → 100%)
- **FarmersTable.vue** (93.08% → 100%)
- **FarmersStatsCards.vue** (97.5% → 100%)

### Componentes AdminAnalisisComponents
- **BatchInfoForm.vue** (90% → 100%)
- **CameraCapture.vue** (80.9% → 100%)
- **ImageUploader.vue** (74.3% → 100%)

### Componentes AdminConfigComponents
- **InputField.vue** (100% statements, 42.85% branch → 100%)
- **LoadingSkeleton.vue** (88.46% → 100%)
- **SelectField.vue** (88.23% → 100%)

### Componentes AdminUserComponents
- **UserFormModal.vue** (75.26% → 100%)
- **UserDetailsModal.vue** (68.42% → 100%)
- **UserActivityModal.vue** (53.56% → 100%)
- **UsersTable.vue** (92.17% → 100%)

### Componentes Common
- **BaseModal.vue** (70.27% → 100%)
- **BaseSearchBar.vue** (85.1% → 100%)
- **GlobalLoader.vue** (66.12% → 100%)
- **Pagination.vue** (93.43% → 100%)
- **SessionExpiredModal.vue** (92.45% → 100%)
- **BaseStatsCard.vue** (93.24% → 100%)
- **BaseSectionCard.vue** (100% statements, 50% branch → 100%)
- **BaseSpinner.vue** (100% statements, 50% branch → 100%)

### FincasViewComponents
- **FincaDetailModal.vue** (93.05% → 100%)
- **FincaList.vue** (100% statements, 14.28% functions → 100%)
- **FincasFilters.vue** (84.09% → 100%)
- **FincasHeader.vue** (100% statements, 57.14% branch → 100%)

### Composables
- **useAdminView.js** (81.32% → 100%)
- **useAnalysis.js** (83.83% → 100%)
- **useAudit.js** (68.88% → 100%)
- **useAuth.js** (55.87% → 100%)
- **useAuthForm.js** (85.61% → 100%)
- **useCatalogos.js** (81.25% → 100%)
- **useChart.js** (60.07% → 100%)
- **useChartConfig.js** (93.75% → 100%)
- **useConfigStoreWrapper.js** (76.41% → 100%)
- **useDashboardMetrics.js** (64.22% → 100%)
- **useDashboardStats.js** (40.3% → 100%)
- **useDataset.js** (82.02% → 100%)
- **useDateFormatting.js** (96.18% → 100%)
- **useEmailValidation.js** (95.5% → 100%)
- **useFileUpload.js** (90.43% → 100%)
- **useFilterableStore.js** (87.09% → 100%)
- **useFincas.js** (84.18% → 100%)
- **useForm.js** (63.04% → 100%)
- **useFormValidation.js** (62.14% → 100%)
- **useImageHandling.js** (67.72% → 100%)
- **useImageStats.js** (63.58% → 100%)
- **useLotes.js** (53.27% → 100%)
- **useModal.js** (98.27% → 100%)
- **usePaginableStore.js** (95.61% → 100%)
- **usePagination.js** (67.71% → 100%)
- **usePasswordValidation.js** (95.28% → 100%)
- **usePeriodDates.js** (92.52% → 100%)
- **usePrediction.js** (51.7% → 100%)
- **usePredictionFlow.js** (72.05% → 100%)
- **usePreferencesWrapperConfig.js** (98% → 100%)
- **useQuickActions.js** (94.88% → 100%)
- **useRecentActivity.js** (71.69% → 100%)
- **useReports.js** (20.99% → 100%)
- **useSearchFilter.js** (97.61% → 100%)
- **useSidebarNavigation.js** (84.61% → 100%)
- **useStoreBase.js** (96.36% → 100%)
- **useTable.js** (96.25% → 100%)
- **useWebSocket.js** (71.13% → 100%)
- **useWebSocketBase.js** (73.58% → 100%)
- **useWebSocketManager.js** (91.17% → 100%)

### Services
- **adminApi.js** (82.05% → 100%)
- **api.js** (39.31% → 100%)
- **apiClient.js** (94.57% → 100%)
- **apiErrorHandler.js** (98% → 100%)
- **auditApi.js** (99.72% → 100%)
- **authApi.js** (88.73% → 100%)
- **catalogosApi.js** (94.49% → 100%)
- **configApi.js** (100% statements, 95.23% branch → 100%)
- **dashboardStatsService.js** (84.56% → 100%)
- **datasetApi.js** (97.74% → 100%)
- **fincasApi.js** (96.13% → 100%)
- **httpClient.js** (75.93% → 100%)
- **lotesApi.js** (97.08% → 100%)
- **predictionApi.js** (87.47% → 100%)
- **reportsApi.js** (84.39% → 100%)
- **reportsService.js** (97.58% → 100%)

### Stores
- **admin.js** (69.39% → 100%)
- **audit.js** (87.95% → 100%)
- **auth.js** (62.01% → 100%)
- **config.js** (97.39% → 100%)
- **fincas.js** (100% statements, 51.06% branch → 100%)
- **notifications.js** (85.56% → 100%)
- **prediction.js** (95.47% → 100%)
- **reports.js** (88.58% → 100%)

### Router
- **guardFactories.js** (98.68% → 100%)
- **guards.js** (98.7% → 100%)
- **index.js** (52.01% → 100%)

### Utils
- **apiConfig.js** (81.29% → 100%)
- **formDataUtils.js** (99.45% → 100%)
- **formFieldConfigs.js** (81.42% → 100%)
- **formatters.js** (99% → 100%)
- **imageValidationUtils.js** (92.59% → 100%)
- **logger.js** (67.81% → 100%)
- **personaDataMapper.js** (97.46% → 100%)
- **security.js** (97.09% → 100%)

### Views
- **AccessDenied.vue** (82.9% → 100%)
- **FincaDetailView.vue** (68.46% → 100%)
- **LoteAnalisisView.vue** (89.47% → 100%)
- **PasswordResetConfirm.vue** (80.82% → 100%)
- **PredictionView.vue** (74.87% → 100%)
- **Reportes.vue** (71.4% → 100%)
- **ReportsManagement.vue** (63.71% → 100%)
- **SubirDatosEntrenamiento.vue** (79.62% → 100%)
- **UploadImagesView.vue** (59.7% → 100%)
- **UserPrediction.vue** (83.89% → 100%)
- **VerifyPrompt.vue** (63.3% → 100%)
- **AdminAgricultores.vue** (53.2% → 100%)
- **AdminConfiguracion.vue** (79.57% → 100%)
- **AdminDashboard.vue** (72.46% → 100%)
- **AdminTraining.vue** (73.13% → 100%)
- **AdminUsuarios.vue** (50.44% → 100%)
- **AgricultorConfiguracion.vue** (45.16% → 100%)
- **AgricultorHistorial.vue** (88.04% → 100%)
- **Analisis.vue** (80.39% → 100%)
- **NotFound.vue** (94% → 100%)

## Archivos a Crear Tests Nuevos (0% coverage)

### Componentes Admin
- **CreateFincaForm.vue** - Crear test completo
- **LoadingSpinner.vue** - Crear test completo

### Componentes Agricultor Configuracion
- **BackupSyncSection.vue** - Crear test completo
- **FincasSection.vue** - Crear test completo
- **NotificationsSection.vue** - Crear test completo
- **ScanPreferencesSection.vue** - Crear test completo
- **VisualSettingsSection.vue** - Crear test completo

### Componentes Analysis
- **AnalysisActions.vue** - Crear test completo
- **AnalysisHeader.vue** - Crear test completo
- **AnalysisSummaryCard.vue** - Crear test completo
- **BatchInfoCard.vue** - Crear test completo
- **ImageGallery.vue** - Crear test completo
- **ImageModal.vue** - Crear test completo
- **DetalleAnalisis.vue** (32.43% → 100%) - Extender test existente
- **PredictionMethodSelector.vue** (68.38% → 100%) - Extender test existente
- **YoloResultsCard.vue** (66.3% → 100%) - Extender test existente

### Componentes Audit
- **AuditCard.vue** - Crear test completo
- **AuditDetailsModal.vue** - Crear test completo
- **AuditStatsModal.vue** - Crear test completo
- **AuditTable.vue** - Crear test completo
- **AuditTimeline.vue** - Crear test completo

### Componentes Auth
- **PasswordResetConfirmation.vue** - Crear test completo
- **PasswordResetForm.vue** - Crear test completo

### Componentes Charts
- **BarChart.vue** - Crear test completo
- **DashboardWidget.vue** - Crear test completo
- **LineChart.vue** - Crear test completo
- **PieChart.vue** - Crear test completo
- **StatsGrid.vue** - Crear test completo
- **TrendChart.vue** - Crear test completo

### Componentes Common
- **BaseAlert.vue** - Crear test completo
- **BaseAnalysisActions.vue** - Crear test completo
- **BaseAnalysisHeader.vue** - Crear test completo
- **BaseAnalysisSummaryCard.vue** - Crear test completo
- **BaseAppLayout.vue** - Crear test completo
- **BaseAuthForm.vue** - Crear test completo
- **BaseBatchInfoCard.vue** - Crear test completo
- **BaseChart.vue** - Crear test completo
- **BaseConfirmModal.vue** - Crear test completo
- **BaseDashboardHeader.vue** - Crear test completo
- **BaseDashboardWidget.vue** - Crear test completo
- **BaseDataTable.vue** - Crear test completo
- **BaseDetailView.vue** - Crear test completo
- **BaseFincaCard.vue** - Crear test completo
- **BaseFincaFilters.vue** - Crear test completo
- **BaseFincaList.vue** - Crear test completo
- **BaseFincasHeader.vue** - Crear test completo
- **BaseFincasSection.vue** - Crear test completo
- **BaseForm.vue** - Crear test completo
- **BaseHeader.vue** - Crear test completo
- **BaseHero.vue** - Crear test completo
- **BaseImageModal.vue** - Crear test completo
- **BaseInputField.vue** - Crear test completo
- **BaseLandingLayout.vue** - Crear test completo
- **BaseLandingSection.vue** - Crear test completo
- **BaseLoadingSkeleton.vue** - Crear test completo
- **BaseLocationMap.vue** - Crear test completo
- **BasePreferences.vue** - Crear test completo
- **BasePreferencesWrapper.vue** - Crear test completo
- **BaseProgressIndicator.vue** - Crear test completo
- **BaseQuickActions.vue** - Crear test completo
- **BaseScanPreferences.vue** - Crear test completo
- **BaseSearchInput.vue** - Crear test completo
- **BaseSection.vue** - Crear test completo
- **BaseSelectField.vue** - Crear test completo
- **BaseStaticPage.vue** - Crear test completo
- **BaseTable.vue** - Crear test completo
- **BaseTimeline.vue** - Crear test completo
- **BaseUploadSection.vue** - Crear test completo
- **BaseVisualSettings.vue** - Crear test completo
- **ErrorAlert.vue** - Crear test completo
- **FormField.vue** - Crear test completo
- **PageHeader.vue** - Crear test completo
- **PersonFormFields.vue** (100% statements, 0% branch → 100%) - Extender test existente
- **FincaCardActions.vue** - Crear test completo

### Componentes Dashboard
- **DashboardHeader.vue** - Crear test completo
- **QuickActions.vue** - Crear test completo
- **RecentAnalyses.vue** - Crear test completo
- **StatsOverview.vue** - Crear test completo
- **SummaryCard.vue** - Crear test completo
- **UploadSection.vue** - Crear test completo

### Componentes Legal
- **LegalLayout.vue** - Crear test completo

### Componentes Notifications
- **NotificationBell.vue** - Crear test completo
- **NotificationCenter.vue** - Crear test completo

### Componentes Reportes
- **ActionButton.vue** - Crear test completo
- **ReportDownloadButton.vue** (42.85% → 100%) - Extender test existente
- **ReportsTable.vue** (86.36% → 100%) - Extender test existente
- **ReportsTimeline.vue** (71.92% → 100%) - Extender test existente
- **StatsCard.vue** (90.9% → 100%) - Extender test existente
- **ReportPreviewModal.vue** (58.53% → 100%) - Extender test existente

### Componentes Training
- **ImageUploadCard.vue** - Crear test completo
- **SamplesTable.vue** - Crear test completo
- **TrainingProgress.vue** - Crear test completo

### Componentes User
- **PredictionResults.vue** (61.73% → 100%) - Extender test existente

### Router
- **index.js** (52.01% → 100%) - Extender test existente

### Views
- **AuditoriaView.vue** - Crear test completo
- **EmailVerification.vue** - Crear test completo
- **FincaLotesView.vue** - Crear test completo
- **LoteDetailView.vue** - Crear test completo
- **PasswordReset.vue** - Crear test completo
- **ResetPassword.vue** - Crear test completo
- **LegalTermsView.vue** - Crear test completo
- **PrivacyPolicyView.vue** - Crear test completo
- **VerifyEmailView.vue** - Crear test completo

## Tareas de Implementación

1. **Actualizar configuración de coverage**
   - Modificar `frontend/vitest.config.js` para excluir solo archivos no testeables
   - Actualizar `sonar-project.properties` con las mismas exclusiones

2. **Extender tests de componentes existentes**
   - Componentes AdminAgricultorComponents
   - Componentes AdminAnalisisComponents
   - Componentes AdminConfigComponents
   - Componentes AdminUserComponents
   - Componentes Common
   - FincasViewComponents

3. **Crear tests nuevos para componentes sin tests**
   - Componentes Admin
   - Componentes Agricultor Configuracion
   - Componentes Analysis
   - Componentes Audit
   - Componentes Auth
   - Componentes Charts
   - Componentes Common
   - Componentes Dashboard
   - Componentes Legal
   - Componentes Notifications
   - Componentes Reportes
   - Componentes Training
   - Componentes User

4. **Extender tests de composables**
   - Prioridad alta: useAuth, useForm, useFormValidation, usePrediction, useReports, useDashboardStats, useChart
   - Resto de composables

5. **Extender tests de services**
   - Prioridad alta: api.js, apiClient.js, httpClient.js, adminApi.js, authApi.js, predictionApi.js
   - Resto de services

6. **Extender tests de stores**
   - auth.js, admin.js, reports.js, notifications.js, prediction.js, audit.js, config.js, fincas.js

7. **Extender tests de router**
   - index.js, guardFactories.js, guards.js

8. **Extender tests de utils**
   - apiConfig.js, formDataUtils.js, formFieldConfigs.js, formatters.js, imageValidationUtils.js, logger.js, personaDataMapper.js, security.js

9. **Extender tests de views**
   - Todas las views con tests existentes

10. **Crear tests nuevos para views sin tests**
    - AuditoriaView, EmailVerification, FincaLotesView, LoteDetailView, PasswordReset, ResetPassword, LegalTermsView, PrivacyPolicyView, VerifyEmailView

11. **Verificación y limpieza SonarQube**
    - Ejecutar tests y verificar cobertura
    - Revisar y corregir code smells en tests
    - Asegurar formato correcto para SonarJS

## Notas Importantes

- Crear tests nuevos para archivos con 0% coverage
- Extender tests existentes para alcanzar 100%
- Excluir SOLO entry points, ejemplos y barrel exports
- Mantener estilo y estructura de tests existentes
- Aplicar principios KISS, DRY, SOLID, Clean Code
- Cubrir líneas exactas, branches, métodos y edge cases
- Asegurar que SonarQube tenga 0 issues excepto cobertura


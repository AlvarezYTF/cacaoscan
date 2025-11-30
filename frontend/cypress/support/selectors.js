/**
 * Centralized selectors for Cypress tests
 * Provides reusable selectors to avoid duplication
 */

export const SELECTORS = {
  // Buttons
  buttons: {
    submit: '[data-cy="submit-button"]',
    cancel: '[data-cy="cancel-button"]',
    delete: '[data-cy="delete-button"]',
    edit: '[data-cy="edit-button"]',
    save: '[data-cy="save-button"]',
    back: '[data-cy="back-button"]',
    next: '[data-cy="next-button"]',
    previous: '[data-cy="previous-button"]',
    login: '[data-cy="login-button"]',
    logout: '[data-cy="logout-button"]',
    refresh: '[data-cy="refresh-button"]',
    export: '[data-cy="export-button"]',
    import: '[data-cy="import-button"]',
    filter: '[data-cy="filter-button"]',
    clear: '[data-cy="clear-button"]',
    search: '[data-cy="search-button"]',
    close: '[data-cy="close-button"]',
    confirm: '[data-cy="confirm-button"]'
  },

  // Inputs
  inputs: {
    email: '[data-cy="email-input"]',
    // NOSONAR: S2068 - This is a CSS selector string for test automation, not a hardcoded password
    password: '[data-cy="password-input"]',
    // NOSONAR: S2068 - This is a CSS selector string for test automation, not a hardcoded password
    confirmPassword: '[data-cy="confirm-password-input"]',
    nombre: '[data-cy="nombre-input"]',
    search: '[data-cy="search-input"]',
    filter: '[data-cy="filter-input"]',
    fileUpload: 'input[type="file"]',
    datePicker: '[data-cy="date-picker"]',
    select: '[data-cy="select-input"]'
  },

  // Forms
  forms: {
    login: '[data-cy="login-form"]',
    register: '[data-cy="register-form"]',
    finca: '[data-cy="finca-form"]',
    lote: '[data-cy="lote-form"]',
    profile: '[data-cy="profile-form"]',
    // NOSONAR: S2068 - This is a CSS selector string for test automation, not a hardcoded password
    passwordReset: '[data-cy="password-reset-form"]',
    prediction: '[data-cy="prediction-form"]'
  },

  // Form fields (finca)
  finca: {
    nombre: '[data-cy="finca-nombre"]',
    ubicacion: '[data-cy="finca-ubicacion"]',
    area: '[data-cy="finca-area"]',
    descripcion: '[data-cy="finca-descripcion"]'
  },

  // Form fields (lote)
  lote: {
    nombre: '[data-cy="lote-nombre"]',
    area: '[data-cy="lote-area"]',
    variedad: '[data-cy="lote-variedad"]',
    edad: '[data-cy="lote-edad"]',
    descripcion: '[data-cy="lote-descripcion"]'
  },

  // Tables
  tables: {
    dataTable: '[data-cy="data-table"]',
    usersTable: '[data-cy="users-table"]',
    auditTable: '[data-cy="audit-table"]',
    reportsTable: '[data-cy="reports-table"]',
    dashboardTables: '[data-cy="dashboard-tables"]',
    tableRow: '[data-cy="table-row"]',
    tableHeader: '[data-cy="table-header"]',
    tableCell: '[data-cy="table-cell"]',
    pagination: '[data-cy="pagination"]',
    pageSize: '[data-cy="page-size-selector"]'
  },

  // Navigation
  navigation: {
    sidebar: '[data-cy="sidebar"]',
    navLink: '[data-cy="nav-link"]',
    breadcrumb: '[data-cy="breadcrumb"]',
    menu: '[data-cy="menu"]',
    menuItem: '[data-cy="menu-item"]'
  },

  // Notifications
  notifications: {
    container: '[data-cy="notification-container"]',
    success: '[data-cy="notification-success"]',
    error: '[data-cy="notification-error"]',
    warning: '[data-cy="notification-warning"]',
    info: '[data-cy="notification-info"]',
    bell: '[data-cy="notification-bell"]',
    center: '[data-cy="notification-center"]'
  },

  // Dashboard
  dashboard: {
    statsCard: '[data-cy="stats-card"]',
    chart: '[data-cy="chart"]',
    widget: '[data-cy="dashboard-widget"]',
    table: '[data-cy="dashboard-table"]'
  },

  // Prediction
  prediction: {
    methodSelector: '[data-cy="prediction-method-selector"]',
    imageUpload: '[data-cy="prediction-image-upload"]',
    results: '[data-cy="prediction-results"]',
    status: '[data-cy="analysis-status"]',
    yoloResults: '[data-cy="yolo-results-card"]'
  },

  // Modals
  modals: {
    confirm: '[data-cy="confirm-modal"]',
    delete: '[data-cy="delete-modal"]',
    edit: '[data-cy="edit-modal"]',
    view: '[data-cy="view-modal"]',
    close: '[data-cy="modal-close"]'
  },

  // Loading states
  loading: {
    spinner: '[data-cy="loading-spinner"]',
    skeleton: '[data-cy="loading-skeleton"]',
    progress: '[data-cy="loading-progress"]'
  },

  // Error states
  errors: {
    accessDenied: '[data-cy="access-denied-message"]',
    notFound: '[data-cy="not-found-message"]',
    errorMessage: '[data-cy="error-message"]',
    fieldError: '[data-cy="field-error"]'
  },

  // Data loaded indicator
  dataLoaded: '[data-cy="data-loaded"]'
}


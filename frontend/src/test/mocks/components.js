/**
 * Component mocks for tests
 */

/**
 * Creates default stubs configuration
 * @returns {Object} Default stubs object
 */
export function createDefaultStubs() {
  return {
    'router-link': true,
    'router-view': true,
    'AdminSidebar': true,
    'KPICards': true,
    'DashboardCharts': true,
    'DashboardTables': true,
    'DashboardAlerts': true
  }
}

/**
 * AdminDashboard component mock configurations
 * These are templates that can be used in vi.mock() calls
 */
export const adminDashboardComponentMocks = {
  Sidebar: {
    default: { name: 'AdminSidebar', template: '<div>Sidebar</div>' }
  },
  KPICards: {
    default: { name: 'KPICards', template: '<div>KPI Cards</div>' }
  },
  DashboardCharts: {
    default: { name: 'DashboardCharts', template: '<div>Charts</div>' }
  },
  DashboardTables: {
    default: { name: 'DashboardTables', template: '<div>Tables</div>' }
  },
  DashboardAlerts: {
    default: { name: 'DashboardAlerts', template: '<div>Alerts</div>' }
  }
}

/**
 * Composable mock configurations
 */
export const composableMocks = {
  useWebSocket: {
    useWebSocket: () => ({
      connect: () => {},
      disconnect: () => {},
      send: () => {}
    })
  }
}

/**
 * SweetAlert2 mock configuration
 */
export const sweetAlert2Mock = {
  default: {
    fire: () => {},
    Swal: {
      fire: () => {}
    }
  }
}


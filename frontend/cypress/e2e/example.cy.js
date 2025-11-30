// https://on.cypress.io/api

describe('My First Test', () => {
  it('visits the app root url', () => {
    cy.visit('/')
    // Verificar que la página carga correctamente
    cy.get('body').should('be.visible')
    // Verificar que hay algún contenido de la aplicación
    cy.get('body').should('not.be.empty')
  })
})

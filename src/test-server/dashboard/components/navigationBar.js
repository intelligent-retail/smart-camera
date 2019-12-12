import React from 'react'
import { Container, Navbar } from 'react-bootstrap'

const NavigationBar = () => (
  <Container>
    <Navbar className="fixed-top navbar-dark bg-primary">
      <Navbar.Brand href="/">Dashboard</Navbar.Brand>
    </Navbar>
  </Container>
)

export default NavigationBar

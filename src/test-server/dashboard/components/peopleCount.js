import React from 'react'
import { Card } from 'react-bootstrap'

const PeopleCount = ({ cameraId, name, count }) => {
  if (!cameraId) {
    return null
  }

  const countDisplay = count ? count : '-'

  return (
    <Card>
      <Card.Body>
        <h5 className="card-title">{`Camera: ${name}`}</h5>
        <h1 className="card-text">{countDisplay}</h1>
      </Card.Body>
    </Card>
  )
}

export default PeopleCount

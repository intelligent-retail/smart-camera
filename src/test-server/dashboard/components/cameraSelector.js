import Select from 'react-select'
import React from 'react'
import ImageMapper from 'react-image-mapper'

const NoMapSelector = (cameras, onCameraChanged) => {
  if (cameras.length === 0) {
    return null
  }

  const options = []
  for (let i = 0; i < cameras.length; i++) {
    options.push(
      {
        value: cameras[i],
        label: cameras[i].name,
      },
    )
  }

  const handle = (selectedOption) => {
    onCameraChanged(selectedOption.value)
  }

  return (
    <Select
      onChange={handle}
      options={options}
    />
  )
}

const MapSelector = (cameras, imageMap, onCameraChanged) => {
  const areas = imageMap.areas.map(area => {
    return {
      _id: area.id,
      shape: 'rect',
      coords: area.coords,
    }
  })

  const onClicked = (area) => {
    const cameraId = area._id
    const camera = cameras.find(c => c.id === cameraId)
    onCameraChanged(camera)
  }

  return (
      <ImageMapper
        imgWidth={imageMap.image.width}
        width={360}
        onClick={onClicked}
        src={imageMap.image.src}
        map={{
          name: 'map',
          areas: areas,
        }}
      />
  )
}

const CameraSelector = ({ cameras, imageMap, onCameraChanged }) => {
  if (cameras.length === 0) {
    return null
  }

  if (imageMap && imageMap.image && imageMap.areas) {
    return MapSelector(cameras, imageMap, onCameraChanged)
  }

  return NoMapSelector(cameras, onCameraChanged)
}

export default CameraSelector

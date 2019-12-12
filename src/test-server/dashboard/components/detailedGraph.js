import React from 'react'
import { Bar } from 'react-chartjs-2'

const DetailedGraph = ({ camera, result }) => {
  if (!camera) {
    return null
  }

  const data = {
    labels: ['Unknown', '0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70~'],
    datasets: [
      {
        label: 'Female',
        backgroundColor: 'rgba(255,99,132,0.2)',
        borderColor: 'rgba(255,99,132,1)',
        borderWidth: 1,
        hoverBackgroundColor: 'rgba(255,99,132,0.4)',
        hoverBorderColor: 'rgba(255,99,132,1)',
        data: result.female,
      },
      {
        label: 'Male',
        backgroundColor: 'rgba(113,181,255,0.45)',
        borderColor: 'rgba(255,99,132,1)',
        borderWidth: 1,
        hoverBackgroundColor: 'rgba(88,118,255,0.4)',
        hoverBorderColor: 'rgba(255,99,132,1)',
        data: result.male,
      },
      {
        label: 'Unknown',
        backgroundColor: 'rgba(78,255,68,0.45)',
        borderColor: 'rgba(255,99,132,1)',
        borderWidth: 1,
        hoverBackgroundColor: 'rgba(97,255,70,0.4)',
        hoverBorderColor: 'rgba(255,99,132,1)',
        data: result.unknown,
      },
    ],
  }

  const options = {
    scales: {
      xAxes: [
        {
          stacked: true,
          scaleLabel: {
            display: true,
            labelString: 'Age',
          },
        },
      ],
      yAxes: [
        {
          stacked: true,
          scaleLabel: {
            display: true,
            labelString: 'Count',
          },
        },
      ],
    },
  }

  return (
    <div>
      <h4 className="text-secondary">{`Camera: ${camera.name}`}</h4>
      <Bar
        data={data}
        options={options}
      />
    </div>
  )
}

export default DetailedGraph

import React from 'react'
import Head from '../components/head'
import { getOneDayCounts, getOneDayDetailByCameraId } from '../misc/db'
import BodyScripts from '../components/bodyScripts'
import CameraSelector from '../components/cameraSelector'
import DatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.css'
import DetailedGraph from '../components/detailedGraph'
import PeopleCount from '../components/peopleCount'
import { Col, Container, Row } from 'react-bootstrap'
import NavigationBar from '../components/navigationBar'
import cameraSettings from '../camera_settings'

const styles = {
  root: {
    paddingTop: 84,
  },
  selectDateTitle: {
    marginTop: 32,
  },
  countRow: {
    marginTop: 48,
    marginLeft: 0,
    marginRight: 0,
    marginBottom: 24,
  },
  countCol: {
    paddingTop: 28,
  },
}

class Home extends React.Component {
  constructor (props) {
    super(props)
    this.state = {
      cameras: [],
      selectedCamera: null,
      startDate: new Date(),
      countResult: [],
      detailedResult: {
        male: [],
        female: [],
        unknown: [],
      },
    }
  }

  async componentDidMount () {
    const cameras = this._getCameras()
    console.log(cameras)
    this.setState({ cameras: cameras })
  }

  async componentDidUpdate (prevProps, prevState, _) {
    if (prevState.startDate.getTime() !== this.state.startDate.getTime()) {
      console.log('reload each cameras UU and selected graph')
      await this._getCounts()
      await this._getGraph()
    }

    if (prevState.selectedCamera !== this.state.selectedCamera
      && this.state.selectedCamera) {
      console.log('reload selected graph')
      await this._getGraph()
    }

    if (prevState.cameras.length !== this.state.cameras.length
      && this.state.cameras.length !== 0) {
      console.log('reload each cameras UU')
      await this._getCounts()
    }
  }

  _getCameras = () => {
    return cameraSettings.cameras
  }

  _getGraph = async () => {
    const camera = this.state.selectedCamera
    if (!camera) {
      return
    }

    const res = await getOneDayDetailByCameraId(camera.id, this.state.startDate)
    this.setState({ detailedResult: res })
  }

  _getCounts = async () => {
    const counts = await getOneDayCounts(this.state.cameras, this.state.startDate)
    this.setState({ countResult: counts })
  }

  _handleCameraChanged = (camera) => {
    console.log(`changed to ${camera.id}`)
    this.setState({ selectedCamera: camera })
  }

  _handleDateChanged = (date) => {
    // console.log(date)
    this.setState({
      startDate: date,
    })
  }

  render () {
    const counts = this.state.countResult.map(v => {
      return (
        <Col className="col-3" key={v.cameraId} style={styles.countCol}>
          <PeopleCount
            cameraId={v.cameraId}
            name={v.name}
            count={v.count}
          />
        </Col>
      )
    })

    return (
      <div>
        <Head/>
        <NavigationBar/>

        <Container style={styles.root}>
          <Row>
            <Col>
              <h5 className="text-secondary">Select Camera</h5>
              <CameraSelector
                cameras={this.state.cameras}
                imageMap={cameraSettings.map}
                onCameraChanged={this._handleCameraChanged}
              />
              <h5 className="text-secondary" style={styles.selectDateTitle}>Select Date</h5>
              <DatePicker
                selected={this.state.startDate}
                onChange={this._handleDateChanged}
              />
            </Col>

            <Col>
              <DetailedGraph
                camera={this.state.selectedCamera}
                result={this.state.detailedResult}
              />
            </Col>
          </Row>

          <Row style={styles.countRow}>
            {counts}
          </Row>
        </Container>

        <BodyScripts/>
      </div>
    )
  }
}

export default Home

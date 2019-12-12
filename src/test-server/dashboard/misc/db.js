import { CosmosClient } from '@azure/cosmos'
import moment from 'moment'

const ENDPOINT = process.env.ENDPOINT
const PRIMARYKEY = process.env.PRIMARYKEY
const DATABASE = process.env.DATABASE
const CONTAINER = process.env.CONTAINER

const queryDb = async (query) => {
  const client = new CosmosClient({
    endpoint: ENDPOINT,
    auth: { masterKey: PRIMARYKEY },
  })

  const response = await client.database(DATABASE)
    .container(CONTAINER)
    .items
    .query(query)
    .toArray()
  return response.result
}

const getOneDayDataByCameraId = async (cameraId, date) => {
  const today = moment(date)
    .hours(0)
    .minutes(0)
    .seconds(0)
  const tomorrow = moment(date)
    .hours(0)
    .minutes(0)
    .seconds(0)
    .add(1, 'days')

  console.log(`today: ${today.unix()}, tomorrow: ${tomorrow.unix()}`)

  const querySpec = {
    query: 'SELECT * FROM r WHERE r.camID = @camerdId AND r.timestamp >= @startTime AND r.timestamp < @endTime',
    parameters: [
      {
        name: '@camerdId',
        value: cameraId,
      },
      {
        name: '@startTime',
        value: today.unix(),
      },
      {
        name: '@endTime',
        value: tomorrow.unix(),
      },
    ],
  }

  const res = await queryDb(querySpec)
  return res
}

const getOneDayCountsByCameraId = async (cameraId, date) => {
  const res = await getOneDayDataByCameraId(cameraId, date)

  const trackIds = []
  for (let i = 0; i < res.length; i++) {
    const frames = res[i].frames
    frames.forEach(f => trackIds.push(f.trackID))
  }

  const uniqueTrackIds = Array.from(new Set(trackIds))
  return uniqueTrackIds.length
}

export const getOneDayCounts = async (cameras, date) => {
  const promises = cameras.map(c => getOneDayCountsByCameraId(c.id, date))
  const res = await Promise.all(promises)
  const ret = []

  for (let i = 0; i < cameras.length; i++) {
    ret.push({
      cameraId: cameras[i].id,
      name: cameras[i].name,
      count: res[i],
    })
  }

  return ret
}

export const getOneDayDetailByCameraId = async (cameraId, date) => {
  const res = await getOneDayDataByCameraId(cameraId, date)

  const trackMap = new Map()
  for (let i = 0; i < res.length; i++) {
    const frames = res[i].frames
    frames.forEach(f => {
      let gender = 'UNKNOWN'
      let age = -1
      if (f.recognition && f.recognition.age_gender) {
        gender = f.recognition.age_gender.gender
        age = f.recognition.age_gender.age
      }
      const tid = f.trackID

      if (trackMap.has(tid)) {
        const oldTrack = trackMap.get(tid)
        trackMap.set(tid, {
          age: oldTrack.age === -1 ? age : oldTrack.age,
          gender: oldTrack.gender === 'UNKNOWN' ? gender : oldTrack.gender,
        })
      } else {
        trackMap.set(tid, {
          age: age,
          gender: gender,
        })
      }
    })
  }

  const results = {
    male: [0, 0, 0, 0, 0, 0, 0, 0, 0],
    female: [0, 0, 0, 0, 0, 0, 0, 0, 0],
    unknown: [0, 0, 0, 0, 0, 0, 0, 0, 0],
  }

  for (const [key, value] of trackMap) {
    const age = value.age
    const gender = value.gender
    let ind = 0
    if (age < 0) {
      ind = 0
    } else if (age >= 0 && age < 10) {
      ind = 1
    } else if (age >= 10 && age < 20) {
      ind = 2
    } else if (age >= 20 && age < 30) {
      ind = 3
    } else if (age >= 30 && age < 40) {
      ind = 4
    } else if (age >= 40 && age < 50) {
      ind = 5
    } else if (age >= 50 && age < 60) {
      ind = 6
    } else if (age >= 60 && age < 70) {
      ind = 7
    } else {
      ind = 8
    }

    if (gender === 'MALE') {
      results.male[ind] += 1
    } else if (gender === 'FEMALE') {
      results.female[ind] += 1
    } else {
      results.unknown[ind] += 1
    }
  }

  return results
}

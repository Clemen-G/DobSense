'use client'
import { useState } from 'react';
import { useEffect } from 'react';
import AlignmentView from './AlignmentView.js';

export default function Page() {

  const [constStars, setConstStars] = useState([])
  let hasInitRun = false;

  function handshake(pos) {
    const coords = pos.coords;
    const payload = {
      params: {
        position: {
          accuracy: coords.accuracy,
          altitude: coords.altitude,
          altitudeAccuracy: coords.altitudeAccuracy,
          latitude: coords.latitude,
          longitude: coords.longitude,
          isSecureContext: window.isSecureContext
        },
        datetime: new Date().getTime(),
      }
    }
    axios.post('/api/handshake', payload)
    .then(function (response) {
      setConstStars(response.data.constellation_data)
    })
    .catch(function (error) {
      console.log(error);
    })
    .finally(function () {
      // always executed
    }); 
  }
  function initialize() {
    if (hasInitRun) return;
    navigator.geolocation.getCurrentPosition(handshake)
    hasInitRun = true;
  }

  useEffect(initialize, [])

  return <div>
    <AlignmentView constellationsStars={constStars}/>
    </div>
}
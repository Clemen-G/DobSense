'use client'
import { useState } from 'react';
import { useEffect } from 'react';
import AlignmentView from './AlignmentView.js';
import { AppContext } from './appContext.js';
import ErrorView from './ErrorView.js';

export default function Page() {

  const [constStars, setConstStars] = useState([])
  const [errorMessage, setErrorMessage] = useState(null)

  let hasInitRun = false;

  const appContext = {
    // global API error handler
    apiErrorHandler: function(e) {
      if (e.code === "ERR_BAD_REQUEST" && e.response.data.error_message) {
        setErrorMessage(e.response.data.error_message);
      }
      else {
        setErrorMessage(e.code);
        console.log(e);
      }
    }
  }

  function handshake(pos) {
    const coords = pos.coords;
    console.log("hello")
    const payload = {
        position: {
          accuracy: coords.accuracy,
          altitude: coords.altitude,
          altitudeAccuracy: coords.altitudeAccuracy,
          latitude: coords.latitude,
          longitude: coords.longitude,
          isSecureContext: window.isSecureContext
        },
        datetime: new Date().getTime() / 1000.0,
    }
    axios.post('/api/handshake', payload)
    .then(function (response) {
      setConstStars(response.data.constellation_data)
    })
    .catch(function (error) {
      appContext.apiErrorHandler(error);
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
    <AppContext.Provider value = {appContext}>
    <AlignmentView constellationsStars={constStars}/>
    <ErrorView errorMessage={errorMessage} setErrorMessage={setErrorMessage}/>
    </AppContext.Provider>
    </div>
}
'use client'
import { useState, useRef, useEffect } from 'react';

import { AppContext } from './appContext.js';

import AlignmentView from './AlignmentView.js';
import PointingView from './PointingView.js';
import TabView from './TabView.js';
import ErrorView from './ErrorView.js';
import WebsocketMessaging from './WebsocketMessaging.js'

export default function Page() {

  const [constStars, setConstStars] = useState([])
  const [errorMessage, setErrorMessage] = useState(null)
  const [isTelescopeAligned, setIsTelescopeAligned] = useState(false)
  const websocketMessaging = useRef(undefined);
  const [activeView, setActiveView] = useState("AlignmentView")

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
  function onTabClick(view) {
    setActiveView(view);
  }

  useEffect(initialize, [])
  useEffect(() => {
    websocketMessaging.current =
      new WebsocketMessaging('wss://' + window.location.host + '/api/websocket');
    websocketMessaging.current.register(
      "Hello",
      (m) => {setIsTelescopeAligned(m.isTelescopeAligned); console.log(m.isTelescopeAligned)})
    websocketMessaging.current.open();
    return () => {websocketMessaging.current.close()}
  }, [])

  const tabs = [
    {text: "Al", key: "AlignmentView"},
    {text: "Po", key: "PointingView", disabled: !isTelescopeAligned}
  ]
  return <div>
    <AppContext.Provider value = {appContext}>
    <AlignmentView constellationsStars={constStars} isVisible={activeView === 'AlignmentView'}/>
    <PointingView isVisible={activeView === 'PointingView'}/>
    <ErrorView errorMessage={errorMessage} setErrorMessage={setErrorMessage}/>
    <TabView tabs={tabs} onClick={onTabClick}/>
    {isTelescopeAligned}
    </AppContext.Provider>
    </div>
}
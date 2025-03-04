'use client'

import axios from 'axios';

import { useState, useEffect } from 'react';

import { appContext } from './appContext.js';

import AlignmentView from './component/AlignmentView.js';
import PointingView from './component/PointingView.js';
import SearchView from './component/SearchView.js';
import TabView from './component/TabView.js';
import ErrorView from './component/ErrorView.js';
import WebsocketMessaging from './WebsocketMessaging.js';

export default function Page() {

  const [constStars, setConstStars] = useState([])
  const [errorMessage, setErrorMessage] = useState(null)
  const [isTelescopeAligned, setIsTelescopeAligned] = useState(false)
  const [activeView, setActiveView] = useState("AlignmentView")

  let hasInitRun = false;


  function handshake(loc) {
    const payload = {
        location: loc,
        datetime: new Date().getTime() / 1000.0,
    }
    return axios.post('/api/handshake', payload)
      .then(function (response) {
        setConstStars(response.data.constellation_data)
      })
      .catch(function (error) {
        appContext.apiErrorHandler(error);
      }); 
  }
  
  function initialize() {
    if (hasInitRun) return;
    appContext.setErrorMessage = setErrorMessage;
    appContext.getLocation()
      .then(handshake);
    hasInitRun = true;
  }
  function onTabClick(view) {
    setActiveView(view);
  }

  //dismiss error messages
  function dismissError(e) {
    setErrorMessage(null);
  }
  
  function switchToPointingView() {
    setActiveView("PointingView");
  }

  useEffect(initialize, []);

  useEffect(
    () => {
      appContext.websocketMessaging.register(
        WebsocketMessaging.IS_ALIGNED_MESSAGE,
        (m) => {
          console.log("updating alignment status: "+ m.isTelescopeAligned);
          setIsTelescopeAligned(m.isTelescopeAligned);
          if (!m.isTelescopeAligned) {
            setActiveView("AlignmentView");
          }
          return () => {appContext.websocketMessaging.close()};
        });
      appContext.websocketMessaging.open('wss://' + window.location.host + '/api/websocket');
    }, []);

  const tabs = [
    {text: "Search", key: "SearchView", disabled: !isTelescopeAligned},
    {text: "Point", key: "PointingView", disabled: !isTelescopeAligned},
    {text: "Align", key: "AlignmentView"},
  ].map(t => {
    t.active = t.key === activeView;
    return t;
  });
  return <div className="canvas" onClick={dismissError}>
    <AlignmentView constellationsStars={constStars} isVisible={activeView === 'AlignmentView'}/>
    <PointingView isVisible={activeView === 'PointingView'}/>
    <SearchView isVisible={activeView === 'SearchView'} onTargetSet={switchToPointingView}/>
    <ErrorView errorMessage={errorMessage} setErrorMessage={setErrorMessage}/>
    <TabView tabs={tabs} onClick={onTabClick}/>
    </div>
}
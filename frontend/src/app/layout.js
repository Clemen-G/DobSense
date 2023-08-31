'use client'

//import './globals.css'
import { Inter } from 'next/font/google'
import { useEffect } from 'react';
import Script from 'next/script'  

const inter = Inter({ subsets: ['latin'] })

let hasInitRun = false;

export default function RootLayout({ children }) {
  function sendInitPayload(pos) {
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
      console.log(response);
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
    navigator.geolocation.getCurrentPosition(sendInitPayload)
    hasInitRun = true;
  }
  useEffect(initialize, [])
  return (
    <html lang="en">
      <head>
        <meta name="giovanni-test" />
        <Script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js" />
      </head>
      <body className={inter.className}>{children}</body>
    </html>
  )
}

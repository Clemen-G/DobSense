'use client'

import './globals.css'

export default function RootLayout({ children }) {
  const htmlStyle = {
    "backgroundColor": "black"
  }
  return (
    <html lang="en" style={htmlStyle}>
      <head>
        <meta name="apple-mobile-web-app-capable" content="yes"/>
        <meta name="apple-mobile-web-app-status-bar-style" content="black"/>
        <meta name="apple-mobile-web-app-title" content="DobSense"/>
        <link rel="icon" href="/images/favicon.ico" />
        <link rel="apple-touch-icon" href="/images/apple-touch-icon.png"/>
        {/* iPhone X, Xs (1125px x 2436px) */}
        <link rel="apple-touch-startup-image"
          media="(device-width: 375px) and (device-height: 812px) and (-webkit-device-pixel-ratio: 3)"
          href="/images/apple-launch-1125x2436.png"/> 
      </head>
      <body>
        {children}
      </body>
    </html>
  )
}

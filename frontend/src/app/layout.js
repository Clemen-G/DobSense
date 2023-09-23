'use client'

import './globals.css'

export default function RootLayout({ children }) {

  return (
    <html lang="en">
      <head>
        <meta name="apple-mobile-web-app-capable" content="yes"/>
        <meta name="apple-mobile-web-app-capable" content="yes"/>
        <meta name="apple-mobile-web-app-status-bar-style" content="white"/>
        <meta name="apple-mobile-web-app-title" content="Nushscope"/>
      </head>
      <body>{children}</body>
    </html>
  )
}

'use client'

import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({ children }) {

  return (
    <html lang="en">
      <head>
        <meta name="apple-mobile-web-app-capable" content="yes"/>
        <meta name="apple-mobile-web-app-capable" content="yes"/>
        <meta name="apple-mobile-web-app-status-bar-style" content="white"/>
        <meta name="apple-mobile-web-app-title" content="Notentool"/>
        <meta name="giovanni-test" />
      </head>
      <body className={inter.className}>{children}</body>
    </html>
  )
}

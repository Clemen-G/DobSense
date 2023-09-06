'use client'

//import './globals.css'
import { Inter } from 'next/font/google'
import Script from 'next/script'  

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({ children }) {

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

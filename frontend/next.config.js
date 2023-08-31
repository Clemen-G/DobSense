/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'export', // builds static assets with no server-side rendering or support
    assetPrefix: '/client' // causes generated assets to be referred as /client/_next/...
}

module.exports = nextConfig

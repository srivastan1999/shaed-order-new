/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  // Don't rewrite /api routes - let Vercel handle them via serverless function
  // Next.js rewrites would interfere with Vercel's routing
}

module.exports = nextConfig


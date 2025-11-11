/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  // Add rewrites to proxy API requests (optional - helps with CORS)
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/:path*`,
      },
      {
        source: '/health',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/health`,
      },
    ];
  },
}

module.exports = nextConfig


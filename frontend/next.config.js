/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    const apiOrigin = process.env.NEXT_PUBLIC_API_ORIGIN || 'http://localhost:8000';
    return [
      { source: '/api/:path*', destination: `${apiOrigin}/api/:path*` },
    ];
  },
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'api.qrserver.com', pathname: '/v1/create-qr-code/**' },
    ],
  },
};

module.exports = nextConfig;

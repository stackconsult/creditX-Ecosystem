/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  experimental: {
    serverActions: {
      bodySizeLimit: "2mb",
    },
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:4000",
    NEXT_PUBLIC_DOMAIN: process.env.DOMAIN || "creditx.credit",
  },
  async rewrites() {
    return [
      {
        // Proxy API calls to internal API Gateway
        source: "/api/backend/:path*",
        destination: `${process.env.API_GATEWAY_URL || "http://127.0.0.1:4000"}/api/v1/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;

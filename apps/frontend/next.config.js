/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  experimental: {
    serverActions: {
      bodySizeLimit: "2mb",
    },
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "https://creditx.credit",
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || "wss://creditx.credit/ws",
    NEXT_PUBLIC_COPILOT_API: process.env.NEXT_PUBLIC_COPILOT_API || "https://creditx.credit/api/copilot",
    NEXT_PUBLIC_DOMAIN: process.env.NEXT_PUBLIC_DOMAIN || "creditx.credit",
  },
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "creditx.credit",
      },
    ],
  },
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://creditx.credit";
    return [
      {
        source: "/api/backend/:path*",
        destination: `${apiUrl}/api/v1/:path*`,
      },
      {
        source: "/api/agents/:path*",
        destination: `${apiUrl}/api/agents/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;

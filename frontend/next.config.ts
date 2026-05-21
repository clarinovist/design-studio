import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "no-cache, no-store, max-age=0, must-revalidate",
          },
          { key: "Pragma", value: "no-cache" },
          { key: "Expires", value: "0" },
        ],
      },
      {
        source: "/_next/static/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=31536000, immutable",
          },
        ],
      },
      {
        source: "/api/health",
        headers: [
          {
            key: "Cache-Control",
            value: "no-cache, no-store, max-age=0, must-revalidate",
          },
        ],
      },
    ];
  },
  async redirects() {
    return [
      {
        source: "/projects",
        destination: "/library?tab=projects",
        permanent: false,
      },
      {
        source: "/my-assets",
        destination: "/library?tab=assets",
        permanent: false,
      },
    ];
  },
  generateBuildId: async () => {
    // Prefer CI/deployment-provided IDs for cache consistency across containers.
    if (process.env.NEXT_PUBLIC_BUILD_ID) {
      return process.env.NEXT_PUBLIC_BUILD_ID;
    }

    if (process.env.VERCEL_GIT_COMMIT_SHA) {
      return process.env.VERCEL_GIT_COMMIT_SHA;
    }

    // Keep local and ad-hoc Docker builds deterministic. Avoid Date.now() here:
    // it changes on every build and increases stale-client/cache mismatch noise.
    return "dev-build";
  },
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**.backblazeb2.com" },
      { protocol: "https", hostname: "fal.media" },
      { protocol: "https", hostname: "**.fal.ai" },
      { protocol: "https", hostname: "images.unsplash.com" },
      { protocol: "https", hostname: "plus.unsplash.com" },
      { protocol: "http", hostname: "localhost" },
    ],
  },
};

export default nextConfig;

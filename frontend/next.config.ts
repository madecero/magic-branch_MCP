import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    domains: [
      "oaidalleapiprodscus.blob.core.windows.net",
      "oaidalleapiprodscus.blob.core.windows.net",
      "replicate.delivery" // Add any other domains as needed
    ],
  },
};

export default nextConfig;
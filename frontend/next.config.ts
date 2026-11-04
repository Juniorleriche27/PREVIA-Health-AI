import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Development and production never share artifacts; this prevents stale-chunk
  // failures after a production build while a dev server was previously active.
  distDir: process.env.PREVIA_DEV_CACHE === "1" ? ".next-dev" : ".next",
};

export default nextConfig;

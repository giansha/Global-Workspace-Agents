import type { NextConfig } from "next";

const isProd = process.env.NODE_ENV === "production";

const nextConfig: NextConfig = {
  output: "export",
  basePath: isProd ? "/Global-Workspace-Agents" : "",
  assetPrefix: isProd ? "/Global-Workspace-Agents/" : "",
  images: {
    unoptimized: true,
  },
};

export default nextConfig;

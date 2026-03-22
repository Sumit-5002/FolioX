/** @type {import('next').NextConfig} */
const nextConfig = {
  // Static export for Firebase Hosting
  output: "export",
  trailingSlash: true,
  images: {
    unoptimized: true, // Required for static export
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  },
};

export default nextConfig;

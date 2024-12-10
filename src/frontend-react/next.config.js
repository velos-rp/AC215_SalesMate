/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    webpack: (config) => {
        config.module.rules.push({
            test: /\.svg$/,
            use: ["@svgr/webpack"]
        });
        return config;
    },
    rewrites: async () => {
        return [
            {
                source: "/api/:path*",
                destination:
                    process.env.NODE_ENV === "development"
                        ? "http://sales-mate-api-service:9876/:path*"
                        : "/api/:path*",
            },
            {
                source: "/docs",
                destination:
                    process.env.NODE_ENV === "development"
                        ? "http://sales-mate-api-service:9876/docs"
                        : "/api/docs",
            },
            {
                source: "/openapi.json",
                destination:
                    process.env.NODE_ENV === "development"
                        ? "http://sales-mate-api-service:9876/openapi.json"
                        : "/api/openapi.json",
            },
        ];
    },
    reactStrictMode: false,

    eslint: {
        ignoreDuringBuilds: true, // Disable ESLint during builds
    },
};

module.exports = nextConfig;
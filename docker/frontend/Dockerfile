# Frontend Dockerfile - Next.js 15 with standalone output
# Single-stage build for Docker Desktop compatibility

FROM node:20-alpine

WORKDIR /app

# Copy package files and install ALL dependencies (including dev for build)
COPY package.json package-lock.json* ./
RUN npm ci

# Copy source code
COPY . .

# Accept API URL as build arg so NEXT_PUBLIC_* is inlined at build time
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Provide build-time placeholder for Better Auth (real secret injected at runtime by k8s)
ENV BETTER_AUTH_SECRET="build-time-placeholder-replaced-at-runtime"

# Build Next.js application (output: standalone)
RUN npm run build

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Set production environment
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Prepare standalone output:
# 1. Copy static assets into the standalone .next directory
# 2. Move standalone to /tmp to avoid conflicts
# 3. Clean the app directory completely
# 4. Move standalone contents (including hidden .next) back to /app
RUN cp -r .next/static .next/standalone/.next/static && \
    cp -r public .next/standalone/public 2>/dev/null || true && \
    mv .next/standalone /tmp/standalone && \
    rm -rf /app/* /app/.next && \
    mv /tmp/standalone/* /tmp/standalone/.next /app/ && \
    rm -rf /tmp/standalone && \
    chown -R nextjs:nodejs /app

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Start the application
CMD ["node", "server.js"]

# OpenClaw Docker Build
# Builds OpenClaw from the official repository

FROM node:22-alpine AS builder

# Install build dependencies
RUN apk add --no-cache git python3 make g++

# Clone OpenClaw repository
WORKDIR /build
RUN git clone --depth 1 https://github.com/openclaw/openclaw.git .

# Install dependencies and build
RUN npm ci && npm run build

# Production stage
FROM node:22-alpine

# Install runtime dependencies
RUN apk add --no-cache curl ca-certificates

# Create app directory
WORKDIR /app

# Copy built application from builder
COPY --from=builder /build/dist ./dist
COPY --from=builder /build/node_modules ./node_modules
COPY --from=builder /build/package.json ./
COPY --from=builder /build/assets ./assets
COPY --from=builder /build/docs ./docs

# Create openclaw user
RUN addgroup -g 1000 openclaw && \
    adduser -u 1000 -G openclaw -s /bin/sh -D openclaw

# Create data directories
RUN mkdir -p /home/openclaw/.openclaw /data/backups/openclaw && \
    chown -R openclaw:openclaw /home/openclaw /data

# Copy entrypoint script
COPY --chown=openclaw:openclaw scripts/entrypoint.sh /opt/openclaw/scripts/entrypoint.sh
RUN chmod +x /opt/openclaw/scripts/entrypoint.sh

USER openclaw

# Environment
ENV HOME=/home/openclaw
ENV OPENCLAW_CONFIG_DIR=/home/openclaw/.openclaw
ENV OPENCLAW_WORKSPACE_DIR=/home/openclaw/.openclaw/workspace
ENV NODE_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:18789/health || exit 1

EXPOSE 18789 18790

ENTRYPOINT ["/opt/openclaw/scripts/entrypoint.sh"]
CMD ["node", "dist/index.js", "gateway", "--bind", "0.0.0.0", "--port", "18789"]

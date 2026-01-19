# ============================================================================
# CreditX API Gateway - Express.js Production Container
# For Spaceship Hyperlift deployment
# ============================================================================

FROM node:20-alpine AS deps
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

FROM node:20-alpine AS builder
WORKDIR /app

# Copy dependencies
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build TypeScript
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app

# Install dumb-init for signal handling
RUN apk add --no-cache dumb-init curl

ENV NODE_ENV=production

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 expressjs

# Copy built files and dependencies
COPY --from=builder --chown=expressjs:nodejs /app/dist ./dist
COPY --from=deps --chown=expressjs:nodejs /app/node_modules ./node_modules
COPY --chown=expressjs:nodejs package*.json ./

USER expressjs

# Default port (Hyperlift will override)
ENV PORT=4000
EXPOSE 4000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health/live || exit 1

# Use dumb-init for graceful shutdown
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "dist/index.js"]

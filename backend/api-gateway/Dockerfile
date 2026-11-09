FROM node:20-alpine AS builder

RUN apk add --no-cache python3 make g++
ENV PYTHON=/usr/bin/python3

WORKDIR /app

# Install shared dependencies
COPY shared/package*.json ./shared/
RUN cd shared && npm ci

# Install API Gateway dependencies
COPY api-gateway/package*.json ./api-gateway/
RUN cd api-gateway && npm ci

# Copy source code
COPY shared ./shared
COPY api-gateway ./api-gateway

# Reinstall dependencies inside Linux after copying source files.
# This prevents Windows native binaries from entering the Linux image.
RUN cd shared && npm ci
RUN cd api-gateway && npm ci

# Compile API Gateway and shared code
WORKDIR /app
RUN cd api-gateway && npm run build

# ==========================================
# PRODUCTION IMAGE
# ==========================================
FROM node:20-alpine

WORKDIR /app

# Copy compiled application
COPY --from=builder /app/api-gateway/dist ./dist

# Copy API Gateway dependencies
COPY --from=builder /app/api-gateway/node_modules ./node_modules

# Copy shared package and its dependencies
COPY --from=builder /app/shared ./shared

# Copy package metadata
COPY --from=builder /app/api-gateway/package.json ./package.json

# Allow Node.js to resolve shared dependencies
ENV NODE_PATH=/app/shared/node_modules:/app/node_modules

EXPOSE 3000

# Correct compiled entry point
CMD ["node", "dist/api-gateway/src/index.js"]


# ------------------------------------------------------------
# Base stage — shared setup
# ------------------------------------------------------------
FROM node:18-alpine AS base

WORKDIR /app

# Install dependencies only when needed
COPY package*.json ./
RUN npm install

COPY . .

# ------------------------------------------------------------
# Development stage — with hot reload
# ------------------------------------------------------------
FROM base AS dev

ENV NODE_ENV=development
EXPOSE 3000

# Run the development server
CMD ["npm", "run", "dev"]

# ------------------------------------------------------------
# Build stage — compile for production
# ------------------------------------------------------------
FROM base AS builder

ENV NODE_ENV=production
RUN npm run build

# ------------------------------------------------------------
# Production stage — optimized runtime
# ------------------------------------------------------------
FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copy only necessary files from builder
# COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000

# Start the optimized server
CMD ["npm", "start"]

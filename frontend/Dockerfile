# Frontend Dockerfile for Security Modeling Platform
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy source code
COPY . .

# Build the application
RUN yarn build

# Production stage
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built app from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs \
    && adduser -S react -u 1001 -G nodejs

# Change ownership of nginx directories
RUN chown -R react:nodejs /var/cache/nginx \
    && chown -R react:nodejs /var/log/nginx \
    && chown -R react:nodejs /etc/nginx/conf.d \
    && touch /var/run/nginx.pid \
    && chown -R react:nodejs /var/run/nginx.pid

USER react

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
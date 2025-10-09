# --- Stage 1: Build the Next.js Frontend ---
FROM node:20-slim AS nextjs-builder

# Set working directory
WORKDIR /app/servers/nextjs

# Copy only package.json to start clean (no old lock file)
COPY servers/nextjs/package.json ./

# Clean any previous installs and generate a fresh package-lock.json
RUN rm -rf node_modules package-lock.json && \
    npm install && \
    npm cache clean --force

# Copy the rest of the Next.js source code
COPY servers/nextjs/ ./ 

# Build the production-ready Next.js app
RUN npm run build


# --- Stage 2: Build the Final Production Image ---
FROM python:3.11-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    curl \
    libreoffice \
    fontconfig \
    chromium \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20 runtime (for start.js)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

# Working directory for the app
WORKDIR /app

# Environment variables
ENV APP_DATA_DIRECTORY=/app_data
ENV TEMP_DIRECTORY=/tmp/presenton
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Install ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Install Python dependencies
RUN pip install --no-cache-dir aiohttp aiomysql aiosqlite asyncpg fastapi[standard] \
    pathvalidate pdfplumber chromadb sqlmodel \
    anthropic google-genai openai fastmcp dirtyjson
RUN pip install --no-cache-dir docling --extra-index-url https://download.pytorch.org/whl/cpu

# Copy FastAPI backend
COPY servers/fastapi/ ./servers/fastapi/

# --- Copy the built Next.js app from builder stage ---
COPY --from=nextjs-builder /app/servers/nextjs/.next ./servers/nextjs/.next
COPY --from=nextjs-builder /app/servers/nextjs/public ./servers/nextjs/public
COPY --from=nextjs-builder /app/servers/nextjs/standalone ./servers/nextjs/standalone

# Copy shared files
COPY start.js LICENSE NOTICE ./
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port for Nginx
EXPOSE 80

# Start app
CMD ["node", "/app/start.js"]

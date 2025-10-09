# --- Stage 1: Build the Next.js Frontend ---
# The base image MUST be pre-loaded on the offline machine using 'docker load'
FROM node:20-slim as nextjs-builder

WORKDIR /app/servers/nextjs

# --- OFFLINE CYPRESS INSTALLATION ---
# 1. Copy your pre-downloaded cypress.zip into the build stage.
#    Make sure cypress.zip is in the same directory as your Dockerfile.
COPY cypress.zip /tmp/cypress.zip

# 2. Set the environment variable to point to the local zip file.
#    The 'npm install' script for Cypress will use this path instead of downloading.
ENV CYPRESS_INSTALL_BINARY=/tmp/cypress.zip
# --- END OFFLINE CYPRESS INSTALLATION ---

# Copy package files first to leverage Docker caching
COPY servers/nextjs/package.json servers/nextjs/package-lock.json ./

# Run npm install. This will now use the local Cypress binary for installation
# and download other dependencies as needed.
RUN npm install

# Unset the environment variable after use (good practice)
ENV CYPRESS_INSTALL_BINARY=""

# Copy the rest of the Next.js source code
COPY servers/nextjs/ ./

# Build the app.
RUN npm run build


# --- Stage 2: Build the Final Production Image ---
# The base image MUST be pre-loaded on the offline machine using 'docker load'
FROM python:3.11-slim-bookworm

# Note: Handling system dependencies (nginx, curl, etc.) offline is complex.
# The most reliable method is to create a custom base image that already has
# these tools pre-installed and use it here. This example assumes they are
# either present in the base image or not strictly required for the final run.
# For this example, we proceed as if the base image is sufficient.
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    curl \
    libreoffice \
    fontconfig \
    chromium \
    # Clean up apt cache to reduce image size
    && rm -rf /var/lib/apt/lists/*

# Install Node.js runtime using the pre-downloaded script
COPY ./scripts/nodesource_setup_20.x /tmp/nodesource_setup_20.x
RUN bash /tmp/nodesource_setup_20.x && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Set environment variables
ENV APP_DATA_DIRECTORY=/app_data
ENV TEMP_DIRECTORY=/tmp/presenton
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Install ollama using the pre-downloaded script
COPY ./scripts/install.sh /tmp/install.sh
# Note: The ollama script itself might try to download things.
# This assumes the script can be run offline or its network calls are not critical.
RUN sh /tmp/install.sh

# Install Python dependencies from the local wheels
# First, create a requirements.txt file with all your dependencies
COPY requirements.txt .
COPY ./wheels /tmp/wheels
RUN pip install --no-cache-dir --no-index --find-links=/tmp/wheels -r requirements.txt

# Copy the FastAPI server code
COPY servers/fastapi/ ./servers/fastapi/

# Copy ONLY the built Next.js app from the 'nextjs-builder' stage
COPY --from=nextjs-builder /app/servers/nextjs/.next ./servers/nextjs/.next
COPY --from=nextjs-builder /app/servers/nextjs/public ./servers/nextjs/public
COPY --from=nextjs-builder /app/servers/nextjs/standalone ./servers/nextjs/standalone


# Copy remaining application and configuration files
COPY start.js LICENSE NOTICE ./
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["node", "/app/start.js"]



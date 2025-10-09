# --- Stage 1: Build the Next.js Frontend ---
# Use an official Node.js image as a temporary build environment.
FROM node:20-slim as nextjs-builder

# Set the working directory for the Next.js app
WORKDIR /app/servers/nextjs

# Copy only the package files to leverage Docker caching
COPY servers/nextjs/package.json servers/nextjs/package-lock.json ./

# Install npm dependencies
RUN npm install

# Copy the rest of the Next.js source code
COPY servers/nextjs/ ./

# Build the production-ready Next.js app
RUN npm run build


# --- Stage 2: Build the Final Production Image ---
# Start from your original Python base image
FROM python:3.11-slim-bookworm

# Combine installation of all system dependencies in a single RUN command
# This reduces the number of layers in the final image.
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    curl \
    libreoffice \
    fontconfig \
    chromium \
    # Clean up apt cache to reduce image size
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20 runtime (needed for start.js)
# We combine this with the previous RUN command in a real-world scenario,
# but separate it here for clarity.
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

# Create a working directory
WORKDIR /app

# Set environment variables
ENV APP_DATA_DIRECTORY=/app_data
ENV TEMP_DIRECTORY=/tmp/presenton
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Install ollama
# Note: This adds a significant layer to the image.
RUN curl -fsSL https://ollama.com/install.sh | sh

# Install Python dependencies
# Copying requirements.txt first and installing from it improves caching
# Assuming your Python dependencies are or can be listed in a requirements.txt file
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# Using your original pip install commands as a fallback:
RUN pip install --no-cache-dir aiohttp aiomysql aiosqlite asyncpg fastapi[standard] \
    pathvalidate pdfplumber chromadb sqlmodel \
    anthropic google-genai openai fastmcp dirtyjson
RUN pip install --no-cache-dir docling --extra-index-url https://download.pytorch.org/whl/cpu

# Copy the FastAPI server code
COPY servers/fastapi/ ./servers/fastapi/

# --- This is the key step of the multi-stage build ---
# Copy ONLY the built Next.js app from the 'nextjs-builder' stage
COPY --from=nextjs-builder /app/servers/nextjs/.next ./servers/nextjs/.next
# Also copy public and static folders if they exist and are needed
COPY --from=nextjs-builder /app/servers/nextjs/public ./servers/nextjs/public
# Copy the standalone server files if using Next.js output standalone feature
COPY --from=nextjs-builder /app/servers/nextjs/standalone ./servers/nextjs/standalone


# Copy remaining application and configuration files
COPY start.js LICENSE NOTICE ./
COPY nginx.conf /etc/nginx/nginx.conf

# Expose the port Nginx will listen on
EXPOSE 80

# Start the application using your process manager script
CMD ["node", "/app/start.js"]

FROM python:3.11-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nginx \
    curl \
    libreoffice \
    fontconfig \
    chromium \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20 using NodeSource
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

# Create working directory
WORKDIR /app  

# Set environment variables
ENV APP_DATA_DIRECTORY=/app_data
ENV TEMP_DIRECTORY=/tmp/presenton
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Install ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Install FastAPI dependencies
RUN pip install aiohttp aiomysql aiosqlite asyncpg fastapi[standard] \
    pathvalidate pdfplumber chromadb sqlmodel \
    anthropic google-genai openai fastmcp dirtyjson
RUN pip install docling --extra-index-url https://download.pytorch.org/whl/cpu

# Install Next.js dependencies
WORKDIR /app/servers/nextjs
COPY servers/nextjs/package.json servers/nextjs/package-lock.json ./
RUN npm install

# ⬇️ COPY your downloaded Cypress bundle here
# Example: if you have `cypress.zip` locally in your project root
COPY cypress.zip /tmp/cypress.zip
RUN mkdir -p /root/.cache/Cypress && \
    unzip /tmp/cypress.zip -d /root/.cache/Cypress && \
    rm /tmp/cypress.zip

# Optionally set Cypress binary path
ENV CYPRESS_CACHE_FOLDER=/root/.cache/Cypress
ENV CYPRESS_RUN_BINARY=/root/.cache/Cypress/<YOUR_CYPRESS_FOLDER>/Cypress

# Copy and build Next.js app
COPY servers/nextjs/ /app/servers/nextjs/
RUN npm run build

# Copy FastAPI and other files
WORKDIR /app
COPY servers/fastapi/ ./servers/fastapi/
COPY start.js LICENSE NOTICE ./

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start servers
CMD ["node", "/app/start.js"]

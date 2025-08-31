# Use an official Node runtime as the base image
FROM node:20-slim

# # Install Docker CLI
# RUN apt-get update && \
#     apt-get install -y docker.io && \
#     rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install dependencies first (better caching)
COPY package*.json tsconfig.json ./
RUN npm install

# Copy the source code
COPY . .

# Build TypeScript
RUN npx tsc

# Expose port for the Express server
EXPOSE 3000
COPY views ./dist/views
COPY templates ./dist/templates
# Run the compiled server (not the .ts file!)
CMD ["node", "dist/server.js"]

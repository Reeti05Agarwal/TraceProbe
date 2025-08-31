# Build stage
FROM node:20-slim as build
WORKDIR /app

COPY package*.json tsconfig.json ./
RUN npm install --include=dev
COPY . .
RUN npm install -g typescript
RUN tsc

# Runtime stage
FROM node:20-slim
WORKDIR /app

# Copy only package.json files and install production deps
COPY package*.json ./
RUN npm install --omit=dev

# Copy built JS + assets
COPY --from=build /app/dist ./dist
COPY --from=build /app/views ./dist/views
COPY --from=build /app/templates ./dist/templates
COPY --from=build /app/public ./dist/public

EXPOSE 3000
CMD ["node", "dist/server.js"]

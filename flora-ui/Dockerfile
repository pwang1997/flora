FROM node:22-alpine

WORKDIR /app
COPY package.json ./
RUN corepack enable && pnpm install --no-frozen-lockfile

COPY . .

CMD ["pnpm", "dev", "--hostname", "0.0.0.0", "--port", "3000"]

# Docker Setup Guide for Superpowers

This guide explains how to run Superpowers in a Docker container, which can be useful for:
- Testing the plugin system in an isolated environment
- Running examples and demos
- Development with consistent dependencies

## Prerequisites

- Docker installed on your system
- Docker Compose installed (usually comes with Docker Desktop)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/paseka10jaroslav-coder/superpowers.git
cd superpowers
```

### 2. Set Up Environment Variables

Copy the example environment file and configure your LLM API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your actual API keys:

```bash
# Required: At least one LLM provider
OPENAI_API_KEY=sk-your-actual-openai-key
ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-key

# If using Ollama locally
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

### 3. Build and Run with Docker Compose

```bash
# Build the container
docker compose build

# Start the container
docker compose up -d

# Access the container shell
docker compose exec superpowers bash
```

## Alternative: Direct Docker Commands

If you prefer not to use Docker Compose:

```bash
# Build the image
docker build -t superpowers .

# Run the container
docker run -it --rm \
  --env-file .env \
  -v $(pwd):/app \
  superpowers bash
```

## Using the Container

Once inside the container, you can:

```bash
# Navigate the skills
ls skills/

# Run the Python test analyzer
python3 tests/claude-code/analyze-token-usage.py <session-file.jsonl>

# Access all repository files
ls -la
```

## Environment Variables

The following environment variables are supported (configured in `.env`):

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | `sk-ant-...` |
| `OLLAMA_BASE_URL` | Base URL for Ollama instance | `http://host.docker.internal:11434` |
| `GOOGLE_API_KEY` | Google AI (Gemini) API key | Optional |
| `COHERE_API_KEY` | Cohere API key | Optional |

## Stopping the Container

```bash
# Stop the container
docker compose down

# Stop and remove volumes
docker compose down -v
```

## Troubleshooting

### Cannot connect to Ollama

If you're running Ollama on your host machine and can't connect from Docker:

- **Mac/Windows**: Use `http://host.docker.internal:11434`
- **Linux**: Use `http://172.17.0.1:11434` or your host's IP address

### Environment variables not loading

1. Ensure `.env` file exists in the repository root
2. Check that `.env` is not in `.gitignore` for your local copy
3. Restart the container after modifying `.env`:
   ```bash
   docker compose down
   docker compose up -d
   ```

### Permission issues

If you encounter permission issues with mounted volumes:

```bash
# Run as current user
docker compose run --rm --user $(id -u):$(id -g) superpowers bash
```

## Development Workflow

For active development:

```bash
# Start container in background
docker compose up -d

# Make changes to files on your host machine
# They're automatically reflected in the container via volume mount

# Access container to test changes
docker compose exec superpowers bash

# View logs
docker compose logs -f
```

## Notes

- The repository is mounted as a volume, so changes you make on your host are immediately reflected in the container
- The `.env` file is excluded from git to protect your API keys
- The container uses Node.js 20 LTS and includes Python 3 for utilities

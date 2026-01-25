# Use Node.js LTS as base image
FROM node:20-slim

# Install Python for test utilities
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the entire repository
COPY . .

# Install Node.js dependencies if package.json exists
# Note: Currently this repo doesn't have npm dependencies,
# but this step is included for extensibility if needed in the future
RUN if [ -f package.json ]; then npm install; fi

# Set default command to bash for interactive use
CMD ["/bin/bash"]

# Use the official micromamba image as the base image
FROM mambaorg/micromamba:1.5.8

# Install build tools and dependencies
USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    && apt-get clean

# Copy environment file and install dependencies
COPY env.yml /tmp/env.yml
RUN micromamba install -y -n base -f /tmp/env.yml && \
    micromamba clean --all --yes

# Activate the environment
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# Expose the port the app runs on
EXPOSE 8888

# Command to run your application (if applicable)
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]

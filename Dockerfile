FROM ghcr.io/faasr/github-actions-python:latest

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python scientific stack
RUN pip install --no-cache-dir \
    numpy \
    pandas \
    mesa==2.1.1

# Clone and install PyCHAMP
RUN git clone https://github.com/philip928lin/PyCHAMP.git /opt/pychamp && \
    cd /opt/pychamp && \
    pip install -e .

# Set Python path
ENV PYTHONPATH="/opt/pychamp:${PYTHONPATH}"

# Set working directory
WORKDIR /action
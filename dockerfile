FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# --- System packages ---
RUN apt-get update && apt-get install -y \
    curl \
    git \
    python3 \
    python3-pip \
    ca-certificates \
    && apt-get clean

# --- Install Ollama ---
RUN curl -fsSL https://ollama.com/install.sh | sh

# --- Clone repo first (to get requirements.txt)
WORKDIR /app
RUN git clone https://github.com/Nettking/llm-dt.git .

# --- Install Python dependencies before copying everything else (caching)
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# --- Expose Ollama's port ---
EXPOSE 11434

# --- Declare persistent model volume ---
VOLUME ["/root/.ollama"]

# --- Start Ollama, wait, pull model, then run the app ---
    CMD ollama serve & \
    sleep 2 && \
    cd /app && \
    git pull && \
    python3 Tools/wait_for_ollama.py && \
    python3 Tools/pull.py && \
    python3 run.py

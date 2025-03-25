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

# --- Clone your project repo ---
WORKDIR /app
RUN git clone https://github.com/Nettking/llm-dt.git .

# --- Install Python dependencies ---
RUN pip3 install --no-cache-dir -r requirements.txt

# --- Expose Ollama's port ---
EXPOSE 11434

# --- Declare persistent model volume ---
VOLUME ["/root/.ollama"]

# --- Start Ollama, wait, pull model, then run the app ---
CMD ollama serve & \
    sleep 2 && \
    python3 Tools/wait_for_ollama.py && \
    python3 Tools/pull.py && \
    python3 run.py

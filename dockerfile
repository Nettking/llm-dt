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

# --- Set working directory
WORKDIR /app

# --- Copy only requirements file for caching
COPY requirements.txt .

# --- Install Python dependencies
RUN pip3 install -r requirements.txt

# --- Copy the rest of the application
COPY . .

# --- Expose Ollama's port ---
EXPOSE 11434

# --- Declare persistent model volume ---
VOLUME ["/root/.ollama"]

# --- Start everything ---
CMD ollama serve & \
    sleep 2 && \
    python3 Tools/wait_for_ollama.py && \
    python3 Tools/pull.py && \
    python3 run.py

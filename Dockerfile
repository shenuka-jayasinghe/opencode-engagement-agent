FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install required system tools and Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    openssh-client \
    openssh-server \
    sudo \
    python3 \
    python3-pip \
    python3-venv \
 && rm -rf /var/lib/apt/lists/*

# Create and configure ubuntu user
RUN useradd -m -s /bin/bash ubuntu \
 && echo 'ubuntu:robin' | chpasswd \
 && usermod -aG sudo ubuntu \
 && echo 'ubuntu ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Configure SSH
RUN mkdir -p /run/sshd \
 && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config \
 && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Switch to ubuntu user for opencode install
USER ubuntu
WORKDIR /home/ubuntu

# Prepare SSH configuration
RUN mkdir -p /home/ubuntu/.ssh \
 && touch /home/ubuntu/.ssh/known_hosts \
 && ssh-keyscan -T 5 github.com 2>/dev/null >> /home/ubuntu/.ssh/known_hosts || true

# Install OpenCode AI as ubuntu user
RUN curl -fsSL https://opencode.ai/install | bash

# Copy project files
COPY --chown=ubuntu:ubuntu . /home/ubuntu/opencode-engagement-agent
WORKDIR /home/ubuntu/opencode-engagement-agent

# Install Python dependencies (no venv needed in container)
RUN pip install --no-cache-dir -r tools/requirements.txt

# Set environment
ENV PATH="/home/ubuntu/.opencode/bin:${PATH}"
ENV OPENCODE_SERVER_PASSWORD=""

EXPOSE 22 3000

# Need root to start sshd, then drop to ubuntu for opencode
USER root
CMD ["sh", "-c", "/usr/sbin/sshd && cd /home/ubuntu/opencode-engagement-agent && sudo -E HOME=/home/ubuntu -u ubuntu /home/ubuntu/.opencode/bin/opencode web --port 3000 --hostname 0.0.0.0"]

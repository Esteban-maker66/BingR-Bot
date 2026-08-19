FROM python:3.12.3-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    ca-certificates \
    cron \
    tzdata \
    wget \
    gnupg \
    unzip \
    curl \
    && curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg \
    && install -o root -g root -m 644 microsoft.gpg /etc/apt/trusted.gpg.d/ \
    && echo "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main" > /etc/apt/sources.list.d/microsoft-edge.list \
    && rm microsoft.gpg \
    && apt-get update && apt-get install -y microsoft-edge-stable \
    && EDGE_VERSION="$(microsoft-edge --version | awk '{print $3}')" \
    && curl -fsSL "https://msedgedriver.microsoft.com/${EDGE_VERSION}/edgedriver_linux64.zip" -o /tmp/edgedriver.zip \
    && unzip /tmp/edgedriver.zip -d /tmp/edgedriver \
    && install -o root -g root -m 755 /tmp/edgedriver/msedgedriver /usr/local/bin/msedgedriver \
    && rm -rf /tmp/edgedriver /tmp/edgedriver.zip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY rewards_bot.py .
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint
COPY run-rewards-bot.sh /usr/local/bin/run-rewards-bot
RUN chmod +x /usr/local/bin/docker-entrypoint /usr/local/bin/run-rewards-bot
RUN mkdir -p /app/evidencias

CMD ["/usr/local/bin/docker-entrypoint"]

FROM python:3.11-slim

WORKDIR /app

# Zainstaluj zależności
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj aplikację
COPY protocol.py .
COPY tcp_server.py .
COPY udp_server.py .
COPY tcp_client.py .
COPY udp_client.py .
COPY load_tester.py .
COPY host_discovery.py .
COPY app.py .

# Skopiuj templates
COPY templates/ templates/

# Expose porty
EXPOSE 5000 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('localhost', 5000), timeout=5)" || exit 1

# Uruchom aplikację
CMD ["python", "app.py"]

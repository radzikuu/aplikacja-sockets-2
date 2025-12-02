# Network Protocol Suite - TCP/UDP Docker Application

## Struktura Projektu

```
sockets-py/
├── .gitignore
├── docker-compose.yml
├── README.md
├── app/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt
│   ├── app.py (Flask backend)
│   ├── protocol.py (Custom protocol implementation)
│   ├── tcp_server.py
│   ├── udp_server.py
│   ├── tcp_client.py
│   ├── udp_client.py
│   ├── load_tester.py
│   └── host_discovery.py
└── templates/
    └── index.html (Frontend)
```

## Uruchomienie

```bash
# Build i uruchomienie
docker-compose up --build

# W nowym terminalu - dostęp do aplikacji
http://localhost:5000
```

## Architektura

- **protocol.py**: Własny format ramek TCP (0xCAFEBABE) i UDP (0xDEADBEEF)
- **tcp_server.py**: Wielowątkowy serwer TCP
- **udp_server.py**: Asynchroniczny serwer UDP
- **load_tester.py**: Testy obciążeniowe (3 tryby)
- **app.py**: Flask API do komunikacji z frontend
- **Flask WebUI**: Obsługa wszystkich funkcji aplikacji

## Funkcje

✅ TCP/UDP Client-Server w jednej aplikacji
✅ Własny protokół z sumami kontrolnymi CRC32
✅ Komunikacja wielowątkowa
✅ Tester obciążenia (normal, flood, slowloris)
✅ Odkrywanie hostów w sieci Docker
✅ Web UI do zarządzania
✅ Logowanie i statystyki

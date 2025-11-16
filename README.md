# Custom Network Protocol with Docker

Implementacja własnego protokołu sieciowego z TCP/UDP w Pythonie przy użyciu Dockera. Projekt edukacyjny demonstrujący:
- Implementację stosu TCP/IP
- Własny protokół warstwy aplikacji z nagłówkami i sumami kontrolnymi
- Komunikację unicast między kontenerami Docker
- Auto-reconnect i heartbeat mechanism
- Web UI do zarządzania połączeniami

## 🚀 Funkcjonalności

- **Własny protokół**: Binarne ramki z nagłówkami, numerami sekwencyjnymi i sumami kontrolnymi SHA256
- **TCP Server**: Niezawodna transmisja tekstów z potwierdzeniami
- **UDP Server**: Szybka transmisja plików (np. audio)
- **Auto-reconnect**: Automatyczne ponowne łączenie z exponential backoff
- **Heartbeat**: Monitoring żywotności połączeń co 5 sekund
- **Web Interface**: Prosty interfejs do wysyłki danych i monitoringu statusu
- **Docker Network**: Izolowana sieć 172.20.0.0/16 z trzema węzłami

## 📋 Wymagania

- Docker Desktop lub Docker Engine
- Docker Compose v2.0+
- Przeglądarka (Chrome, Firefox, Edge)

## 🔧 Instalacja

1. Sklonuj repozytorium:

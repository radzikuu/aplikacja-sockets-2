# Custom Network Protocol with Docker

Implementacja własnego protokołu sieciowego z TCP/UDP w Pythonie przy użyciu Dockera. Projekt edukacyjny demonstrujący:
- Implementację stosu TCP/IP
- Własny protokół warstwy aplikacji z nagłówkami i sumami kontrolnymi
- Komunikację unicast między kontenerami Docker
- Auto-reconnect i heartbeat mechanism
- Web UI do zarządzania połączeniami

## Funkcjonalności

- **Własny protokół**: Binarne ramki z nagłówkami, numerami sekwencyjnymi i sumami kontrolnymi SHA256
- **TCP Server**: Niezawodna transmisja tekstów z potwierdzeniami
- **UDP Server**: Szybka transmisja plików (np. audio)
- **Auto-reconnect**: Automatyczne ponowne łączenie z exponential backoff
- **Heartbeat**: Monitoring żywotności połączeń co 5 sekund
- **Web Interface**: Prosty interfejs do wysyłki danych i monitoringu statusu
- **Docker Network**: Izolowana sieć 172.20.0.0/16 z trzema węzłami

## Wymagania

- Docker Desktop lub Docker Engine
- Docker Compose v2.0+
- Przeglądarka (Chrome, Firefox, Edge)

## Instalacja

1. Sklonuj repozytorium:

- `git clone https://github.com/radzikuu/sockets-py`
- `cd sockets-py`

2. Zbuduj i uruchom kontenery:

- `docker-compose up --build`

3. Otwórz interfejsy web:
- Node 1: http://localhost:8081
- Node 2: http://localhost:8082
- Node 3: http://localhost:8083

## Użycie

### Wysyłanie Tekstu (TCP)

1. Otwórz http://localhost:8081
2. W sekcji "Send Data":
   - Host: `172.20.0.11` (Node 2)
   - Port: `5000`
   - Protocol: `TCP`
   - Text: Twoja wiadomość
3. Kliknij "Send Text (TCP)"
4. Sprawdź logi: `docker logs protocol_node2`

### Wysyłanie Pliku (UDP)

1. Wybierz plik (najlepiej < 64KB)
2. Ustaw:
   - Host: `172.20.0.12` (Node 3)
   - Port: `5001`
   - Protocol: `UDP`
3. Kliknij "Send File"
4. Plik zostanie zapisany na węźle docelowym

### Logi wszystkich węzłów:
`docker-compose logs -f`

### Logi konkretnego węzła:
`docker logs -f protocol_node1`

### Status połączeń:
`curl http://localhost:8081/api/status`

### Odkrywanie hostów:
`curl http://localhost:8081/api/discover`
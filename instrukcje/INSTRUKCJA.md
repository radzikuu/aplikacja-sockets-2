# 🌐 Network Protocol Suite - TCP/UDP Docker Application

## Architektura Projektu

```
sockets-py/
├── .gitignore                 # Git ignore file
├── docker-compose.yml         # Orkiestracja kontenerów
├── README.md                  # Ten plik
│
└── app/
    ├── .dockerignore          # Docker ignore file
    ├── Dockerfile             # Konfiguracja kontenera
    ├── requirements.txt       # Zależności Python
    ├── app.py                 # Flask backend API
    │
    ├── protocol.py            # Własny protokół TCP/UDP (CRC32, custom frames)
    ├── tcp_server.py          # Wielowątkowy serwer TCP
    ├── udp_server.py          # Asynchroniczny serwer UDP
    ├── tcp_client.py          # Klient TCP z auto-reconnectem
    ├── udp_client.py          # Klient UDP stateless
    ├── load_tester.py         # Narzędzie testów obciążeniowych (3 tryby)
    ├── host_discovery.py      # Odkrywanie hostów w sieci Docker
    │
    └── templates/
        └── index.html         # Frontend WebUI (React-like)
```

## Instrukcja Uruchomienia

### 1. Przygotowanie plików

```bash
# Utwórz katalog projektu
mkdir sockets-py && cd sockets-py

# Utwórz katalog app
mkdir app && mkdir templates

# Skopiuj zawartość z poniższych plików do odpowiednich lokalizacji
```

### 2. Struktura katalogów po skopiowaniu

```
sockets-py/
├── .gitignore
├── docker-compose.yml
├── README.md
├── app/
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py
│   ├── protocol.py
│   ├── tcp_server.py
│   ├── udp_server.py
│   ├── tcp_client.py
│   ├── udp_client.py
│   ├── load_tester.py
│   ├── host_discovery.py
│   └── templates/
│       └── index.html
```

### 3. Uruchomienie

```bash
# Przejdź do katalogu projektu
cd sockets-py

# Build i uruchomienie
docker-compose up --build

# W nowym terminalu - dostęp do aplikacji
# Otwórz przeglądarkę na: http://localhost:5000
```

## 5. Przewodnik Testowania

### UDP - Streaming (Unicast i Multicast)

#### Unicast (Point-to-Point)
1. Otwórz UI: http://localhost:5000
2. Przejdź do karty **Klient** → **UDP Klient**
3. Ustaw:
   - Host: `app` (lub `node1`, `node2`)
   - Port: `5001`
   - Tryb wysyłania: `Unicast`
4. Zainstaluj serwer UDP:
   - Przejdź do **Serwer** → **UDP Serwer**
   - Ustaw Host: `0.0.0.0`, Port: `5001`
   - Kliknij **Start**
5. Wyślij wiadomość:
   - W **UDP Klient** wpisz wiadomość lub wybierz plik (mp3/audio)
   - Kliknij **Wyślij wiadomość** lub **Wyślij plik**
   - Sprawdź logi w obydwu kierunkach

#### Multicast (Broadcasting)
1. W **UDP Serwer**:
   - Zmień Host na adres multicast: `239.255.0.1`
   - Port: `5001`
   - Kliknij **Start**
   - Serwer dołączy do grupy multicast
2. W **UDP Klient**:
   - Ustaw Host: `239.255.0.1` (ta sama grupa)
   - Port: `5001`
   - Tryb wysyłania: `Multicast`
   - Wybierz plik (np. mp3) i kliknij **Wyślij plik**
3. Pakiety UDP będą wysyłane do grupy multicast — wszyscy serwery dołączeni do `239.255.0.1:5001` je otrzymają

**Uwaga:** Multicast działa wewnątrz sieci Dockera. Upewnij się, że twoja konfiguracja dockera wspiera multicast (domyślnie tak).

### TCP - Transmisja Blokowa (Tekst)

1. Przejdź do **Serwer** → **TCP Serwer**
   - Port: `6000`
   - Kliknij **Start**
2. Przejdź do **Klient** → **TCP Klient**
   - Host: `app` (lub `localhost`)
   - Port: `6000`
   - Zaznacz checkbox **Auto Reconnect** (jeśli chcesz automatycznego reconnectu po stracie połączenia)
   - Kliknij **Połącz**
3. Wpisz wiadomość tekstową i kliknij **Wyślij**
4. Sprawdź odpowiedź serwera w logach
5. TCP używa custom frame (`0xCAFEBABE` + CRC32)

### Auto Reconnect - TCP

1. Połącz TCP klienta (instrukcja wyżej)
2. Wyłącz serwer TCP (kliknij **Stop** w **TCP Serwer**)
3. Jeśli zaznaczony **Auto Reconnect**, klient będzie próbować się reconnectować co 5 sekund
4. Włącz serwer TCP z powrotem
5. Klient automatycznie się reconnectuje
6. Wyślij wiadomość — powinna przejść

### Wysyłanie Pliku UDP

1. W **UDP Klient**:
   - Ustaw Host i Port (unicast lub multicast)
   - Kliknij **Wybierz plik** i zaznacz plik audio (mp3, wav) lub binarny
   - Wybierz tryb: `Unicast` lub `Multicast`
   - Kliknij **Wyślij plik**
2. Aplikacja:
   - Wczyta plik
   - Podzieli na chunki (65500B każdy)
   - Wyśle jako sekwencję ramek UDP (0xDEADBEEF + CRC32)
   - Wyświetli status i liczbę wysłanych bajtów
3. UDP Server odbiera ramki i wysyła echo — sprawdź statystyki

### Testowanie z Wieloma Kontenerami (node1, node2)

1. Uruchom `docker-compose up --build` — buduje `app`, `node1`, `node2` w tej samej sieci
2. Otwórz UI na `http://localhost:5000` (połączenie do `app`)
3. Zainstaluj serwer UDP na multicast w `app`:
   - Host: `239.255.0.1`, Port: `5001`, **Start**
4. Wyślij stream multicast z `app`
5. (Opcjonalnie) Wejdź do kontenera `node1` lub `node2` i zainstaluj tam UDP Server na tej samej grupie multicast — będzie odbierać pakiety

**Sprawdzenie kontenerów:**
```bash
docker ps
docker exec -it aplikacja-sockets-2-node1-1 bash
# Wewnątrz kontenera możesz uruchomić Python script lub testować tcpdump
```

### Weryfikacja Blokowa - Statystyki

Po każdej operacji (send/recv) sprawdź:
- **Bytes sent/received**
- **Packets sent/received**
- **Connection status** (kolor zielony = połączony)
- **Logi** (color-coded: info/success/error/warning)

### Troubleshooting

**UDP Multicast nie działa:**
- Sprawdź, czy dockera wspiera multicast: `docker network inspect aplikacja-sockets-2_docker-net`
- Upewnij się, że host (adres multicast) to `239.x.x.x` (zarezerwowany zakres)

**TCP connection refused:**
- Upewnij się, że serwer TCP jest uruchomiony (Start)
- Sprawdź port: domyślnie `6000`
- Jeśli port w użyciu: `docker-compose down` i spróbuj ponownie

**Brak logów:**
- Sprawdź logi kontenera: `docker-compose logs -f app`
- Odśwież przeglądarkę (F5)

**Auto Reconnect nie działa:**
- Upewnij się, że checkbox **Auto Reconnect** jest zaznaczony przed kliknięciem **Połącz**
- Sprawdź konsolę przeglądarki (DevTools) — może być błąd JS

### Rekomendowane Sektory Testów

1. **Unicast UDP** — tekstowa wiadomość do specific host:port
2. **Multicast UDP** — streaming audio (mp3) do grupy
3. **TCP Blokowy** — tekstowy tekst z auto-reconnect
4. **Multi-kontener** — node1, node2 odbierające multicast od app
5. **Load Tester** — stres test serwera TCP (Tester tab)

### 4. Wytłumaczenie modułów

#### **protocol.py** - Własny protokół sieciowy
- Format ramki TCP: `0xCAFEBABE` (magiczny numer)
  - Nagłówek: 20 bajtów
  - Pola: Magic (4B) + Type (1B) + Length (2B) + CRC32 (4B) + Timestamp (4B) + Sequence (4B)
  - Payload: maksymalnie 65535 bajtów
  
- Format ramki UDP: `0xDEADBEEF` (magiczny numer)
  - Nagłówek: 16 bajtów
  - Pola: Magic (4B) + Type (1B) + Length (2B) + CRC32 (4B) + PacketID (2B) + Total (2B) + Timestamp (1B)
  - Payload: maksymalnie 65500 bajtów

- Weryfikacja integralności: CRC32 na każdej ramce

#### **tcp_server.py** - Wielowątkowy serwer TCP
- Obsługuje wielu klientów jednocześnie
- Każdy klient w oddzielnym wątku
- Echo-responder
- Tracking statystyk (bytes received, packets received, connected clients)

#### **udp_server.py** - Asynchroniczny serwer UDP
- Nasłuchuje na portach UDP
- Echo-responder
- Obsługuje pofragmentowane pakiety
- Statystyki odboru

#### **tcp_client.py** - Klient TCP
- Automatyczne reconnectowanie
- Wysyłanie wiadomości tekstowych i binarnych
- Statystyki połączenia
- Thread-safe

#### **udp_client.py** - Klient UDP
- Stateless (bez utrzymywania połączenia)
- Pofragmentowanie dużych plików
- Wysyłanie audio/binarnych danych
- Obsługa wielu pakietów w sekwencji

#### **load_tester.py** - Narzędzie testów obciążeniowych
- **Tryb Normal**: Normalne pakiety TCP z czekaniem na response
- **Tryb Flood**: Zalewanie pakietami bez czekania na ACK
- **Tryb Slowloris**: Powolne wysyłanie pakietów (edukacyjne)
- Wielowątkowe połączenia
- Pomiar czasów odpowiedzi, min/max, średnia

#### **host_discovery.py** - Skanowanie sieci Docker
- Skanuje zakresy CIDR (domyślnie 172.17.0.0/16)
- Wielowątkowe sondowanie portów
- Rezolucja nazw hostów
- Możliwość dodawania hostów ręcznie

#### **app.py** - Backend Flask
- API endpoints dla wszystkich operacji
- Zarządzanie cyklem życia serverów/klientów
- JSON responses
- Thread-safe state management
- Integracja z index.html

#### **index.html** - Frontend WebUI
- Responsywny design
- 4 główne karty:
  1. **Klient** - TCP i UDP klienci
  2. **Serwer** - TCP i UDP serwery
  3. **Tester Obciążenia** - Load testing tool
  4. **Odkrywanie** - Network scanning
- Real-time statystyki
- Logi z color-coding
- Status indicators

## Funkcjonalność

### ✅ Zakonczone
- ✅ Własny protokół TCP/UDP z CRC32
- ✅ TCP Serwer wielowątkowy
- ✅ UDP Serwer z obsługą fragmentacji
- ✅ TCP Klient z auto-reconnectem
- ✅ UDP Klient stateless
- ✅ Load Tester (3 tryby)
- ✅ Host Discovery w sieci Docker
- ✅ WebUI z APIem
- ✅ Logowanie i statystyki
- ✅ Docker Compose setup

## API Endpoints

### TCP Server
- `POST /api/tcp-server/start` - Uruchomienie serwera
- `POST /api/tcp-server/stop` - Zatrzymanie serwera
- `GET /api/tcp-server/stats` - Statystyki

### UDP Server
- `POST /api/udp-server/start` - Uruchomienie serwera
- `POST /api/udp-server/stop` - Zatrzymanie serwera
- `GET /api/udp-server/stats` - Statystyki

### TCP Client
- `POST /api/tcp-client/connect` - Połączenie
- `POST /api/tcp-client/send` - Wysyłanie wiadomości
- `POST /api/tcp-client/disconnect` - Rozłączenie
- `GET /api/tcp-client/stats` - Statystyki

### UDP Client
- `POST /api/udp-client/send` - Wysyłanie wiadomości
- `POST /api/udp-client/send-file` - Wysyłanie pliku

### Load Tester
- `POST /api/load-tester/start` - Rozpoczęcie testu
- `POST /api/load-tester/stop` - Zatrzymanie testu
- `GET /api/load-tester/stats` - Statystyki testu

### Host Discovery
- `POST /api/discovery/scan` - Skanowanie sieci
- `GET /api/discovery/hosts` - Odkryte hosty
- `POST /api/discovery/add-manual` - Dodanie hosta
- `GET /api/discovery/check-status/<ip>` - Status hosta

## Troubleshooting

### Port już w użyciu
```bash
# Zmień port w docker-compose.yml lub użyj innego
docker ps
docker kill <container_id>
```

### Problemy z siecią Docker
```bash
# Sprawdź sieć
docker network ls
docker network inspect docker_docker-net
```

### Logi
```bash
docker-compose logs -f app
```

### Przebudowanie
```bash
docker-compose up --build --no-cache
```

## Uwagi Bezpieczeństwa

⚠️ **Ta aplikacja jest narzędziem edukacyjnym**
- Używaj tylko w izolowanych, kontrolowanych środowiskach
- Nie używaj w produkcji
- Load Tester nie zawiera rzeczywistego ataku SYN Flood - to narzędzie edukacyjne
- Zawsze uzyskaj zgodę przed testowaniem systemów sieciowych

## Dalsze Rozszerzenia

Możliwe ulepszenia:
- [ ] WebSocket dla real-time updates
- [ ] Kompresja danych
- [ ] Encryption (TLS/SSL)
- [ ] Database dla historii
- [ ] Metryki Prometheus
- [ ] Visualization grafów
- [ ] Multi-container orchestration
- [ ] Kubernetes support
- [ ] Performance benchmarking

## Licencja

Projekt edukacyjny - do użytku w celach nauki i badań.

## Kontakt

W razie pytań - sprawdź dokumentację kodu w plikach Python.

# 📚 Kompletny Przewodnik Użytkownika - Network Protocol Suite

## Spis Treści
1. [Wstęp](#wstęp)
2. [Instalacja i Setup](#instalacja-i-setup)
3. [Architektura Aplikacji](#architektura-aplikacji)
4. [Interfejs Użytkownika](#interfejs-użytkownika)
5. [Instrukcje Poszczególnych Modułów](#instrukcje-poszczególnych-modułów)
6. [Własny Protokół Sieciowy](#własny-protokół-sieciowy)
7. [Przykłady Użycia](#przykłady-użycia)
8. [Troubleshooting](#troubleshooting)
9. [Zaawansowane](#zaawansowane)
10. [FAQ](#faq)

---

## Wstęp

### Co to jest Network Protocol Suite?

**Network Protocol Suite** jest aplikacją edukacyjną do nauki protokołów sieciowych TCP/UDP, implementacji własnych formatów ramek, komunikacji wielowątkowej i testów obciążeniowych.

**Główne cechy:**
- 🔧 Własny protokół sieciowy z CRC32
- 🔄 TCP/UDP klienci i serwery
- ⚡ Wielowątkowa komunikacja
- 🧪 Tester obciążeniowych (3 tryby)
- 🔍 Skanowanie sieci Docker
- 🎨 Responsywny WebUI
- 📊 Statystyki real-time

### Wymagania

- **Docker** (wersja 20.0+)
- **Docker Compose** (wersja 1.29+)
- **Przeglądarka** (Chrome, Firefox, Safari, Edge)
- **4GB RAM** (rekomendowane)

---

## Instalacja i Setup

### Krok 1: Przygotowanie Struktury Katalogów

```bash
# Utwórz główny katalog projektu
mkdir sockets-py
cd sockets-py

# Utwórz podkatalogi
mkdir app
mkdir app/templates

# Inicjalizuj Git (opcjonalnie)
git init
```

### Krok 2: Skopiowanie Plików

Skopiuj wszystkie pliki w poniższej strukturze:

```
sockets-py/
├── .gitignore
├── .dockerignore (w app/)
├── docker-compose.yml
├── README.md
├── INSTRUKCJA.md
│
└── app/
    ├── Dockerfile
    ├── requirements.txt
    ├── app.py
    ├── protocol.py
    ├── tcp_server.py
    ├── udp_server.py
    ├── tcp_client.py
    ├── udp_client.py
    ├── load_tester.py
    ├── host_discovery.py
    └── templates/
        └── index.html
```

### Krok 3: Uruchomienie

```bash
# Przenieś się do katalogu projektu
cd sockets-py

# Build i uruchomienie
docker-compose up --build

# Output powinien wyglądać mniej więcej tak:
# Building app
# Step 1/11 : FROM python:3.11-slim
# ...
# app_1  | * Running on http://0.0.0.0:5000
```

### Krok 4: Dostęp do Aplikacji

Otwórz przeglądarkę:
```
http://localhost:5000
```

✅ Powinieneś zobaczyć kolorowy interfejs z 4 kartami.

---

## Architektura Aplikacji

### Diagram Komponentów

```
┌─────────────────────────────────────────────────────────────┐
│                    WebUI (index.html)                       │
│              Responsywny interfejs React-like               │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/JSON
┌────────────────────▼────────────────────────────────────────┐
│                   Flask Backend (app.py)                    │
│          API Endpoints do zarządzania wszystkim             │
└────┬──────────┬─────────────┬──────────────┬────────────────┘
     │          │             │              │
     │          │             │              │
┌────▼──┐ ┌────▼────┐ ┌──────▼──────┐ ┌────▼──────────┐
│TCP    │ │UDP      │ │LoadTester   │ │HostDiscovery │
│Server │ │Server   │ │Tool         │ │Skanowanie    │
└────┬──┘ └────┬────┘ │(3 tryby)    │ └────┬──────────┘
     │         │      │             │      │
     └────┬────┴──────┴─────────────┴──────┘
          │
          │
     ┌────▼────────────────────────────────┐
     │    CustomProtocol (protocol.py)     │
     │  • TCP Ramka 0xCAFEBABE (20B)      │
     │  • UDP Ramka 0xDEADBEEF (16B)      │
     │  • CRC32 Weryfikacja                │
     └────────────────────────────────────┘
```

### Moduły i Odpowiedzialności

| Moduł | Odpowiedzialność | Wątki |
|-------|------------------|-------|
| **protocol.py** | Budowanie/parsowanie ramek TCP/UDP | N/A |
| **tcp_server.py** | Nasłuchiwanie i obsługa TCP | Wielowątkowy |
| **udp_server.py** | Nasłuchiwanie i obsługa UDP | Główny |
| **tcp_client.py** | Połączenie i wysyłanie TCP | Wielowątkowy |
| **udp_client.py** | Wysyłanie UDP bez stanu | Główny |
| **load_tester.py** | Testy obciążeniowe | Wielowątkowy |
| **host_discovery.py** | Skanowanie sieci | Wielowątkowy |
| **app.py** | Zarządzanie API Flask | Główny |

---

## Interfejs Użytkownika

### Layout Strony

```
┌─────────────────────────────────────────────────────────────┐
│  🌐 Network Protocol Suite - Docker Edition                │
│  Aplikacja TCP/UDP Client-Server...            │
└─────────────────────────────────────────────────────────────┘

┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Klient       │ Serwer       │ Tester       │ Odkrywanie   │
│ (aktywna)    │              │ Obciążenia   │ Hostów       │
└──────────────┴──────────────┴──────────────┴──────────────┘

┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  [Karty - zawartość zależy od wybranej]                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Elementy Interfejsu

#### Status Indicators
- 🟢 **Zielony** - Połączony/uruchomiony
- 🔴 **Czerwony** - Rozłączony/zatrzymany
- 🟡 **Żółty** - W toku/oczekiwanie

#### Logi
```
[HH:MM:SS] [INFO] Gotowy...
[HH:MM:SS] [SUCCESS] ✓ Wysłano
[HH:MM:SS] [ERROR] ✗ Błąd połączenia
[HH:MM:SS] [WARNING] ⚠️ Timeout
```

#### Statystyki
Wyświetlane w postaci kafelków:
- Wysłane bajty
- Odebrane bajty
- Wysłane pakiety
- Odebrane pakiety

---

## Instrukcje Poszczególnych Modułów

### 1. Karta Klient (TCP/UDP)

#### TCP Klient

**Cel:** Wysyłanie wiadomości do serwera TCP

**Instrukcje:**

1. **Wpisz adres hosta:**
   ```
   Adres hosta: localhost  (lub server-app, lub IP)
   Port: 5000
   ```

2. **Kliknij "Połącz"**
   - Status zmieni się na 🟢 Połączony
   - W logu pojawi się: `[SUCCESS] ✓ Pomyślnie połączono`

3. **Wpisz wiadomość:**
   ```
   Wiadomość: Cześć z klienta TCP!
   ```

4. **Kliknij "Wyślij"**
   - Wiadomość zostanie wysłana
   - Serwer zwróci echo
   - Statystyki się zaktualizują

5. **Aby rozłączyć, kliknij "Rozłącz"**

**Formaty ramek TCP:**
```
┌─────────────────────────────────┐
│ Nagłówek (20 bajtów)            │
├─────────────────────────────────┤
│ Magic: 0xCAFEBABE (4B)          │
│ Type: 0x01=DATA (1B)            │
│ Length: 2B                      │
│ CRC32: 4B                       │
│ Timestamp: 4B                   │
│ Sequence: 4B                    │
├─────────────────────────────────┤
│ Payload (dane)                  │
└─────────────────────────────────┘
```

#### UDP Klient

**Cel:** Wysyłanie wiadomości UDP (bez gwarancji dostarczenia)

**Instrukcje:**

1. **Wpisz adres i port:**
   ```
   Adres: localhost
   Port: 5001
   ```

2. **Wpisz wiadomość lub plik audio**

3. **Kliknij "Wyślij wiadomość"**
   - UDP wysle wiadomość
   - Bez potrzeby połączenia
   - Brak gwarancji dostarczenia

**Różnice TCP vs UDP:**

| Aspekt | TCP | UDP |
|--------|-----|-----|
| Połączenie | Wymagane | Nie potrzebne |
| Gwarancja | Tak | Nie |
| Kolejność | Gwarantowana | Nie |
| Szybkość | Wolniejszy | Szybszy |
| Użycie | Pliki, email | Video, VoIP |

### 2. Karta Serwer (TCP/UDP)

#### TCP Serwer

**Cel:** Nasłuchiwanie na porcie TCP

**Instrukcje:**

1. **Skonfiguruj parametry:**
   ```
   Port: 5000
   Max klientów: 10
   ```

2. **Kliknij "Start"**
   - Status zmieni się na 🟢 Nasłuchuje
   - Log: `[SUCCESS] ✓ TCP Serwer nasłuchuje na 0.0.0.0:5000`

3. **Serwer czeka na połączenia klientów**
   - Każdy klient w osobnym wątku
   - Echo-responder (zwraca to co otrzyma)
   - Maksymalnie 10 jednoczesnych połączeń

4. **Aby zatrzymać, kliknij "Stop"**

#### UDP Serwer

**Cel:** Nasłuchiwanie na porcie UDP

**Instrukcje:**

1. **Ustaw port:**
   ```
   Port: 5001
   ```

2. **Kliknij "Start"**
   - Log: `[SUCCESS] ✓ UDP Serwer nasłuchuje na 0.0.0.0:5001`

3. **Serwer przyjmuje pakiety UDP**
   - Obsługuje pofragmentowane dane
   - Echo-responder

### 3. Karta Tester Obciążenia

**Cel:** Testowanie wydajności serwera TCP

**Instrukcje:**

1. **Ustaw parametry testu:**
   ```
   Host: localhost
   Port: 5000
   Wątki: 5
   Pakiety/wątek: 10
   Rozmiar pakietu: 1024 B
   Tryb: Normalny
   ```

2. **Wybierz tryb testu:**

   **Tryb Normalny**
   - Wysyła pakiety TCP
   - Czeka na odpowiedź (echo)
   - Mierzy czasy odpowiedzi
   - Idealny do testów wydajności
   
   ```javascript
   // Logika
   for każdy_pakiet:
       połącz() → wyślij() → czekaj_na_echo() → zamknij()
   ```

   **Tryb Flood**
   - Wysyła pakiety szybko
   - Nie czeka na ACK
   - Testuje odporność serwera
   - ⚠️ Używaj ostrożnie
   
   ```javascript
   // Logika
   for każdy_pakiet:
       połącz() → wyślij_bez_czekania()
   ```

   **Tryb SlowLoris**
   - Wysyła pakiety powoli
   - Część po części
   - Testuje obsługę połączeń długotrwałych
   - Edukacyjny
   
   ```javascript
   // Logika
   for każdy_pakiet:
       połącz() → wyślij_kawałkami(0.1s_opóźnienie) → czekaj()
   ```

3. **Kliknij "Rozpocznij"**
   - Status: 🟡 Test w toku...
   - Real-time aktualizacja statystyk
   - Log pokazuje postęp

4. **Obserwuj metryki:**
   ```
   Wysłane pakiety: 50
   Udane połączenia: 48
   Błędy: 2
   Średni czas: 45.3 ms
   ```

5. **Aby zatrzymać, kliknij "Zatrzymaj"**

### 4. Karta Odkrywanie Hostów

**Cel:** Znalezienie dostępnych usług w sieci Docker

**Instrukcje:**

1. **Wpisz zakres CIDR:**
   ```
   Zakres IP: 172.17.0.0/16  (domyślnie)
   ```

2. **Kliknij "Skanuj"**
   - Status: 🟡 Skanowanie...
   - Wielowątkowe sondowanie portów
   - Szuka hostów na porcie 5000

3. **Czekaj na wyniki**
   ```
   [INFO] Skanowanie zakresu 172.17.0.0/16...
   [SUCCESS] ✓ Znaleziono 2 hostów
   ```

4. **Kliknij na host, aby go wybrać**
   - Automatycznie wypełni pola TCP/UDP Klientów
   - Możesz się natychmiast połączyć

---

## Własny Protokół Sieciowy

### Format Ramki TCP

```
0         1         2         3         4
0123456789012345678901234567890123456789
+---+---+---+---+---+---+---+---+---+---+
| MAGIC NUMBER (0xCAFEBABE)              | 4 bajty
+---+---+---+---+---+---+---+---+---+---+
| TYPE  | LENGTH            | CRC32     | 10 bajtów
+---+---+---+---+---+---+---+---+---+---+
| TIMESTAMP             | SEQUENCE      | 8 bajtów
+---+---+---+---+---+---+---+---+---+---+
|                                       |
|  PAYLOAD (dane zmiennej długości)     |
|  Do 65535 bajtów                      |
|                                       |
+---+---+---+---+---+---+---+---+---+---+
```

### Pola Ramki TCP

| Pole | Rozmiar | Opis |
|------|---------|------|
| **Magic** | 4B | 0xCAFEBABE (identyfikator ramki TCP) |
| **Type** | 1B | 0x01=DATA, 0x02=AUDIO, 0x03=CONTROL |
| **Length** | 2B | Długość payload'u (big-endian) |
| **CRC32** | 4B | Suma kontrolna (big-endian) |
| **Timestamp** | 4B | Czas wysłania w ms (big-endian) |
| **Sequence** | 4B | Numer sekwencyjny (big-endian) |
| **Payload** | ∞ | Dane do 65535 bajtów |

### Format Ramki UDP

```
0         1         2         3
0123456789012345678901234567890
+---+---+---+---+---+---+---+---+
| MAGIC NUMBER (0xDEADBEEF)     | 4 bajty
+---+---+---+---+---+---+---+---+
| TYPE  | LENGTH     | CRC32    | 9 bajtów
+---+---+---+---+---+---+---+---+
| PKT_ID       | TOTAL   | TIME| 5 bajtów
+---+---+---+---+---+---+---+---+
|                               |
|  PAYLOAD (do 65500 bajtów)    |
|                               |
+---+---+---+---+---+---+---+---+
```

### CRC32 Weryfikacja

Każda ramka zawiera **CRC32 (Cyclic Redundancy Check)** do weryfikacji integralności:

```python
# Jak to działa:
1. Oblicz CRC32 na całej ramce + payload
2. Umieść wartość w polu CRC32
3. Przy odbiorze:
   - Odczytaj CRC32 z ramki
   - Oblicz CRC32 na otrzymanych danych
   - Porównaj - jeśli się nie zgadza, ramka uszkodzona
```

---

## Przykłady Użycia

### Przykład 1: Prosta Komunikacja TCP

**Scenariusz:** Wysyłanie wiadomości między dwoma instancjami aplikacji

**Kroki:**

1. **Terminal 1 - Uruchomienie Serwera:**
   ```bash
   # Aplikacja już uruchomiona na localhost:5000
   # W WebUI karta "Serwer" → "TCP Serwer" → Kliknij "Start"
   ```

2. **Terminal 2 - Uruchomienie Klienta:**
   ```bash
   # W WebUI karta "Klient" → "TCP Klient"
   # Wpisz:
   # - Adres hosta: localhost
   # - Port: 5000
   # - Wiadomość: "Cześć serwer!"
   # Kliknij "Połącz", potem "Wyślij"
   ```

3. **Rezultat:**
   ```
   [CLIENT LOG]
   [INFO] Łączenie z localhost:5000...
   [SUCCESS] ✓ Pomyślnie połączono z localhost:5000
   [INFO] Wysyłanie TCP do localhost:5000...
   [SUCCESS] ✓ TCP: Wysłano "Cześć serwer!"
   
   [SERVER LOG]
   [INFO] TCP Serwer nasłuchuje na 0.0.0.0:5000
   [DEBUG] TCP: Odebrano 16 B od 127.0.0.1:xxxxx
   [SUCCESS] ✓ Wiadomość odebrana i odesłana
   ```

### Przykład 2: Test Obciążenia

**Scenariusz:** Symulacja 10 jednoczesnych klientów

**Kroki:**

1. **Uruchom TCP Serwer** (karta Serwer)

2. **Przejdź do karty "Tester Obciążenia"**

3. **Ustaw parametry:**
   ```
   Host: localhost
   Port: 5000
   Wątki: 10
   Pakiety/wątek: 5
   Rozmiar pakietu: 512 B
   Tryb: Normalny
   ```

4. **Kliknij "Rozpocznij"**

5. **Obserwuj:**
   ```
   Wysłane pakiety: 50
   Udane połączenia: 50
   Błędy: 0
   Średni czas: 12.4 ms
   Min: 8.1 ms
   Max: 18.7 ms
   ```

### Przykład 3: Odkrywanie Hostów Docker

**Scenariusz:** Znalezienie innych instancji aplikacji w Docker

**Kroki:**

1. **Przejdź do karty "Odkrywanie Hostów"**

2. **Domyślnie skan zakresu: 172.17.0.0/16**

3. **Kliknij "Skanuj"**

4. **Czekaj ~15 sekund**

5. **Wyniki:**
   ```
   [INFO] Skanowanie zakresu 172.17.0.0/16...
   [SUCCESS] ✓ Znaleziono 3 hostów:
   
   - network-suite (172.17.0.2) - Network Service - online
   - client-app (172.17.0.3) - Network Service - online
   - monitor (172.17.0.4) - Network Service - online
   ```

6. **Kliknij na host, aby go wybrać**
   - Pola IP w TCP/UDP Kliencie się zaktualizują
   - Możesz się teraz połączyć

---

## Troubleshooting

### Problem: ERR_UNSAFE_PORT - Nie mogę dostać się do port 6000

**Symptomy:**
```
Ta witryna jest nieosiągalna
Strona internetowa pod adresem http://localhost:6000/ może być tymczasowo niedostępna
ERR_UNSAFE_PORT
```

**Wyjaśnienie:**
Port 6000 jest **niebezpiecznym portem** zablokowanym przez przeglądarki. Dodatkowo port 6000 **nie jest HTTP serwerem** - to surowy serwer TCP z vlastnym protokołem, niedostępny bezpośrednio z przeglądarki.

**Rozwiązanie - PRAWIDŁOWY WORKFLOW:**

1. **Otwórz aplikację WebUI na porcie 5000:**
   ```
   http://localhost:5000  ✓ POPRAWNIE
   http://localhost:6000  ✗ NIE DZIAŁA (blokada przeglądarki)
   ```

2. **Używaj aplikacji WebUI do kontroli serwerów:**
   - **Karta "Serwer"** → Kliknij "Start" → TCP Server uruchomi się na porcie 6000
   - **Karta "Klient"** → Połącz się z serwerem (port 6000 zostanie obsłużony przez aplikację)

3. **Architektura portów:**
   | Port | Typ | Dostęp | Użycie |
   |------|-----|--------|--------|
   | 5000 | HTTP (Flask) | ✓ Przeglądarka | WebUI |
   | 6000 | TCP (Raw Socket) | ✗ Przeglądarka (blokada) | Serwer TCP |
   | 5001 | UDP (Raw Socket) | ✗ Przeglądarka | Serwer UDP |

---

### Problem: Port już w użyciu

**Symptomy:**
```
Error: Port 5000 is already in use
```

**Rozwiązanie:**

```bash
# Opcja 1: Zatrzymaj istniejący kontener
docker ps
docker stop <container_id>

# Opcja 2: Zmień port w docker-compose.yml
ports:
  - "5005:5000"  # Zamiast 5000 użyj 5005
  - "5002:5001"  # Zamiast 5001 użyj 5002

# Opcja 3: Zbadaj co siedzi na porcie (Linux/Mac)
lsof -i :5000
kill -9 <PID>
```

### Problem: Aplikacja nie ładuje się

**Symptomy:**
```
Błąd 404 / Connection refused
```

**Rozwiązanie:**

```bash
# 1. Sprawdź czy kontener się uruchamia
docker ps
docker logs network-suite

# 2. Poczekaj ~10 sekund na start aplikacji
# 3. Spróbuj inny port
# 4. Przeładuj stronę (Ctrl+R lub Cmd+R)
```

### Problem: Brak połączenia między klientem a serwerem

**Symptomy:**
```
[ERROR] ✗ Błąd połączenia
```

**Rozwiązanie:**

```bash
# 1. Sprawdź czy serwer jest uruchomiony
# Karta "Serwer" - Status powinien być 🟢 Nasłuchuje

# 2. Sprawdź adres hosta
# W Docker: localhost lub app (nazwa usługi)
# Na innym hoście: IP kontenera (np. 172.17.0.2)

# 3. Sprawdź porty
# TCP Server: domyślnie 5000
# UDP Server: domyślnie 5001

# 4. Sprawdź logi
docker logs -f network-suite

# 5. Test z konsoli
docker exec network-suite nc -zv localhost 5000
```

### Problem: Brak danych w statystykach

**Symptomy:**
```
Wysłanych bajtów: 0
Odebranych pakietów: 0
```

**Rozwiązanie:**

```bash
# 1. Sprawdź czy dane zostały wysłane
# Powinien być log [SUCCESS]

# 2. Statystyki aktualizują się co 2 sekundy
# Poczekaj trochę

# 3. Spróbuj wysłać więcej danych
# Kliknij "Wyślij" kilka razy

# 4. Przeładuj stronę
# Statystyki mogą być cache'owane
```

### Problem: Test obciążenia zbyt wolny

**Symptomy:**
```
Niezadowalnie mały throughput
```

**Rozwiązanie:**

```bash
# 1. Zmniejsz rozmiar pakietu
Rozmiar pakietu: 256 B  (zamiast 1024)

# 2. Zmniejsz opóźnienie
Opóźnienie: 0 ms  (zamiast 10)

# 3. Zwiększ liczbę wątków
Wątki: 20  (zamiast 5)

# 4. Użyj trybu Flood
Tryb: Flood  (zamiast Normal)
```

---

## Zaawansowane

### Zmiana Portów

Edytuj `docker-compose.yml`:

```yaml
services:
  app:
    ports:
      - "8000:5000"   # Web UI na porcie 8000
      - "6000:5001"   # UDP na porcie 6000
```

Potem:
```bash
docker-compose up --build
# Dostęp: http://localhost:8000
```

### Zmiana Limitu Klientów TCP

W WebUI:
```
Karta "Serwer" → "TCP Serwer" → Max klientów: 50
```

Lub w kodzie `tcp_server.py`:
```python
max_clients = 50  # Zamiast 10
```

### Dostosowanie Buforu UDP

W WebUI:
```
Karta "Serwer" → "UDP Serwer" → Max rozmiar pakietu: 131072 B
```

### Debugowanie - Logowanie

Włącz verbose logowanie w terminalu:

```bash
docker-compose logs -f app

# Pokażą się wszystkie logi DEBUG
# [DEBUG] TCP: Odebrano 16 B od 127.0.0.1:12345
```

### Dodatkowe Metryki

Monitoruj w real-time:

```bash
# Terminal 1: Logi
docker logs -f network-suite

# Terminal 2: Statystyka CPU/Pamięć
docker stats network-suite

# Terminal 3: Sieciowe statystyki
docker exec network-suite netstat -an
```

### Nagrywanie Pakietów (tcpdump)

```bash
# Wewnątrz kontenera
docker exec network-suite tcpdump -i eth0 -w packets.pcap

# Potem pobierz plik
docker cp network-suite:/app/packets.pcap .

# Otwórz w Wireshark
wireshark packets.pcap
```

---

## FAQ

### P: Czy mogę wysyłać bardzo duże pliki UDP?

**O:** UDP automatycznie fragmentuje pliki. Max rozmiar ramki UDP to 65500 B, ale możesz wysyłać pliki wielkości gigabajtów - będą podzielone na wiele pakietów. Każdy pakiet ma ID i Total count do rekonstrukcji.

### P: Czy mogę uruchomić wiele instancji?

**O:** Tak! Docker pozwala na wiele kontenerów:
```bash
docker run -p 5002:5000 network-suite  # Instancja 2
docker run -p 5003:5000 network-suite  # Instancja 3
```

### P: Jaki jest max throughput?

**O:** Zależy od:
- Rozmiaru pakietu
- Liczby wątków
- Maszyny hosta
- Sieci

Typowo: **50-500 MB/s** w LAN, **5-50 MB/s** w Internet.

### P: Czy CRC32 jest bezpieczny?

**O:** CRC32 to **checksum**, nie **hash**. Chroni przed błędami transmisji, nie przed atakami. Do bezpieczeństwa użyj TLS/SSL.

### P: Czy test Flood to DDoS?

**O:** Nie, to **test obciążenia** na własnym serwerze. Rzeczywisty DDoS: wysyła z wielu IP. Ta aplikacja wysyła z jednego miejsca i jest edukacyjna.

### P: Jaka jest różnica między Flood a SlowLoris?

**O:**
- **Flood**: Szybko, bez czekania na ACK
- **SlowLoris**: Powoli, część po części (atakuje słowością połączeń)

### P: Czy mogę zobaczyć surowe pakiety?

**O:** Tak, użyj tcpdump lub Wireshark. Patrz sekcja "Zaawansowane - Nagrywanie Pakietów".

### P: Czy to działa na Windowsie?

**O:** Tak, pod warunkiem, że masz:
- Docker Desktop dla Windows
- WSL2 (Windows Subsystem for Linux 2)
- Lub natywny Docker na Windows Server

### P: Jak zmienić format ramki?

**O:** Edytuj `protocol.py`:
```python
# Zmień magic number
TCP_MAGIC = 0xDEADBEEF  # Zamiast 0xCAFEBABE
UDP_MAGIC = 0xCAFEBABE  # Zamiast 0xDEADBEEF
```

### P: Czy mogę wyłączyć CRC32?

**O:** Nie zalecam, ale możesz w `protocol.py` skomentuować weryfikację CRC.

### P: Jaka jest maksymalna ilość połączeń?

**O:** Domyślnie 10. Możesz zmienić na dowolną wartość, ale limit systemu operacyjnego to zwykle 65535.

---

## Podsumowanie

**Network Protocol Suite** to kompletne narzędzie edukacyjne do nauki:
- ✅ Protokołów sieciowych TCP/UDP
- ✅ Implementacji własnych formatów ramek
- ✅ Programowania wielowątkowego
- ✅ Testów obciążeniowych
- ✅ Skanowania sieci

**Używaj go do nauki, eksperymentów i zadań szkolnych!**

---

**Ostatnia aktualizacja:** 2025-12-02
**Wersja:** 1.0
**Status:** Produkcja edukacyjna

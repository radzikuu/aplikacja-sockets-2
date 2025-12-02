# ⚡ Quick Start Guide - Network Protocol Suite

## 🚀 Szybki Start (5 minut)

### 1. Przygotowanie
```bash
mkdir sockets-py && cd sockets-py
mkdir app && mkdir app/templates
```

### 2. Skopiuj pliki
Wszystkie pliki Python, HTML, YAML do odpowiednich katalogów (patrz struktura poniżej)

### 3. Uruchomienie
```bash
docker-compose up --build
```

### 4. Otwórz przeglądarkę
```
http://localhost:5000
```

✅ **Gotowe!**

---

## 📁 Struktura Plików

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

---

## 🎯 Podstawowe Operacje

### Start TCP Serwera
```
1. Karta "Serwer" → TCP Serwer
2. Kliknij "Start"
3. Status: 🟢 Nasłuchuje
```

### Wysłanie Wiadomości TCP
```
1. Karta "Klient" → TCP Klient
2. Wpisz: host=localhost, port=5000
3. Kliknij "Połącz"
4. Wpisz wiadomość
5. Kliknij "Wyślij"
```

### Test Obciążenia
```
1. Karta "Tester Obciążenia"
2. Ustaw: host, port, wątki, pakiety
3. Wybierz tryb: Normal/Flood/SlowLoris
4. Kliknij "Rozpocznij"
5. Obserwuj metryki
```

### Skanowanie Sieci
```
1. Karta "Odkrywanie Hostów"
2. Kliknij "Skanuj"
3. Czekaj ~15 sekund
4. Kliknij na host, aby go wybrać
```

---

## 🔧 Porty

| Usługa | Port | Opis |
|--------|------|------|
| WebUI | 5000 | Flask + API |
| TCP Server | 5000 | (ten sam) |
| UDP Server | 5001 | Oddzielny port |

---

## 📊 Statystyki Real-time

```
Wysłanych bajtów: liczba
Odebranych bajtów: liczba
Wysłanych pakietów: liczba
Odebranych pakietów: liczba
```

Aktualizują się co 2 sekundy.

---

## 🟢🔴🟡 Status Indicators

- 🟢 **Zielony** = Połączony/Uruchomiony
- 🔴 **Czerwony** = Rozłączony/Zatrzymany
- 🟡 **Żółty** = W toku/Oczekiwanie

---

## 📝 Logi

```
[HH:MM:SS] [INFO] Gotowy...
[HH:MM:SS] [SUCCESS] ✓ Wysłano
[HH:MM:SS] [ERROR] ✗ Błąd
[HH:MM:SS] [WARNING] ⚠️ Uwaga
```

---

## 🔐 Format Ramek

### TCP (0xCAFEBABE)
```
Nagłówek: 20B
┌─────────┬─────┬────┬──────┬────┬────┐
│ Magic   │Type │Len │CRC32 │TS  │Seq │
│ 0xCAFE  │ 1B  │2B  │4B    │4B  │4B  │
└─────────┴─────┴────┴──────┴────┴────┘
Payload: Do 65535B
```

### UDP (0xDEADBEEF)
```
Nagłówek: 16B
┌────────────┬─────┬────┬──────┬────┬────┬──────┐
│ Magic      │Type │Len │CRC32 │PID │Tot│ Time │
│ 0xDEADBEEF │ 1B  │2B  │4B    │2B  │2B │ 1B   │
└────────────┴─────┴────┴──────┴────┴────┴──────┘
Payload: Do 65500B
```

---

## 🧵 Tryby Testu Obciążenia

### 1. Normal
- Wysyła TCP pakiety
- Czeka na echo
- Mierzy czasy
- ✅ Rekomendowany

### 2. Flood
- Szybko, bez czekania
- Testuje odporność
- ⚠️ Intensywny

### 3. SlowLoris
- Powoli, kawałkami
- Testuje long-polling
- 📚 Edukacyjny

---

## 🐛 Troubleshooting

| Problem | Rozwiązanie |
|---------|------------|
| Port 5000 w użyciu | `docker kill $(docker ps -q)` |
| Nie ładuje się | Czekaj 10s, przeładuj stronę |
| Brak połączenia | Sprawdź czy serwer startuje |
| Brak statystyk | Wysłij dane i czekaj 2s |
| Kontener się crashuje | `docker logs network-suite` |

---

## 📚 Pełna Dokumentacja

Patrz: `UZYTKOWNIK-GUIDE.md` (kompletny przewodnik)

---

## 🔍 Docker Komendy

```bash
# Uruchomienie
docker-compose up --build

# Logi
docker-compose logs -f

# Stop
docker-compose down

# Rebuild
docker-compose up --build --no-cache

# Wejście do kontenera
docker exec -it network-suite bash
```

---

## 📧 Kontakt / Błędy

Sprawdź logi:
```bash
docker logs -f network-suite
```

---

**Happy Testing! 🎉**

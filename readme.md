

# FireBot

FireBot to lekki system do analizy logów firewalli (PAN‑OS) i automatycznego zarządzania blokadami adresów IP na podstawie wykrytych zdarzeń (np. brute‑force). Aplikacja jest napisana w Django i zawiera komponenty do odbioru logów UDP, parsowania wpisów THREAT, agregacji prób logowań, eskalacji blokad oraz interfejs webowy do zarządzania listami i statystykami.

English quick summary: FireBot is a lightweight PAN‑OS firewall log analytics and automated IP blocking system built with Django. It ingests UDP THREAT logs, aggregates failed login attempts, escalates blocking levels and offers a web UI for black/white lists and statistics visualization.

Ten README zawiera: funkcje, architekturę, instalację lokalną oraz Docker, konfigurację, testowanie, debugowanie, zalecenia produkcyjne, roadmap i licencję.

## Spis treści
1. [Opis / FireBot](#firebot)
2. [Funkcje](#funkcje)
3. [Architektura (krótko)](#architektura-krótko)
4. [Szybka instalacja (lokalnie)](#szybka-instalacja-lokalnie)
5. [Uruchomienie w Dockerze](#uruchomienie-w-dockerze-docker-compose)
6. [Konfiguracja](#konfiguracja)
7. [Testowanie / wysyłanie przykładowych logów](#testowanie--wysyłanie-przykładowych-logów)
8. [Debugowanie i logi](#debugowanie-i-logi)
9. [Zalecenia produkcyjne](#zalecenia-produkcyjne)
10. [Roadmap](#roadmap)
11. [Contributing](#contributing)
12. [Licencja](#licencja)

## Funkcje

- Odbiór logów UDP w formacie PAN‑OS (THREAT)
- Parsowanie i zapis logów do bazy (`ThreatLog`)
- Agregacja nieudanych prób logowania (`FailedLoginSummary`)
- Mechanizm eskalacji blokad (poziomy 1..4) i automatyczne/ręczne odblokowywanie (`BlockedAddress`)
- Zarządzanie `blacklist` / `whitelist` przez UI
- Widok statystyk (wykresy D3.js)
- Prosty mechanizm generowania komend do PAN‑OS (curl) w `tests/rules.py`
- Skrypty testowe do wysyłania sztucznych logów w `tests/send_log.py`

## Architektura (krótko)

- Backend: Django (widoki, modele, formularze)
- Baza danych: SQLite (plik `db.sqlite3` w repozytorium - w produkcji zalecany PostgreSQL)
- Workery: wątki (LogFetcher, LogAnalyzer, ActionExecutor) uruchamiane z poziomu app config `worker.apps`
- Frontend: Django templates + D3.js do wizualizacji statystyk

## Pliki ważne w repo

- `FireBot/` – aplikacja Django (widoki, modele, middleware)
- `dashboard/` – panel administracyjny, ustawienia, statystyki
- `worker/` – implementacja fetchera, analizera i executora (odbiór UDP, parsowanie, logika blokad)
- `tests/` – skrypty pomocnicze: `send_log.py` (symulacja logów), `rules.py` (generatory poleceń dla PAN‑OS)
- `Dockerfile`, `docker-compose.yml` – konteneryzacja
- `requirements.txt` – zależności (Django, python-dotenv)

## Szybka instalacja (lokalnie)

Wymagane: Python 3.10+, virtualenv

1. Utwórz i aktywuj virtualenv

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Zainstaluj zależności

```powershell
pip install -r requirements.txt
```

3. Uruchom migracje

```powershell
python manage.py makemigrations FireBot
python manage.py makemigrations dashboard
python manage.py migrate
python manage.py migrate dashboard
python manage.py createsuperuser
```

4. Uruchom aplikację deweloperską

```powershell
python manage.py runserver 0.0.0.0:8000
```

Frontend dostępny będzie pod `http://localhost:8000/`.

## Uruchomienie w Dockerze (Docker Compose)

Szybkie uruchomienie aplikacji przy użyciu `docker-compose` (plik `docker-compose.yml` jest dołączony do repozytorium).

Budowanie i uruchomienie w tle:

```powershell
docker compose build
docker compose up -d
```

(opcjonalnie) Sprawdź logi kontenera:

```powershell
docker compose logs -f web
```

Jeśli chcesz uruchomić w trybie interaktywnym (bez detacha):

```powershell
docker compose up
```

Przykład `docker-compose.yml` mapuje porty `8000` (UI) i `514/udp` (syslog) oraz montuje `db.sqlite3` i `settings_docker.py` do kontenera. W środowisku produkcyjnym rozważ użycie zewnętrznej bazy (Postgres) oraz bezpieczne przechowywanie sekretów (zmienne środowiskowe lub Secret Manager).

Uwaga: przed uruchomieniem skontenerowanej aplikacji zaktualizuj domyślnego superużytkownika w `entrypoint.sh` (login i hasło):

```sh
# entrypoint.sh
username = "admin"
password = "adminpass"
```

Zmień wartości na własne poświadczenia lub wyłącz automatyczne tworzenie superusera zgodnie z potrzebami środowiska.

## Konfiguracja

- Aplikacja czyta podstawowe ustawienia z Django settings.
- Ustawienia dostępne w panelu `Dashboard → Settings`:
	- `log_server_ip`, `log_server_port` – adres i port, na którym LogFetcher nasłuchuje
	- `failed_attempts_limit`, `reset_attempts_time` – parametry detekcji brute‑force
	- `block_duration_1..3`, `block_period_reset_time`, `permanent_block` – parametry eskalacji blokad
	- `executor_automated` – czy ActionExecutor ma wykonywać blokady automatycznie (API)

Po zmianie ustawień workerzy są restartowani przez `worker.apps`.

## Testowanie / wysyłanie przykładowych logów

W repo dostępny jest skrypt `send_log.py`, który generuje i wysyła przykładowy log THREAT do wskazanego serwera syslog UDP.

Przykład użycia (lokalnie):

```powershell
python tests/send_log.py
```

Funkcja `send_random_threats()` pozwala generować ciąg losowych logów z podsieci (domyślnie `192.168.64.0/24`), z losowym interwałem (30s–180s) i losowym `repeat_count` (10–70). Możesz ją wywołać w REPL lub z innego skryptu.


## Debugowanie i logi

- Workery wypisują debug do konsoli (w zależności od flag debug w kodzie). Jeśli coś nie działa, sprawdź logi serwera Django oraz konsolę Dockera, jeśli włączysz debugowanie poszczególnego pliku.

## Zalecenia produkcyjne

- Zastąpić SQLite PostgreSQL dla lepszej skalowalności.
- Dodać bezpieczną integrację z API urządzeń (PAN‑OS) z retry/backoff i audytem akcji.


## Licencja

Projekt jest dostępny na warunkach licencji MIT — plik `LICENSE.txt` znajduje się w repozytorium.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.txt)


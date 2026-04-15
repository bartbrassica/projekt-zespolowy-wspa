# Harmonogram Projektu – Digital Lockbox

## Informacje ogólne

| | |
|---|---|
| **Nazwa projektu** | Digital Lockbox – Menedżer Haseł |
| **Typ aplikacji** | Aplikacja webowa SPA + REST API |
| **Stos technologiczny** | Django + Django Ninja, React + TypeScript, PostgreSQL, Docker |
| **Czas realizacji** | 20.04.2026 – 31.05.2026 (~6 tygodni) |

---

## Etapy realizacji

### Etap 1 – Analiza wymagań i projektowanie architektury
**Okres:** 20.04.2026 – 24.04.2026

| Zadanie | Wymagania |
|---|---|
| Analiza wymagań funkcjonalnych i niefunkcjonalnych | FR1–FR4, NFR1–NFR3 |
| Projekt architektury systemu (API + GUI + DB) | NFR2.1 |
| Wybór stosu technologicznego | NFR2.1, NFR3.4 |
| Projekt schematu bazy danych (PostgreSQL) | NFR2.1, NFR2.2 |
| Projekt modelu szyfrowania (PBKDF2 + Fernet, Argon2) | NFR1.1, NFR1.2 |
| Konfiguracja środowiska deweloperskiego i repozytoriów | — |

---

### Etap 2 – Implementacja modułu uwierzytelniania (Backend)
**Okres:** 25.04.2026 – 10.05.2026 *(równolegle z Etapem 3)*

| Zadanie | Wymagania |
|---|---|
| Inicjalizacja projektu Django, konfiguracja bazy danych | NFR2.1 |
| Rejestracja użytkownika z walidacją siły hasła | FR1.1, NFR1.6 |
| Logowanie e-mail + hasło | FR1.2 |
| Haszowanie hasła algorytmem Argon2 | NFR1.2 |
| Generowanie i weryfikacja tokenów JWT (Access/Refresh) | FR1.4, NFR1.3 |
| Single-Use Refresh Token (zapobieganie Replay Attack) | NFR1.4 |
| Weryfikacja konta przez e-mail z tokenem | FR1.3 |
| Wylogowanie z unieważnieniem Refresh Tokena | FR1.5 |
| Zarządzanie sesjami (lista aktywnych, zdalne zakończenie) | FR1.8 |

---

### Etap 3 – Implementacja frontendu uwierzytelniania (GUI)
**Okres:** 25.04.2026 – 10.05.2026 *(równolegle z Etapem 2)*

| Zadanie | Wymagania |
|---|---|
| Inicjalizacja projektu React + TypeScript + Vite + TailwindCSS | NFR3.4 |
| Formularz rejestracji z walidacją klienta | FR1.1, NFR3.2 |
| Formularz logowania | FR1.2, NFR3.2 |
| Strona weryfikacji e-mail (token z URL) | FR1.3 |
| Integracja z JWT (przechowywanie, odświeżanie tokenów) | FR1.4, NFR1.3 |
| Responsywny layout aplikacji (SPA) | NFR3.1, NFR3.4 |
| System powiadomień (Alerts: sukces/błąd, auto-zamykanie) | NFR3.3 |

---

### Etap 4 – Implementacja zarządzania hasłami
**Okres:** 11.05.2026 – 17.05.2026

| Zadanie | Wymagania |
|---|---|
| Endpoints CRUD dla wpisów haseł (API) | FR2.1, FR2.3, FR2.4 |
| Szyfrowanie/odszyfrowywanie haseł (PBKDF2 + Fernet AES-128-CBC) | FR2.2, NFR1.1 |
| Historia zmian hasła | FR2.3 |
| Wyszukiwanie i sortowanie wpisów | FR2.5 |
| Logowanie dostępów (IP, User Agent, akcja) | NFR1.5 |
| Generator bezpiecznych haseł (długość, symbole, cyfry, wykluczenia) | FR2.7 |
| Widok listy haseł w GUI (React) | FR2.1, FR2.5 |
| Kopiowanie hasła/loginu do schowka + auto-czyszczenie po 30s | FR2.6 |
| Bulk Delete (zbiorcze usuwanie) | FR2.4 |
| Ulubione, daty wygaśnięcia haseł | FR3.3, FR3.4 |

---

### Etap 5 – Reset hasła i zmiana hasła
**Okres:** 18.05.2026 – 22.05.2026

| Zadanie | Wymagania |
|---|---|
| Endpoint „Forgot Password" (e-mail z tokenem czasowym) | FR1.6 |
| Endpoint reset hasła (weryfikacja tokena + nowe hasło) | FR1.6 |
| Endpoint zmiany hasła (wymaga podania aktualnego hasła) | FR1.7 |
| Formularze GUI: Forgot Password, Reset Password | FR1.6, NFR3.2 |
| Powiadomienia e-mail o zmianie/resecie hasła | FR1.6 |
| Refaktoryzacja i linting kodu (API + GUI) | — |

---

### Etap 6 – Dockeryzacja i wdrożenie
**Okres:** 23.05.2026 – 27.05.2026 *(równolegle z Etapem 7)*

| Zadanie | Wymagania |
|---|---|
| Dockerfile dla API (Django) | — |
| Dockerfile dla GUI (React + Nginx) | — |
| docker-compose.yml (API + GUI + PostgreSQL) | NFR2.1 |
| docker-compose.test.yml (środowisko testowe) | — |
| Konfiguracja zmiennych środowiskowych (.env) | — |
| Aktualizacja README z instrukcją uruchomienia | — |

---

### Etap 7 – Testy automatyczne
**Okres:** 23.05.2026 – 27.05.2026 *(równolegle z Etapem 6)*

| Zadanie | Wymagania |
|---|---|
| Konfiguracja pytest + pytest-xdist (testy równoległe) | — |
| Testy modeli bazy danych | NFR2.1 |
| Testy endpointów uwierzytelniania (rejestracja, logowanie, JWT) | FR1.1–FR1.8 |
| Testy endpointów zarządzania hasłami | FR2.1–FR2.7 |
| Osiągnięcie 100% pokrycia kodu testami (coverage) | — |
| Generowanie raportów HTML z pokrycia | — |

---

### Etap 8 – Finalizacja i dokumentacja
**Okres:** 28.05.2026 – 31.05.2026

| Zadanie | Wymagania |
|---|---|
| Endpoints CRUD folderów i tagów (hierarchia, przenoszenie, kolor) | FR3.1, FR3.2 |
| Filtrowanie haseł po folderze i tagach | FR2.5 |
| Widoki GUI: zarządzanie folderami i tagami | FR3.1, FR3.2 |
| Optymalizacja zapytań – indeksy dla folderów, tagów, dat wygaśnięcia | NFR2.2, NFR2.3 |
| Refaktoryzacja i usunięcie zbędnych logów | — |
| Aktualizacja dokumentacji (README, sekcja szyfrowania) | — |
| Finalne testy integracyjne | — |

---

## Podsumowanie harmonogramu

| Etap | Nazwa | Okres |
|---|---|---|
| 1 | Analiza wymagań i projektowanie | 20.04 – 24.04.2026 |
| 2 | Backend – uwierzytelnianie | 25.04 – 10.05.2026 |
| 3 | Frontend – uwierzytelnianie | 25.04 – 10.05.2026 |
| 4 | Zarządzanie hasłami (API + GUI) | 11.05 – 17.05.2026 |
| 5 | Reset i zmiana hasła | 18.05 – 22.05.2026 |
| 6 | Dockeryzacja i wdrożenie | 23.05 – 27.05.2026 |
| 7 | Testy automatyczne (100% coverage) | 23.05 – 27.05.2026 |
| 8 | Finalizacja i dokumentacja | 28.05 – 31.05.2026 |

**Łączny czas realizacji: ~6 tygodni (20.04.2026 – 31.05.2026)**

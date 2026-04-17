# KARTA PROJEKTU: DigitalLockbox (DLB)

## 1. Informacje Ogólne
| Sekcja | Treść |
| :--- | :--- |
| **Tytuł projektu** | **DigitalLockbox (DLB) – Secure Password Manager** |
| **Cel projektu** | Dostarczenie intuicyjnego narzędzia o klasie bezpieczeństwa **Military-Grade**, opartego na zasadzie **Zero-Knowledge**, gdzie użytkownik zachowuje pełną kontrolę nad swoimi danymi poprzez szyfrowanie E2EE. |
| **Uzasadnienie** | Odpowiedź na potrzebę suwerenności cyfrowej. System eliminuje barierę między zaawansowaną kryptografią a nowoczesnym UX, chroniąc przed wyciekami danych. |
| **Stos technologiczny** | Django + Django Ninja (Backend), React + TypeScript (Frontend), PostgreSQL, Docker. |

## 2. Zespół Projektowy i Role
* **Amanda Krasnowska-Szymańska (Project Manager)**: Planowanie cykli, nadzór nad harmonogramem, zarządzanie ryzykiem i spójnością dokumentacji.
* **Bartłomiej Kapuśniak (Developer)**: Architektura bazy danych, implementacja logiki API oraz modułów kryptograficznych (Argon2, AES).
* **Agata Smelkowska (QA Engineer / Tester)**: Zapewnienie jakości, automatyzacja testów (pytest), weryfikacja bezpieczeństwa i zgodności z NFR.

## 3. Wizja i Filozofia Systemu
DigitalLockbox to holistyczna odpowiedź na zagrożenia w cyberprzestrzeni. System opiera się na trzech fundamentach:
1. **Harmonia UX i Kryptografii**: Bezpieczeństwo, które nie jest uciążliwe dla użytkownika.
2. **Zasada Zero-Knowledge**: Architektura uniemożliwiająca dostawcy odczytanie haseł (szyfrowanie po stronie klienta).
3. **Skalowalność**: Optymalizacja zapytań PostgreSQL i warstwy SPA dla najwyższej wydajności.

## 4. Specyfikacja Wymagań (Wybrane)

### 4.1 Wymagania Funkcjonalne (FR)
| ID | Nazwa | Opis |
| :--- | :--- | :--- |
| **FR-1** | Rejestracja | Walidacja siły hasła (min. 8 znaków, wielka/mała litera, cyfra, znak specjalny). |
| **FR-4** | Tokeny JWT | Wydawanie tokenów Access (15 min) i Refresh (14 dni). |
| **FR-9** | Tworzenie haseł | Dodawanie zaszyfrowanych wpisów (nazwa, URL, login, hasło). |
| **FR-16** | Foldery | Organizacja haseł w strukturze hierarchicznej. |
| **FR-22** | Udostępnianie | Generowanie bezpiecznych linków do haseł. |

### 4.2 Wymagania Niefunkcjonalne (NFR)
| ID | Nazwa | Specyfikacja Techniczna |
| :--- | :--- | :--- |
| **NFR-1** | Szyfrowanie E2EE | PBKDF2-HMAC-SHA256 (200k iteracji) + Fernet (AES-128-CBC). |
| **NFR-2** | Haszowanie | Hasło główne składowane przy użyciu algorytmu **Argon2**. |
| **NFR-4** | Replay Attack | Mechanizm rotacji Refresh Tokena (jednorazowy użytek). |
| **NFR-5** | Logowanie zdarzeń | Rejestracja IP, User Agent oraz typu akcji dla celów audytowych. |

## 5. Szczegółowy Harmonogram Realizacji (20.04.2026 – 31.05.2026)

| Etap | Okres | Kluczowe zadania |
| :--- | :--- | :--- |
| **1. Analiza i Projekt** | 20.04 – 24.04 | Projekt bazy danych i modelu szyfrowania (PBKDF2, Fernet, Argon2). |
| **2. Uwierzytelnianie** | 25.04 – 10.05 | Rejestracja, logowanie, obsługa tokenów JWT w Django Ninja. |
| **3. Logika Biznesowa** | 11.05 – 15.05 | Modele haseł, szyfrowanie pól, CRUD haseł (Backend). |
| **4. Frontend Core** | 16.05 – 20.05 | Integracja React z API, dashboard użytkownika, formularze. |
| **5. Funkcje Extra** | 21.05 – 23.05 | Generator haseł, logi audytowe, reset hasła przez e-mail. |
| **6. UI/UX Design** | 24.05 – 25.05 | Stylowanie TailwindCSS, responsywność (RWD). |
| **7. Testy i Jakość** | 26.05 – 27.05 | Konfiguracja pytest, testy endpointów, 100% code coverage. |
| **8. Finalizacja** | 28.05 – 31.05 | Zarządzanie folderami, optymalizacja SQL, Docker, dokumentacja. |

## 6. Analiza Ryzyka
* **Błędy kryptograficzne**: Niewłaściwa implementacja bibliotek. *Mitygacja: Audyt kodu przez QA (Agata) i testy jednostkowe.*
* **Wydajność bazy**: Wolne zapytania przy dużej liczbie haseł. *Mitygacja: Indeksowanie PostgreSQL przez Dewelopera (Bartłomiej).*
* **Terminowość**: Opóźnienia w integracji. *Mitygacja: Zarządzanie w Scrumie przez PM (Amanda).*

---
**Zatwierdzono przez Zespół DigitalLockbox**
Data: 17.04.2026
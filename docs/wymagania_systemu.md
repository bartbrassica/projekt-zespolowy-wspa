# 1. Wymagania systemu

## 1.1 Wymagania funkcjonalne

| ID    | Nazwa                    | Opis |
|-------|--------------------------|------|
| FR-1  | Rejestracja użytkownika  | System musi umożliwiać rejestrację konta z walidacją siły hasła (min. 8 znaków, wielka/mała litera, cyfra, znak specjalny). |
| FR-2  | Logowanie                | Użytkownik musi móc zalogować się za pomocą adresu e-mail i hasła. |
| FR-3  | Weryfikacja konta        | System musi wysyłać e-mail weryfikacyjny i weryfikować konto za pomocą tokena. |
| FR-4  | Zarządzanie tokenami     | System musi wydawać tokeny JWT (Access i Refresh) i umożliwiać ich odświeżanie. |
| FR-5  | Wylogowanie              | Użytkownik musi mieć możliwość wylogowania (unieważnienie tokenów). |
| FR-6  | Reset hasła              | Możliwość resetu hasła przez e-mail i token czasowy. |
| FR-7  | Zmiana hasła             | Możliwość zmiany hasła po zalogowaniu. |
| FR-8  | Zarządzanie sesjami      | Lista aktywnych sesji i możliwość ich zakończenia. |
| FR-9  | Tworzenie haseł          | Dodawanie wpisów (nazwa, URL, login, hasło szyfrowane). |
| FR-10 | Szyfrowanie danych       | Szyfrowanie i odszyfrowywanie haseł hasłem głównym. |
| FR-11 | Aktualizacja haseł       | Edycja wpisów + historia zmian. |
| FR-12 | Usuwanie haseł           | Usuwanie pojedyncze i masowe. |
| FR-13 | Wyszukiwanie             | Wyszukiwanie i filtrowanie haseł. |
| FR-14 | Kopiowanie danych        | Kopiowanie do schowka z automatycznym czyszczeniem. |
| FR-15 | Generator haseł          | Generowanie bezpiecznych haseł. |
| FR-16 | Foldery                  | Zarządzanie folderami (hierarchia). |
| FR-17 | Tagi                     | Tworzenie i przypisywanie tagów. |
| FR-18 | Ulubione                 | Oznaczanie wpisów jako ulubione. |
| FR-19 | Wygasanie haseł          | Ustawianie dat wygaśnięcia. |
| FR-20 | Eksport danych           | Eksport do JSON/CSV. |
| FR-21 | Import danych            | Import z JSON/CSV. |
| FR-22 | Udostępnianie            | Generowanie bezpiecznych linków do haseł. |

---

## 1.2 Wymagania niefunkcjonalne

| ID     | Nazwa                    | Opis |
|--------|--------------------------|------|
| NFR-1  | Szyfrowanie end-to-end   | PBKDF2-HMAC-SHA256 (200k iteracji) + Fernet (AES-128-CBC). |
| NFR-2  | Haszowanie hasła         | Hasło główne haszowane algorytmem Argon2. |
| NFR-3  | Autoryzacja              | JWT (Access: 15 min, Refresh: 14 dni). |
| NFR-4  | Replay attack            | Refresh Token jednorazowy. |
| NFR-5  | Logowanie zdarzeń        | Rejestrowanie operacji (IP, User Agent, akcja). |
| NFR-6  | Walidacja haseł          | Wymaganie silnych haseł. |
| NFR-7  | Baza danych              | PostgreSQL. |
| NFR-8  | Optymalizacja            | Indeksy i optymalizacja zapytań. |
| NFR-9  | Wydajność                | Odpowiedzi API < 1 sekunda. |
| NFR-10 | Responsywność            | UI responsywny. |
| NFR-11 | Walidacja formularzy     | Walidacja po stronie klienta i serwera. |
| NFR-12 | Komunikaty               | System powiadomień (alerts). |
| NFR-13 | Architektura klienta     | Aplikacja typu SPA. |
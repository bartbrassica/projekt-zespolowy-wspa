# KARTA PROJEKTU – Digital Lockbox

---

## 1. Informacje ogólne

**Tytuł projektu:**  
Digital Lockbox – System Zarządzania Hasłami  

**Akronim projektu:**  
DLB  

**Data utworzenia:**  
20.04.2026  

**Wersja dokumentu:**  
1.0  

### Zespół projektowy

| Imię i nazwisko | Rola w projekcie | Zakres odpowiedzialności |
|----------------|------------------|--------------------------|
| Amanda Krasnowska-Szymańska | Kierownik projektu | Koordynacja prac, analiza wymagań, nadzór nad dokumentacją |
| Bartłomiej Kapuśniak | Programista | Implementacja backendu, architektura systemu |
| Agata Smelkowska | Tester | Testy systemu, scenariusze testowe, kontrola jakości |

**Prowadzący:**  
[uzupełnij]  

**Jednostka dydaktyczna:**  
[uzupełnij]  

---

## 2. Cel projektu

Celem projektu jest opracowanie i implementacja aplikacji webowej umożliwiającej bezpieczne zarządzanie hasłami użytkowników.

System ma umożliwiać:
- przechowywanie haseł w postaci zaszyfrowanej,
- zarządzanie danymi logowania (CRUD),
- generowanie bezpiecznych haseł,
- organizację danych (foldery, tagi),
- bezpieczne udostępnianie haseł,
- zarządzanie sesjami oraz monitorowanie aktywności użytkownika.

---

## 3. Uzasadnienie projektu

W dobie rosnącej liczby usług cyfrowych użytkownicy zmuszeni są do zarządzania wieloma kontami, co prowadzi do:

- stosowania słabych haseł,
- powielania tych samych danych logowania,
- przechowywania haseł w niezabezpieczonych miejscach.

Projekt Digital Lockbox stanowi odpowiedź na te problemy poprzez dostarczenie systemu zapewniającego wysoki poziom bezpieczeństwa przy zachowaniu intuicyjnego interfejsu użytkownika.

---

## 4. Zakres projektu

### W zakresie projektu:
- analiza wymagań funkcjonalnych i niefunkcjonalnych,
- projekt architektury systemu (API + frontend + baza danych),
- implementacja aplikacji webowej (Django + React),
- implementacja mechanizmów bezpieczeństwa,
- zarządzanie hasłami (CRUD, wyszukiwanie, filtrowanie),
- implementacja funkcji organizacyjnych (foldery, tagi),
- testowanie systemu,
- przygotowanie dokumentacji projektowej i technicznej.

### Poza zakresem projektu:
- aplikacja mobilna,
- integracja z zewnętrznymi systemami (np. LDAP),
- wdrożenie produkcyjne,
- komercjalizacja systemu.

---

## 5. Główne wymagania

### Wymagania funkcjonalne:
- rejestracja i logowanie użytkownika,
- weryfikacja konta przez e-mail,
- zarządzanie sesjami użytkownika,
- dodawanie, edycja i usuwanie haseł,
- szyfrowanie i odszyfrowywanie danych,
- wyszukiwanie i filtrowanie wpisów,
- generator bezpiecznych haseł,
- organizacja danych (foldery, tagi),
- eksport i import danych,
- udostępnianie haseł.

### Wymagania niefunkcjonalne:
- szyfrowanie danych z wykorzystaniem nowoczesnych algorytmów kryptograficznych,
- bezpieczne przechowywanie haseł z użyciem funkcji haszujących odpornych na ataki,
- mechanizmy autoryzacji i uwierzytelniania użytkowników,
- ochrona przed podstawowymi typami ataków,
- wydajność (czas odpowiedzi < 1 sekunda),
- responsywność interfejsu (SPA),
- logowanie zdarzeń systemowych.

Szczegółowa specyfikacja wymagań funkcjonalnych i niefunkcjonalnych została opracowana w ramach dokumentacji projektowej i stanowi rozszerzenie niniejszej karty projektu.

---

## 6. Zespół projektowy i role

| Rola | Osoba | Odpowiedzialność |
|------|--------|------------------|
| Kierownik projektu | Amanda Krasnowska-Szymańska | Planowanie, koordynacja, nadzór |
| Programista | Bartłomiej Kapuśniak | Implementacja backendu i logiki systemu |
| Tester | Agata Smelkowska | Testy funkcjonalne i jakościowe |

---

## 7. Zasoby i narzędzia

| Kategoria | Narzędzie / Technologia | Zastosowanie |
|----------|------------------------|--------------|
| Backend | Django, Django Ninja | API i logika systemu |
| Frontend | React, TypeScript | Interfejs użytkownika |
| Baza danych | PostgreSQL | Przechowywanie danych |
| Repozytorium | GitHub | Kontrola wersji |
| Konteneryzacja | Docker | Środowisko uruchomieniowe |
| Testy | Pytest | Testy automatyczne |
| Komunikacja | Teams / Discord | Praca zespołowa |

---

## 8. Harmonogram realizacji

| Etap | Zakres | Okres |
|------|--------|-------|
| 1 | Analiza wymagań i projekt architektury | 20.04 – 24.04.2026 |
| 2 | Backend – uwierzytelnianie | 25.04 – 10.05.2026 |
| 3 | Frontend – uwierzytelnianie | 25.04 – 10.05.2026 |
| 4 | Zarządzanie hasłami | 11.05 – 17.05.2026 |
| 5 | Reset i zmiana hasła | 18.05 – 22.05.2026 |
| 6 | Dockeryzacja i wdrożenie | 23.05 – 27.05.2026 |
| 7 | Testy automatyczne | 23.05 – 27.05.2026 |
| 8 | Finalizacja i dokumentacja | 28.05 – 31.05.2026 |

---

## 9. Ryzyka i działania zapobiegawcze

| Nr | Ryzyko | Działanie zapobiegawcze |
|----|--------|--------------------------|
| 1 | Opóźnienia w realizacji | Regularne spotkania zespołu |
| 2 | Błędy implementacyjne | Testy i przegląd kodu |
| 3 | Problemy bezpieczeństwa | Testy bezpieczeństwa |
| 4 | Problemy komunikacyjne | Stała komunikacja online |
| 5 | Utrata danych | Repozytorium Git i backupy |

---

## 10. Oczekiwane rezultaty

- działająca aplikacja webowa (Digital Lockbox),
- system zarządzania hasłami,
- dokumentacja projektowa,
- dokumentacja techniczna,
- raport z testów,
- prezentacja projektu.

---

## 11. Kryteria sukcesu

- system działa poprawnie i stabilnie,
- spełnia wszystkie wymagania funkcjonalne,
- zapewnia bezpieczeństwo danych,
- dokumentacja jest kompletna,
- projekt został ukończony w terminie.

---

## 12. Akceptacja projektu

| Funkcja | Imię i nazwisko | Data | Podpis |
|--------|----------------|------|--------|
| Kierownik projektu | Amanda Krasnowska-Szymańska | | |
| Prowadzący | [uzupełnij] | | |
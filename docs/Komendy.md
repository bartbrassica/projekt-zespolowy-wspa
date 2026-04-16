# Git i Github

## Instrukcja - najważniejsze komendy

- **git status** - podgląd aktualnych plików, które znajdują się w repozytorium
- **git add** - dodawanie propozycji zmian w plikach
- **git commit** - tworzenie kopii zapasowej zmian i zapisanie w historii lokalnej
- **git log** - wyświetlenie historii commitów 
- **git checkout [nazwa_branch]** - przejście do gałęzi - [nazwa gałęzi]
- main -> **git checkout -b [nazwa_branch]** - utworzenie nowej gałęzi i przejście na nią
- **git pull** - pobranie zmian z repozytorium online 
- **git push origin** [nazwa_branch] - wysłanie lokalnych zmian na serwer do repo, na określony branch
- **git branch -D [nazwa_branch]** - usunięcie brancha lokalnie

## Praca w repo krok po kroku
1. Przejdź na branch main
1. Pobierz najnowsze zmiany
1. Stwórz nowy branch wg. schematu **Inicjały_NrPR** i przejdź na ten branch
1. Przygotuj zmiany 
1. Dodaj zmiany do commita
1. Scommituj zmiany, w wiadomości commita opisz co zostało zmienione
1. Wypchnij zmiany do repo
1. Stwórz PR - pullrequest na github
1. Wyślij innym do sprawdzenia
1. Po zatwierdzeniu poproś o scalenie zmian

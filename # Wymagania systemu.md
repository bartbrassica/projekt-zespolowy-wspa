# Wymagania systemu

## Wymagania funkcjonalne (FR)

FR1.1, Rejestracja Użytkownika, System musi umożliwiać rejestrację konta z walidacją
siły hasła (min. 8 znaków, wielka/mała litera, cyfra, znak specjalny).
FR1.2, Logowanie, Użytkownik musi móc zalogować się za pomocą adresu e-mail
i hasła.
FR1.3, Weryfikacja Konta, System musi wysyłać e-mail weryfikacyjny i weryfikować
konto za pomocą tokena. Niezalogowany użytkownik musi zostać zablokowany.
FR1.4, Zarządzanie Tokenami, System musi wydawać tokeny JWT (Access i Refresh)
i umożliwiać odświeżanie Access Tokena za pomocą Refresh Tokena.
FR1.5, Wylogowanie, Użytkownik musi mieć możliwość wylogowania, co unieważnia
aktywne tokeny odświeżające.
FR1.6, Reset Hasła, Użytkownik musi móc zażądać resetu hasła (Forgot Password) za
pomocą e-maila i tokena z limitem czasowym.
FR1.7, Zmiana Hasła, Użytkownik musi mieć możliwość zmiany hasła po zalogowaniu,
podając aktualne hasło.
FR1.8, Zarządzanie Sesjami, Użytkownik musi mieć dostęp do listy aktywnych sesji
i możliwość zdalnego ich zakończenia.
FR2.1, Tworzenie Hasła, Użytkownik musi móc tworzyć nowe wpisy haseł, podając nazwę, stronę/URL, login i hasło (szyfrowane hasłem głównym).
FR2.2, Szyfrowanie/Odszyfrowywanie, Hasła muszą być szyfrowane hasłem głównym
przed zapisem i odszyfrowywane przed wyświetleniem lub skopiowaniem.
FR2.3, Aktualizacja Hasła, Użytkownik musi mieć możliwość edycji wpisów, w tym
zmiany hasła (co wymaga ponownego szyfrowania). Poprzednie hasło musi zostać zapisane w historii.
FR2.4, Usuwanie Hasła, Użytkownik musi móc usuwać pojedyncze wpisy lub zbiorczo
(Bulk Delete).
FR2.5, Wyszukiwanie i Sortowanie, System musi umożliwiać wyszukiwanie haseł (po
nazwie, stronie, loginie, notatkach) oraz filtrowanie po folderach i tagach.
FR2.6, Kopiowanie Hasła/Loginu, Użytkownik musi móc skopiować odszyfrowane hasło/login do schowka, z automatycznym czyszczeniem schowka po 30 sekundach.
FR2.7, Generator Haseł, System musi oferować generator bezpiecznych haseł z opcjami
dostosowania (długość, symbole, cyfry, wielkie/małe litery, wykluczenie znaków niejednoznacznych).
FR3.1, Foldery, Użytkownik musi móc tworzyć, edytować i usuwać foldery w celu organizacji haseł (Foldery mogą być hierarchiczne, ale usunięcie folderu przenosi wpisy do
głównego widoku).
FR3.2, Tagi, Użytkownik musi móc tworzyć, zarządzać (kolor, nazwa) i przypisywać tagi
do haseł.
FR3.3, Ulubione, Użytkownik musi móc oznaczać wpisy jako ulubione.
FR3.4, Wygasanie Haseł, Użytkownik musi móc ustawiać datę wygaśnięcia hasła.
FR4.1, Eksport Danych, System musi umożliwiać eksport haseł do plików JSON lub
CSV, z opcją dołączenia odszyfrowanych haseł (wymaga hasła głównego).
FR4.2, Import Danych, System musi umożliwiać import haseł z plików JSON lub CSV
(wymaga hasła głównego do szyfrowania nowych wpisów).
FR4.3, Udostępnianie, Użytkownik musi mieć możliwość wygenerowania bezpiecznego
linku do udostępnienia hasła, chronionego unikalnym kluczem (w URL) oraz opcjonalnymi ograniczeniami (max. wyświetleń, czas wygaśnięcia, wymóg autoryzacji/e-mail).

##1.4.2 Wymagania niefunkcjonalne (NFR)

NFR1.1, Szyfrowanie End-to-End, Hasła muszą być szyfrowane hasłem głównym użytkownika przy użyciu kombinacji PBKDF2-HMAC-SHA256 (200,000 iteracji)
i Fernet (AES-128-CBC).
NFR1.2, Haszowanie Hasła, Hasło Użytkownika (Master Password) musi być haszowane
przy użyciu algorytmu Argon2.
NFR1.3, Mechanizm Autoryzacji, Użycie Tokenów JWT (wsparcie dla HS256/ES512)
z krótkim czasem życia dla Access Tokena (15 minut) i dłuższym dla Refresh Tokena (14
dni).
NFR1.4, Zapobieganie Replay Attack, Wpisy odświeżających tokenów (Refresh Token)
w bazie danych muszą być unieważniane po użyciu (Single Use Token), aby zapobiec ich
ponownemu wykorzystaniu.
NFR1.5, Zapis Dostępu, Każda operacja odszyfrowania, kopiowania, aktualizacji, udostępniania i usuwania hasła musi być rejestrowana w logach dostępu (IP, User Agent,
akcja).
NFR1.6, Walidacja Haseł, Wymaganie silnych haseł w procesach rejestracji i zmiany hasła (min. 8 znaków, wielka/mała litera, cyfra, znak specjalny).
NFR2.1, Baza Danych,System musi być zbudowany na skalowalnej bazie danych PostgreSQL.
NFR2.2, Optymalizacja Zapytań, Warstwa API musi optymalizować zapytania do bazy
danych, minimalizując operacje I/O i wykorzystując indeksy (np. dla folderów, tagów
i dat wygaśnięcia).
NFR2.3, Szybkość Decyzyjna, Zapytania do API (np. lista haseł, statystyki) powinny
zwracać wyniki w czasie krótszym niż 1 sekunda.
NFR3.1, Responsywność, Interfejs użytkownika (GUI) musi być w pełni responsywny
i działać poprawnie na różnych urządzeniach.
NFR3.2, Walidacja, Wszystkie formularze (rejestracja, logowanie, hasła) muszą posiadać
walidację po stronie klienta (natychmiastowa informacja zwrotna) i walidację po stronie
serwera.
NFR3.3, Komunikacja, Powiadomienia o błędach i sukcesach muszą być wyświetlane
w interfejsie użytkownika z opcją automatycznego zamykania (Alerts).
NFR3.4, Wymagania Techniczne, Klient (GUI) musi być nowoczesną aplikacją SPA.
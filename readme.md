# to do

- dodać aby worker sprawdzał blacklist (w celu odblokowania adresu) i whitelist (w celu)
- Wyświetlanie aktualnie zablokowanych adresów z godz ich odblokowania (czyli kiedy zostaną odblokowane)
- Zbieranie statystyk
- Wyświetlanie statystyk
- Wypisanie komendy do wklejenia dla operatora
- Konteneryzacja
- Obsługa streamu logów
- Dane do statystyk
  - ilość ataków od godziny (wykres)
  - ilość zablokowanych adresów
  - najcześciej atakujący adres
  - najczeście zablokowany ades
  - najczęsciej atakujący kraj
  - najczęsciej atakowany adres
- Przetwarzanie streamu udp i zapis danych do bazy
- Analizowanie danych w bazie i dodawanie adresów do listy do zbanowania
- przemyślenie struktury bazy danych

# Done
- Config file - to do przemyślenia
- testy czasu dostępu dla pobrania wartości z configu a z classy
- - zrobić setting 
  - Ilość prób nieudanych logowań w celu zablokowania
  - Czy blokować adresy permamentnie 
  - Długość 1, 2, 3 blokady, (4 permamentna)
  - Jaki ma być czas aby zresetować pamięć ostatnich prób nieudanych logowań
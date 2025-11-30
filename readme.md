# to do

- sprawdzić od ilu nieudanych prób generowany jest log oraz czy nie dodawać tej liczby
- weryfikacja w statystykach czy zakres od jest mniejszy niz do
- ogarnać zapisywanie danych dla konteneru po zatrzymaniu, może obraz ubuntu?]
- zweryfikować endpointy


# Done
- Wypisanie komendy do wklejenia dla operatora
- Konteneryzacja
- poprawić opisy
- generowanie reguł
- Config file - to do przemyślenia
- testy czasu dostępu dla pobrania wartości z configu a z classy
- zrobić setting 
- Ilość prób nieudanych logowań w celu zablokowania
- Czy blokować adresy permamentnie 
- Długość 1, 2, 3 blokady, (4 permamentna)
- Jaki ma być czas aby zresetować pamięć ostatnich prób nieudanych logowań
- Obsługa streamu logów
- Przetwarzanie streamu udp i zapis danych do bazy
- przemyślenie struktury bazy danych
- dodać aby serwer udp resetował się po zmianie adresu/portu i dodać komuniakt na stronie w help ze to spowoduje reset
- dodać aby worker sprawdzał blacklist (w celu odblokowania adresu) i whitelist (w celu)
- Analizowanie danych w bazie i dodawanie adresów do listy do zbanowania
- sprawdzanie czy coś jest w settings jeśli nie to cos trzeba wymyśleć
- dodać ustawienia dla kata
- weryfikacje kto wysyła log, chyba tylko po ip się da ale zawsze jakaś ochrona
- Zbieranie statystyk
- Wyświetlanie aktualnie zablokowanych adresów z godz ich odblokowania (czyli kiedy zostaną odblokowane)
- Wyświetlanie statystyk

# Tworzenie obrazu
```shell
sudo docker build -f Dockerfile -t firebot .  
```
# Uruchomienie 
```shell
sudo docker run --user root -p 514:514/udp -p 8000:8000 firebot
```

# Uruchomienie w tle
```shell
sudo docker run -d --user root -p 514:514/udp -p 8000:8000 firebot
```


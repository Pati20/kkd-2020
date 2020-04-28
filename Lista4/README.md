# Lista 4. Kodowanie i kompresja danych 2020
## Laboratorium nr 7. i 8. (na zaliczenie)

Napisać program, który dla nieskompresowanych obrazów zapisanych w formacie TGA policzy wyniki kodowania za pomocą różnicy między predyktorami JPEG-LS (7 starych standardów i nowy standard, jako kolor otoczenia obrazka przyjmujemy czarny - RGB(0,0,0)) i poda entropię dla kodu całego obrazka jak i poszczególnych składowych koloru. Dla porównania program powinien drukować także entropię wejściowego obrazu i entropię poszczególnych składowych koloru. Na końcu program powinien podać, która metoda jest optymalna (daje najmniejszą entropię) dla danego obrazu jako całości oraz optymalne metody dla poszczególnych składowych koloru.

Entropia w każdym przypadku liczona jest bez udziału bitów z footera i headera.
## Dostarczone pliki
Podstawowym dostarczonym plikiem jest:
- <b>lab4.py</b> - wykonuje wszystkie wymienione w poleceniu zadania

### Kompilacja i uruchamianie
W celu prawidłowego uruchomienia programu wpisz w konsoli `python lab4.py <plik_wejsciowy>`.
Pliki testowe powinny znajdować się w tym samym katalogu. 

### Author
Patrycja Paradowska, 244952

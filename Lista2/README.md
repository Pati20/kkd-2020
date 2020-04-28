# Lista 2 Kodowanie i kompresja danych 2020
## Laboratorium nr 3 i 4 (na ocenę)

Napisać program kodujący i program dekodujący dany plik wejściowy do pliku wyjściowego. Program kodujący powinien dodatkowo na koniec zwrócić na ekeran odpowiednią entropię kodowanych danych, średnią długość kodowania i stopień kompresji. Alfabetem wejściowym są 8-bitowe kody ASCII. Programy kodujący i dekodujący zostały napisane w języku `Python`.

## Wersja na ocenę 5.0
Programy mają używać adaptacyjnego kodowania arytmetycznego ze skalowaniem.
Podstawowymi dostarczonymi plikami są:

- <b>lab2_kodowanie.py</b> - koduje wczytywany plik i zwraca określone informacje
- <b>lab2_dekodowanie.py</b> - program dekodujący dany plik

### Kompilacja i uruchamianie
Najpierw celu prawidłowego uruchomienia programu wpisz w konsoli `python lab2_kodowanie.py <plik_wejsciowwy> <plik_wynikowy>`.
Pliki testowe powinny znajdować się w tym samym katalogu. 
Zostaną wydrukowane podstawowe informacje oraz utworzy się plik wynikowy o danej nazwie.

Następnie w celu zdekodowania pliku wpisujemy w konsoli wpisz w konsoli `python lab2_dekodowanie.py <plik_wejsciowwy> <plik_wynikowy>`.
W pliku_wynikowym zostanie zapisany odkodowany plik, który oczywiście po kompresji i dekompresji będzie zawierał dokładnie to samo, co plik źródłowy - kompresja będzie zatem bezstratna.
### Author
Patrycja Paradowska, 244952
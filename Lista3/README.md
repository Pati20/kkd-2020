# Lista 3 Kodowanie i kompresja danych 2020
## Laboratorium nr 5 i 6 (na ocenę)

Napisz program kodujący i dekodujący dany plik za pomocą algorytmu LZW. Ciąg
wartości indeksów słownika ma być zakodowany kodowaniem uniwersalnym. Alfabetem wejściowym są 8-bitowe kody. Domyślnie program powinien używać kodowania
Eliasa ω oraz mieć możliwość opcjonalnego użycia pozostałych kodowań Eliasa oraz
kodowania Fibonacciego.
Program dodatkowo podczas kodowania ma podawać długość kodowanego pliku, długość uzyskanego kodu, stopień kompresji, entropię kodowanego tekstu i entropię uzyskanego kodu.
## Wersja na ocenę 5.0
Podstawowymi dostarczonymi plikami są:
- <b>lab3_kodowanie.py</b> - koduje wczytywany plik i zwraca określone informacje
- <b>lab3_dekodowanie.py</b> - program dekodujący dany plik

### Kompilacja i uruchamianie
Najpierw celu prawidłowego uruchomienia programu wpisz w konsoli `python3 lab3_kodowanie.py <plik_wejsciowwy> <plik_wynikowy> [-opcja]`.
Jako -opcja możemy się posłużyć:
- <b>-gamma</b>
- <b>-delta</b>
- <b>-omega</b>
- <b>-fibb</b>

Przykładowo `python3 lab3_kodowanie.py test2.bin wynik.out -gamma`.
 
Pliki testowe powinny znajdować się w tym samym katalogu. 
Zostaną wydrukowane podstawowe informacje oraz utworzy się plik wynikowy o danej nazwie.

Następnie w celu zdekodowania pliku wpisz w konsoli `python3 lab3_dekodowanie.py <plik_wejsciowwy> <plik_wynikowy> [-opcja]` analogicznie do kodowania.
W pliku_wynikowym zostanie zapisany odkodowany plik, który oczywiście po kompresji i dekompresji będzie zawierał dokładnie to samo, co plik źródłowy - kompresja będzie zatem bezstratna.
W razie problemów, wymagane jest zainstalowanie pakietu python-bitarray:
sudo apt-get install -y python-bitarray .
### Author
Patrycja Paradowska, 244952
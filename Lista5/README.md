# Lista 5. Kodowanie i kompresja danych 2020
## Laboratorium nr 9 i 10 (na ocenę)

Napisz program który dla nieskompresowanego obrazu zapisanego w formacie
TGA policzy obraz uzyskany w wyniku kwantyzacji wektorowej kolorów. Program
powinien dodatkowo wypisać błąd średniokwadratowy dla całego obrazu oraz stosunek
sygnału do szumu. Do uzyskania wymaganej liczby kolorów należy użyć algorytmu
Linndego-Buza-Graya (dla uproszczenia implementacji do mierzenia odległości między
kolorami można użyć metryki taksówkowej).
Program powinien czytać trzy argumenty w linii poleceń: obraz wejściowy, obraz wyjściowy, liczba kolorów (między 0 a 24, liczba kolorów to dwójkowa potęga podanej
liczby). (Program nie musi w obrazku wyjściowym kodować mapy kolorów, może
wstawić wybrane kolory bezpośrednio do obrazka.)

## Wersja na ocenę 5.0
Podstawowym dostarczonym plikiem jest:
- <b>lista5.py</b> 

### Kompilacja i uruchamianie
W celu prawidłowego uruchomienia programu wpisz w konsoli `python lista5.py <obraz_wejsciowy> <obraz_wyjsciowy> <liczba_kolorow>`

### Author
Patrycja Paradowska, 244952

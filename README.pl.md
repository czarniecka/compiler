# Kompilator języka imperatywnego

## Autor

Aleksandra Czarniecka 272385

## Opis projektu

Projekt został wykonany w ramach laboratorium kursu Języki Formalne i Techniki Translacji na PWr w semestrze zimowym 2024/2025.

Ten projekt to kompilator prostego języka imperatywnego, który tłumaczy kod źródłowy na kod dla maszyny wirtualnej. Kompilator obsługuje zmienne, tablice, procedury oraz podstawowe działania arytmetyczne i instrukcje sterujące, takie jak pętle czy warunki.

## Struktura projektu

Projekt składa się z następujących plików:

- `lexer.py` – analizator leksykalny, który dzieli kod źródłowy na tokeny.
- `parser.py` – analizator składniowy, który buduje na bazie tokenów tworzy proste syntax tree reprezentowane przez zagnieżdżone krotki.
- `symbol_table.py` – obsługuje tablicę symboli, przechowującą informacje o zmiennych, iteratorach, tablicach i procedurach.
- `code_generator.py` – moduł generujący kod wynikowy dla maszyny wirtualnej na podstawie drzewa skonstruowanego przez parser.
- `compiler.py` – główny plik uruchamiający cały proces kompilacji.

## Katalogi i pliki dodatkowe
Wszystkie poniższe katalogi i pliki zostały przygotowane przez prowadzącego kursu (dr Maciej Gębala).

- katalog `tests`- przykładowe programy pozwalające na sprawdzenie poprawności generowanego kodu.
- katalog `programs`- dodatkowe pomocnicze skrypty.
- katalog `virtual_machine` - kod maszyny wirtualnej.
- `gramatyka.txt` - gramatyka języka imperatywnego.
- `labor4.pdf` - specyfikacja projektu.

## Instalacja i uruchomienie

### Wymagania

- Python 3.10 (`sudo apt install python3.10`)
- Biblioteka `sly` do analizy składniowej (`pip install sly`)

### Kompilacja

Aby skompilować program, należy uruchomić kompilator z terminala:

```sh
python3 compiler.py <plik_wejsciowy> <plik_wyjsciowy>
```

gdzie:
- `<plik_wejsciowy>` – nazwa pliku zawierającego kod źródłowy w języku imperatywnym,
- `<plik_wyjsciowy>` – nazwa pliku, w którym zostanie zapisany wynikowy kod dla maszyny wirtualnej.

## Uwagi

W pliku `example6.imp` należy usunąć z deklaracji programu zmienną 'j' ze względu na jej overloading (w programie jest użyta jako iterator).
W pliku `example8.imp` w linii 25 należy zamienić nazwę tablicy 'tab' na poprawną nazwę, czyli 't'.
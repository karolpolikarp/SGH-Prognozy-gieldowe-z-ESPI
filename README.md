# Prognozy giełdowe na podstawie raportów ESPI

Projekt realizowany w ramach zajęć na SGH. Celem jest zbadanie, czy model językowy (GPT) jest w stanie przewidywać krótkoterminowe zmiany kursu akcji Allegro na podstawie komunikatów ESPI (Elektroniczny System Przekazywania Informacji). 

## Struktura projektu

| Plik | Opis |
|------|------|
| `main.py` | Scraper raportów ESPI ze strony espiebi.pap.pl |
| `predykcje_sgh.ipynb` | Notebook z analizą i prognozowaniem |
| `allegro_reports.csv` | Zescrapowane raporty ESPI Allegro (~1500 raportów) |
| `ale_d.csv` | Dzienne dane cenowe akcji Allegro (OHLCV, od 2020-10) |
| `objaśnienie kodu prognozowania.pdf` | Dokumentacja kodu |

## Jak to działa

### 1. Scraping raportów (`main.py`)

Skrypt pobiera komunikaty ESPI dotyczące Allegro z serwisu PAP (espiebi.pap.pl) i zapisuje je do pliku CSV z polami: data, tytuł, treść, typ raportu, URL.

### 2. Analiza i prognozowanie (`predykcje_sgh.ipynb`)

Notebook realizuje pełny pipeline analizy:

- **Załadowanie danych** — dane cenowe (OHLCV) i raporty ESPI
- **Statystyki historyczne** — analiza 100 ostatnich sesji przed raportem (średnie wzrosty/spadki, zmienność, % dni wzrostowych)
- **Wskaźniki techniczne** — średnie kroczące (SMA 5/10/20/50/100), zmienność 100-dniowa
- **Prognoza GPT** — na podstawie treści raportu, danych historycznych i wskaźników technicznych model GPT-4o-mini generuje prognozy zmian kursu w horyzontach D0, D3, D7, D14, D30
- **Porównanie z rzeczywistością** — tabela zestawiająca prognozowane i faktyczne zmiany procentowe
- **Wizualizacja** — wykresy kursów z SMA, zmiennością oraz interpolowaną linią predykcji GPT

## Wymagania

```
pip install requests beautifulsoup4 pandas matplotlib scipy numpy openai
```

Wymagany klucz API OpenAI (ustawiony w notebooku).

## Uruchomienie

1. **Scraping raportów** (opcjonalnie — dane już zawarte w repozytorium):
   ```bash
   python main.py
   ```

2. **Analiza i prognozowanie**:
   - Otwórz `predykcje_sgh.ipynb` w Jupyter Notebook
   - Ustaw klucz API OpenAI
   - Uruchom komórki notebooka

## Dane

- **Raporty ESPI**: komunikaty giełdowe Allegro z systemu PAP (2020–2024)
- **Dane cenowe**: dzienne notowania Allegro (otwarcie, najwyższy, najniższy, zamknięcie, wolumen)

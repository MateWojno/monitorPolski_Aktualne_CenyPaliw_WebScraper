# MonitorPolskiWebScraper

Automatyczny skrypt monitorujący i pobierający oficjalne obwieszczenia Ministra Energii dotyczące maksymalnych cen paliw bezpośrednio z dziennika urzędowego **Monitor Polski** (`monitorpolski.gov.pl`).

* **Wersja:** 1.0.8
* **Autor:** matewojno
* **Przeznaczenie:** Automatyzacja procesów biznesowych / Pobieranie danych rynkowych



##  Kluczowe funkcjonalności

1. **Inteligentne wyszukiwanie:** Przeszukuje stronę główną oraz dynamiczny zakres numerów wokół ostatnio zapisanej pozycji (`ostatni.txt`), priorytetyzując najnowsze akty prawne.
2. **Weryfikacja daty (Fail-safe):** Skrypt rygorystycznie sprawdza, czy publikacja posiada dzisiejszą datę systemową w polskim formacie (np. *13 listopada 2026 r.*) zarówno w treści strony, jak i w pobranym pliku PDF.
3. **Ochrona biznesowa ("Ochrona Firmy"):** W przypadku braku aktualnego obwieszczenia lub błędu sieciowego skrypt natychmiast przerywa działanie, uniemożliwiając użycie przestarzałych lub niezweryfikowanych cen.
4. **Automatyczne parsowanie PDF:** Wykorzystuje bibliotekę `pypdf` do ekstrakcji tekstu z oficjalnych dokumentów PDF i za pomocą wyrażeń regularnych (`regex`) wyciąga stawki brutto dla:
   * Benzyny bezołowiowej 95 (`Pb95`)
   * Benzyny bezołowiowej 98 (`Pb98`)
   * Oleju napędowego (`ON`)
5. **Eksport danych:** Automatycznie zapisuje pobrane stawki do gotowych plików:
   * `cenyMaks.csv` (rozdzielany średnikami, gotowy do systemów ERP / Excel)
   * `cenyMaks.json` (struktura z datą aktualizacji i słownikiem cen)
6. **Optymalizacja zakresu:** Aktualizuje plik `ostatni.txt` w celu szybszego odnajdywania kolejnych obwieszczeń w przyszłych uruchomieniach.



## Wymagania wstępne

Skrypt napisany jest w języku Python. Do poprawnego działania wymagane są następujące biblioteki zewnętrzne:

```bash
pip install -r requirements.txt
```
<br>Uruchom program:
```bash
python mpws.py
```

## Informacja o użyciu AI
Dokumentacja jest pisana przy uzyciu modelu Ai na podstawie mojego `kodu`, `notatek @todo` oraz `komentarzy`, przy minimalnym wkładzie własnym.

## Ostrzeżenie
<u>Używasz na własną odpowiedzialność.</u><br>Autor nie ponosi żadnej odpowiedzialności za ewentualne szkody spowodowane wykorzystaniem tego narzędzia.
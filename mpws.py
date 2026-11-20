# MonitorPolskiWebScraper
# @version  :   1.0.8
# @author   :   matewojno
# @purpouse :   homemade automation script
# @todo     :   
#           1.  split functions to other files
from datetime import datetime
from io import BytesIO
import json
import csv
import os
import re
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

PLIK_OSTATNI = "ostatni.txt"


def generuj_datę_systemową():
    miesiace = {
        1: "stycznia",
        2: "lutego",
        3: "marca",
        4: "kwietnia",
        5: "maja",
        6: "czerwca",
        7: "lipca",
        8: "sierpnia",
        9: "września",
        10: "października",
        11: "listopada",
        12: "grudnia",
    }
    now = datetime.now()
    data_akt = f"{now.day} {miesiace[now.month]} {now.year} r."
    print(f"Dzisiejsza data: {data_akt}")
    return data_akt


def wczytaj_ostatni_numer(domyslny=23):
    if os.path.exists(PLIK_OSTATNI):
        try:
            with open(PLIK_OSTATNI, "r", encoding="utf-8") as f:
                zawartosc = f.read().strip()
                if zawartosc.isdigit():
                    nr = int(zawartosc)
                    print(f"[*] Wczytano ostatni numer z pliku {PLIK_OSTATNI}: {nr}")
                    return nr
        except Exception as e:
            print(f"[!] Błąd odczytu pliku {PLIK_OSTATNI}: {e}")
    print(f"[*] Brak poprawnego pliku {PLIK_OSTATNI}, używam domyślnego numeru: {domyslny}")
    return domyslny


def zapisz_ostatni_numer(numer):
    try:
        with open(PLIK_OSTATNI, "w", encoding="utf-8") as f:
            f.write(str(numer))
        print(f"[+] Zapisano nowy numer {numer} do pliku {PLIK_OSTATNI}")
    except Exception as e:
        print(f"[!] Błąd zapisu pliku {PLIK_OSTATNI}: {e}")


def parsuj_ceny_z_tekstu(tekst):
    ceny = {}

    def na_float(t):
        return float(t.replace(",", "."))

    # Normalizacja tekstu PDF (usuwa nadmiarowe entery i spacje)
    tekst_czysty = re.sub(r"\s+", " ", tekst)


# 1. Parsowanie Pb95
    pb95_brutto = re.search(
        r"bezołowiowej\s+95.*?(?:brutto|usług)\s+wynosi\s*([\d,]+)\s*zł", tekst_czysty, re.IGNORECASE
    )
    
    # 2. Parsowanie Pb98
    pb98_brutto = re.search(
        r"bezołowiowej\s+98.*?(?:brutto|usług)\s+wynosi\s*([\d,]+)\s*zł", tekst_czysty, re.IGNORECASE
    )
    
    # 3. Parsowanie Oleju Napędowego (uwzględnia kody CN w nawiasie oraz skrót ON)
    on_brutto = re.search(
        r"(?:oleju\s+napędowego|olej\s+napędowy|\bON\b).*?(?:brutto|usług)\s+wynosi\s*([\d,]+)\s*zł", tekst_czysty, re.IGNORECASE
    )
   
    
    if pb95_brutto:
        ceny["Pb95"] = {"brutto": na_float(pb95_brutto.group(1))}
    if pb98_brutto:
        ceny["Pb98"] = {"brutto": na_float(pb98_brutto.group(1))}
    if on_brutto:
        ceny["ON"] = {"brutto": na_float(on_brutto.group(1))}

    return ceny


def zapisz_do_csv(ceny, data_publikacji):
    nazwa_pliku = "cenyMaks.csv"
    try:
        with open(nazwa_pliku, mode="w", newline="", encoding="utf-8") as plik:
            writer = csv.writer(plik, delimiter=";")
            writer.writerow(["Paliwo", "Brutto", "DataAktualizacji"])
            for paliwo, stawki in ceny.items():
                writer.writerow([paliwo, stawki["brutto"], data_publikacji])
        print(f"[+] Zapisano dane do pliku CSV: {nazwa_pliku}")
    except Exception as e:
        print(f"[!] Błąd zapisu CSV: {e}")


def zapisz_do_json(ceny, data_publikacji):
    nazwa_pliku = "cenyMaks.json"
    dane_kompletne = {
        "data_aktualizacji": data_publikacji,
        "ceny": ceny
    }
    try:
        with open(nazwa_pliku, mode="w", encoding="utf-8") as plik:
            json.dump(dane_kompletne, plik, ensure_ascii=False, indent=4)
        print(f"[+] Zapisano dane do pliku JSON: {nazwa_pliku}")
    except Exception as e:
        print(f"[!] Błąd zapisu JSON: {e}")


def pobierz_i_parsuj_monitor():
    dzisiejsza_data = generuj_datę_systemową()
    ostatni_nr = wczytaj_ostatni_numer(domyslny=23)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
            " like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    # Budowanie dynamicznej listy URL-i:
    # 1. Strona główna Monitora Polskiego na pierwszym miejscu
    # 2. Zakres wokół ostatniego numeru z pliku (np. ostatni + 2)
    numery_do_sprawdzenia = [ostatni_nr]
    for offset in range(1, 3):
        numery_do_sprawdzenia.append(ostatni_nr + offset)

    # Usuwamy duplikaty, zachowując priorytet najnowszych (najwyższych numerów)
    numery_do_sprawdzenia = sorted(list(set([n for n in numery_do_sprawdzenia if n > 0])), reverse=True)

    glowna_url_list = ["https://monitorpolski.gov.pl/MP"]
    for nr in numery_do_sprawdzenia:
        glowna_url_list.append(f"https://monitorpolski.gov.pl/MP/rok/2026/{nr}")

    print(f"[*] Lista adresów do sprawdzenia: {glowna_url_list}")

    doc_url = None
    znaleziony_url = None

    for glowna_url in glowna_url_list:
        print(f"[*] Próbuję pobrać stronę: {glowna_url}")
        try:
            response = requests.get(glowna_url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"[-] Strona zwróciła kod statusu: {response.status_code}, pomijam.")
                continue
        except Exception as e:
            print(f"[-] Błąd sieciowy dla {glowna_url}: {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # Jeśli sprawdzamy stronę główną lub pojedynczy akt:
        # Szukamy odnośników do aktów w Monitorze Polskim 2026
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/MP/2026/" in href and len(href.split("/")) == 4:
                pełny_url = (
                    f"https://monitorpolski.gov.pl{href}"
                    if href.startswith("/")
                    else href
                )
                
                try:
                    akt_resp = requests.get(pełny_url, headers=headers, timeout=5)
                    if akt_resp.status_code == 200:
                        akt_soup = BeautifulSoup(akt_resp.text, "html.parser")
                        tekst_aktu = akt_soup.get_text()

                        if "Ministra Energii" in tekst_aktu and "maksymalnej ceny paliw" in tekst_aktu:
                            print(f"[i] Znaleziono akt w treści: {pełny_url}")
                            if dzisiejsza_data in tekst_aktu:
                                doc_url = pełny_url
                                znaleziony_url = pełny_url
                                print(f"[+] Sukces! Dokument posiada dzisiejszą datę: {dzisiejsza_data}")
                                print(f"[+] Ostatni url to {znaleziony_url}")
                                break
                            else:
                                print(f"[-] Pomijam starszy dokument pod adresem {pełny_url}")
                except Exception:
                    continue

        if doc_url:
            break

    if not doc_url:
        print(f"\n[!] BŁĄD KRYTYCZNY: Brak oficjalnego obwieszczenia z dnia {dzisiejsza_data} w przeszukanych źródłach!")
        print("[!] OCHRONA FIRMY: Skrypt przerywa działanie. Żadne stare ceny nie zostaną użyte.")
        return

    # Pobieranie pliku PDF ze zweryfikowanego linku
    doc_response = requests.get(doc_url, headers=headers)
    doc_soup = BeautifulSoup(doc_response.text, "html.parser")

    pdf_url = None
    for a in doc_soup.find_all("a", href=True):
        if ".pdf" in a["href"].lower():
            href = a["href"]
            pdf_url = (
                f"https://monitorpolski.gov.pl{href}" if href.startswith("/") else href
            )
            break

    if not pdf_url:
        print("[!] BŁĄD KRYTYCZNY: Nie znaleziono pliku PDF dla dzisiejszego aktu.")
        return

    print(f"[+] Pobieranie pliku PDF: {pdf_url}")
    pdf_response = requests.get(pdf_url, headers=headers)
    if pdf_response.status_code != 200:
        print(f"[!] Błąd pobierania PDF. Kod: {pdf_response.status_code}")
        return

    pdf_file = BytesIO(pdf_response.content)
    reader = PdfReader(pdf_file)
    tekst_pdf = ""
    for page in reader.pages:
        tekst_pdf += page.extract_text() + "\n"

    if dzisiejsza_data not in tekst_pdf:
        print("[!] BŁĄD KRYTYCZNY: Treść pobranego pliku PDF nie zgadza się z dzisiejszą datą! Przerywam.")
        return

    ceny = parsuj_ceny_z_tekstu(tekst_pdf)

    print(f"\n--- SUKCES: POBRANO AKTUALNE CENY NA DZISIAJ ({dzisiejsza_data}) ---")
    if ceny:
        for paliwo, stawki in ceny.items():
            print(f" \t{paliwo}: \tBrutto = {stawki['brutto']} \tzł")
        
        # Zapis do plików wymaganych w zadaniu
        zapisz_do_csv(ceny, dzisiejsza_data)
        zapisz_do_json(ceny, dzisiejsza_data)

        # Wyciągnięcie numeru `i` z URL-a (np. z https://monitorpolski.gov.pl/MP/rok/2026/24) i zapis do ostatni.txt
        match_nr = re.search(r'/2026/(\d+)', znaleziony_url)
        if match_nr:
            nowy_nr = int(match_nr.group(1))//50
            nowy_nr = nowy_nr + 1   #
            
            print(f" [+] Zapisano nowy numer {nowy_nr} \tdo pliku {PLIK_OSTATNI}")
            zapisz_ostatni_numer(nowy_nr)
    else:
        print("[!] BŁĄD KRYTYCZNY: Nie udało się sparsować cen z pliku PDF.")


if __name__ == "__main__":
    pobierz_i_parsuj_monitor()
# MonitorPolskiWebScraper

An automated web scraping script designed to monitor and retrieve official announcements from the Polish Minister of Energy regarding maximum fuel prices directly from the official journal **Monitor Polski** (`monitorpolski.gov.pl`).

* **Version:** 1.0.8
* **Author:** matewojno
* **Purpose:** Business process automation / Market data retrieval

## Key Features

1. **Smart Search Mechanism:** Scans the main page and a dynamic range of document numbers around the last saved index (`ostatni.txt`), prioritizing the newest acts.
2. **Strict Date Verification (Fail-safe):** Rigorously checks whether the publication matches today's system date in the Polish format (e.g., *13 listopada 2026 r.*) both within the HTML body and the downloaded PDF text.
3. **Business Protection ("Company Shield"):** If today's official announcement is missing or a network error occurs, the script immediately aborts execution, preventing the fallback to outdated or unverified prices.
4. **Automated PDF Parsing:** Leverages `pypdf` to extract text from official PDF documents and uses regular expressions (`regex`) to accurately capture gross price rates for:
   * Unleaded 95 Gasoline (`Pb95`)
   * Unleaded 98 Gasoline (`Pb98`)
   * Diesel Fuel (`ON`)
5. **Data Export:** Automatically saves retrieved rates into standard output formats:
   * `cenyMaks.csv` (semicolon-delimited, ERP/Excel-ready)
   * `cenyMaks.json` (structured dictionary containing the update date and price data)
6. **Range Optimization:** Automatically updates the `ostatni.txt` tracking index for faster lookups during subsequent runs.



## Prerequisites

Written in Python, the script requires the following external libraries:

```bash
pip install -r requirements.txt
```
<br>

Run program:
```bash
python mpws.py
```

## AI notice
Documentation is written by AI based on my `code changes`, `@todo notes` and `commments`, with minimal to zero manual work.

## Warning
<u>You use it at your own risk.</u> <br>
The author assumes no liability for any damages resulting from the use of this tool.
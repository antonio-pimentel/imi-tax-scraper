from bs4 import BeautifulSoup
import requests
import csv
import argparse
import time
from colorama import init, Fore, Style
init(autoreset=True)

districts = [
    "01AVEIRO", "02BEJA", "03BRAGA", "04BRAGANCA", "05CASTELOBRANCO", "06COIMBRA",
    "07EVORA", "08FARO", "09GUARDA", "10LEIRIA", "11LISBOA", "12PORTALEGRE",
    "13PORTO", "14SANTAREM", "15SETUBAL", "16VIANA", "17VILAREAL", "18VISEU",
    "19ANGRA+DO+HEROISMO", "20HORTA", "21PONTA+DELGADA", "22FUNCHAL"
]

years = list(range(2025, 1988, -1))

default_output_file = "imi_tax_data.csv"

def fetch_imi_data(year, distrito_code):
    url = f"https://www.portaldasfinancas.gov.pt/pt/main.jsp?body=%2Fimi%2FconsultarTaxasIMI.jsp&ano={year}&distrito={distrito_code}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    response.encoding = 'iso-8859-1'

    soup = BeautifulSoup(response.text, 'html.parser')
    main_table = soup.find('table', class_='eT')

    if not main_table:
        return []

    try:
        data_table = main_table.find_all('tr')[1].find('table')
        rows = data_table.find_all('tr')[1:]
    except Exception:
        return []

    data = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 6:
            data.append({
                'Ano': year,
                'Distrito': distrito_code[2:].replace('+', ' '),
                'Código Município': cols[0].text.strip(),
                'Município': cols[1].text.strip(),
                'Prédios Urbanos': cols[2].text.strip(),
                'Prédios Rústicos': cols[3].text.strip(),
                'Taxas por Freguesia': cols[4].text.strip(),
                'Dedução Fixa': cols[5].text.strip(),
            })
    return data

def main():
    parser = argparse.ArgumentParser(
        description="Scrape IMI municipal tax data from Portal das Finanças."
    )
    parser.add_argument(
        "--output", "-o",
        default=default_output_file,
        help=f"Output CSV file name (default: {default_output_file})"
    )
    parser.add_argument(
        "--silent", "-s",
        action="store_true",
        help="Suppress fetch logs (only show errors and summary)"
    )
    args = parser.parse_args()

    output_file = args.output
    silent = args.silent

    total_rows = 0
    total_success = 0
    total_empty = 0
    total_errors = 0

    # Scrape and write to CSV
    with open(output_file, mode='w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['Ano', 'Distrito', 'Código Município', 'Município', 'Prédios Urbanos', 'Prédios Rústicos', 'Taxas por Freguesia', 'Dedução Fixa']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for year in years:
            for distrito in districts:
                if not silent:
                    print(f"Fetching {distrito} {year}...", end=" ")
                try:
                    records = fetch_imi_data(year, distrito)
                    if records:
                        for record in records:
                            writer.writerow(record)
                        total_rows += len(records)
                        total_success += 1
                        if not silent:
                            print(f"✅ {Fore.GREEN}[OK]{Style.RESET_ALL} {len(records)} rows")
                    else:
                        total_empty += 1
                        if not silent:
                            print(f"⚠️ {Fore.YELLOW}[No Data]{Style.RESET_ALL}")
                except Exception as e:
                    total_errors += 1
                    if not silent:
                        print(f"❌ {Fore.RED}[ERROR]{Style.RESET_ALL} {e}")
                    else:
                        print(f"❌ {Fore.RED}[ERROR]{Style.RESET_ALL} {distrito} {year}: {e}")

                time.sleep(0.5) # polite delay between requests

    print("\nDone!")
    print("\nSummary")
    print("="*40)
    print(f"{Fore.GREEN}Successful fetches:{Style.RESET_ALL} {total_success}")
    print(f"{Fore.YELLOW}Empty results:     {Style.RESET_ALL} {total_empty}")
    print(f"{Fore.RED}Errors:            {Style.RESET_ALL} {total_errors}")
    print(f"Total rows written: {total_rows}")
    print(f"\nData saved to {output_file}")


if __name__ == "__main__":
    main()

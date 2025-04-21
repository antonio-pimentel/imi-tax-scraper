# imi-tax-scraper

![Python](https://img.shields.io/badge/Python-3.7+-blue)

Script to scrape [IMI data from Portal das Finanças](https://www.portaldasfinancas.gov.pt/pt/main.jsp?body=/imi/consultarTaxasIMIForm.jsp)

## Usage

```bash
pip install -r requirements.txt
python scrape.py
```

## Options

- --output / -o : Output CSV filename (default: imi_tax_data.csv)

- --silent / -s : Hide fetch logs (only shows errors and summary)

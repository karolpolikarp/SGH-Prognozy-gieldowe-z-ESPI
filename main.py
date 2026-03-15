import requests
from bs4 import BeautifulSoup
import csv
from random import choice
import re
from datetime import datetime

BASE_URL = "https://espiebi.pap.pl/wyszukiwarka?search=allegro"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]


def fetch_url(url):
    headers = {"User-Agent": choice(USER_AGENTS)}
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Failed to fetch URL {url}: {e}")
        return None


def parse_espi_report(html_content, url):
    soup = BeautifulSoup(html_content, 'html.parser')

    report_data = {
        'data': '',
        'symbol_spolki': 'ALLEGRO',
        'tytul': '',
        'tresc': '',
        'typ_raportu': '',
        'numer_raportu': '',
        'url': url  # Dodaj URL
    }

    # Find title - first check in the nDokument table
    doc_table = soup.find('table', {'class': 'nDokument'})
    if doc_table:
        rows = doc_table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                key = cells[0].text.strip()
                value = cells[1].text.strip()

                if key == 'Data sporządzenia':
                    report_data['data'] = value
                elif key == 'Tytuł':
                    if value:
                        report_data['tytul'] = value

    if not report_data['tytul']:
        title = soup.find('h1', {'class': 'mainTitle'})
        if title and title.find('span', {'class': 'field--name-title'}):
            report_data['tytul'] = title.find('span', {'class': 'field--name-title'}).text.strip()

    report_type_div = soup.find('div', {'class': 'field--name-field-report-type'})
    if report_type_div:
        type_item = report_type_div.find('div', {'class': 'field__item'})
        if type_item:
            report_data['typ_raportu'] = type_item.text.strip()

    content = ""
    content_div = soup.find('div', {'class': 'field-body-xml-content'})
    if content_div:
        for section in content_div.find_all('div', {'class': 'arkusz'}):
            rows = section.find_all('tr')
            found_tresc = False
            for row in rows:
                cells = row.find_all('td')
                for cell in cells:
                    if 'Treść raportu:' in cell.text:
                        found_tresc = True
                    elif found_tresc:
                        content = cell.text.strip()
                        if content:
                            break
                if content:
                    break
            if content:
                break

    if content:
        report_data['tresc'] = content

    return report_data


def scrape_reports(max_pages=6):
    all_reports = []
    seen_urls = set()

    for page in range(max_pages):
        current_url = f"{BASE_URL}&page={page}" if page > 0 else BASE_URL

        print(f"\nFetching page {page + 1}: {current_url}")
        html_content = fetch_url(current_url)
        if not html_content:
            break

        soup = BeautifulSoup(html_content, 'html.parser')

        links = []
        for a in soup.find_all('a', href=True):
            if a['href'].startswith("/node/") and "ALLEGRO" in a.text:
                full_url = f"https://espiebi.pap.pl{a['href']}"
                if full_url not in seen_urls:
                    links.append(full_url)
                    seen_urls.add(full_url)

        if not links:
            print(f"No reports found on page {page + 1}")
            break

        for link in links:
            print(f"Processing report from: {link}")
            report_html = fetch_url(link)
            if report_html:
                report_data = parse_espi_report(report_html, link)  # Przekaż URL
                if report_data and report_data['data'] and report_data['tytul']:
                    all_reports.append(report_data)

    all_reports.sort(key=lambda x: x['data'], reverse=True)

    for i, report in enumerate(all_reports, 1):
        report['numer_raportu'] = f"{i}/allegro"

    return all_reports


def save_to_csv(reports, filename="allegro_reports2.csv"):
    fieldnames = ['data', 'symbol_spolki', 'tytul', 'tresc', 'typ_raportu', 'numer_raportu', 'url']  # Dodaj URL

    reports = [report for report in reports if report['data'] and report['tytul']]

    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(reports)



if __name__ == "__main__":
    reports = scrape_reports()
    save_to_csv(reports)
    print(f"\nScraped {len(reports)} reports and saved to allegro_reports.csv")
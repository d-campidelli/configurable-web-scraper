import requests  
import os
from bs4 import BeautifulSoup 
import csv  
import argparse  
import warnings  
from urllib3.exceptions import InsecureRequestWarning 

warnings.simplefilter('ignore', InsecureRequestWarning)

def load_model(file_path):
    config = {}
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                config[key.strip()] = value.strip()
    return config

def fetch_page(url, headers):
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def scrape_page(html_content, config, base_url):
    soup = BeautifulSoup(html_content, 'html.parser')
    items = soup.select(config['item_selector'])
    data = []
    count = 0

    main_fields = [key for key in config.keys() if key.endswith('_selector')]

    for item in items:
        row = {}
        for field in main_fields:
            field_name = field.replace('_selector', '')
            selector = config[field]
            element = item.select_one(selector)

            if field == 'link_selector' and element:
                detail_url = element.get('href', 'N/A')
                if detail_url != 'N/A' and not detail_url.startswith('http'):
                    detail_url = base_url.rstrip('/') + '/' + detail_url.lstrip('/')
                row[field_name] = detail_url
            elif field == 'rating_selector' and element:
                classes = element.get('class', [])
                row[field_name] = classes[1] if len(classes) > 1 else 'N/A'
            elif 'item' not in field:
                if element:
                    row[field_name] = element.get('title') or element.get_text(strip=True)
                else:
                    row[field_name] = 'N/A'

        count += 1
        print(f'Row {count} scraped.', end='\r')

        # Skip rows where all values are N/A (e.g. header rows)
        if all(v == 'N/A' for v in row.values()):
            continue

        data.append(row)

    return data, main_fields

def save_to_csv(data, fieldnames, file_name):
    if not data or not fieldnames:
        print("No data to save.")
        return

    filtered_fieldnames = [
        field.replace('_selector', '')
        for field in fieldnames
        if 'item' not in field
    ]

    with open(file_name, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=filtered_fieldnames)
        writer.writeheader()
        for row in data:
            filtered_row = {k: v for k, v in row.items() if 'item' not in k}
            writer.writerow(filtered_row)


def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
    }

    parser = argparse.ArgumentParser(description="Configurable web scraping tool")
    parser.add_argument('-u', '--url', type=str, required=True, help="Base URL to scrape")
    parser.add_argument('-p', '--pages', type=int, default=1, help="Number of pages to scrape")
    parser.add_argument('-f', '--file', type=str, required=True, help="Model config file")
    parser.add_argument('--page-param', type=str, default='page', help="URL query parameter for pagination (default: 'page')")
    parser.add_argument('-o', '--output', type=str, default='output.csv', help="Output CSV file name")
    args = parser.parse_args()

    config = load_model(args.file)

    all_data = []
    fieldnames = []

    for page_num in range(1, args.pages + 1):
        url = f"{args.url}?{args.page_param}={page_num}"
        print(f"Scraping page {page_num}: {url}")

        html_content = fetch_page(url, headers)
        if html_content:
            page_data, fieldnames = scrape_page(html_content, config, args.url)
            all_data.extend(page_data)
            print(f"\nPage {page_num} done — {len(page_data)} rows collected.")
        else:
            print(f"Skipping page {page_num} — could not fetch.")

    save_to_csv(all_data, fieldnames, args.output)
    print(f"\nDone. Data saved to {args.output}")


if __name__ == "__main__":
    main()
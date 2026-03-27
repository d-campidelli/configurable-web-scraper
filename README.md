# Configurable Web Scraper 

## Overview

A Python-based web scraping tool that extracts structured data from static websites using user-defined CSS selector config files. 
No code changes needed to scrape a new website, you just write a new config file.

> Originally developed during an internship at Airipm Srl. Refactored and generalized for broader use.

## Features

- Configurable via simple `.txt` model files
- Supports multi-page pagination
- Exports data to CSV
- Handles relative URLs, encoding, and empty rows automatically
- Extensible: `scrape_page()` supports custom special cases for non-standard data (e.g. CSS-class-encoded values like star-ratings)

## Requirements

- Python 3.x
- `requests`
- `beautifulsoup4`
- `urllib3`
  
## Installation

Install the required libraries using pip:

```bash
pip install requests beautifulsoup4 urllib3
```

## Usage

### Command Line Arguments

- `-u` or `--url`: Base URL to scrape (required).
- `-p` or `--pages`: Number of pages to scrape (default is 1).
- `-f` or `--file`: Model file (required).
- `-o` or `--output`: CSV Output file (required).

### Running the Scraper

To run the web scraper:

```bash
python web_scraper_gen.py -u "<URL>" -p <NUM_PAGES> -f "<MODEL_FILE>" -o "<OUTPUT_FILE>"
```

Example:

```bash
python Web_scraper.py -u "https://books.toscrape.com/" -f Book_toscrape.txt -o Output.csv
```

## Model File Format
Create a `.txt` file with CSS selectors:
```
item_selector = article.product_pod
title_selector = h3 a
price_selector = .price_color
rating_selector = .star-rating
```
## Included Examples
- `wikipedia_companies.txt` — largest US companies by revenue
- `books.txt` — books.toscrape.com

## Limitations
- Does not support JavaScript-rendered websites (e.g. eBay, Amazon)

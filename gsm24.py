import aiohttp
import asyncio
import time
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from product import Product
from fetch_page import fetch_page
from bs4 import BeautifulSoup
from database import saveData

import requests

async def main():
    main_sites = ['https://gsm24.pl/12-smartfony',
               'https://gsm24.pl/15-tablety',
                 'https://gsm24.pl/63-smartwatche',
                   'https://gsm24.pl/13-akcesoria']
    prod_sites = []
    for strona in main_sites:
        try:
            html_cont = requests.get(strona).text
            soup = BeautifulSoup(html_cont, 'html.parser')

            pages = soup.find('div', {"class": "pages-num"})
            if pages is not None:
                ostatnia = int(pages.find_all('li')[-2].text.strip())
                temp = [f'{strona}?page={i}' for i in range(1,ostatnia +1)]
                prod_sites += temp
            else:
                prod_sites.append(strona)
        except Exception as e:
            print(f"Nie udało się wygenerować linków do {strona}: {e}")

    connector = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(connector=connector) as session:
        #Pobranie szczegółowych informacji produktów
        try:
            tasks = []

            for url in prod_sites:
                tasks.append(fetch_page(session, url))
            htmls = await asyncio.gather(*tasks)
        except Exception as e:
            print(f"Błąd podczas pobierania zawartości stron z produktami. Program kończy działanie: {e}")
            return
        
        produkty = []
        for url, soup in zip(prod_sites, htmls):
            try:
                section_main = soup.find('section', {"id": "main"})
                prod = section_main.find_all('article')
                kat = soup.find('h1').text
                for product in prod:
                    nazwa = product.find('h3').text
                    prod_url = product.find('h3').find('a')['href']
                    cena = product.find('span', {"class": "price"}).text.strip()[:-2]
                    
                    clean_price = cena.replace('\xa0', '').replace(',', '.')
                    p = Product(nazwa.strip(),kat,float(clean_price),prod_url)
                    produkty.append(p)

                    if len(produkty) >= 1000:
                        saveData(produkty,'gsm24')
                        produkty = []
            except Exception as e:
                print(f"Nie udało się pobrać danych ze strony: {url}: {e}")
    
        saveData(produkty, 'gsm24')

asyncio.run(main())
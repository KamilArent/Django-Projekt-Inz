import aiohttp
import asyncio
import time
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from product import Product
from fetch_page import fetch_page
from database import saveData

async def main():
    start = time.time()

    sferis_gsm = 'https://www.sferis.pl/telefony-i-tablety-3909'
    strony = []

    #Sprawdzenie ilości stron oraz utwórzenie linków
    try:
        driver.get(sferis_gsm)
        paginacja = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'nav.jsPagination'))
        )
        max_strona = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'nav.jsPagination > a'))
        )
        max_strona = paginacja.find_elements(By.CSS_SELECTOR, 'a')
        last_page = max_strona[2].get_attribute('textContent')
        for i in range(1, int(last_page) +1):
            strony.append(f'{sferis_gsm}?p={i}')
    except:
        print("Wystąpił błąd podczas pobierania oraz tworzenia linków stron. Program nie będzie kontynuował")
        return
    finally:
        driver.quit()
    connector = aiohttp.TCPConnector(limit=10)

    #Pobranie linków do każdego produktu w celu pobrania szczegółowych informacji
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            
            tasks = []

            for url in strony:
                tasks.append(fetch_page(session, url))
            pobrane_strony = await asyncio.gather(*tasks)
        except:
            print("Błąd podczas pobierania zawartości głównych stron. Program nie będzie kontynuował")
            return
        
        urls = []
        for url, soup in zip(strony, pobrane_strony):
            try:
                article = soup.find('article')
                prods = article.find_all('div', {"class": "tv_ jsSwipe"})
                for prod in prods:
                    urls.append(f'https://www.sferis.pl{prod.find('a')['href']}')
            except:
                print(f'Nie udało się pobrać linku jedngo z produktów na stronie: {url}')

        #Pobranie szczegółowych informacji produktów
        try:
            tasks = []

            for url in urls:
                tasks.append(fetch_page(session, url))
            htmls = await asyncio.gather(*tasks)
        except Exception as e:
            print(f"Błąd podczas pobierania zawartości stron produktów. Program kończy działanie: {e}")
            return
        
        produkty = []
        for url, soup in zip(urls, htmls):
            try:
                nazwa = soup.find('h1').text
                art_cena = soup.find('section', {"class": "ui zf"})
                cena = art_cena.find('div', {"class": "sf"}).text[:-3].strip()
                kat = soup.find('div', {"class": "qd yy bx"}).find_all('a')[-2].text
                clean_price = cena.replace(' ', '').replace(',', '.')
                p = Product(nazwa.strip(),kat,float(clean_price),url)
                produkty.append(p)
                if len(produkty) >= 1000:
                    saveData(produkty, 'sferis')
                    produkty=[]
            except Exception as e:
                print(f"Nie udało się pobrać danych ze strony: {url}: {e}")

        saveData(produkty,'sferis')
        end = time.time()
        czas = end-start
        print(f'Czas wykonania {czas}')
    

options = webdriver.ChromeOptions()
options.add_argument("headless")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

asyncio.run(main())
import aiohttp
import asyncio
import time
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from product import Product
from fetch_page import fetch_page
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import requests
from database import saveData

#Jeżeli ciasteczka muszą być on
#WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="onetrust-accept-btn-handler"]'))).click()
async def main():
    strony = ['https://www.komputronik.pl/category/1596/telefony.html',
              'https://www.komputronik.pl/category/18499/smartwatche-i-zegarki.html',
              'https://www.komputronik.pl/category/8923/tablety.html',
              'https://www.komputronik.pl/category/8011/czytniki-ebook.html'
    ]
    produkty =[]
    try:
        driver.get('https://www.komputronik.pl')
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="onetrust-accept-btn-handler"]'))).click()
    except:
        print("Nie udało się zaakceptować ciasteczek. Koniec programu")
        return

    for strona in strony:
        driver.get(strona)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        try:
            kategoria = soup.find('h1').text
        except:
            print(f"Nie znaleziono nazwy kategorii. Pomijam stronę: {strona}")
        next_page = True
        while next_page is not None:
            #Znalezienie sekcji z produktami oraz pobranie danych
            try:
                article = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-name="listingContent"]'))
                )
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                article = soup.find('div', {"data-name": "listingContent"})
                article_products = article.find('div', {"class": "xl:col-span-3"})
                products = article_products.find_all('div', {"class": "relative my-6"})
                for prod in products:
                    nazwa = prod.find('a')['title']
                    url = prod.find('a')['href']
                    url = f'https://www.komputronik.pl{url}'
                    cena = prod.find('div', {"data-price-type": "final"}).text[:-2]
                    cena = cena.replace('\xa0', '').replace(' ', '').replace(',', '.')
                    produkty.append(Product(nazwa.strip(), kategoria, float(cena), url))
                if len(produkty)>1000:
                    saveData(produkty, 'komputronik')
            except Exception as e:
                print(e)
                #print(f'Nie znaleziono produktów na stronie lub nie udało się pobrać danych produktu: {strona}. Przechodzę na kolejną stronę.')
            #Sprawdzenie czy jest kolejna strona oraz zmiana na następną stronę lub kategorię
            try:
                paginacja = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="pageContent"]/div/div[4]/div[2]/nav[2]'))
                )
                next_page_icon = paginacja.find_element(By.CLASS_NAME, 'i-arrow-right') 
                if next_page_icon:
                    parent_element = next_page_icon.find_element(By.XPATH, '..')  # Znalezienie rodzica
                    time.sleep(1)  # Opcjonalne opóźnienie przed kliknięciem
                    ActionChains(driver).move_to_element(parent_element).click().perform()
                else:
                    break
            except:
                break
    if len(produkty)>0:
        saveData(produkty, 'komputronik')


options = webdriver.ChromeOptions()
options.add_argument("headless")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)


asyncio.run(main())
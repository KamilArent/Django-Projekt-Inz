import aiohttp
import asyncio
import time
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from product import Product
from fetch_page import fetch_page
import requests
from bs4 import BeautifulSoup
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from database import saveData

def main():
    strony= [
        'https://www.neonet.pl/smartfony-i-navi/smartfony.html',
        'https://www.neonet.pl/smartfony-i-navi/sluchawki.html',
        'https://www.neonet.pl/smartfony-i-navi/akcesoria-gsm-i-gps.html'
    ]
    kategorie= {}
    produkty = []
    for strona in strony:
        driver.get(strona)
        if strona in strony[:3]:
            paginacja = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="categoryProducts"]/section/div[3]/section[2]/div'))                                                      
                        )
            soupPage = BeautifulSoup(paginacja.get_attribute('outerHTML'), 'html.parser')
            last_page = soupPage.find('input')['max']
            temp = [f'{strona}?p={i}' for i in range(2,int(last_page) + 1)]
            strony += temp
            soupFullPage = BeautifulSoup(driver.page_source, 'html.parser')
            kategoria = soupFullPage.find('h1').text
            kategorie.update({strona:kategoria})

        
        time.sleep(1.3)

        # Wait for the section containing products to load
        article = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="categoryProducts"]/section/div[3]/section[1]/section'))
        )
        

        scroll_count = 0
        scroll_limit = 17
        while scroll_count < scroll_limit:
            # Scroll down a small amount to trigger loading new products
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(0.3)  # Wait for lazy loading to fetch the products  
            
            scroll_count += 1
        
        article = driver.find_element(By.XPATH, '//*[@id="categoryProducts"]/section/div[3]/section[1]/section')

        soupProduct = BeautifulSoup(article.get_attribute('outerHTML'), 'html.parser')
        products = soupProduct.find_all('div', {"class": "listingItemScss-root-1KP"})

        try:
            question_mark_index = strona.index("?")
            kategoria =  kategorie[strona[:question_mark_index]]
        except:
            kategoria = kategorie[strona]
        print(f"Jestem na: {strona}")
        
        for product in products:
            try:
                nazwa = product.find('h2').text
                link = product.find('a')['href']
                url = f'https://www.neonet.pl{link}'
                cena = product.find('span', {"class": "uiPriceSimpleScss-priceWrapper-2zA"}).text[:-2].strip()
                real_price = cena.replace(' ', '').replace(',', '.')
                produkty.append(Product(nazwa.strip(), kategoria, float(real_price), url))
            except:
                nazwa = nazwa if nazwa is not None else ''
                print(f"Niezapisany produkt na stronie {nazwa} :{strona}")
                continue
        if len(produkty) >= 1000:
            saveData(produkty, 'neonet')
            produkty = []
    if len(produkty) > 0:
        saveData(produkty, 'neonet')


#driver_path = "C:\\Users\\kamil\\Downloads\\chromedriver-win64\\chromedriver.exe"
#service = Service(driver_path)
#options = webdriver.ChromeOptions()
#options.add_experimental_option("prefs", {
#    "profile.default_content_setting_values.cookies": 2
#   })
#options.add_argument("headless")
#driver = webdriver.Chrome(service=service, options=options)


options = webdriver.ChromeOptions()
options.add_argument("headless")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

main()
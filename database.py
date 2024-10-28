import random
import pyodbc
from datetime import datetime
from product import Product

conn_string="localhost;Database=master;Trusted_Connection=True"

SERVER = 'DESKTOP-5PLQBPB'
DATABASE = 'engineer'

# Używając Trusted_Connection dla uwierzytelniania Windows
connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=yes;'



def saveData(produkty, tabela):
    try:
        conn = pyodbc.connect(connectionString) 
        SQL_StATEMENT = f"""
    INSERT INTO [dbo].[{tabela}]
            ([nazwa]
            ,[kategoria]
            ,[cena]
            ,[url]
            ,[data])
            VALUES (?,?,?,?,?)
    """

        
        cursor = conn.cursor()
        data = datetime.today().date()
        for produkt in produkty:
            cursor.execute(SQL_StATEMENT, 
                        produkt.nazwa, 
                        produkt.kategoria,
                        produkt.cena,
                        produkt.url,
                        data
                        )
    
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Błąd podczas zapisywania danych do {tabela}: {e}")
            


def fillProduktyMockData():
    categories = ["smartfon", "tablet", "laptop", "telewizor"]
    brands = ["Samsung", "Apple", "Huawei", "Sony", "LG"]
    model_numbers = range(10, 30)
    
    try:
        conn = pyodbc.connect(connectionString) 
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produkty")
        conn.commit()

        
        for product_id in range(1, 1000):  # Generate 20 random products
            category = random.choice(categories)
            brand = random.choice(brands)
            model_number = random.choice(model_numbers)
            name = f"{category.capitalize()} {brand} {model_number}"
            price = round(random.uniform(500, 5000), 2)
            cursor.execute(
                "INSERT INTO produkty (id, nazwa, kategoria, cena) VALUES (?, ?, ?, ?)",
                product_id, name, category, price
            )
        cursor.commit()
        conn.close()
        
    except Exception as e:
        print(f"Błąd podczas tworzenia dancych produktów sklepu: {e}")
            


def addEditConnection(id, nazwaSferis, nazwaNeonet,nazwaGsm, nazwaKomputronik):
    try:
        conn = pyodbc.connect(connectionString) 
        cursor =conn.cursor()
        selectId = f'SELECT * FROM ProduktyConnections WHERE id={id}'
        cursor.execute(selectId)
        if cursor.rowcount == 0:
            statement = f'''INSERT INTO ProduktyConnections(
            id,
            nazwaSferis,
            nazwaNeonet,
            nazwaGsm,
            nazwaKomputronik
            ) VALUES (?,?,?,?,?)'''
            cursor.execute(statement,id, nazwaSferis,nazwaNeonet,nazwaGsm,nazwaKomputronik)
        else:
            statement = f'''
                UPDATE ProduktyConnections
                SET 
                nazwaSferis = ?,
                nazwaNeonet = ?,
                nazwaGsm = ?,
                nazwaKomputronik = ?
                WHERE 
                id = ?
            '''

            cursor.execute(statement, nazwaSferis,nazwaNeonet,nazwaGsm,nazwaKomputronik,id)

        cursor.commit()
        conn.close()
    except Exception as e:
        print(f'Błąd: {e}')
            

def removeConnection(id):
    try:
        conn = pyodbc.connect(connectionString) 
        statement = f"DELETE ProduktyConnections WHERE id = {id}"
        conn.cursor().execute(statement).commit()
        conn.close()
    except Exception as e:
        print(f'Błąd przy usuwaniu połączenia: {e}')
            


def selectConnectionId(id):
    try:
        conn = pyodbc.connect(connectionString) 
        statement = f"SELECT * FROM ProduktyConnections WHERE id = {id}"
        res = conn.cursor().execute(statement)
        res = res.fetchall()
        conn.close()
        return res
    except Exception as e:
        print(f'Błąd przy usuwaniu połączenia: {e}')
            



def selectNajnowsze(tabela):
    try:
        conn = pyodbc.connect(connectionString) 
        test_st = f"""SELECT nazwa, cena, data, url
                FROM (
                    SELECT nazwa,
                        cena,
                        data,
                        url,
                        ROW_NUMBER() OVER(PARTITION BY nazwa ORDER BY data DESC) AS rn
                    FROM {tabela}
                ) AS latest_products
                WHERE rn = 1;"""
        cursor = conn.cursor()
        cursor.execute(test_st)
        res = cursor.fetchall()
        conn.close()
        return res
    except Exception as e:
        print(f"Błąd podczas pobierania najnowszych danych z {tabela}: {e}")
            

def selectAll(tabela):
    try:
        conn = pyodbc.connect(connectionString) 
        st = f"SELECT * FROM [dbo].[{tabela}]"
        cursor = conn.cursor()
        cursor.execute(st)
        res = cursor.fetchall()
        conn.close()
        return res
    except Exception as e:
        print(f'Błąd podczas wybierania z {tabela}: {e}')
            

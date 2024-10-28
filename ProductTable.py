import database as db

class ProductTable:
    def __init__(self, id, nazwa, cena,
                 cenaSferis, urlSferis
    , cenaNeonet, urlNeonet,
      cenaGsm, urlGsm,
        cenaKomputronik, urlKomputronik):
        self.id = id
        self.nazwa = nazwa
        self.cena = cena
        self.cenaSferis = cenaSferis
        self.urlSferis = urlSferis
        self.cenaNeonet = cenaNeonet
        self.urlNeonet = urlNeonet
        self.cenaGsm = cenaGsm
        self.urlGsm = urlGsm
        self.cenaKomputronik = cenaKomputronik
        self.urlKomputronik = urlKomputronik

def convertToTable(produkty, sferis, neonet, gsm, komputronik):
    result = []
    connections = db.selectAll('produktyConnections')
    for item in produkty:
        element = ProductTable(item[0], item[1], item[3],'Brak', None, 'Brak', None, 'Brak', None, 'Brak', None)
        hasConnection = [index1 for index1, value1 in enumerate(connections) if item[0] in value1]
        if len(hasConnection) > 0:
            if connections[hasConnection[0]][1] is not None:
                #bierzemy info z tabeli sferis
                prodId = [index1 for index1, value1 in enumerate(sferis) if connections[hasConnection[0]][1].strip() in str(value1).strip()]
                if len(prodId) > 0:
                    element.cenaSferis = sferis[prodId[0]][1]
                    element.urlSferis = sferis[prodId[0]][3]
            if connections[hasConnection[0]][2] is not None:
                #bierzemy info z tabeli neonet
                prodId = [index1 for index1, value1 in enumerate(neonet) if connections[hasConnection[0]][2].strip() in str(value1[0]).strip()]
                if len(prodId) > 0:
                    element.cenaNeonet = neonet[prodId[0]][1]
                    element.urlNeonet = neonet[prodId[0]][3]
            if connections[hasConnection[0]][3] is not None:
                #bierzemy info z tabeli gsm
                prodId = [index1 for index1, value1 in enumerate(gsm) if connections[hasConnection[0]][3].strip() in str(value1).strip()]   
                if len(prodId) > 0:
                    element.cenaGsm = gsm[prodId[0]][1]
                    element.urlGsm = gsm[prodId[0]][3]
                
            if connections[hasConnection[0]][4] is not None:
                #bierzemy info z tablei komputronik
                prodId = [index1 for index1, value1 in enumerate(komputronik) if connections[hasConnection[0]][4].strip() in str(value1).strip()]
                if len(prodId) > 0:
                    element.cenaKomputronik = komputronik[prodId[0]][1]
                    element.urlKomputronik = komputronik[prodId[0]][3]
        result.append(element)
    return result

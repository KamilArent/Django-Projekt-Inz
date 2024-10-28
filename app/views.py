import zlib
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, HttpResponse
import database as db 
import product as p
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from ProductTable import convertToTable
from django.core.cache import cache
from manage import cacheData

# Create your views here.
@login_required
def home(request):
    return render(request, "home.html")

@login_required
def filterData(request):
    if cache.get('sferis') is None or cache.get('produkty') is None:
        cacheData()

    conns = convertToTable(cache.get('produkty'), cache.get('sferis'),  cache.get('neonet'),cache.get('gsm'), cache.get('komputronik'))
    query_id = request.GET.get('id', '')
    query_name = request.GET.get('name', '')
    query_conns = request.GET.get('conns', '')

    query_conns = int(query_conns) if query_conns.isdecimal() else 1

    #1 - wszystkie | 2 - produkty z połączeniami | 3 - produkty bez połączeń
    filtered_data = conns
    match query_conns:
        case 2:
            filtered_data = [product for product in filtered_data if product.urlSferis is not None or product.urlNeonet is not None or product.urlGsm is not None or product.urlKomputronik is not None]
        case 3:
            filtered_data = [product for product in filtered_data if product.urlSferis is None and product.urlNeonet is None and product.urlGsm is None and product.urlKomputronik is None]

    if query_id is not None or query_id != '':
        filtered_data = [product for product in filtered_data if query_id.lower() in str(product.id).lower()]

    if query_name is not None or query_name != '':
        filtered_data = [product for product in filtered_data if query_name.lower() in product.nazwa.lower()]

    

    products_json = [
        {
            'id': product.id,
            'nazwa': product.nazwa,
            'cena': float(product.cena),
            'cenaSferis': product.cenaSferis,
            'urlSferis': product.urlSferis,
            'cenaNeonet': product.cenaNeonet,
            'urlNeonet': product.urlNeonet,
            'cenaGsm': product.cenaGsm,
            'urlGsm': product.urlGsm,
            'cenaKomputronik': product.cenaKomputronik,
            'urlKomputronik': product.urlKomputronik
        } for product in filtered_data
    ]
    return JsonResponse({'products': products_json})

@login_required
def importData(request):
    error_message = None
    uploaded_file = request.FILES.get('file')
    if request.method == 'POST':
        #uploaded_file = request.FILES['file']

        if uploaded_file:
            #zapisanie pliku na serwerze, a następnie uzyskanie ścieżki do niego
            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = fs.path(filename)  

            #Przetworzenie i zapisanie danych z pliku do bazy danych
            if db.saveProduktyCSV(file_path):
                products = db.selectAll("Produkty")
                cache.set('produkty', products, timeout=60 * 15)
                return redirect('home')
        error_message = "Nieprawidłowy format pliku lub jego brak. Nagłówki powinny być następujące: ID, Nazwa, Cena_Brutto"
        

    return render(request, "importData.html", {'error_message': error_message})

@login_required
def edit_product(request, product_id):
    if cache.get('sferis') is None or cache.get('produkty') is None:
        cacheData()
    selectedProduct = cache.get('produkty')
    selectedProductID = None
    sferis = cache.get('sferis')
    neonet = cache.get('neonet')
    gsm = cache.get('gsm')
    komputronik = cache.get('komputronik')
    names = db.selectConnectionId(product_id)
    error_msg = None

    #Szukamy nazwy oraz ceny wybrangeo produktu 
    for item in selectedProduct:
        if item[0] == product_id:
            selectedProductID = item
            break

    if selectedProductID is None:
        return redirect('home')

    
    #Po zapisaniu zmian edycji połączeń
    if request.method == 'POST':
        isSferis = request.POST.get('checkSferis')
        isNeonet = request.POST.get('checkNeonet')
        isGsm = request.POST.get('checkGsm')
        isKomputronik = request.POST.get('checkKomputronik')

        if isNeonet and isGsm and isSferis and isKomputronik:
            db.removeConnection(product_id)
            return redirect('home')

        prodSferis = None if isSferis else request.POST.get('sferis')
        prodNeonet = None if isNeonet else request.POST.get('neonet')
        prodGsm = None if isGsm else request.POST.get('gsm')
        prodKomputronik = None if isKomputronik else request.POST.get('komputronik')

        #Sprawdzenie czy nazwa produktu jest identyczna co w bazie danych
        checkedSferis = prodSferis is  None or  len([product for product in sferis if prodSferis.strip().lower() == product[0].strip().lower()]) > 0
        checkedNeonet = prodNeonet is  None or  len([product for product in neonet if prodNeonet.strip().lower() == product[0].strip().lower()]) > 0
        checkedGsm = prodGsm is  None or  len([product for product in gsm if prodGsm.strip().lower() == product[0].strip().lower()]) > 0
        checkedKomputronik = prodKomputronik is  None or len([product for product in komputronik if prodKomputronik.strip().lower() == product[0].strip().lower()]) > 0
        

        if not checkedSferis or not checkedKomputronik or not checkedGsm or not checkedNeonet:
            error_msg = 'Jeden z produktów nie zgadza się z bazą danych. Wybierz produkty z dostępnych list.'
        else:
            db.addEditConnection(product_id, prodSferis, prodNeonet, prodGsm, prodKomputronik)
            return redirect('home')
    names = [{  
            'id': product_id,
            'nazwaSferis': names[0][1] if len(names) > 0 and names[0][1] else item[1],
            'nazwaNeonet': names[0][2] if len(names) > 0 and names[0][2] else item[1],
            'nazwaGsm': names[0][3] if len(names) > 0 and names[0][3]  else item[1],
            'nazwaKomputronik': names[0][4] if len(names) > 0 and names[0][4] and len(names) else item[1]
        }] if request.method == 'GET' else [
            {
                'id': product_id,
                'nazwaSferis': prodSferis.strip() if prodSferis else item[1],
                'nazwaNeonet': prodNeonet.strip() if prodNeonet else item[1],
                'nazwaGsm': prodGsm.strip() if prodGsm else item[1],
                'nazwaKomputronik': prodKomputronik.strip() if prodKomputronik else item[1]
            }
        ]

    return render(request, 'edit.html', {'product': selectedProductID, 'sferis': sferis, 'neonet': neonet, 'gsm': gsm, 'komputronik': komputronik, 'connectedNames': names, 'error_message': error_msg})

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request,user)  # Loguje użytkownika i tworzy sesję
            return redirect('home')  # Przekierowanie po udanym logowaniu
        else:
            messages.error(request, 'Błędny login lub hasło')  # Wyświetlanie błędu

    return render(request, 'login.html')  # Wyświetla formularz logowania

def logout_user(request):
    logout(request)
    return redirect("login")
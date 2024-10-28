#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import json
import os
import sys
import zlib
import database as db
from ProductTable import convertToTable
from django.core.cache import cache

def cacheData():
    products = db.selectAll("produkty")
    sferis = db.selectNajnowsze('sferis')
    gsm = db.selectNajnowsze('gsm24')
    neonet = db.selectNajnowsze('neonet')
    komputronik = db.selectNajnowsze('komputronik')

    cache.set('sferis', sferis, timeout=60 * 15)
    cache.set('gsm', gsm, timeout=60 * 15)
    cache.set('neonet', neonet, timeout=60 * 15)
    cache.set('komputronik', komputronik, timeout=60 * 15)
    cache.set('produkty', products, timeout=60 * 15)

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'front.settings')

    #Pobranie danych z bazy danych oraz zapisanie ich w pamięci podręcznej
    cacheData()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

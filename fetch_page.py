import random
import asyncio
from bs4 import BeautifulSoup


async def fetch_page(session, url, retries=3):
    try:
        # Random sleep to avoid overloading the server
        timeout = random.uniform(1, 3)
        await asyncio.sleep(timeout)
        
        # Attempt to fetch the page
        async with session.get(url) as response:
            if response.status == 200:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                return soup
            else:
                print(f"Failed with status {response.status} for URL: {url}")
                return None

    except Exception as e:
        if retries > 0:
            print(f"Retrying {url}. Attempts left: {retries}. Error: {e}")
            await asyncio.sleep(random.uniform(2, 5))  # Longer wait before retry
            return await fetch_page(session, url, retries - 1)
        else:
            print(f"Błąd podczas wyciągania zawartości ze strony: {url}: {e}")
            return None
        












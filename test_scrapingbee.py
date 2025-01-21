import requests
import urllib.parse
from bs4 import BeautifulSoup
import pandas as pd

API_KEY = "MT6LMO04YLGDYHMRBCKNGH48W5FKBJ3HRRY9LDCEU2EYAAZTXWPPN0L04C2KPCR080LJBCWZBM7FECC0"

def scrape_google_results(query):
    encoded_query = urllib.parse.quote(query)
    url = f"https://app.scrapingbee.com/api/v1/?api_key={API_KEY}&custom_google=True&block_resources=False&stealth_proxy=True&country_code=us&url=https://www.google.com/search?q={encoded_query}"

    response = requests.get(url, timeout=60)

    if response.status_code == 200:
        print("Scraping exitoso!")
        return response.text
    else:
        print(f"Error: {response.status_code}, Respuesta: {response.text}")
        return None

def parse_google_results(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    search_results = []

    for result in soup.select('div.tF2Cxc'):
        title = result.select_one('h3').text if result.select_one('h3') else "No encontrado"
        link = result.select_one('a')['href'] if result.select_one('a') else "No encontrado"
        description = result.select_one('.VwiC3b').text if result.select_one('.VwiC3b') else "No encontrado"

        search_results.append({
            "Título": title,
            "URL": link,
            "Descripción": description
        })

    return pd.DataFrame(search_results)

# Ejecutar el scraping
query = "Auditoría SEO"
html_content = scrape_google_results(query)

if html_content:
    df_results = parse_google_results(html_content)
    print(df_results.head())  # Mostrar los primeros resultados
    df_results.to_csv("resultados_google.csv", index=False)  # Guardar los resultados en un archivo CSV
else:
    print("No se obtuvieron resultados.")


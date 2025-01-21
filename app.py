
import streamlit as st 
import requests
import urllib.parse
import pandas as pd
from bs4 import BeautifulSoup
import re

# Configuración de la página
st.set_page_config(page_title="AuditX - SEO Auditing Tool", layout="wide")

st.title("AuditX")
st.subheader("Herramienta de auditoría SEO automatizada")
st.markdown("Ingrese un término de búsqueda para analizar los primeros 20 resultados de Google.")

# Entrada del usuario
query = st.text_input("🔎 Buscar en Google:", placeholder="Ejemplo: servicios de marketing digital")

API_KEY = "MT6LMO04YLGDYHMRBCKNGH48W5FKBJ3HRRY9LDCEU2EYAAZTXWPPN0L04C2KPCR080LJBCWZBM7FECC0"

# Función para extraer palabras clave eliminando palabras irrelevantes
def extract_keywords(text):
    stop_words = ["de", "y", "el", "la", "los", "las", "un", "una", "para", "con", "en", "por", "del", "se", "a", "que", "es"]
    words = re.findall(r'\b\w{4,}\b', text.lower())  # Extraer palabras de 4 o más letras
    keywords = [word for word in words if word not in stop_words]
    return ", ".join(keywords) if keywords else "No encontrado"

def scrape_google_results(query):
    encoded_query = urllib.parse.quote(query)
    url = f"https://app.scrapingbee.com/api/v1/?api_key={API_KEY}&custom_google=True&block_resources=False&stealth_proxy=True&country_code=us&url=https://www.google.com/search?q={encoded_query}"

    response = requests.get(url, timeout=60)

    if response.status_code == 200:
        return response.text
    else:
        st.error(f"Error en la solicitud: {response.status_code}")
        return None

def parse_google_results(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    search_results = []

    for result in soup.select('div.tF2Cxc'):
        title = result.select_one('h3').text if result.select_one('h3') else "No encontrado"
        link = result.select_one('a')['href'] if result.select_one('a') else "No encontrado"
        description = result.select_one('.VwiC3b').text if result.select_one('.VwiC3b') else "No encontrado"

        # Extraer palabras clave encontradas
        keywords_found = extract_keywords(title + " " + description)

        search_results.append({
            "Título": title,
            "URL": link,
            "Descripción": description,
            "Palabras Clave Encontradas": keywords_found
        })

    return pd.DataFrame(search_results)

if st.button("Iniciar Auditoría"):
    if query:
        with st.spinner("Realizando auditoría SEO..."):
            html_content = scrape_google_results(query)
            if html_content:
                df_results = parse_google_results(html_content)
                st.success(f"✅ Se encontraron {len(df_results)} resultados.")
                
                # Mostrar la tabla de resultados con palabras clave
                st.dataframe(df_results)

                # Opción para descargar CSV
                csv = df_results.to_csv(index=False).encode('utf-8')
                st.download_button(label="⬇️ Descargar informe en CSV", data=csv, file_name="resultados_seo.csv", mime="text/csv")
    else:
        st.warning("⚠️ Por favor, ingrese un término de búsqueda.")

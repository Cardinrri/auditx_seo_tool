
import re
import random
import time
import pandas as pd
from collections import Counter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Lista de User-Agents para evitar bloqueos
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]

# Función para limpiar el texto y manejar caracteres especiales
def clean_text(text):
    text = text.encode("utf-8", "ignore").decode("utf-8")  # Asegurar codificación correcta
    text = re.sub(r'[^\x00-\x7FñÑáéíóúÁÉÍÓÚüÜ]', '', text)  # Eliminar caracteres no imprimibles
    text = text.strip()  # Eliminar espacios extra
    return text

# Análisis SEO de los resultados
def analyze_seo(title, description, url, query):
    query_lower = query.lower()

    # Buscar correos electrónicos y teléfonos
    email_match = re.findall(r'[\w\.-]+@[\w\.-]+', description)
    phone_match = re.findall(r'\+?\d{1,3}?[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}', description)

    # Buscar precios en la descripción
    price_match = re.findall(r'\$?\€?\d+[\.,]?\d*\s?(USD|EUR|\$|\€)?', description)

    # Identificar rich snippets
    has_rating = "★" in description or "★★★★★" in description
    has_faq = "preguntas frecuentes" in description.lower() or "FAQ" in description.upper()

    # Identificar si la URL contiene palabras clave de servicios
    service_keywords = ["servicios", "products", "pricing", "planes"]
    is_service_url = any(keyword in url.lower() for keyword in service_keywords)

    # Extraer palabras clave más comunes
    words = re.findall(r'\b\w{4,}\b', description.lower())
    common_words = Counter(words).most_common(5)

    keywords_detected = ", ".join([word[0] for word in common_words]) if common_words else "No encontrado"

    return {
        "Palabra Clave en Título": "Sí" if query_lower in title.lower() else "No",
        "Palabra Clave en Descripción": "Sí" if query_lower in description.lower() else "No",
        "Palabra Clave en URL": "Sí" if query_lower in url.lower() else "No",
        "Palabras Clave Encontradas": keywords_detected,
        "Título": title,
        "Descripción": description,
        "URL": url,
        "Longitud Título": len(title),
        "Longitud Descripción": len(description),
        "Dominio": re.findall(r'https?://(www\.)?([^/]+)', url)[0][1],
        "Correos electrónicos": ", ".join(email_match) if email_match else "No encontrado",
        "Teléfonos": ", ".join(phone_match) if phone_match else "No encontrado",
        "Precios": ", ".join(price_match) if price_match else "No encontrado",
        "Rich Snippets": "Sí" if has_rating or has_faq else "No",
        "URL de Servicios": "Sí" if is_service_url else "No"
    }

# Función de scraping de Google
def scrape_google_results(query, num_results=20, country="google.com"):
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")

    driver = webdriver.Chrome(options=options)
    search_url = f"https://www.{country}/search?q={query.replace(' ', '+')}&num={num_results}"
    driver.get(search_url)

    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "q")))
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.tF2Cxc")))

        results = driver.find_elements(By.CSS_SELECTOR, "div.tF2Cxc")
        extracted_data = []

        for result in results[:num_results]:
            try:
                title = clean_text(result.find_element(By.CSS_SELECTOR, "h3").text)
                link = clean_text(result.find_element(By.CSS_SELECTOR, "a").get_attribute("href"))

                # Buscar la descripción con múltiples selectores para evitar errores
                description = "Descripción no encontrada"
                possible_selectors = ["div.VwiC3b", "span.aCOpRe", "div.BNeawe.s3v9rd.AP7Wnd"]

                for selector in possible_selectors:
                    elements = result.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        description = clean_text(elements[0].text)
                        break

                seo_data = analyze_seo(title, description, link, query)
                extracted_data.append(seo_data)

            except Exception as e:
                print(f"Error al obtener un resultado: {e}")

    except Exception as e:
        print(f"Error durante la búsqueda: {e}")
        extracted_data = []

    finally:
        time.sleep(random.randint(3, 6))  # Espera aleatoria para evitar bloqueos
        driver.quit()

    df = pd.DataFrame(extracted_data)
    return df


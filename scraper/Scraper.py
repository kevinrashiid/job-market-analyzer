from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3
import time
import os

BASE_URL = "https://www.tecnoempleo.com/busqueda-empleo.php?te=desarrollador&pr=Madrid&pagina={}"
DB_PATH = "../data/jobs.db"


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ofertas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            empresa TEXT,
            ubicacion TEXT,
            tecnologias TEXT,
            fecha_scraping TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Eliminar duplicados existentes antes de crear el índice único
    cursor.execute("""
        DELETE FROM ofertas WHERE id NOT IN (
            SELECT MIN(id) FROM ofertas GROUP BY titulo, empresa
        )
    """)

    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_titulo_empresa
        ON ofertas (titulo, empresa)
    """)
    conn.commit()
    conn.close()


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver


def extraer_tecnologias(texto):
    keywords = [
        "Java", "Python", "JavaScript", "TypeScript", "React", "Angular", "Vue",
        "Spring", "Django", "Flask", "Node", "SQL", "MySQL", "PostgreSQL",
        "MongoDB", "Docker", "Kubernetes", "AWS", "Azure", "Git", "PHP", "Laravel"
    ]
    encontradas = [kw for kw in keywords if kw.lower() in texto.lower()]
    return ", ".join(encontradas)


def scrape_pagina(driver, pagina):
    url = BASE_URL.format(pagina)
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.p-3.border.rounded"))
        )
    except Exception:
        print(f"  [!] Timeout en página {pagina}")
        return []

    ofertas = driver.find_elements(By.CSS_SELECTOR, "div.p-3.border.rounded")
    resultados = []

    for oferta in ofertas:
        try:
            titulo = oferta.find_element(By.CSS_SELECTOR, "h3 a").text.strip()
            empresa = oferta.find_element(By.CSS_SELECTOR, "a.text-primary").text.strip()
            ubicacion_el = oferta.find_elements(By.CSS_SELECTOR, "span.d-none.d-sm-inline")
            ubicacion = ubicacion_el[0].text.strip() if ubicacion_el else "No especificada"
            texto_completo = oferta.text
            tecnologias = extraer_tecnologias(texto_completo)
            resultados.append((titulo, empresa, ubicacion, tecnologias))
        except Exception:
            continue

    return resultados


def guardar_ofertas(ofertas):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    nuevas = 0
    for oferta in ofertas:
        try:
            cursor.execute(
                "INSERT INTO ofertas (titulo, empresa, ubicacion, tecnologias) VALUES (?, ?, ?, ?)",
                oferta
            )
            nuevas += 1
        except sqlite3.IntegrityError:
            # Oferta duplicada, la ignoramos
            pass
    conn.commit()
    conn.close()
    return nuevas


def main():
    init_db()
    driver = get_driver()
    todas_las_ofertas = []

    try:
        for pagina in range(1, 6):
            print(f"Scrapeando página {pagina}...")
            ofertas = scrape_pagina(driver, pagina)
            if not ofertas:
                print("  Sin resultados, parando.")
                break
            todas_las_ofertas.extend(ofertas)
            print(f"  {len(ofertas)} ofertas encontradas.")
            time.sleep(2)
    finally:
        driver.quit()

    if todas_las_ofertas:
        nuevas = guardar_ofertas(todas_las_ofertas)
        print(f"\nOfertas nuevas añadidas: {nuevas}")

    # Total acumulado en la DB
    conn = sqlite3.connect(DB_PATH)
    total = conn.execute("SELECT COUNT(*) FROM ofertas").fetchone()[0]
    conn.close()
    print(f"Total acumulado en DB: {total} ofertas")


if __name__ == "__main__":
    main()
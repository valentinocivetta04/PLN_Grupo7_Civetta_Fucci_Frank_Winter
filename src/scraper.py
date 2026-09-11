"""
scraper.py

Scraper para el TP de Procesamiento del Lenguaje Natural (Unidad 1).

Recorre una categoría de Lectulandia, visita cada ficha de libro, extrae
sus metadatos y sinopsis, y guarda todo en data/libros.csv.

Herramientas:
- Playwright: navega el sitio (carga las páginas como lo haría un browser real).
- BeautifulSoup: parsea el HTML ya descargado y permite buscar con selectores CSS.
- pandas: da formato tabular a cada libro y lo escribe como fila del CSV.
"""

import asyncio          # código asíncrono (esperar sin bloquear el programa)
import os                # manejo de carpetas/archivos
import re                # regex, para extraer el número de serie de un texto
import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from datetime import datetime  # timestamp de cada extracción


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================
# Constantes para no tener valores hardcodeados en el código.

URL_BASE = "https://ww3.lectulandia.co"
CATEGORIA = "Clásico"
URL_CATEGORIA = f"{URL_BASE}/genero/clasico/page/"
LIBROS_OBJETIVO = 150
ARCHIVO_CSV = "data/libros.csv"


async def extraer_datos_ficha(page, url_libro):
    """
    Visita la ficha de un libro y extrae sus metadatos: título, autores,
    géneros, serie (y número dentro de la serie), sinopsis y datos de
    contexto de la extracción.

    page : pestaña de Playwright ya abierta, reutilizada para cada ficha.
    url_libro : URL completa de la ficha a visitar.

    Devuelve un dict con los datos, o None si falló la extracción de esa
    ficha puntual (así un libro con error no corta todo el scraping).
    """
    try:
        # Carga la página (sin esperar imágenes/recursos extra, más rápido)
        # y parsea el HTML resultante con BeautifulSoup.
        await page.goto(url_libro, wait_until="domcontentloaded")
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')

        # --- Título ---
        # <div id="title"><h1>Nombre del libro</h1></div>
        nodo_titulo = soup.select_one('div#title h1')
        titulo = nodo_titulo.get_text(strip=True) if nodo_titulo else None

        # --- Autores y géneros ---
        # select() (plural) porque puede haber más de uno de cada uno.
        lista_autores = [a.get_text(strip=True) for a in soup.select('div#autor a')]
        lista_generos = [a.get_text(strip=True) for a in soup.select('div#genero a')]

        # --- Serie y número dentro de la serie ---
        # HTML esperado si el libro pertenece a una serie:
        #   <div id="serie"><span class="tagTitle">Libro 9 de: </span>
        #       <a class="dinSource">Nombre de la Serie</a></div>
        # Si no pertenece a ninguna serie, div#serie no existe.
        nodo_serie_div = soup.select_one('div#serie')

        if nodo_serie_div:
            nodo_serie_link = nodo_serie_div.select_one('a.dinSource')
            serie = nodo_serie_link.get_text(strip=True) if nodo_serie_link else "N/A"

            # El número ("9") viene mezclado como texto plano junto con
            # "Libro" y "de:", así que se extrae con una regex.
            nodo_tag_title = nodo_serie_div.select_one('span.tagTitle')
            texto_tag_title = nodo_tag_title.get_text(strip=True) if nodo_tag_title else ""
            match_numero = re.search(r'Libro\s+(\d+)\s+de', texto_tag_title)
            numero_serie = match_numero.group(1) if match_numero else "N/A"
        else:
            serie = "N/A"
            numero_serie = "N/A"

        # --- Sinopsis ---
        # separator=' ' evita que el texto de distintas etiquetas internas
        # (<p>, <br>, etc.) quede pegado sin espacios.
        nodo_sinopsis = soup.select_one('div#sinopsis')
        sinopsis = nodo_sinopsis.get_text(separator=' ', strip=True) if nodo_sinopsis else "Sin sinopsis"

        return {
            "titulo": titulo,
            "autores": lista_autores,
            "generos": lista_generos,
            "serie": serie,
            "numero_serie": numero_serie,
            "sinopsis": sinopsis,
            "url_libro": url_libro,
            "categoria_origen": CATEGORIA,
            "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    except Exception as e:
        # Error en ESTA ficha puntual: se informa y se sigue con la próxima.
        print(f"Error extrayendo {url_libro}: {e}")
        return None


async def main():
    """
    Orquesta el scraping completo:
    1. Prepara la carpeta y el CSV de salida (borra el de la corrida anterior).
    2. Abre un Chromium headless.
    3. Recorre el listado de la categoría, página por página.
    4. Por cada libro nuevo, visita su ficha y extrae los datos.
    5. Guarda cada libro en el CSV de forma incremental, hasta llegar al
       objetivo o quedarse sin páginas.
    """

    os.makedirs("data", exist_ok=True)

    # Se borra el CSV de una corrida anterior para generar el dataset desde cero.
    if os.path.exists(ARCHIVO_CSV):
        os.remove(ARCHIVO_CSV)
        print(f"Archivo {ARCHIVO_CSV} existente eliminado. Se generará uno nuevo.")

    # Set para no procesar dos veces el mismo libro si aparece repetido en
    # el listado (buscar en un set es más rápido que en una lista).
    urls_visitadas = set()
    total_extraidos = 0
    pagina_actual = 1

    # async_playwright() + "async with" asegura que el navegador se cierre
    # bien incluso si hay un error en el medio.
    async with async_playwright() as p:
        # headless=True: el navegador corre sin ventana visible.
        browser = await p.chromium.launch(headless=True)

        # context = perfil de navegación aislado (como una ventana de
        # incógnito); page es la pestaña que se reutiliza para todo.
        context = await browser.new_context()
        page = await context.new_page()

        # Recorre páginas del listado hasta juntar LIBROS_OBJETIVO o
        # quedarse sin páginas nuevas.
        while total_extraidos < LIBROS_OBJETIVO:
            print(f"Inspeccionando listado: página {pagina_actual}...")
            try:
                await page.goto(f"{URL_CATEGORIA}{pagina_actual}", wait_until="domcontentloaded")
                html_cat = await page.content()
                soup_cat = BeautifulSoup(html_cat, 'html.parser')

                # Links a cada ficha de libro dentro de las cards del listado.
                enlaces_libros = soup_cat.select('article.card a.title')

                # Sin links = no hay más páginas en esta categoría.
                if not enlaces_libros:
                    print("No hay más páginas disponibles en esta categoría.")
                    break

                for enlace in enlaces_libros:
                    # Ya se llegó al objetivo: no hace falta seguir con esta página.
                    if total_extraidos >= LIBROS_OBJETIVO:
                        break

                    # href suele ser una ruta relativa; se antepone la URL base.
                    url_libro = URL_BASE + enlace.get('href')

                    # Libro repetido en el listado: se saltea sin reprocesar.
                    if url_libro in urls_visitadas:
                        continue

                    datos_libro = await extraer_datos_ficha(page, url_libro)

                    # Se guarda solo si la extracción no falló y tiene título
                    # (campo mínimo para considerar válido el registro).
                    if datos_libro and datos_libro["titulo"]:
                        urls_visitadas.add(url_libro)
                        total_extraidos += 1
                        print(f"[{total_extraidos}/{LIBROS_OBJETIVO}] OK: {datos_libro['titulo']}")

                        # DataFrame de una sola fila con el libro recién extraído.
                        df_incremental = pd.DataFrame([datos_libro])

                        # Encabezado solo la primera vez, cuando el CSV no existe aún.
                        guardar_encabezado = not os.path.exists(ARCHIVO_CSV)

                        # mode='a': guardado incremental, no se pierde lo ya
                        # escrito si el script se corta a mitad de camino.
                        df_incremental.to_csv(
                            ARCHIVO_CSV,
                            mode='a',
                            header=guardar_encabezado,
                            index=False,          # no guarda el índice de pandas
                            encoding='utf-8'      # tildes y ñ se guardan bien
                        )

                    # Pausa entre libros para no saturar el servidor.
                    await asyncio.sleep(2)

            except Exception as e:
                # Error en toda una página de listado: se informa y se sigue
                # con la página siguiente.
                print(f"Error procesando la página de listado {pagina_actual}: {e}")

            pagina_actual += 1

        await browser.close()

    print(f"\n¡Proceso finalizado! Se guardaron {total_extraidos} libros en {ARCHIVO_CSV}.")


# Se ejecuta solo si el script corre directamente, no si se importa.
if __name__ == "__main__":
    asyncio.run(main())

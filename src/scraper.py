import asyncio
import os
import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from datetime import datetime

# variables globales para no hardcodear todo abajo
URL_BASE = "https://ww3.lectulandia.co"
CATEGORIA = "Clásico"
URL_CATEGORIA = f"{URL_BASE}/genero/clasico/page/"
LIBROS_OBJETIVO = 150
ARCHIVO_CSV = "data/libros.csv"

async def extraer_datos_ficha(page, url_libro):
    """Visita la ficha del libro y extrae los metadatos completos."""
    try:
        # entramos a la pagina del libro y esperamos que cargue
        await page.goto(url_libro, wait_until="domcontentloaded")
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # agarramos el titulo, si no hay le ponemos None
        nodo_titulo = soup.select_one('div#title h1')
        if nodo_titulo:
            titulo = nodo_titulo.get_text(strip=True)
        else:
            titulo = None
            
        # sacamos los autores y los armamos en una lista 
        lista_autores = []
        nodos_autores = soup.select('div#autor a')
        for a in nodos_autores:
            texto_autor = a.get_text(strip=True)
            lista_autores.append(texto_autor)
            
        # lo mismo para los generos
        lista_generos = []
        nodos_generos = soup.select('div#genero a')
        for a in nodos_generos:
            texto_genero = a.get_text(strip=True)
            lista_generos.append(texto_genero)
            
        # nos fijamos si pertenece a una serie, sino queda en N/A
        nodo_serie = soup.select_one('div#serie a')
        if nodo_serie:
            serie = nodo_serie.get_text(strip=True)
        else:
            serie = "N/A"
            
        # nos traemos toda la sinopsis de la pagina interna y unimos parrafos
        nodo_sinopsis = soup.select_one('div#sinopsis')
        if nodo_sinopsis:
            sinopsis = nodo_sinopsis.get_text(separator=' ', strip=True)
        else:
            sinopsis = "Sin sinopsis"
            
        return {
            "titulo": titulo,
            "autores": lista_autores,
            "generos": lista_generos,
            "serie": serie,
            "sinopsis": sinopsis,
            "url_libro": url_libro,
            "categoria_origen": CATEGORIA,
            "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"Error extrayendo {url_libro}: {e}")
        return None

async def main():
    # creamos la carpeta data por si no esta creada
    os.makedirs("data", exist_ok=True)
    
    urls_visitadas = set()
    total_extraidos = 0
    pagina_actual = 1
    
    async with async_playwright() as p:
        # levantamos el navegador en modo invisible (headless)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # iteramos hasta llegar a los 150 libros que pide el tp
        while total_extraidos < LIBROS_OBJETIVO:
            print(f"Inspeccionando listado: página {pagina_actual}...")
            try:
                # vamos a la url del listado de la pagina actual
                await page.goto(f"{URL_CATEGORIA}{pagina_actual}", wait_until="domcontentloaded")
                html_cat = await page.content()
                soup_cat = BeautifulSoup(html_cat, 'html.parser')
                
                # buscamos todos los links a las fichas
                enlaces_libros = soup_cat.select('article.card a.title')
                
                # si nos quedamos sin paginas, cortamos el while
                if not enlaces_libros:
                    print("No hay más páginas disponibles en esta categoría.")
                    break
                
                for enlace in enlaces_libros:
                    # chequeo extra por si llegamos al limite en el medio de la pagina
                    if total_extraidos >= LIBROS_OBJETIVO:
                        break
                        
                    url_libro = URL_BASE + enlace.get('href')
                    
                    # pasamos de largo si ya visitamos este link (no duplicar)
                    if url_libro in urls_visitadas:
                        continue
                        
                    # nos traemos el diccionario con la data de este libro
                    datos_libro = await extraer_datos_ficha(page, url_libro)
                    
                    # validamos que haya traido la data bien 
                    if datos_libro and datos_libro["titulo"]:
                        urls_visitadas.add(url_libro)
                        total_extraidos += 1
                        print(f"[{total_extraidos}/{LIBROS_OBJETIVO}] OK: {datos_libro['titulo']}")
                        
                        # armamos un dataframe de 1 fila y lo ponemos en el csv
                        df_incremental = pd.DataFrame([datos_libro])
                        guardar_encabezado = not os.path.exists(ARCHIVO_CSV)
                        df_incremental.to_csv(ARCHIVO_CSV, mode='a', header=guardar_encabezado, index=False, encoding='utf-8')
                        
                    # esperamos 2 segs para no saturar al server
                    await asyncio.sleep(2)
                    
            except Exception as e:
                print(f"Error procesando la página de listado {pagina_actual}: {e}")
                
            pagina_actual += 1
            
        await browser.close()
        
    print(f"\n¡Proceso finalizado! Se guardaron {total_extraidos} libros en {ARCHIVO_CSV}.")

if __name__ == "__main__":
    asyncio.run(main())
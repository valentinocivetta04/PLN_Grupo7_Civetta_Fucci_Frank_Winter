"""
scraper.py

Scraper para el Trabajo Práctico de Unidad 1 (Procesamiento del Lenguaje Natural).

Objetivo del programa
----------------------
Construir un corpus de libros a partir de la información pública disponible
en Lectulandia. El programa recorre una categoría del sitio, visita cada
ficha individual de libro, extrae sus metadatos y su sinopsis, y guarda todo
en un archivo CSV (data/libros.csv).

Herramientas utilizadas
------------------------
- Playwright: controla un navegador real (Chromium) para cargar las páginas
  tal como las vería una persona navegando, incluyendo contenido que se arma
  con JavaScript. Se usa para la NAVEGACIÓN (moverse entre páginas).
- BeautifulSoup: no navega ni descarga nada; solo interpreta el HTML que ya
  fue descargado por Playwright y permite buscar elementos dentro de él
  usando selectores CSS. Se usa para el PARSEO (extraer datos puntuales).
- pandas: se usa únicamente para dar formato tabular a cada libro extraído
  y escribirlo como una fila del CSV final.
"""

import asyncio        # permite ejecutar código asíncrono (esperar sin bloquear todo el programa)
import os              # para chequear/crear carpetas y archivos del sistema
import re              # expresiones regulares, usadas para extraer el número de serie de un texto
import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from datetime import datetime  # para registrar la fecha y hora exacta de cada extracción


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================
# Se definen acá arriba como "constantes" (en mayúsculas, por convención en
# Python) para no tener valores sueltos escritos a mano ("hardcodeados") en
# medio del código. Si mañana cambia la categoría o la cantidad de libros
# objetivo, solo hay que tocar estas líneas.

URL_BASE = "https://ww3.lectulandia.co"          # dominio base del sitio
CATEGORIA = "Clásico"                             # nombre legible de la categoría (va en el CSV)
URL_CATEGORIA = f"{URL_BASE}/genero/clasico/page/"  # URL del listado paginado de esa categoría
LIBROS_OBJETIVO = 150                             # cantidad de libros que se quiere extraer en total
ARCHIVO_CSV = "data/libros.csv"                   # ruta de salida del dataset final


async def extraer_datos_ficha(page, url_libro):
    """
    Visita la página individual (ficha) de un libro y extrae todos sus
    metadatos: título, autores, géneros, serie (y número dentro de la
    serie), sinopsis y datos de contexto de la extracción.

    Parámetros
    ----------
    page : playwright.async_api.Page
        La pestaña del navegador ya abierta, que se reutiliza para visitar
        cada ficha (evita el costo de abrir una pestaña nueva por libro).
    url_libro : str
        URL completa de la ficha del libro a visitar.

    Retorna
    -------
    dict con todos los campos del libro, o None si ocurrió un error al
    procesar esa ficha en particular (para no interrumpir todo el scraping
    por un solo libro problemático).
    """
    try:
        # --- Descarga y parseo de la página ---
        # page.goto() le dice al navegador que cargue esa URL.
        # wait_until="domcontentloaded" espera a que el HTML esté listo,
        # sin necesidad de esperar a que carguen imágenes o recursos extra
        # (más rápido que esperar la carga completa de la página).
        await page.goto(url_libro, wait_until="domcontentloaded")

        # page.content() devuelve el HTML ya renderizado de la página actual.
        html = await page.content()

        # BeautifulSoup convierte ese texto HTML en un árbol navegable de
        # elementos, sobre el cual se pueden hacer búsquedas con selectores
        # CSS (select / select_one), similares a los que se usan en CSS.
        soup = BeautifulSoup(html, 'html.parser')

        # --- Título ---
        # select_one() busca el PRIMER elemento que matchea el selector.
        # Estructura esperada: <div id="title"><h1>Nombre del libro</h1></div>
        nodo_titulo = soup.select_one('div#title h1')
        titulo = nodo_titulo.get_text(strip=True) if nodo_titulo else None
        # get_text(strip=True) extrae solo el texto visible del elemento,
        # sin las etiquetas HTML, y "strip=True" recorta espacios/saltos
        # de línea sobrantes al principio y al final.

        # --- Autores ---
        # Puede haber más de un autor, por eso se usa select() (plural),
        # que devuelve una LISTA de todos los elementos que matchean,
        # no solo el primero.
        lista_autores = [a.get_text(strip=True) for a in soup.select('div#autor a')]
        # Esto es una "list comprehension": una forma compacta de escribir
        # un for que arma una lista nueva. Es equivalente a:
        #   lista_autores = []
        #   for a in soup.select('div#autor a'):
        #       lista_autores.append(a.get_text(strip=True))

        # --- Géneros ---
        # Mismo patrón que autores: puede haber varios géneros por libro.
        lista_generos = [a.get_text(strip=True) for a in soup.select('div#genero a')]

        # --- Serie y número dentro de la serie ---
        # Estructura real del sitio (confirmada inspeccionando el HTML):
        #   <div id="serie">
        #       <span class="tagTitle">Libro 9 de: </span>
        #       <a class="dinSource">Nombre de la Serie</a>
        #   </div>
        # El div#serie directamente no existe en el HTML si el libro no
        # pertenece a ninguna serie.
        nodo_serie_div = soup.select_one('div#serie')

        if nodo_serie_div:
            # El nombre de la serie está en el link con clase "dinSource"
            nodo_serie_link = nodo_serie_div.select_one('a.dinSource')
            serie = nodo_serie_link.get_text(strip=True) if nodo_serie_link else "N/A"

            # El número de libro ("9") está mezclado como texto plano
            # dentro del <span class="tagTitle">, junto con las palabras
            # "Libro" y "de:". No hay una etiqueta HTML que aísle solo el
            # número, así que se extrae con una expresión regular (re)
            # sobre el texto completo de ese span.
            nodo_tag_title = nodo_serie_div.select_one('span.tagTitle')
            texto_tag_title = nodo_tag_title.get_text(strip=True) if nodo_tag_title else ""

            # re.search busca dentro del texto un patrón que matchee:
            # la palabra "Libro", uno o más espacios, uno o más dígitos
            # (ese grupo entre paréntesis es lo que se va a extraer),
            # más espacios y la palabra "de".
            match_numero = re.search(r'Libro\s+(\d+)\s+de', texto_tag_title)
            numero_serie = match_numero.group(1) if match_numero else "N/A"
        else:
            # El libro no pertenece a ninguna serie: ambos campos en N/A
            # para mantener consistencia en el dataset (nunca dejar un
            # campo vacío/None mezclado con otros que sí tienen texto).
            serie = "N/A"
            numero_serie = "N/A"

        # --- Sinopsis ---
        # get_text(separator=' ', strip=True) además de recortar espacios,
        # inserta un espacio entre fragmentos de texto que podrían haber
        # quedado separados por etiquetas HTML internas (por ejemplo, si
        # la sinopsis tuviera varios <p> o <br> en el medio), evitando que
        # las palabras queden pegadas entre sí.
        nodo_sinopsis = soup.select_one('div#sinopsis')
        sinopsis = nodo_sinopsis.get_text(separator=' ', strip=True) if nodo_sinopsis else "Sin sinopsis"

        # Se arma y devuelve un diccionario con todos los campos exigidos
        # por la consigna del TP, más los datos de contexto de la extracción.
        return {
            "titulo": titulo,
            "autores": lista_autores,
            "generos": lista_generos,
            "serie": serie,
            "numero_serie": numero_serie,
            "sinopsis": sinopsis,
            "url_libro": url_libro,
            "categoria_origen": CATEGORIA,
            # datetime.now() captura el momento exacto de la extracción;
            # strftime() lo formatea como texto legible (año-mes-día hora:min:seg)
            "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    except Exception as e:
        # Si algo falla al procesar ESTA ficha puntual (ej. la página no
        # respondió, o tiene una estructura inesperada), se informa el
        # error por consola pero se devuelve None en vez de detener todo
        # el programa. Así el scraping general puede seguir con el
        # próximo libro de la lista.
        print(f"Error extrayendo {url_libro}: {e}")
        return None


async def main():
    """
    Función principal: orquesta todo el proceso de scraping.

    Flujo general:
    1. Prepara la carpeta y el archivo de salida (borrando el CSV de una
       corrida anterior, si existe).
    2. Abre un navegador Chromium en modo headless (sin ventana visible).
    3. Recorre el listado de la categoría, página por página.
    4. Por cada libro nuevo encontrado en el listado, visita su ficha y
       extrae sus datos.
    5. Guarda cada libro en el CSV de forma incremental (fila por fila),
       hasta alcanzar la cantidad objetivo o quedarse sin páginas.
    """

    # os.makedirs(..., exist_ok=True) crea la carpeta "data" si no existe
    # todavía; si ya existe, no hace nada y no tira error (gracias a
    # exist_ok=True).
    os.makedirs("data", exist_ok=True)

    # Si ya existe un CSV de una ejecución anterior del script, se elimina
    # antes de arrancar. Esto asegura que cada corrida genere el dataset
    # desde cero, en vez de ir acumulando filas de corridas viejas.
    if os.path.exists(ARCHIVO_CSV):
        os.remove(ARCHIVO_CSV)
        print(f"Archivo {ARCHIVO_CSV} existente eliminado. Se generará uno nuevo.")

    # Set (conjunto) que guarda las URLs de libros ya procesados, para
    # evitar guardar el mismo libro dos veces si aparece repetido en el
    # listado. Se usa un set (y no una lista) porque comprobar si un
    # elemento ya está adentro es mucho más rápido en un set.
    urls_visitadas = set()
    total_extraidos = 0
    pagina_actual = 1

    # async_playwright() es el punto de entrada de Playwright en su modo
    # asíncrono. El "async with" se asegura de que el navegador se cierre
    # correctamente al terminar, incluso si ocurre un error en el medio.
    async with async_playwright() as p:

        # Se inicia un navegador Chromium. headless=True significa que el
        # navegador corre "invisible", sin abrir ninguna ventana gráfica
        # (más rápido y liviano, ideal para scraping automatizado).
        browser = await p.chromium.launch(headless=True)

        # Un "context" es como un perfil de navegación aislado (similar a
        # una ventana de incógnito). new_page() abre una pestaña dentro
        # de ese contexto, que es la que se va a reutilizar para todas
        # las páginas que se visiten.
        context = await browser.new_context()
        page = await context.new_page()

        # Bucle principal: sigue recorriendo páginas del listado hasta
        # juntar la cantidad de libros objetivo, o hasta quedarse sin
        # páginas nuevas para recorrer.
        while total_extraidos < LIBROS_OBJETIVO:
            print(f"Inspeccionando listado: página {pagina_actual}...")
            try:
                # Se arma la URL de la página de listado actual y se carga.
                await page.goto(f"{URL_CATEGORIA}{pagina_actual}", wait_until="domcontentloaded")
                html_cat = await page.content()
                soup_cat = BeautifulSoup(html_cat, 'html.parser')

                # Se buscan todos los links a fichas de libros dentro de
                # cada "card" (tarjeta) del listado.
                enlaces_libros = soup_cat.select('article.card a.title')

                # Si el selector no encuentra ningún link, se interpreta
                # que ya no hay más páginas disponibles en la categoría
                # (se llegó al final de la paginación), y se corta el
                # bucle principal con "break".
                if not enlaces_libros:
                    print("No hay más páginas disponibles en esta categoría.")
                    break

                # Se recorre cada link encontrado en la página de listado.
                for enlace in enlaces_libros:

                    # Chequeo de seguridad: si ya se alcanzó el objetivo a
                    # mitad de una página (no hace falta terminarla entera),
                    # se corta el for.
                    if total_extraidos >= LIBROS_OBJETIVO:
                        break

                    # El atributo href del link suele ser una ruta relativa
                    # (ej. "/libro/nombre/"), por eso se le antepone la URL
                    # base del sitio para armar la URL completa y válida.
                    url_libro = URL_BASE + enlace.get('href')

                    # Si esta URL ya fue procesada antes (el libro apareció
                    # repetido en el listado, algo común en sitios con
                    # paginación), se salta directamente al siguiente link
                    # sin volver a visitarla ni contarla de nuevo.
                    if url_libro in urls_visitadas:
                        continue

                    # Se visita la ficha del libro y se extraen sus datos
                    # usando la función definida más arriba.
                    datos_libro = await extraer_datos_ficha(page, url_libro)

                    # Solo se guarda el libro si la extracción no falló
                    # (datos_libro no es None) Y si logró obtener al menos
                    # el título (se considera el campo mínimo indispensable
                    # para que el registro sea válido).
                    if datos_libro and datos_libro["titulo"]:
                        urls_visitadas.add(url_libro)
                        total_extraidos += 1
                        print(f"[{total_extraidos}/{LIBROS_OBJETIVO}] OK: {datos_libro['titulo']}")

                        # Se arma un DataFrame de pandas con una sola fila
                        # (el libro recién extraído). Un DataFrame es la
                        # estructura de tabla que usa pandas internamente.
                        df_incremental = pd.DataFrame([datos_libro])

                        # Se decide si hay que escribir el encabezado
                        # (nombres de columnas) en esta escritura: solo la
                        # primera vez, cuando el archivo todavía no existe.
                        guardar_encabezado = not os.path.exists(ARCHIVO_CSV)

                        # to_csv con mode='a' (append/agregar) escribe esta
                        # fila al final del archivo sin borrar lo que ya
                        # había, logrando así el guardado INCREMENTAL: si
                        # el script se corta a mitad de camino, no se pierde
                        # el trabajo ya hecho hasta ese punto.
                        df_incremental.to_csv(
                            ARCHIVO_CSV,
                            mode='a',
                            header=guardar_encabezado,
                            index=False,          # no guarda el índice numérico de pandas como columna
                            encoding='utf-8'      # asegura que tildes y ñ se guarden correctamente
                        )

                    # Pausa entre libro y libro para no saturar al servidor
                    # del sitio con pedidos demasiado seguidos (buena
                    # práctica ética/técnica de scraping).
                    await asyncio.sleep(2)

            except Exception as e:
                # Si algo falla al procesar toda una página de listado
                # (no una ficha individual), se informa el error pero se
                # continúa con la página siguiente en vez de cortar todo
                # el programa.
                print(f"Error procesando la página de listado {pagina_actual}: {e}")

            # Se avanza a la siguiente página del listado, tanto si la
            # actual se procesó bien como si tuvo un error.
            pagina_actual += 1

        # Se cierra el navegador al terminar el bucle principal, liberando
        # los recursos del sistema que estaba usando.
        await browser.close()

    print(f"\n¡Proceso finalizado! Se guardaron {total_extraidos} libros en {ARCHIVO_CSV}.")


# Este bloque solo se ejecuta si el archivo se corre directamente
# (ej. "python scraper.py"), y no si se lo importa como módulo desde otro
# script. asyncio.run() es la forma estándar de arrancar una función
# asíncrona (async def) como punto de entrada de un programa.
if __name__ == "__main__":
    asyncio.run(main())